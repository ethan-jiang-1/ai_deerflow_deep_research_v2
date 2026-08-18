## Why

BUG-048（第 5 项 ValidationError 类别保真已并入 fix-request-envelope-coherence；
BUG-052 已单独落地 preserve-failed-run-bundles）。2026-08-18 四次真实 003 run
排障时，五类关键事实"系统已算出/已知道"却没有进入事件流，定位从"grep 一行"
退化成"写脚本推断"：

1. admission/预算停止事件只有 `budget_stop_reason`，middleware 当时已算出的
   `projected/budget/cap` 三个操作数未外抛（BUG-047 定位需离线复算请求字节）。
2. run-summary 不含各 phase 策略信封快照——readiness 的 total_token_budget
   是多少要读源码才知道。
3. readiness critic 走保守兜底（`conservative_readiness_output`）时无节点级
   事件，"critic 从未真正运行"只藏在 `limitation_note` 文本里（BUG-047 期间
   4 轮兜底完全不可见）。
4. `model_tool completed` 不带 usage tokens（usage_metadata 有值未记），预算
   校准无据可查。
5. 同一 attempt 多次模型调用（wave1 一轮 3 次）的事件无调用序号，无法与请求
   内容对应。

（原第 6 项 state.json/checkpoint 自洽：该投影面（`sync_graph_progress`）当前
无主 spec，本 change 划为 follow-up 并在 design 记录理由，不盲开新 spec 面。）

全部**零研究行为变更**：只让已存在的安全事实可见。

## What Changes

- `agents/middleware.py`：`AgentBudgetError` 携带闭集安全操作数
  （`projected_bytes`/`total_budget`/`output_cap`，token_admission 类）；
  bridge `_record` 把操作数写入 model_tool 事件（非预算事件不带）。
- `runtime/node_agent_bridge.py`：`model_tool` 事件增 `usage_tokens`
  （completed 且 usage 可得时）与 `call_ordinal`（bridge 实例内 per-attempt
  递增计数，started/completed 成对对应）。
- `runtime/run_observation.py`：RunSummary 增 `policy_envelopes` 快照
  （per phase：name/total_token_budget/per_call_output_token_cap/max_model_calls），
  由 demo 运行组装时从策略装配处采集。
- `graph/nodes/readiness/node.py`：critic 走保守兜底时发一条节点级
  `readiness_critic_fallback` 事件（closed reason：execution_failed /
  candidate_invalid），成功路径不发。

## Capabilities

### New Capabilities
- 无

### Modified Capabilities
- `run-event-journal`：REJ-007 增补——预算停止事件 SHALL 携带闭集操作数；
  model_tool 事件 SHALL 携带 usage tokens（可得时）与 per-attempt 调用序号。
- `runtime-observability`：run-summary SHALL 含各 phase 策略信封快照。
- `readiness-node`：critic 保守兜底 SHALL 发一条 closed-reason 节点级事件。

## Impact

- 代码：`agents/middleware.py`、`runtime/node_agent_bridge.py`、
  `runtime/run_observation.py`、`graph/nodes/readiness/node.py`。
- 测试：各 seam 就近单测（操作数落事件、序号单调、usage 透传、兜底事件、
  state.json 投影字段）。
- 行为：零——事件与摘要的新增字段全部为只读观测事实；不加事件不改变
  研究结果路径（除兜底事件外均为既有事件的字段增补）。
