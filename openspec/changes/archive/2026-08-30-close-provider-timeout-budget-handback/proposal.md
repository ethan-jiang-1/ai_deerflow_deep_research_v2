# Proposal: close-provider-timeout-budget-handback

## Why

2026-08-30 020 战役 B1 第 1 跑（bundle `b_l_W3Z6jthJlZwk0G9ANJMOzQr-acZEW26q1aHn9teZ4`，
BUG-062）实证：wave2_synthesis 唯一一次模型调用被 `bridge_wall_time` 掐死
（`provider.timeout`，16m22s，journal seq 42-43），该失败经现行 budget-class
判定进入"首次耗尽诚实降级继续"路径（`_budget_handback_update`，非终态），
图继续走到 readiness，才因 `synthesis_findings_unavailable` 终局 blocked——
wave0/wave1 证据完好、`max_model_calls=4` 预算只用了 1 次、无任何重试，
约 40 分钟真实研究（含真人 HITL1 交互）在最后一步作废。

根因是分类学缺口：`_is_budget_class` 只看 `finish_reason is BUDGET_EXHAUSTED`，
把 **token 耗尽（重试无意义）** 与 **wall-time/sdk provider 超时（瞬态，重试
可能成功）** 混为同一失败类。domain 已有 `ProviderTimeoutOrigin
= "bridge_wall_time_budget" | "provider_sdk_timeout"` 类型化事实
（`domain/run_observation.py:40`、`domain/workflow_outcomes.py:326`），但
没有任何 owner 消费它做恢复决策。

## What Changes

- 把 provider 超时（两个 `ProviderTimeoutOrigin`）从 budget-class 中拆出为
  **可重试瞬态类**：wave2_synthesis 的模型调用失败先走**有界重试**（在既有
  `max_model_calls` 策略包预算内，消耗 call_ordinal），重试耗尽才进入现行
  budget-handback / degrade / blocked 机器。
- 重试期间 journal 照常记录每次 model_tool attempt（ordinal 续进）；路由权
  仍在 gate——重试是 node 内的调用恢复，不新增任何 route/admission 权威。
- 非瞬态失败（token 耗尽、结构非法、内部错误）行为不变：仍走现行
  `_exhausted_update` / `_budget_handback_update` 分类处置。
- 确定性回归：注入式 provider 挂起/超时（fixture/scripted provider），证明
  "第 1 次超时 → 重试成功 → run 正常完成"与"重试耗尽 → 现行降级/阻断不变"。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave2_synthesis/` — 失败分类与调用恢复决策的 semantic owner；`_is_budget_class` 只认 `NodeFinishReason.BUDGET_EXHAUSTED`，把瞬态 provider 超时并入"首次耗尽降级放行"，无任何调用级恢复（BUG-062 现场 bundle `b_l_W3Z6…`）。
- **Seam classification:** deterministic-guardrail — 重试判定与预算边界是确定性策略（给定失败事实与 ordinal 预算，可重试与否是纯函数），无认知成分；分类输入是既有类型化事实（`ProviderTimeoutOrigin`），不新增认知面。
- **Question:** wave2_synthesis 如何把 provider 瞬态超时（`bridge_wall_time_budget` / `provider_sdk_timeout` 两 origin）识别为可重试类、在既有 `max_model_calls` 策略包预算内有界重试、耗尽后回落现行 budget-handback 处置，而不改变 gate 路由权威、不新建预算计数器、不动非瞬态失败的现行分类？
- **Necessary adjacent/external contracts:** `domain/run_observation.py`（`ProviderTimeoutOrigin` 类型化事实——超时起源足以区分可重试类：两 origin 均瞬态，答案已核）；`agents/policies.py`（`max_model_calls` 策略包——重试预算复用既有调用预算而非新增计数器，避免双预算漂移；预算执法形态在 apply 任务 3 取证）。
- **Evidence seam:** `diagnostics/events.jsonl` 的 model_tool attempt/ordinal 序列 + run-summary `policy_envelopes`（实证侧）；`tests/graph/` wave2 node 注入式 provider 超时确定性用例（门槛侧，零凭证零网络）。
- **Not in scope:** readiness 门行为（`synthesis_findings_unavailable` 阻断本身正确）；gate 路由权威与 degrade/blocked 规则；`_exhausted_update` / budget-handback 语义；跨节点通用重试框架（其他节点各自演进）；attach/resume（BUG-064 → C2）；journal schema；`deerflow/` gitlink 不改动、不 source-browse（ordinary downstream work）。
- **Triggered review policies:** workflow-outcome-review

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| provider timeout（bridge_wall_time / provider_sdk_timeout） | bridge 记录 `ProviderTimeoutOrigin`（既有类型化事实） | wave2 node 有界重试：消耗 call_ordinal，上限 = 既有 `max_model_calls` 策略包 | 重试耗尽 → 现行 budget-handback（gate 决定 degrade/blocked） | 无新增；gate 既有路由不变 | events.jsonl model_tool ordinal 序列 + 注入超时的确定性测试 |
| token 预算耗尽（非 provider 超时） | 既有 budget 事实 | 不变：`_budget_handback_update` | 不变（gate 决定） | 不变 | 既有回放 |
| 结构非法 / 内部错误 | 既有 | 不变：`_exhausted_update` | 不变 | 不变 | 既有回放 |

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `wave2-synthesis-node`: 新增/修订 requirement——provider 瞬态超时的有界重试
  与耗尽后回落既有 budget 处置；明确"provider 超时不属于首次降级直接放行的
  budget-class"。

## Impact

- **代码**：`src/deerflow_deep_research/graph/nodes/wave2_synthesis/node.py`
  （失败分类 + 重试循环）、可能的 `contracts.py`（分类谓词）；不改
  `runtime/node_agent_bridge.py` 权威（若需透传 origin 事实，只读消费）。
- **测试**：新增注入式超时的确定性用例（红→绿）；既有 wave2 回放保持绿。
- **规格**：`wave2-synthesis-node` delta（见 specs/）。
- **运行时行为变化**：真实跑中 wave2 首次 provider 挂起/超时不再导致整 run
  在 readiness 终局作废；战役主线（B1 第 3 跑）依赖此修复。
- **deerflow gitlink**：本 change 的全部下游工作既不修改也不源码浏览
  `deerflow/` gitlink；所需能力均经 `deep_research_harness` 自有层实现。
