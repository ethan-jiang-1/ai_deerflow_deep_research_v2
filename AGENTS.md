# AGENTS.md

本仓库 = **跑在 DeerFlow 之上的 deep research 应用**。它由两层组成，顺序很重要：

```
deep_research_harness/    ★ 你的应用（本仓库的主角，几乎所有工作发生在这里）
deerflow/                 被 leverage 的外部框架（submodule 锁 commit `66b9e7f2`，ethan 分支），只用来跑，绝不修改
```

## 你的工作范围（按优先级）

| 目录 | 是什么 | 怎么对待 |
|------|--------|---------|
| `deep_research_harness/` | **你的 deep research runtime 应用**（src/deerflow_deep_research，graph/runtime/agents/engine/domain） | ★ 主角。改代码、写测试、跑它 |
| `openspec/` | 设计规格（specs / changes / governance） | 改设计时在这里写 spec，用 `openspec` CLI |
| `_backlog/` | 任务账本（bugs / plans / todos） | 任务追踪 |

## 框架：只 leverage，不修改

**`deerflow/` 是一个 git submodule（锁在 commit `66b9e7f2`，ethan 分支的一个 commit），提供运行环境。** 对它：

- ✅ **用它的 API**——你的应用通过 `import deerflow`（editable 装自 `deerflow/backend/packages/harness`）继承框架能力，有什么用什么。
- ❌ **不要探索 / 修改它的源码**。它是上游镜像，不是你的代码。
- ❌ **不要为了解决问题去翻它内部**——如果某任务要求你读框架源码才能继续，停下来重新界定范围（大概率是你在尝试不该改的东西）。
- 需要理解它内部怎么工作 → 看 `deerflow/AGENTS.md` 与 `deerflow/backend/AGENTS.md`（框架自带的只读指引）。旧的研究笔记（digest）不随 submodule 分发，不要去寻找它。

> 术语提示：本仓库的 `harness` 默认指 `deep_research_harness/`（你的应用）；`deerflow/backend/packages/harness` 是框架包。两者同名——前者是主角，后者是只读背景板。

## 运行方式

```bash
cd deep_research_harness
uv sync                              # 或 python -m venv .venv && pip install -e .
.venv/bin/pip install -e ../deerflow/backend/packages/harness   # editable 装框架
.venv/bin/python -m pytest tests/    # 跑你的测试
```

详细命令见 `deep_research_harness/Makefile` 与 `deep_research_harness/README.md`。

## 可用技能（Coding Agent）

共享的 grillme 技能集（grilling / tdd / code-review / domain-modeling 等）由全局安装提供（`~/.claude/skills/` 与 `~/.agents/skills/`，symlink 到 grillme-skills checkout），本仓库不保存副本。适合本仓的：`grilling`（质疑方案）、`tdd`、`code-review`、`domain-modeling`、`codebase-design`。项目自有的 openspec 技能在 `.agents/skills/`（Codex 通用入口，见 `.openspec-target`）。

## 边界铁律

1. **应用是主角**——所有产出都该服务于 `deep_research_harness/` 的构建。
2. **框架是背景板**——`deerflow/` 只被 import，从不被改。
3. **根目录刻意很小**——如果发现自己在框架内部打转，说明范围错了。
