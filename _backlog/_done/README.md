# _done — 已完成/暂停的归档记录

> 最后更新: 2026-09-12（关闭逗留 plan，CLS-059；补登 CLS-058） | `_backlog/_done/` — 已完成内容与明确暂停项的归档根目录。
> **`_done/` = 归档工作件，coding agent 默认忽略，除非显式点名要读**（`_` 前缀的两类语义见 [`../README.md`](../README.md)）。
>
> 状态总览和查阅指南在本文件。活跃工作的 PENDING 表、依赖链、执行顺序 → 见 [`../todos/README.md`](../todos/README.md)。

## 目录

```
_done/
├── README.md              # 本文件（状态总览 + 查阅指南）
├── _fixed_bugs/           # 已修复 Bug（编号权威源）
├── _suspended_bugs/        # 悬挂 Bug（暂未确认修复）
├── _done_todos/           # 已完成 TODO（DONE-NNN）
├── _closed_plans/         # 已完成 Plan（CLS-NNN）
└── _suspended_plans/      # 明确暂停、保留重启条件的计划/延期跟进
```

---

## 状态总览

### ✅ DONE（已完成/已归档）

| 归档目录 | 数量 | Next ID |
|---------|------|---------|
| `_fixed_bugs/` | 67 | BUG-068 |
| `_done_todos/` | 5 | DONE-006 |
| `_closed_plans/` | 58 | CLS-060 |

### ⏸ SUSPENDED（明确暂停）

| 归档目录 | 数量 | 重启方式 |
|---------|------|---------|
| `_suspended_bugs/` | 0 | 确认修复后移回活跃 bug 流程 |
| `_suspended_plans/` | 6 | — |

_Closed plan count follows the indexed CLS records; each future move increments the count and Next ID together._

---

## 快速查阅指南

### 想看"现在该做什么"
→ [`../todos/README.md`](../todos/README.md) 的"推荐执行顺序"。

### 想看 _backlog 的规矩
→ [`../README.md`](../README.md) — 三套搬迁 ritual（todo / bug / plan）+ 铁律 + 外部文件地图。

### 想看历史决策
→ `_closed_plans/` 下的 plan（分析/复盘）与 `_done_todos/` 下的 DONE 文件（按文件名主题查阅）。

### 想看已明确暂停的工作
→ [`_suspended_plans/`](_suspended_plans/)；其中的记录不是已完成项，只有在重新获准排期时才回到活跃目录。

### 想看复盘经验
→ [`../_learning/`](../_learning/) — apply / 研究 retro。

### 想看具体 TODO 的设计思路
→ `../todos/todo-*.md`，每个都含：Why、现状对齐、Current Direction、Design Questions、Non-Goals、Next Step。
