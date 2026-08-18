# BUG-054: readiness 判定与 synthesis findings 脱节——有高置信结论的证据下产出"零结论"报告计划

> 严重级别: P2 | 发现: 2026-08-18 | 状态: 活跃

## 症状

同 run 4（b_M_sAiRI1…）：`synthesis/findings.json` 含直接回答 must_answer 问题
（"What is one bounded fact about China's EV battery market in 2024?"）的高置信
finding（2024 中国动力电池装机 548.4 GWh，+41.5%，CAPBIIA/Gasgoo 来源，backing_refs
完备），但 readiness 一次通过后产出的 report plan 是 `writable_conclusions: []` +
1 条 uncertainty——**研究做出来了，交付计划却一个结论都不写**。

若 final_delivery 正常渲染（BUG-053 修复后），报告将是"Findings 空 + 1 条
Uncertainties"——runbook 003 §5 的验收（"报告是真实内容、有 claim-citation 映射"）
形同虚设：`verify` 的形状检查（report.md 存在）会 PASS，内容却为空壳。

## 根因

readiness critic 的 verdict 语义（`ready_substantive` / `ready_insufficient_judgment`
/ `blocked_repair_required`）与 materializer 的结论生成之间：`ready_insufficient_judgment`
映射为"不写结论、只记 limitation"，而 critic 判断"insufficient"时看的是**证据对问题的
完整覆盖**（2024 全年精确总量存在来源分歧 → 保守），不看"是否存在至少一条高置信、
引用完备、直接回答问题主干的部分结论"。honest-gap 语义（只披露 gap）与"部分可写
结论"（写结论 + 同时披露不确定）不兼容——现在的实现把"证据不完美"放大成
"零交付"。

## 复现

任一 honest gap 不收敛但存在高置信部分结论的 003 run：readiness pass +
`writable_conclusions: []`。

## 修复关联

待讨论：materializer 支持"部分结论 + 强制不确定项并存"（readiness critic 输出
或 synthesis findings 直接映射可写结论）；或 runbook 003 验收语义明确接受
"零结论报告"为合法 degraded 交付（需用户决策产品语义）。

## 修复关联

已由 change `honest-degraded-delivery` 落地（2026-08-18）：实现与回归见该
change 的 tasks/design；真实 003 复跑验证见 runbook §5.1/§7。
