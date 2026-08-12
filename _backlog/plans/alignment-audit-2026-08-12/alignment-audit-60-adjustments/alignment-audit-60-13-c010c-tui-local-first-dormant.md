# C-010.c - Dedicated TUI And Local-First Are Dormant

> Stage: 2 - `retire-stale-context-concepts`
> 类型: `RELABEL-DORMANT`
> 状态: **REVIEWED - PLANNING ONLY**

## 调整内容到底是什么

将 Dedicated Deep Research TUI 及以它为首个 scope 的 Local-First Deployment 标为
`dormant`；保留当前 Dedicated Agent + reflected tool route，也保留历史 ADR。

## 主要风险

`dormant` 可能被误读成永久取消路线，或者把 ADR 中仍有效的产品原则一并判废。

## 可能副作用

README、CONTEXT、ADR 会出现 current/planned/dormant 多种状态，导航复杂度增加；旧外部
材料仍可能继续称 TUI 为 primary。

## 控制与停止条件

- 定义 dormant 为“保留历史但无 active commitment”。
- 只增加 status/applicability，不重写 ADR 正文。
- 不删除未来重新激活该路线的可能。

## 审阅结论

- [x] 调整内容准确：2026-08-12，`make demo-tui` / `make demo-tui-fake` 保持 current
  contributor/operator visualizer；current Primary User route 是 Dedicated Agent + reflected
  `deep_research` tool。仅 dedicated Primary-User TUI 及以它为首个 scope 的 Local-First
  Deployment 标为 `dormant`。
- [x] 风险与副作用已充分披露：`dormant` 是保留历史理由和未来重启可能、但没有 active
  commitment；不把 demo TUI 或 Cognitive Evaluation 的 local evaluation surface 一并降级。
- [x] 批准进入 Stage 2 planning（不包含创建 OpenSpec change 或 apply 授权）
- [ ] 需要修改或补充，原因：
