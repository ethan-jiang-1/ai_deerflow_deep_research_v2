# D-001 - Rubric / Runner Terminology After A-003

> Stage: 6 - `normalize-post-decision-terminology-status`
> 类型: conditional terminology sync
> 状态: **WAITING FOR A-003 DECISION**

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
- A-003 未选择前，本文件不得进入 planning 或 apply。

## 审阅结论

- [ ] 调整内容准确
- [ ] 风险与副作用已充分披露
- [ ] 条件同步方式获准；等待 A-003
- [ ] 需要修改或补充，原因：
