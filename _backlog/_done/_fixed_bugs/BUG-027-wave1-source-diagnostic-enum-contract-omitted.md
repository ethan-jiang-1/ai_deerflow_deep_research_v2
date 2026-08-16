# BUG-027: Wave1 SourceDiagnostic 提示词漏掉枚举契约

> 严重级别: P1 | 发现: 2026-08-15 | 状态: 已修复（2026-08-16）

## 症状

真实 Wave1 的 12 个 worker submission 都被接纳，但其后没有生成任何
`source-diagnostic.json` review artifact。安全解码 checkpoint 发现 12 份候选 JSON；它们的
结构大体有效，却使用了 `high`、`medium` 等不被 `materiality` 字段接受的值，最终使
`wave1_review_presence` gate 失败。

## 根因

SourceDiagnostic 的结构化输出契约要求 `trust_tier` 为 `high`、`medium`、`low` 或
`untrusted`，`materiality` 为 `primary`、`secondary` 或 `peripheral`。原提示词只列字段名，
没有列出闭合枚举、也未说明 `source_ids` 与 `sources` 的顺序关系。模型因此产生了 JSON，
但不是可接纳的 JSON。

## 复现

对 Wave1 evidence submission 调用原 critic prompt，并提供其来源诊断输出。将模型返回的
`materiality: "high"` 交给 SourceDiagnostic 验证，验证失败且 review artifact 不会落盘。

## 修复关联

`graph/nodes/wave1/prompts.py` 已补充允许值和顺序要求，
`tests/unit/test_wave1_critic_prompts.py` 已补充契约断言。还需跑聚焦测试，并和 BUG-029 一起
验证非法结果的可诊断性。

2026-08-16 验证：`tests/unit/test_wave1_critic_prompts.py` 10 例全过（枚举与顺序契约断言）。
"非法结果可诊断性"属于 BUG-029 的新 change（诊断事件），由该卡单独跟踪。
