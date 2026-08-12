# C-010.b - Support Handoff Status

> Stage: 2 - `retire-stale-context-concepts`
> 类型: `RELABEL-PLANNED`
> 状态: **REVIEW REQUIRED**

## 调整内容到底是什么

将没有 current producer/schema/public entry 的 Support Handoff 标为 `planned`；不在本
Stage 回答它能否在 Bundle loss 后留存。

## 主要风险

`planned` 容易被误读成 external retention 已获产品批准，从而暗中替 A-004 选边。

## 可能副作用

CONTEXT 会同时保留未来 capability 和未决 lifecycle 语义；这种张力是刻意披露，不是
完成态错误。

## 控制与停止条件

- capability status 与 bytes retention、supported reader、participant presentation 分开。
- 生命周期三项全部 quarantine 到 Stage 5。
- 若 wording 必须回答外部留存，停止并等待 A-004 决策。

## 审阅结论

- [ ] 调整内容准确
- [ ] 风险与副作用已充分披露
- [ ] 批准进入 Stage 2 planning
- [ ] 需要修改或补充，原因：
