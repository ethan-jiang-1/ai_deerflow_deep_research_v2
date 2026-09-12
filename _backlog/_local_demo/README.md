# _local_demo — 已迁移（保留为冻结的战役证据）

> **本目录的活手册已迁出。** 本地跑法阶梯（001–004 / 010 / 020 / 030 / 031）
> 现位于 [`deep_research_harness/docs/runbooks/`](../../deep_research_harness/docs/runbooks/README.md)，
> 与 `docs/` 其余 operator 文档同处正常阅读路径。
>
> 本目录按 `_backlog` 约定（`_` 前缀 = 已归档 / 长期留存）**只保留冻结的战役证据**，
> coding agent 默认不读，除非要查 020 战役的历史 provenance：
>
> - [`handoff-020-tui-manual.md`](handoff-020-tui-manual.md) — 020 手动 TUI 战役交接记录
> - `.evidence/` — 本地证据快照（git-ignored）

## 为什么迁走

`_local_demo` 曾是 `_` 前缀目录，却在持续活跃编辑——与 `_backlog/README.md`
「`_` = 已结束 / 默认忽略」的约定直接冲突。runbook 本质是 **operator 文档**，
不是待办工作件；迁入 `docs/runbooks/` 后，agent 靠**已声明的阅读路径**
（`docs/README.md`、`harness/README.md`、`AGENTS.md` 信息图、`COMMANDS.md`）
发现它，而不是靠猜目录名前缀。本目录因此恢复 `_` 的诚实含义：只剩归档证据。
