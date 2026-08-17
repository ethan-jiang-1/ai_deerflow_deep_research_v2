## Context

See proposal.md — Why. 现状事实（2026-08-16/17 验证）：`make_attempt_id`（`domain/lifecycle.py:501`）产出 `g{gen}-{phase}-a{n}`，消费点 `graph/builder.py:144,323`、`graph/nodes/targeted_evidence/node.py:40`；`allocate_attempt_id`（`engine/work_units/ids.py:24`）产出 `g{gen}_{phase}_w{ordinal}_a{ordinal}`，唯一匹配 `ATTEMPT_ID_RE`（`domain/work_units.py:60`）。bundle-id 正则 `^b_[A-Za-z0-9_-]{43}$` 有 6 份定义；`CONTENT_HASH_RE` 两份 + `WORK_UNIT_HASH_RE` 别名；`SANDBOX_PATH_RE == BUNDLE_REF_RE`；11 个 phase 列表 5 份。`project_lifecycle_status`（`domain/state.py:1097`）仅测试使用，非 terminal 一律返回 `SUSPENDED`，与 `runtime/bundle_lifecycle.py:854` 的真实投影（活跃即 ACTIVE）矛盾。`GATED_FIELDS`/`MAX_FAKE_*`/`dedupe_source_urls`/`serialize_research_state`/`validate_research_state`/`bundle_control._request_id`/`_pending_interrupt` 与 `engine/work_units/reducers.py`、`graph/routing.py` 无生产调用者（grep 验证）。`runtime/research.py:397-469` 的 WAVE0/WAVE1 工具集与 policy 函数 ~60 行拷贝。

## Goals / Non-Goals

**Goals:**
- 每个 canonical 标识符（bundle-id、content-hash、sandbox-path、phase 列表）在 src 中只有一个定义。
- 「attempt_id」的两种 scheme 生产者可区分命名，wire/持久化格式零变化。
- 移除全部已验证零生产调用的死代码与其仅测试的消费方。
- 投影事实单一来源：删除矛盾的测试专用投影，真实投影保持唯一。

**Non-Goals:**
- 不改变任何已持久化/已观察值的格式（`RunEvent.attempt_id`、work-unit id、bundle id 的取值形态）。
- 不拆分巨型文件（单列 follow-up）。
- 不迁移 phase 列表为 enum、不改 marker/测试目录、不碰 `tests/fixtures/`。
- 不修改 `deerflow/`。

## Decisions

### D1. 生产者改名而非统一格式

将 `make_attempt_id` 改名 `make_node_visit_id`（值格式 `g{gen}-{phase}-a{n}` 不变；`RunEvent.attempt_id`/`agent_context.attempt_id` 字段名与取值不变），并在 `lifecycle.py` 与 `engine/work_units/ids.py` 两处生产者注释各自 scheme 的语义边界与校验归属。
- 为什么不是统一格式：`RunEvent.attempt_id` 是 run-event-journal 的 wire 字段（REJ），work-unit attempt id 有 `ATTEMPT_ID_RE` 强校验（WOU-001）；统一格式会改变已观察/已持久化值，违反硬约束。改名保留全部 wire 兼容，同时消除「同名不可区分」。
- 备选「什么都不做只加注释」被否：注释无法消除 grep/IDE 层面的同名歧义。

### D2. 标识符常量单一来源

新增 `domain/identifiers.py`（或并入 `domain/lifecycle.py`——apply 时按导入面最小化选择，倾向独立模块）持有：`BUNDLE_ID_RE`、`CONTENT_HASH_RE`、`SANDBOX_PATH_RE`、`LOGICAL_PHASE_NAMES`（11 个 phase 的权威 tuple）。全部 6+2+2+5 处重复定义改为从该模块导入；`state.py` 的 `WORK_UNIT_HASH_RE` 别名删除（直接导入同一个 `CONTENT_HASH_RE`）。
- 为什么独立模块：`lifecycle.py` 已 693 行，且这些常量被 domain/engine/graph/runtime 跨层引用，独立模块导入面最小、无环依赖风险。

### D3. 投影矛盾：删除测试专用投影

删除 `project_lifecycle_status` 及其测试（`test_state_persistence.py`、`test_state_contracts.py` 中相关用例），真实投影 `result_for_state` 保持唯一。
- 为什么删除而非对齐：该函数生产零调用，其语义（非 terminal 一律 SUSPENDED）与真实投影矛盾；保留一个错误的影子投影只会在 agent 阅读时制造两套说法。属 authority-and-projections 政策覆盖的投影事实退役。

### D4. 顺序耦合：单一来源 + 可读报错

`graph/builder.py:359` 的 `tuple(loaded) != LOGICAL_NODES` 改为显式对比 registry 包序与 `LOGICAL_NODES`，报错信息列出缺失/多余/乱序项；或让 registry 直接从 `LOGICAL_NODES` 派生包序（apply 时选一，倾向后者——单一来源）。
- 为什么：现状报错「research registry order does not match topology」无法定位是哪一项、什么顺序。

### D5. 死代码：grep 零调用清单驱动

每项删除前跑全仓 grep（含 `tests/`、`scripts/`、`tests/assets`）确认零生产调用；`serialize/validate_research_state` 与 `project_lifecycle_status` 的**测试消费方在同 change 内同步删除/调整**。`engine/work_units/reducers.py`、`graph/routing.py` 整文件删除（核对 `project-structure.toml` 是否注册了这两个路径——若注册则同步移除注册行）。
- 为什么：死代码是 agent 阅读噪音；但删除必须可证（grep 清单进 tasks 完成证据）。

### D6. 去重与注释修正

`runtime/research.py` 的 WAVE0/WAVE1 合并为 `_worker_policy(policy_name, ...)` 参数化工厂（工具集 frozenset 保留一份）；修正 `middleware.py:69` docstring（实际 `return -1`）、`gate.py:142` 注释、`state.py` 模块 docstring；`real_gates.py:139` 改用常量。

## Risks / Trade-offs

- [D1 改名漏改消费点，格式混入] → 缓解：改名后全仓 grep `make_attempt_id` 必须零残留（contract 断言）；值格式由既有 REJ/WOU 契约测试锁定。
- [D2 常量收敛引入循环导入] → 缓解：独立 `domain/identifiers.py` 只 import re/typing，不依赖其他 domain 模块；apply 先改模块再逐文件替换导入。
- [D3 删除被动态引用（getattr/importlib）] → 缓解：删除前 grep 全仓含 `project_lifecycle_status` 的字符串引用；`__all__` 同步。
- [D5 删错仍被某测试间接依赖] → 缓解：`UV_OFFLINE=1 make verify` 是最终 oracle；每项删除单独跑归属测试文件。
- [project-structure.toml 注册路径与删除冲突] → 缓解：apply 时先查 toml 是否注册 `routing.py`/`reducers.py`，同 change 内同步移除并跑 `check_project_architecture.py`。

## Migration Plan

纯重构，无数据/schema 迁移。顺序：红测 contract（`test_identifier_single_sourcing.py`）→ 常量单源 → 改名 → 删投影/死代码 → 去重与注释 → 全量 verify。回滚 = revert commit（无持久化影响）。

## Open Questions

无——所有决策已在 D1-D6 定稿；apply 中的二选一（D2 模块位置、D4 实现方式）都有明确倾向与验收标准。
