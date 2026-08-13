# D-001 - Rubric / Runner Terminology After A-003

> Stage: 6 - `normalize-post-decision-terminology-status`
> 类型: conditional terminology sync
> 状态: **STAGE 6 PLANNING COMPLETE - APPLY NOT AUTHORIZED**

## 调整内容到底是什么

只把 Stage 4 已接受的 main-spec 决定投影到 glossary 与 ADR applicability，统一 identity,
criterion IDs, content, model-facing input 和 verdict 的用词，不再次作产品决定。

## 主要风险

术语简化可能重新合并已刻意拆开的 authority，或让 CONTEXT 单独扩大 Stage 4 的决定。

## 可能副作用

历史 ADR 和旧材料仍可能使用宽泛的 “input”；读者需要通过 applicability note 区分
historical wording 与 current contract。

## 控制与停止条件

- 每个句子追溯到 accepted requirement；无法映射的句子不改并登记。
- 若 required/current 仍不一致，必须显式显示 gap。
- A-003 已在 Stage 4 选定并同步；本文件只允许其既有决定进入 Stage 6 planning，仍不得
  以此授权 apply。

## 审阅结论

- [x] 调整内容准确：只投影 Stage 4 已接受的 metadata/content/verdict 边界。
- [x] 风险与副作用已充分披露：见 Stage 6 D-001 Adjustment Record。
- [x] 条件同步方式获准；A-003 已完成，Stage 6 planning 已获授权。
- [ ] 需要修改或补充，原因：

Stage 6 planning 的 closed occurrence allowlist、Before/After、风险、副作用、控制和
verification 记录于
`stage-6-planning/00-stage-6-planning-baseline-and-adjustment-records.md`。任何实际 glossary
或 ADR 修改仍等待单独 `APPLY` 授权。
