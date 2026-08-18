# BUG-050: 节点级 exhausted 直接 blocked，绕过 gate 降级语义——runbook 5.1 的"降级交付"承诺两次真实 run 均 0 兑现

> 严重级别: P1 | 发现: 2026-08-18 | 状态: 活跃

## 症状

runbook-003 §5.1（BUG-035 + BUG-044/046 修复后的验收语义）承诺："wave2 gate 预算耗尽时
**首次**降级为 degraded pass，run 继续走 hitl2 → readiness → final_delivery，终态
completed，RESULT: PASS"。实际两次完整失败 run 均未发生降级：

- **run 2**（b_fTetY-…，2026-08-18 21:30 terminal）：`wave2_synthesis` a5 被
  `per_call_output_cap` 打断 → 节点级 `_exhausted_update` → blocked。state 中
  `degraded_decisions` 为 None（gate 降级标记从未写入）。
- **run 3**（b_Ameegc4A…，2026-08-18 21:54 terminal）：pre-model ValidationError →
  节点级 `_exhausted_update` → blocked，同样无降级。

## 根因

`degraded_pass_on_exhaustion=True`（real_gates.py wave2 gate 定义）只覆盖 **GATE**
阻塞路径（gate 规则不满足且 repair 预算耗尽）。但 `wave2_synthesis/node.py` 的
`_exhausted_update`（节点内预算事故/InvocationFailure/校验失败）**直接写 terminal
blocked**，控制流根本不回到 gate——降级语义对节点级失败完全不生效。

也就是说：真实 run 里 wave2 失败的主路径（模型调用层面的预算/输出/校验事故）恰好
都在降级语义覆盖不到的那一侧。**honest gap 降级交付目前在真实 003 里是纸面机制。**

（注：run 2/3 的 bundle 已被后续 run 清理销毁，见 BUG-052；本卡数字来自排障时摘录。）

## 复现

任一 wave2 节点级失败（如触发 per_call_output_cap / candidate_invalid）即复现：
terminal 直接 blocked，state 无 `degraded_decisions`，无 final/report.md。

## 修复关联

待讨论（设计决策，不是单纯补丁）：节点级 exhausted 是否应把"可降级"的失败类别
（预算类、非结构性的输出类）交还 gate 走 degraded-pass，还是 runbook 5.1 的承诺
范围需要收窄为"仅 gate 路径"。涉及 lifecycle 语义，建议开 openspec change 评审。

## 修复关联

已由 change `honest-degraded-delivery` 落地（2026-08-18）：实现与回归见该
change 的 tasks/design；真实 003 复跑验证见 runbook §5.1/§7。
