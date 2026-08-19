# BUG-057: readiness critic 被 per_call_output_cap 截停后保守回退仍遭 gate blocked——降级通路在 readiness 不彻底

> 严重级别: P1 | 发现: 2026-08-19 | 修复: 2026-08-19 | 状态: 已修复

## 症状

真实 003 run（bundle `b_hxxd16dhKAh_hcvAVfOt4QAnQoV21HJfXf4HOOakfhY`，诊断引用
`diag_db4086f958d6e993672263ef`）：

- 前序全通（wave2_synthesis a1 一次通过、hitl2 通过、`degraded_profile=true`），
  到 readiness：
  - 事件 61：critic 模型调用 `budget.exhausted` / `per_call_output_cap`（输出超
    单次上限被截停）；
  - 事件 62：保守回退生效 `readiness_critic_fallback.execution_failed`
    （BUG-047/050 时代机制，本应保住 run）；
  - 事件 63-64：**gate 仍写 terminal `research.blocked` @ readiness**，
    `terminal_reason=gate_blocked`。
- 全部真实研究产出（wave0/wave1/wave2）不交付，`RESULT: FAIL`。
- 检查器还报告"Bundle 内 Event Journal 记录不可用"（terminal 已发布诊断引用
  时 journal 可用性行应如实显示"已创建"——与 runbook §5.1 既有口径不符，
  一并归入本卡观察）。

与 BUG-055 change（fix-final-delivery-layout-fragility）无关：该 run 未触达
final_delivery；readiness/gate 代码未被该 change 修改。

## 根因

readiness 把 critic 执行/候选观察失败保守投影成全量
`blocked_repair_required`。route owner 随即把 blocked count 投向
`repair_targeted`；但 targeted-evidence 只从 gate-owned `unresolved_gaps`
派工，gapless visit 必然 drained no-op，于是形成 readiness → targeted → wave2
→ hitl2 → readiness 自旋，直到预算或结构失败写 blocked terminal。另一个同类
入口是已采纳 blocked verdict + 空 `unresolved_gaps`。同时，run-experience 只在
存在 `terminal_incident` 的分支验证已发布 diagnostic ref；readiness 自写 blocked
terminal 没有 incident，因而错误显示 Journal unavailable。

## 复现

```bash
cd deep_research_harness
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run <root> --mode 003"
```

非必现（依赖真实模型输出长度越过 per-call cap）。确定性线索见 BUG-056 的
conformance 失败。

## 修复关联

OpenSpec change `fix-readiness-fallback-degraded-delivery`（归档：
`openspec/changes/archive/2026-08-19-fix-readiness-fallback-degraded-delivery/`）：

- 观察失败投影为 `ready_insufficient_judgment` + 固定 limitation，直接披露交付；
- admitted blocked 仅在 gap 非空且 wave2 未降级时 repair，gapless 时披露交付；
- readiness visit 与 targeted drained no-op 使用闭合 Journal 事实；
- readiness 自写 blocked terminal 使用与 incident 分支相同的已发布引用校验；
- scripted-real `readiness-cap-trip` 通过真实 bridge 的 `per_call_output_cap`
  截停，确定性证明终态 `completed`、发布 report/citation map、无 targeted spin，
  并保留 cap failure、fallback 与 readiness decision 三类事实。

验证：窄集 `104 passed`；全量 `UV_OFFLINE=1 make verify` 通过（2608 fast、
254 integration + 4 expected skips、35 workflow）。
