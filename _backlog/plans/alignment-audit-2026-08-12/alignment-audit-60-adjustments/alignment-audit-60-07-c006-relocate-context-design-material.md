# C-006 - Relocate CONTEXT Design Material

> Stage: 2 - `retire-stale-context-concepts`
> 类型: `RELOCATE-LINK-OWNER`
> 状态: **REVIEW REQUIRED**

## 调整内容到底是什么

对 `CONTEXT.md:468-541` 六个非 glossary 章节逐段分类；安全部分从 CONTEXT 移出并链接
ADR/main spec/policy，词典只保留稳定术语与 Avoid。

## 主要风险

这些章节并非全部错误。整块删除可能丢掉有效设计，尤其可能暗中删掉 A-003
Rubric/Runner 冲突的一侧证据。

## 可能副作用

信息从单页集中阅读变成按需导航，agent 的首次发现成本可能上升；错误 relocation 还会
让冲突“看不见但仍存在”。

## 控制与停止条件

- 逐段、逐句 disposition，禁止整块删除。
- A-003/A-004 相交内容原样 quarantine。
- 局部复审必须证明没有通过删除文本伪造 resolved。

## 审阅结论

- [ ] 调整内容准确
- [ ] 风险与副作用已充分披露
- [ ] 批准进入 Stage 2 planning
- [ ] 需要修改或补充，原因：
