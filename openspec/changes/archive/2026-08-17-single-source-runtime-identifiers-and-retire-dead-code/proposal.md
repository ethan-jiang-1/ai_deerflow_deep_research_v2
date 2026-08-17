## Why

2026-08-16 的 coding-agent 友善度审查确认 domain 层存在会误导 agent 且增大静默改错风险的歧义与死重：同一名字下有两种不相容的 `attempt_id` 格式（node-visit 的 `g{gen}-{phase}-a{n}` vs work-unit 的 `g{gen}_{phase}_w{ordinal}_a{ordinal}`，只有后者匹配 `ATTEMPT_ID_RE`）；同一标识符正则与 11 个 phase 列表被定义 5-6 份；一个仅测试使用且与真实投影矛盾的 `project_lifecycle_status`；一个顺序耦合、报错不可读的 registry 检查；若干误导注释；以及多个全文件/全函数死代码。全部是机械性收敛，不改任何行为或 wire 格式。

## What Changes

- 将 node-visit 的 attempt-id 生产者 `make_attempt_id` 改名为 `make_node_visit_id`（**产出值格式与 wire 字段不变**，`RunEvent.attempt_id`/`agent_context.attempt_id` 保持原样），并在两个生产者处注释两种 scheme 的边界；`ATTEMPT_ID_RE` 校验保持只作用于 work-unit attempt id。
- 单一来源标识符常量：bundle-id 正则（6 份）、content-hash 正则（2 份+别名）、sandbox-path 正则（2 份）、11 个 phase 列表（5 份）收敛到一个 domain 常量模块，删除重复定义。
- 删除仅测试使用且与真实投影（`bundle_lifecycle.result_for_state`）矛盾的 `project_lifecycle_status` 及其测试。
- `graph/builder.py:359` 的 registry 顺序检查改为单一来源 + 可读报错。
- 删除死代码：`engine/work_units/reducers.py`、`graph/routing.py` 整文件；`GATED_FIELDS`、`MAX_FAKE_TRACE_ENTRIES`/`MAX_FAKE_REPAIR_ATTEMPTS`、`dedupe_source_urls`、`bundle_control._request_id`/`_pending_interrupt`。（apply 复核后 `serialize_research_state`/`validate_research_state` **保留**：它们是 state serde 的规范测试缝，支撑 `test_state_bounds` 的 checkpoint 边界不变量，并非误导性死重——从删除范围撤出。）
- 修正误导注释：`agents/middleware.py` docstring（None→实际 -1）、`domain/gate.py:142` 注释类型、`domain/state.py` 模块 docstring（提及已删模块）；`engine/real_gates.py:139` 魔法字符串改用 `FINAL_DELIVERY_GATE_VIEW_KEY`。
- 去重 `runtime/research.py` 的 WAVE0/WAVE1 worker policy（~60 行拷贝）为参数化工厂。

## Capabilities

### New Capabilities

（无——纯重构，无 spec 级行为变化，`.openspec.yaml` 声明 `skip_specs: true`。）

### Modified Capabilities

（无。`RunEvent.attempt_id` 的 wire 字段（run-event-journal REJ）与 work-unit attempt id 格式（work-unit-kernel WOU-001）均保持不变，仅作为相邻契约被核对。）

## Impact

- `deep_research_harness/src/deerflow_deep_research/domain/{state,lifecycle,work_units,bundle,run_observation,run_experience,tool,gate}.py`
- `deep_research_harness/src/deerflow_deep_research/engine/{real_gates.py, work_units/{ids,kernel,validation}.py}`（`work_units/reducers.py` 删除）
- `deep_research_harness/src/deerflow_deep_research/graph/{builder.py, routing.py（删除）}`
- `deep_research_harness/src/deerflow_deep_research/runtime/{bundle_control.py, research.py}`
- `deep_research_harness/src/deerflow_deep_research/agents/middleware.py`
- `deep_research_harness/src/deerflow_deep_research/graph/nodes/targeted_evidence/node.py`
- 测试：`tests/unit/test_state_persistence.py`、`tests/unit/test_state_contracts.py`、`tests/domain/test_gate.py`、`tests/unit/test_bundle.py`（随被删符号调整）；新增 `tests/contract/test_identifier_single_sourcing.py`
- `deerflow/` 不修改。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/domain/`——标识符权威与投影事实的语义核心；`engine/work_units`、`graph/builder`、`runtime/research` 是消费面。
- **Seam classification:** deterministic-guardrail 只改确定性标识符/投影/死代码与注释，不触碰任何 LLM 行为、持久化格式或 wire 契约。
- **Question:** 能否在不改变任何已持久化/已观察值格式的前提下，让「attempt_id」「bundle 标识」「phase 列表」等术语在代码里各有一个权威定义，并移除全部已验证无生产调用的死代码？
- **Necessary adjacent/external contracts:** `run-event-journal`（`RunEvent.attempt_id` wire 字段与格式不变，仅生产者改名）；`work-unit-kernel`（`ATTEMPT_ID_RE`/`WORK_ID_RE` 语义不变）；`project-structure`（`routing.py`/`reducers.py` 删除需核对 toml 注册路径——如已注册则同步移除）。
- **Evidence seam:** 新增 `tests/contract/test_identifier_single_sourcing.py`（先红后绿：断言每个 canonical 正则/phase 列表全仓仅一处定义、`make_attempt_id`/`project_lifecycle_status`/`GATED_FIELDS`/`routing`/`reducers` 不存在）；`UV_OFFLINE=1 make verify` 全绿；每项删除有 grep 零调用清单。
- **Not in scope:** 巨型文件拆分（`state.py` 1851 行等，单列 follow-up change）；更改任何持久化/观察值的格式；phase 列表升级为 enum（超出单源化）；`tests/fixtures/` 命名；`deerflow/`。
- **Triggered review policies:** change-admission, authority-and-projections
