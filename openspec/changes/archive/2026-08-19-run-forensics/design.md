# Design: run-forensics

## Context

BUG-048 排障实录：四类"系统已知道"的事实不进事件流——admission 操作数、策略
信封、critic 兜底、usage/序号。每次定位都要读源码或离线复算。

## Goals / Non-Goals

- **Goal**：五类只读观测事实进入 journal/summary；排障回到"grep 一行"。
- **Non-Goal**：零研究行为变更；不改 admission 判定本身（那是
  fix-request-envelope-coherence 的职责）；state.json/checkpoint 投影扩面
  （原第 6 项）划为 follow-up——`sync_graph_progress` 的有界投影目前无主
  spec，盲扩投影面需要一个独立的合同决定（投影哪些字段、字节上界、旧
  bundle 兼容），不应搭观测性车。

## Decisions

### D1 操作数在 middleware 计算、在 bridge 落事件

`AgentBudgetError` 增加闭集操作数属性（`operands: dict[str, int]`——
token_admission：projected_request_bytes/total_token_budget/
per_call_output_token_cap；per_call_output_cap：observed_output_tokens/cap；
total_token_budget：cumulative_tokens/budget）。bridge 的 `_record` 把
`problem` 上的 operands 并入 model_tool 事件。整数、闭集键、无请求内容——
与 REJ-007"无原始异常细节"一致。

### D2 序号是 bridge 实例内 per-attempt 计数

`_record` 调用点天然成对（started→completed/failed）。bridge 内
`dict[attempt_id, int]` 计数器，started 时分配、completed 时复用同一序号；
attempt 结束（bridge 释放）不显式清理——计数器随 bridge 生命周期有界
（attempt 数有限）。

### D3 usage 从 NodeExecutionResult 透传

`usage_metadata` 在 bridge 成功路径已可得；`_record` 在 outcome=completed 且
usage 非空时写 `usage_tokens={input,output,total}`。缺 usage → 字段缺席，
不是失败（与 REJ-006 usage_unavailable 失败类别互不混淆）。

### D4 信封快照在 summary 组装点采集

RunSummary 增 `policy_envelopes: list[{phase, policy_name,
total_token_budget, per_call_output_token_cap, max_model_calls}]`。采集点在
demo 运行组装 summary 时从已装配的策略对象读取（运行时事实，非源码默认）；
phase 未执行不出现。快照无 prompt/能力体/凭据。

### D5 兜底事件走既有 node 事件通道

readiness node 在 except 分支发 `category=node,
type=readiness_critic_fallback, reason∈{execution_failed, candidate_invalid}`。
需要区分两个 except 块（invocation 失败 vs parse/admit 失败）。事件失败被
吞（观测不改变行为，与全仓观测纪律一致）。

## Risks / Trade-offs

- [事件体积微增] → 每事件 ≤4 个整数字段；journal 上界（字节/条数）不受
  实质影响。
- [序号在 bridge 重建后归零] → bridge 生命周期 = 单节点构建期；同 attempt
  跨 bridge 实例的场景不存在（一个 attempt 一个 bridge）。
- [operands 与 BudgetStopReason 漂移] → 闭集键随 reason 一一对应，单测锁
  每种 reason 的键集。

## Migration Plan

旧 events.jsonl/summary 无新字段——读取方按字段缺席处理（journal 读取本就
宽容）。无持久化格式破坏。
