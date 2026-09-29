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
deerflow/                 被 leverage 的框架（submodule 锁 commit `ceebf97f`，ethan 分支，= 上游 v2.1.0；fork 携带的 `_digest/` 旧笔记是只读历史背景），只读
openspec/                 设计规格（openspec CLI 管理）
_backlog/                 任务账本
.agents/skills/           openspec 技能（Codex 通用入口，项目自有）
（grillme 技能集由全局 ~/.claude/skills、~/.agents/skills 提供）
```

其他根目录居民（各自的权威在指向处，这里只登记存在与性质）：

- `config.yaml`、`.env` — 宿主运行时配置与凭证（均 gitignored；按 DeerFlow 宿主约定从模板/环境准备，模型列表只含环境变量展开，无明文密钥）
- `profiles/` — 已注册的本地运行 profile（权威：[`deep_research_harness/docs/local-operations.md`](deep_research_harness/docs/local-operations.md) 与 [profiles/README.md](profiles/README.md)）
- `skills/public/` — 由 spec 物化的公共 controller skill（权威：`openspec/specs/deployment-configuration/spec.md`）
- `RUN-010.command`、`RUN-020.command` — 本地双击启动器（gitignored，不在新 clone 中；索引见 [`deep_research_harness/COMMANDS.md`](deep_research_harness/COMMANDS.md)）
- `CONTEXT.md`、`CONTEXT-MAP.md` — 三个 bounded context 的词汇边界（Host / Product / Governance）

## 快速开始

```bash
cd deep_research_harness
make install                              # 准备 harness 环境（uv sync + extras；Gateway 观察路线另需 make profile-setup）
UV_OFFLINE=1 make verify                  # 跑确定性测试 gate
```

## 跑实验（CLI / TUI 入口）

实验、演示与操作入口都在 `deep_research_harness/` 里，用 `make` 驱动。根目录只指路，细节去子目录看：

| 想看什么 | 去哪 |
| --- | --- |
| 想跑哪个入口 → 用哪条命令（CLI/TUI/调试阶梯速查） | [`deep_research_harness/COMMANDS.md`](deep_research_harness/COMMANDS.md) + [runbooks](deep_research_harness/docs/runbooks/README.md) |
| 有哪些入口、各自是什么（Entry Surfaces 表） | [`deep_research_harness/README.md`](deep_research_harness/README.md) |
| 每条命令怎么跑、环境怎么准备 | [`deep_research_harness/docs/local-operations.md`](deep_research_harness/docs/local-operations.md) |
| 入口背后的架构与 composition | [`deep_research_harness/docs/runtime-architecture.md`](deep_research_harness/docs/runtime-architecture.md) |

常用示例：`cd deep_research_harness && make demo-tui-fixture`（零凭据 TUI）、`make demo-tui-real-auto`（010 自动 TUI，真人零操作）、`make demo-real-scripted`（嵌入式 smoke 校准）。注意 `make demo` 与不带 `--fixture`/`--auto` 的 `make demo-tui` 默认**交互读 stdin**，agent/非交互环境会立刻 EOF 退出——非交互零凭据跑法见 [`COMMANDS.md`](deep_research_harness/COMMANDS.md) 的 001 阶梯或 `make demo-scripted`。环境未就绪时先 `make install`。

## 给 Coding Agent

见 [AGENTS.md](AGENTS.md)——重点是：应用是主角，框架只 leverage 不改。

## 备注

- `deerflow/` submodule 需 `git clone --recurse-submodules` 或 `git submodule update --init` 才完整。
- 框架运行时基座：submodule 锁在 commit `ceebf97f`（ethan 分支 tip，= 上游 v2.1.0；声明见 `openspec/governance/project-structure.toml` 的 `upstream_gitlink`，与 `deep_research_harness/tests/contract/test_deerflow_public_api.py` 的 `CURRENT_DEERFLOW_PIN` 互为镜像锚点）。
