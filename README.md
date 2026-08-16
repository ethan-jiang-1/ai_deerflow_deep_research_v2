# ai_deerflow_deep_research_v2

跑在 **DeerFlow** 之上的 deep research 应用：broad question in, evidence-backed gated research report out。

## 布局

```
deep_research_harness/    ★ 你的应用（deep research runtime，基于 deerflow 的 API 构建）
deerflow/                 被 leverage 的框架（submodule 锁 commit `66b9e7f2`，ethan 分支；含研究笔记 _digest/_faq），只读
openspec/                 设计规格（openspec CLI 管理）
_backlog/                 任务账本
.agents/skills/           openspec 技能（Codex 通用入口，项目自有）
（grillme 技能集由全局 ~/.claude/skills、~/.agents/skills 提供）
```

## 快速开始

```bash
cd deep_research_harness
make install                              # 准备本地运行环境（等价于 uv sync + editable 装框架）
UV_OFFLINE=1 make verify                  # 跑确定性测试 gate
```

## 跑实验（CLI / TUI 入口）

实验、演示与操作入口都在 `deep_research_harness/` 里，用 `make` 驱动。根目录只指路，细节去子目录看：

| 想看什么 | 去哪 |
| --- | --- |
| 有哪些入口、各自是什么（Entry Surfaces 表） | [`deep_research_harness/README.md`](deep_research_harness/README.md) |
| 每条命令怎么跑、环境怎么准备 | [`deep_research_harness/docs/local-operations.md`](deep_research_harness/docs/local-operations.md) |
| 入口背后的架构与 composition | [`deep_research_harness/docs/runtime-architecture.md`](deep_research_harness/docs/runtime-architecture.md) |

常用示例：`cd deep_research_harness && make demo`（零凭据演示）、`make demo-real-scripted`（真实流程）、`make demo-tui`（TUI 可视化）。环境未就绪时先 `make install`。

## 给 Coding Agent

见 [AGENTS.md](AGENTS.md)——重点是：应用是主角，框架只 leverage 不改。

## 备注

- `deerflow/` submodule 需 `git clone --recurse-submodules` 或 `git submodule update --init` 才完整。
- 框架运行时基座：submodule 锁在 commit `66b9e7f2`（ethan 分支的一个 commit，见 `openspec/governance/project-structure.toml` 的 `upstream_gitlink`）。
