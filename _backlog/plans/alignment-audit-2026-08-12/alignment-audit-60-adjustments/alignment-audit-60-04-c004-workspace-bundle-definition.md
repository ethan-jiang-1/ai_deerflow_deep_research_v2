# C-004 - Evaluation Workspace And Bundle Definition

> Stage: 2 - `retire-stale-context-concepts`
> 类型: `UNAMBIGUOUS-RETIRE`
> 状态: **REVIEW REQUIRED**

## 调整内容到底是什么

将 `deep_research_harness/CONTEXT.md` 中 Workspace “contains Bundle”的物理从属关系，
改为 execution-scoped working directory；不在 glossary 中承诺 Workspace 与 Bundle 的
父子路径。

## 主要风险

过度抽象会丢失 execution scope；继续描述具体 layout 又会让 glossary 绑定易漂移的
实现细节。

## 可能副作用

过去依赖词典查路径的读者需要转到 owning runtime/spec；复审还可能暴露其他
sibling/containment 残留。

## 控制与停止条件

- 只修改术语事实，不修改 storage/runtime contract。
- 新发现先登记，不自动扩入本 change。
- 若定义需要改变 runtime layout 才能诚实，停止并转为 code work。

## 审阅结论

- [ ] 调整内容准确
- [ ] 风险与副作用已充分披露
- [ ] 批准进入 Stage 2 planning
- [ ] 需要修改或补充，原因：
