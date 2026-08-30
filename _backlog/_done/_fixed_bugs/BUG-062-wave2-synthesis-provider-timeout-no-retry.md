# BUG-062: wave2_synthesis 单次 provider.timeout 无重试即全 run 终局 blocked

> 严重级别: P1 | 发现: 2026-08-30 | 状态: 活跃
> 发现场景: 020 手动 TUI 战役 Stage B1 第 1 跑（真人 HITL1 交互全部成功后）

## 症状

真人完整跑通 hitl1 交互 → topic_planning → wave0 → wave1（证据已入库）后，
wave2_synthesis 的**唯一一次**模型调用挂起 16 分 22 秒被 wall-time 预算掐死
（`provider.timeout`），节点随即按"完成"记账但**零 findings 产出**；后续
readiness 门正确检测 `synthesis_findings_unavailable` → `readiness_route:
exhausted` → 整 run 终局 `blocked`。约 40 分钟的真实研究（含真人交互与
web 证据采集）在最后合成一步作废。

## 证据（exact bundle）

`b_l_W3Z6jthJlZwk0G9ANJMOzQr-acZEW26q1aHn9teZ4`（scope
`s_WwIyPhgXRkVr6hD6Cvqi-7fOvbiehPOF_-BEke7q_7Q`，2026-08-30 13:19-13:59 本地）：

- `diagnostics/events.jsonl` seq 42-43：
  `05:42:01 model_tool started` → `05:58:23 model_tool failed`，
  `failure_category=provider.timeout`、`budget_stop_reason=bridge_wall_time`、
  `worker_failure_category=agent_invocation`——单次调用挂 16m22s；
- run-summary `policy_envelopes`：`wave2-evidence-synthesis` 明示
  `max_model_calls: 4`，实际只用了 **1** 次即失败，**没有任何重试**；
- `synthesis/` 目录为空（建 bundle 时创建后再无写入）；`work/` 无 wave2 工作单元；
- wave0/wave1 证据完好：`evidence/submissions.jsonl` 两条（2191B + 2143B，
  各带 result_hash/spec_hash 链）；
- readiness critic 自己的 `review/report-plan.json` 都写出了
  "Evidence supports a substantive answer…"（backing_claim_ids 正指向
  wave0/wave1 两条提交）——即证据足以支撑结论，缺的只是合成产物；
- seq 50：`readiness_failure_codes=['synthesis_findings_unavailable']`、
  `readiness_route='exhausted'`；seq 52 terminal
  `failure_category=research.blocked`。

## 根因（待 change 内确认）

wave2_synthesis 的模型调用失败路径**一次失败即耗尽**该 phase：尽管策略包
允许 4 次调用，`provider.timeout` 后既不重试也不降级重排队，节点带着空
findings"完成"，把单次 provider 抖动（慢/挂起）放大成整 run 终局损失。
readiness 门本身行为正确（无合成产物不得交付）——缺陷在 wave2 的失败
恢复策略，不在门。provider 慢（16 分钟不返回）是环境诱因，但"单点即死"
是产品侧结构问题。

## 复现

1. `make demo-tui-embedded-smoke` 起真实图；
2. hitl1 照 runbook-020 §3.1 应答确认；
3. 等 wave2_synthesis 期间 provider 挂起（本次为 16m22s 触发
   `bridge_wall_time`）；
4. 观察：无重试、`synthesis/` 空、readiness blocked、终态 `blocked`。

（确定性复现思路：可在 change 里用注入 provider 延迟/超时的方式替代等待
真实抖动。）

## 修复关联

未开始。按战役纪律走独立 openspec change（004 先例）；primary causal owner
候选在 graph 侧 wave2_synthesis 节点 / 模型调用重试策略，**不是** TUI 层。
方向候选：`provider.timeout` 重试（预算已有 max_model_calls=4 余量）/
合成 checkpoint 可恢复 / 挂起调用的 wall-time 预算与熔断阈值复核。
