# BUG-057: readiness critic 被 per_call_output_cap 截停后保守回退仍遭 gate blocked——降级通路在 readiness 不彻底

> 严重级别: P1 | 发现: 2026-08-19 | 状态: 活跃

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

待定位。表面链条：critic 输出超 cap（模型波动，常态）→ 保守回退产出保守
readiness 判定 → readiness gate 把回退结果判为规则失败 → repair 预算耗尽 →
blocked。疑点：保守回退的产物在 gate 规则里缺少"降级通过"通路（对照
BUG-044 在 wave2、BUG-050 在节点预算、BUG-055 在 final_delivery 的同类修复
——readiness 阶段没有等价物）。另注意 BUG-056（readiness 一致性测试在 HEAD
上 route=exhausted 而非 pass）可能是同一根因的确定性投影，诊断时一并看。

## 复现

```bash
cd deep_research_harness
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run <root> --mode 003"
```

非必现（依赖真实模型输出长度越过 per-call cap）。确定性线索见 BUG-056 的
conformance 失败。

## 修复关联

待讨论。方向：readiness 的保守回退产物应有"降级 pass"或"带披露继续"通路
（与 wave2/final_delivery 的降级语义对齐），而不是把保守判定送进 repair →
blocked；顺带核对 journal 可用性行在 blocked terminal 时的如实呈现。
