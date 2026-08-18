# BUG-048: 真实 run 观测性缺口——排障时"推断"多于"读到"的四项改进

> 严重级别: P2 | 发现: 2026-08-18 | 状态: 活跃

## 症状

以 2026-08-18 三次真实 003 run（b_CsmLjjF9…/b_fTetY-…/b_Ameegc4A…）为样本排障时，
事件与诊断信息存在四处缺口，每处都让定位从"grep 一行"变成"写脚本推断"：

1. **admission 拒绝事件不带算术操作数**：事件只有 `budget_stop_reason: token_admission`，
   而 middleware 当时已算出 `projected/budget/cap` 三个数却未外抛（BUG-047 定位时
   需离线复算请求字节数才能重建算式）。
2. **无策略信封快照**：readiness 的 total_token_budget 是 8192 这一事实需读源码确认；
   run-summary 不含各 phase 的 policy envelope。
3. **critic 保守兜底无节点级事件**：readiness 因 admission 拒绝走
   `conservative_readiness_output` 路由 `repair_targeted` 4 轮，事件层不可见
   "critic 从未真正运行"，只藏在 `limitation_note` 文本里。
4. **成功调用无 token 用量事件**：`model_tool completed` 不带
   `total_tokens/output_tokens`（usage_metadata 有值未记），预算校准无据可查。
5. **state.json 与 graph checkpoint 不自洽**：`state.json` 中
   `accepted_submission_refs`/`wave1_open_questions` 等为 null，真实值只在
   graph.sqlite 的合并 checkpoint 里（排障时需手工解码 msgpack 才能恢复现场）。
6. **model_tool 事件无调用序号**：同一 attempt 内多次模型调用（wave1 一轮 3 次）
   的事件只有 started/completed 对，无法区分是第几次调用、无法与请求内容对应。

另（并入本卡，BUG-049 排障时暴露）：**pre-model 校验失败的类别兜底过宽**——
pydantic `ValidationError` 落入 `candidate_invalid` 桶，丢失具体消息
（"objective 超 16384 字符"被归类为 candidate invalid），类别应携带具体失败原因。

## 根因

观测事件按"最小安全事实"设计，但排障所需的**已算出/已知道**的操作数与快照
没有进入事件流；这不是行为 bug，是可诊断性缺口。

## 复现

任一真实 003 run 的 `diagnostics/events.jsonl` + 排障过程：上述四类信息均需
读源码或离线复算才能恢复。

## 修复关联

待立窄 change（不阻塞 003 主线）：
1. `AgentBudgetError` detail/事件字段带 `projected_bytes/total_budget/output_cap`；
2. run-summary 增补各 phase policy envelope 快照（name/total_token_budget/output_cap）；
3. readiness 增加 `readiness_critic_fallback` 类别事件；
4. `model_tool completed` 事件带 usage tokens；
5. `_pre_model_problem`/bridge 对 pydantic ValidationError 保留具体消息。

## 修复关联

- 第 1 项（admission 操作数）：`openspec/changes/run-forensics/` —
  `AgentBudgetError.operands`（token_admission：projected_request_bytes/
  total_token_budget/per_call_output_token_cap；per_call_output_cap：observed/cap；
  total_token_budget：cumulative/budget），bridge 落入 model_tool 事件
  `budget_operands`（RunEvent 封闭校验：≤4 键、非负整数、仅随 budget_stop_reason）。
- 第 2 项（策略信封快照）：同 change — `policy_envelope_table()`（research.py，
  纯构造一次投影）→ `_journal_envelope` 注入 → store 构造参数
  `policy_envelopes` → RunSummary `policy_envelopes`（仅含有 model_tool 事实的
  phase；裸 store publish 从旧 summary 保留合并，不抹除）。
- 第 3 项（critic 兜底事件）：同 change — readiness node 区分
  `execution_failed`/`candidate_invalid` 两条路径，发 node 级事件
  `failure_category=readiness_critic_fallback.<reason>`；成功路径零事件；
  记录失败不改投影/route/修复计数。
- 第 4 项（usage tokens）：同 change — bridge `_usage_tokens` 从成功响应
  usage_metadata 抽取 `{input,output,total}`（UsageTokensEvidence 封闭校验
  total=in+out），仅随 completed 事件；缺 usage 是字段缺席不是失败。
- 第 5 项（ValidationError 类别保真）：已并入 `openspec/changes/fix-request-envelope-coherence/`（落地）。
- 第 6 项（调用序号）：同 change — bridge 实例内 per-attempt 计数
  `call_ordinal`，started 分配、completed/failed 复用；每个 model_tool 事件携带。
- 第 7 项（state.json/checkpoint 自洽投影）：**未修** — `sync_graph_progress`
  的有界投影无主 spec，划为 follow-up（见 run-forensics design.md Non-Goals）。
