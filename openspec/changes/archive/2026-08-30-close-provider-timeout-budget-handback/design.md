# Design: close-provider-timeout-budget-handback

## Context

实证现场（bundle `b_l_W3Z6…`，2026-08-30，全证据在 BUG-062）：

- journal seq 42-43：wave2 唯一一次模型调用 `started → failed`
  （`failure_category=provider.timeout`、`budget_stop_reason=bridge_wall_time`、
  `worker_failure_category=agent_invocation`，耗时 16m22s）；
- seq 44：wave2 node `completed`（execution_trace 证实 wave2 只经过一次、
  无终态写入）→ hitl2 → readiness → readiness 以
  `synthesis_findings_unavailable` 终局 blocked（seq 50/52）；
- run-summary `policy_envelopes.wave2-evidence-synthesis.max_model_calls=4`，
  实际消耗 1；
- domain 既有类型化事实：`ProviderTimeoutOrigin =
  "bridge_wall_time_budget" | "provider_sdk_timeout"`
  （`domain/run_observation.py:40`；`workflow_outcomes.py::_timeout_origin`
  把 `provider_observation` 映射为 origin 或 None）；
- wave2 node 既有失败处置：`InvocationFailure` → `_is_budget_class`
  （仅 `NodeFinishReason.BUDGET_EXHAUSTED`）→ handback；否则
  `_exhausted_update`（终态 blocked）；`graph/builder.py::observed_run`
  的 catch-all 只兜未分类异常。

结论：provider 超时事实已经流到节点决策点（`outcome.problem.provider_observation`），
但没有人消费它——瞬态可重试的失败被并入 budget-class 一次性"降级放行/阻断"，
且没有任何调用级恢复。触发 policy：`workflow-outcome-review`（proposal 已附）、
node-agent profile（retry 属其管辖）。

## Goals / Non-Goals

**Goals:**

- provider 瞬态超时（两个 origin）在 wave2_synthesis 内获得有界调用恢复
  （重试消耗既有 `max_model_calls` 预算），重试耗尽回落现行 budget 处置；
- 路由/admission 权威零变化：gate 独占，重试是 node 内调用恢复；
- 分类谓词复用既有类型化事实，不新增 fact/schema/journal 变更；
- 全部行为确定性可测（注入式超时，零凭证零网络）。

**Non-Goals:**

- 不改 readiness 门、不改 gate 规则、不改 `_exhausted_update`/handback 语义；
- 不建跨节点通用重试框架（其他节点各自演进）；
- 不做进程死亡/attach 恢复（BUG-064 → C2）、不改 journal schema；
- 不修改/浏览 `deerflow/` gitlink。

## Decisions

### D1 分类谓词：消费既有 timeout-origin 事实（非新增分类学）

`_is_provider_transient(outcome: InvocationFailure) -> bool`：
timeout origin = `workflow_outcomes` 既有映射
（`_timeout_origin(problem.provider_observation)`，两 provider-timeout origin
之一即瞬态）。`_timeout_origin` 今日是模块私有函数——本 change 将其提升为
`workflow_outcomes` 的公开导出（改名/导出，不复制实现、不改语义），wave2
包导入公开名。非瞬态 = 其余一切（token 耗尽、结构非法、内部错误），保持
现行分类逐字不变。

- 理由：类型化事实已存在且已流到决策点；新增枚举只会制造第二套口径。
- 替代方案（否决）：扩展 `_is_budget_class` 加 origin 分支——会让
  budget-class 同时承担"不可重试耗尽"与"可重试瞬态"两种语义，命名与
  行为分裂。

### D2 重试循环：node 内有界循环，预算权威保持在调用层

wave2 node 的合成调用（以及同形的 repair 调用点）包一层
`invoke_with_provider_retry`：`provider-transient` 失败 → 重试同一受约束
invocation；退出条件 = 非 transient 结果（成功 / budget-class / 其他失败）。

- **重试上界不新建计数器**：每次 `run_agent` 消耗一个 call ordinal，
  `max_model_calls` 预算由既有策略层执法；预算耗尽时下一次 invocation
  以 budget-class 失败 → 进入现行 handback。节点不复制预算记账。
- **apply 前置验证（任务 3）**：确认策略层确实在预算耗尽时以失败结果
  （而非别的方式）拒绝调用；若证据不成立，退化为 node 侧 ordinal 上界
  （读取当次 envelope），并在 tasks 记录偏离理由。
- 理由：预算权威单点（策略层），节点循环无自造状态；
- `asyncio.CancelledError` 与取消语义不在重试捕获范围内（透传）。

### D3 作用域：wave2 包内私有，不进 shared 层

谓词与循环放 `graph/nodes/wave2_synthesis/`（contracts/node），不进
`graph/components/` 或 `engine/`——直到第二个节点撞出同类 bug 再提炼
（YAGNI；与"primary causal owner 最小模块"纪律一致）。

### D4 journal / summary：零改动

每次 `run_agent` 本就独立记账（ordinal 续进）；重试自然产生
`ordinal n failed → ordinal n+1 …` 序列。WSN-012 的可观察性 scenario 由
既有事实满足，不需要新事件类别。

## Risks / Trade-offs

- **R1 策略层预算执法形态——已取证解决（polish 阶段）**：
  `agents/middleware.py::awrap_model_call`（:121-128）在
  `model_calls >= max_model_calls` 时 `raise AgentBudgetError(
  NodeFinishReason.BUDGET_EXHAUSTED, "maximum model calls reached",
  BudgetStopReason.MODEL_CALL_LIMIT)`；该错误无 provider_observation/
  timeout origin → `_is_provider_transient` 判否 → 现行 `_is_budget_class`
  → handback。重试循环因此**确定性终止**，无需 node 侧备用上界
  （任务 3 降级为证据锁定）。
- **R2 每次重试获得新的 wall-time 窗口**（deadline 是 per-invocation）：
  最坏情况总时长 = 重试次数 × 窗口；接受（真实跑中 provider 挂死的
  替代方案是整 run 作废，更贵）；journal 如实记录各次耗时。
- **R3 agent 内部既有重试叠加——已取证排除（polish 阶段）**：
  `awrap_model_call` 是"检查 → 调用 → 计数"（:173 `model_calls += 1`），
  无内部重试循环；BUG-062 现场（单次失败即终局）与之互证。重试只存在于
  本 change 新增的 node 层循环，单层无叠加。
- **R4 回放/既有测试兼容**：budget-handback 与 exhausted 回放必须逐字
  不变（Non-Goal 承诺），任何漂移 = 实现错误。
- **R5 全部重试耗尽后的终局仍可能是 readiness blocked**（degrade-honestly
  后零 findings）：这是既有 gate/readiness 契约的既定行为，本 change 的
  收益是"瞬态失败获得 N-1 次恢复机会"；provider 持续死亡时诚实阻断是
  正确形态（C1 Non-Goal 边界，不做 gate/readiness 语义变更）。
