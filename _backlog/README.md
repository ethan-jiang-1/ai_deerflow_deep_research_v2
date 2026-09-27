# _backlog — 项目待办与决策记录

> 最后更新: 2026-09-26 | 本目录追踪本仓库的工作项、设计决策、上游分析。
> 活跃工作走 OpenSpec（`openspec/changes/`）；本目录是 **上游分析与决策记录 + 待办池**，不是运行时真相。
>
> **本文件是 `_backlog` 的规矩手册。** 搬迁流程在下面定死，今后大家都遵循这里头定的规矩。
>
> **命名约定：`_` 前缀 = "不在活跃工作件队列里"，分两个诚实类别，别混：**
>
> 1. **归档工作件**（会关闭；coding agent 默认忽略，除非点名）：`_done/`
>    （含 `_fixed_bugs/`、`_done_todos/`、`_closed_plans/`、`_suspended_bugs/`、`_suspended_plans/`）。
> 2. **留存参考 / 证据**（不参与工作件搬迁；agent 按任务按需读，**不**默认忽略）：
>    `_reference/`（外部系统分析）。
>
> 活跃工作件在无前缀目录（`bugs/`、`todos/`、`plans/`）。**`_` 只表示"不在活跃队列"，不表示"禁止读"**——读不读由任务决定。`check_doc_hygiene.py` 校验：磁盘上任何 `_` 目录必须在此声明，且每个声明名必须出现在本文件中。

## 这个仓库是什么

