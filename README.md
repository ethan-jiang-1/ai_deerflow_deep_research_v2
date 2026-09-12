# ai_deerflow_deep_research_v2

一个跑在 [DeerFlow](https://github.com/bytedance/deer-flow) 之上的 **Deep Research Harness**。
它不是"问一句、拿报告"的单管道 deep research 应用，而是一套 deep research 的**运行 / 控制底座**：
把每一次研究变成一个独立、可检查、可单独删除的 **Run Bundle**，用嵌套 `StateGraph` 控制器管理生命周期
（`start` / `resume` / `status` / `cancel` / `refine`），并在有界 LLM 节点外做确定性准入（gate / evidence ledger / validator）。

"harness" 在这里的三层含义：

1. **运行底座，不持有持久 run 状态。** 持久真相在 Run Bundle 里；删掉 Bundle，Harness 照常工作，那次 run 永久不可用且不会被重建。
2. **explicit composition（显式组成）。** 每张图都有一份显式 recipe——公开 host 固定 `all_real`，零凭据 demo / 测试用 `fixture`，混合用 `mixed`；生产节点只暴露真实工厂，确定性 fixture 适配器隔离在被排除于产物与运行时的 `src_fixtures/` 包里。同一张图因此能在零凭据下被驱动。
3. **模型提议、代码裁决。** LLM 节点只提出候选；候选、证据、路由由确定性边界（validator / ledger / gate / graph）准入。

DeerFlow 是宿主运行时，**不 import 本包**；它通过反射出的 `deep_research` 工具与公开 controller skill 触达本 Harness。

细节：入口地图见 [`deep_research_harness/README.md`](deep_research_harness/README.md)，权威边界见 [`docs/runtime-architecture.md`](deep_research_harness/docs/runtime-architecture.md)。

## 布局

```
deep_research_harness/    ★ 你的应用（deep research runtime，基于 deerflow 的 API 构建）
deerflow/                 被 leverage 的框架（submodule 锁 commit `66b9e7f2`，ethan 分支；旧研究笔记不随 submodule 分发），只读
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

常用示例：`cd deep_research_harness && make demo`（零凭据演示）、`make demo-real-scripted`（嵌入式 smoke 校准）、`make demo-tui`（TUI 可视化）。环境未就绪时先 `make install`。

## 给 Coding Agent

见 [AGENTS.md](AGENTS.md)——重点是：应用是主角，框架只 leverage 不改。

## 备注

- `deerflow/` submodule 需 `git clone --recurse-submodules` 或 `git submodule update --init` 才完整。
- 框架运行时基座：submodule 锁在 commit `66b9e7f2`（ethan 分支的一个 commit，见 `openspec/governance/project-structure.toml` 的 `upstream_gitlink`）。
