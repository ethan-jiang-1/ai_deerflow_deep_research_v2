# C-005.a - Retire Completed-Work Tense

> Stage: 2 - `retire-stale-context-concepts`
> 类型: `UNAMBIGUOUS-RETIRE`
> 状态: **REVIEW REQUIRED**

## 调整内容到底是什么

移除 “new Cognitive Evaluation Suite” 和 “V1 structural change must...” 等仍把已落地
结构写成未来任务的措辞，改链 current structure/spec owner。

## 主要风险

整段删除可能连同仍有效的 control/run-data separation invariant 一起丢失。

## 可能副作用

CONTEXT 会变短，读者需要沿链接理解结构；如果 owner link 选择错误，会把旧 duplication
换成新的错误 owner。

## 控制与停止条件

- 只退役实施时态；有效术语保留或链接 canonical owner。
- 验证所有相对链接。
- 若某句同时定义当前 invariant 和历史实施任务，拆句后再审，不整体删除。

## 审阅结论

- [ ] 调整内容准确
- [ ] 风险与副作用已充分披露
- [ ] 批准进入 Stage 2 planning
- [ ] 需要修改或补充，原因：
