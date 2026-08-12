# C-006 - Withdraw Broad CONTEXT Relocation

> Stage: 2 - `retire-stale-context-concepts`
> 类型: `WITHDRAWN-NO-ACTION`
> 状态: **WITHDRAWN - NO PLANNING OR APPLY WORK**

## 调整内容到底是什么

撤回原先“把 `CONTEXT.md:468-541` 的六个设计章节逐段迁出”的提议。该提议没有指出一个
确定错误，而是把“是否应让 CONTEXT 更短”的偏好误包装成对齐任务。

已经确认的具体错误仍由 C-004、C-005.a、C-005.b 和后续独立项分别处理；本项不再要求
移动、删减或链接这六段其余文字。

## 主要风险

若继续执行，会扩大 Stage 2 scope，并可能删掉对人和 agent 有用的当前上下文，尤其会
掩盖尚未决的 A-003 Rubric/Runner 语义问题。

## 可能副作用

保留现有文字意味着 CONTEXT 不会因本项变短；没有运行时、规格或文档链接副作用。以后若
发现某一段存在具体的事实错误，必须以新的、单独编号的 adjustment 审阅，不能复活本项的
宽泛迁移范围。

## 控制与停止条件

- 本项不创建 OpenSpec change task，也不产生 target edit。
- C-004/C-005 已审动作仍保持各自独立的范围和控制，不因本项撤回而扩大。
- A-003/A-004 继续隔离，直到独立产品决定；不得将撤回理解为已解决。

## 审阅结论

- [x] 原提议撤回：2026-08-12。它不是确定的错位，也不应通过一般性“精简 CONTEXT”扩大
  cleanup scope。
- [x] 不进入 Stage 2 planning 或 apply；无 target edit。
- [ ] 日后发现具体事实错误时，建立新的独立 adjustment，不复用 C-006。
