# C-005.a - Retire Completed-Work Tense

> Stage: 2 - `retire-stale-context-concepts`
> 类型: `UNAMBIGUOUS-RETIRE`
> 状态: **REVIEWED - PLANNING ONLY; NOT AUTHORIZED FOR APPLY**

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

- [x] 调整内容准确：2026-08-12，`evals/control/`、被忽略的 `evals/runs/`、
  `runtime/evaluation/` 与 `tests/eval/` 都是当前已落地边界；只有“new”及“must
  explicitly update”的实施时态过期。
- [x] 风险与副作用已充分披露：不得因清理时态整段删除 control/run-data separation
  invariant，必须保留或链接当前 owner。
- [x] 批准进入 Stage 2 planning（不包含创建 OpenSpec change 或 apply 授权）
- [ ] 需要修改或补充，原因：
