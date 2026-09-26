# Done Todos Index — 已完成 todo 归档

> 最后更新: 2026-09-27（DONE-006 wave2 预算对齐经 change 落地；DONE-007 手动 TUI 验收退役进 runbook-020） | `_backlog/_done/_done_todos/` — 已完成 todo 的归档目录。
> 接收来自 [`../../todos/`](../../todos/) 的 todo。`_` 前缀 = coding agent 默认忽略。
>
> **todo 完成后文件名不变（`todo-<name>.md`），位置即状态。** 移入时分配 `DONE-NNN` 序号，按完成时间递增。

## 接收一个完成的 todo

todo 完成后从 `_backlog/todos/` 通过 `git mv` 移入本目录：
1. 在本文件表格加一行（DONE-NNN + 日期 + 文件名 + 简述），编号 = 当前最大 + 1
2. 更新最后的 "Next available DONE ID" 行
3. 更新 `../../todos/README.md`（移除该 todo 的行）
4. 更新 `../README.md`（计数 +1）

---

## 已完成列表

| ID | Date | File | Summary |
|----|------|------|---------|
| DONE-001 | 2026-08-13 | [todo-n002-policy-routing-cardinality.md](todo-n002-policy-routing-cardinality.md) | 统一多 policy 路由术语，并归档对应 OpenSpec change。 |
| DONE-002 | 2026-08-13 | [todo-a002-gitlink-boundary-detector.md](todo-a002-gitlink-boundary-detector.md) | 建立 `deerflow/` metadata-only gitlink boundary detector，并归档对应 OpenSpec change。 |
| DONE-003 | 2026-08-31 | [todo-run-lifecycle-walkthrough.md](todo-run-lifecycle-walkthrough.md) | `docs/run-lifecycle-walkthrough.md`（97 行 reader projection）：一个 bundle 的一生，CONTEXT.md 术语按登场加粗；登记进 doc gate 范围并挂 Information Map（CLS-057 缺口 B）。 |
| DONE-004 | 2026-08-31 | [todo-demo-workspace-cleanup-command.md](todo-demo-workspace-cleanup-command.md) | `make demo-workspace-report` + `make demo-clean`（dry-run 默认 / CONFIRM=1 仅删 terminal / 日志分离 / 基线警示），change `2026-08-31-demo-workspace-cleanup` 归档（DPL-014） |
| DONE-005 | 2026-09-12 | [todo-entry-doc-prose-and-search-guidance.md](todo-entry-doc-prose-and-search-guidance.md) | 修 `docs/README.md` 重复 `the`/重复链接；`AGENTS.md` 加 `rg` 探索指引（走账本，不开 change）。 |
| DONE-006 | 2026-09-27 | [todo-wave2-repair-timeout-budget-evaluation.md](todo-wave2-repair-timeout-budget-evaluation.md) | wave2 calibration case 预算对齐：四个 `wave2-synthesis` case 从 `_ZERO`（60s/16k）迁入 `_WAVE2`（180s/32k，= corpus worker 档，< 生产 300s/64k 上限），validator 分支键控 fail-closed 保留；change `align-wave2-calibration-case-budget` 归档，全门禁绿；live 窗口验证为非阻塞补充证据。 |
| DONE-007 | 2026-09-27 | [todo-manual-demo-tui-human-validation.md](todo-manual-demo-tui-human-validation.md) | 手动 TUI 真人验收退役：未测增量收窄为"真实运行时 × 真 Textual 输入组件"组合缝（两侧各有 Pilot fake 驱动覆盖），追踪职责转移至 runbook-020 顶部"验收状态"注记（可选操作员自检，跑通一次即勾销）。 |

**Next available DONE ID: DONE-008**