`ai_deerflow_deep_research_v2` 是对上游 [bytedance/deer-flow](https://github.com/bytedance/deer-flow)（基于 LangGraph 的 AI super-agent 框架）之上，以 OpenSpec spec-driven 规范开发的 **Deep Research 智能体应用**。硬约束：**绝不修改上游源码**（`deerflow/backend/`、`deerflow/frontend/` 是上游镜像，位于 `deerflow/` submodule 内；fork 分支携带的 `_digest/` 旧笔记是只读历史背景）。Deep Research 智能体开发走 `openspec/`。

## 目录结构

```
_backlog/
├── README.md                          # 本文件（规矩手册 + 索引）
│
├── _done/                             # ✅ 归档工作件（会关闭；默认忽略）
│   ├── README.md                      #   状态总览、快速查阅指南
│   ├── _fixed_bugs/                   #   已修复 Bug（编号权威源）
│   ├── _done_todos/                   #   已完成 TODO（DONE-NNN）
│   ├── _closed_plans/                 #   已完成 Plan（CLS-NNN）
│   ├── _suspended_bugs/               #   悬挂 Bug（暂未确认修复）
│   └── _suspended_plans/              #   明确暂停、保留重启条件
│
├── bugs/                              # 🐛 活跃 bug → 修完移入 _done/_fixed_bugs/
├── todos/                            # 📋 活跃 todo → 做完移入 _done/_done_todos/
├── plans/                            # 📐 活跃 plan → 完成移入 _done/_closed_plans/
│
└── _reference/                       # 📚 留存：外部系统分析资料（消化后产出 plan）
```

---

## 知识地图：从活跃到归档，三对生命周期 🗺️

`_backlog` 里追踪三种工作件；完成时移入 `_done/` 下对应的 `_` 前缀子目录。明确不排期、但保留重启条件的记录则移入 `_suspended_plans/`，它不是完成状态：

| 类型 | 活跃（当前工作） | 归档（已完成） | 编号方式 |
|------|-----------------|---------------|---------|
| 🐛 **Bug** | [`bugs/`](bugs/) — 活跃 bug 列表 | [`_done/_fixed_bugs/`](_done/_fixed_bugs/) — 已修复 | BUG-NNN 递增，编号权威在 `_fixed_bugs/`；新号 = 已分配的最大编号 + 1（已修复 ∪ 活跃） |
| 📋 **Todo** | [`todos/`](todos/) — 活跃 todo + 依赖链 + 执行顺序 | [`_done/_done_todos/`](_done/_done_todos/) — 已完成 | DONE-NNN 递增，移入时分配 |
| 📐 **Plan** | [`plans/`](plans/) — 活跃 plan 列表 | [`_done/_closed_plans/`](_done/_closed_plans/) — 已完成 | CLS-NNN 递增，移入时分配 |
| ⏸ **Suspended follow-up** | 无；不进入推荐执行顺序 | [`_done/_suspended_plans/`](_done/_suspended_plans/) — 明确暂停 | 文件名不变；重新开启时移回活跃目录 |

> 📖 **想看全局状态、历史决策、查阅指南** → [`_done/README.md`](_done/README.md)
>
> 📖 **想看当前该做什么、依赖关系、执行顺序** → [`todos/README.md`](todos/README.md)

---

### 暂停而非完成

当一个 todo 或 plan 已明确不再排期、但仍须保留问题背景和重启条件时，用 `git mv` 将其移入
`_done/_suspended_plans/`，文件名和内容保持不变。随后更新原活跃索引、
`_done/_suspended_plans/README.md` 与 `_done/README.md`；不要把它记为 DONE 或 CLS。

---

## 搬迁规矩

三种工作件的搬迁步骤完全一样：**`git mv` 过去，文件名不变，位置即状态，连带更新三处 README。** 各子目录 README（`bugs/`、`todos/`、`plans/` 及对应的 `_done/` 下级）里也写了具体步骤。

### 铁律

- **`_backlog` 独立于 OpenSpec** —— 两层各自簿记，不交叉判定。不要为了在 `_backlog` 标 done 而去动 OpenSpec。
- **文件内容原样保留**，不重写。用 `git mv`（不是普通 `mv`）。
- **反向可以**：`git mv` 回活跃目录即可。极少用，但允许。

### 三条命令

```bash
# Bug 修完
git mv bugs/BUG-<NNN>-<slug>.md _done/_fixed_bugs/BUG-<NNN>-<slug>.md

# Todo 做完
git mv todos/todo-<name>.md _done/_done_todos/todo-<name>.md

# Plan 完成
git mv plans/<name>.md _done/_closed_plans/<name>.md
```

### 搬完更新

> ⚠️ **README 文件本身永不删除。** "移除"指的是从活跃列表中移除该条目的行，不是删文件。每个 README 永远留在目录里做索引。**文件内容原样保留，`git mv` 搬迁。**

**🐛 Bug 修完：**
| 操作 | 怎么改 |
|------|--------|
| `bugs/README.md` | 从活跃列表移除该 bug 的行 |
| `_done/_fixed_bugs/README.md` | 表格加一行 + 更新 Next available bug ID |
| `_done/README.md` | 已修复 bug 计数 +1 |

**📋 Todo 做完：**
| 操作 | 怎么改 |
|------|--------|
| `todos/README.md` | 从活跃列表移除该 todo 的行 |
| `_done/_done_todos/README.md` | 表格加一行 + 更新 Next available DONE ID |
| `_done/README.md` | DONE 计数 +1 |

**📐 Plan 完成：**
| 操作 | 怎么改 |
|------|--------|
| `plans/README.md` | 从活跃列表移除该 plan 的行 |
| `_done/_closed_plans/README.md` | 表格加一行 + 更新 Next available plan ID |
| `_done/README.md` | 已关闭 plan 计数 +1 |

---

## 相关外部文件

> 以下路径相对于 **本仓库根目录**，不是 `_backlog/` 目录。

| 路径 | 角色 |
|------|------|
| `AGENTS.md` / `CLAUDE.md` | repo 最高指引（monorepo 定位 + 跨切约定；`CLAUDE.md` 经 `@AGENTS.md` 导入） |
| `openspec/config.yaml` | OpenSpec 项目上下文 + 4 artifact（proposal/specs/design/tasks）规则 |
| `openspec/specs/` | 已接受 spec（运行时真相层，与 `_backlog` 各自簿记） |
| `openspec/changes/` | 活跃 change（完成归档于 `openspec/changes/archive/`） |
| `deerflow/AGENTS.md`、`deerflow/backend/AGENTS.md` | 框架 submodule 自带的只读指引（fork 分支携带的 `_digest/` 旧笔记是只读历史背景） |
| `_backlog/_reference/` | 外部系统分析资料（如 imported workflow framework），消化后产出 `_backlog/plans/` |
| `deerflow/backend/` `deerflow/frontend/` | 上游镜像（**禁改**，submodule 锁定在 `deerflow/` 内） |
