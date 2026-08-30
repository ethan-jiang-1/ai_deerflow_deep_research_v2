# BUG-063: HITL interrupt 挂起被 journal 记为 failure_category=internal.unexpected

> 严重级别: P2 | 发现: 2026-08-30 | 状态: 活跃
> 发现场景: 020 战役 Stage B1 实跑监控（两个 bundle 交叉验证）

## 症状

hitl1 发出 interrupt 等真人回答（完全正常的挂起）时，journal 把该 attempt
记成 `outcome=failed` + `failure_category=internal.unexpected` +
`worker_failure_category=unknown`。读 journal 的人/agent 会把"等人"误读成
"内部意外故障"——2026-08-30 实跑监控中实际发生了这次误读（同一个
attempt_id 先 "failed"，三分钟后同一 attempt_id 重新 started → completed）。

## 证据（两个 bundle 一致复现）

- 第 1 跑 `b_l_W3Z6jthJlZwk0G9ANJMOzQr-acZEW26q1aHn9teZ4`：
  `05:19:57 g0-hitl1-a2 failed failure_category=internal.unexpected`、
  `05:20:30 g0-hitl1-a3 failed failure_category=internal.unexpected`——
  均为正常挂起点，后续同 attempt 恢复并 completed；
- 第 2 跑 `b_yFAvXIr8zct6c8sraXXuDcIUhjhtpmA6M-tOJ-0jCeU`：
  `06:11:02 g0-hitl1-a2 failed internal.unexpected` →
  `06:14:10 g0-hitl1-a2 started → completed`（**同一 attempt_id 复活**），
  随后 `06:14:10 g0-hitl1-a3 failed internal.unexpected` 同款；
- Stage A fixture 观察已记录过"首个 attempt 记 failed 后 retry completed
  是 interrupt 挂起-恢复的记账形态"（handoff-020），但当时未注意它带着
  `internal.unexpected` 这个误导性 failure_category。

## 根因（待 change 内确认）

journal 对 interrupt 挂起的 attempt 关闭记账时，把"挂起"映射成了
`internal.unexpected` 失败类别（且 `worker_failure_category=unknown`），
没有区分"awaiting human（正常挂起）"与"真实内部异常"。诊断口径上，
正常人机等待与真故障共用同一失败标签，journal 分诊不可用。

## 复现

任一 hitl1 interrupt 跑次（fixture 即可，零凭证）：
`make demo-tui-fixture`，起 run 后不回答，读 bundle `diagnostics/
events.jsonl`——挂起 attempt 即带 `failure_category=internal.unexpected`。

## 修复关联

未开始。观测性/诊断口径修复（P2，不阻断主链路）；可与 journal fact
schema 的 closed observation fact 讨论合流（plan v4 已推迟的 capability
归因议题同族，若做可一并考虑挂起语义）。独立小 change 即可，勿与
BUG-062 混同。
