# harden-entry-doc-navigation

## Change Focus

- **Primary module / causal owner:** 仓库根 `README.md`（布局表与 Direction Controls 节）、`deep_research_harness/docs/README.md`（Living References 路由）、`deep_research_harness/src/deerflow_deep_research/runtime/README.md`（新增 reader index）；git 跟踪面（`RUN-020.command` `git rm --cached`）。全部为文档/索引/git 元数据，无运行时行为。
- **Seam classification:** wiring —— 纯导航投影、指针修复与 git 跟踪对齐；无认知面、无人工决策面、无运行时行为变化。
- **Question:** 能否在不动任何运行时代码、不改 `deerflow/` submodule 的前提下，消除入口文档的三类探索摩擦：runtime/ 层 34 文件无索引、根目录散件未登记、Direction Controls 对 runtime-architecture/spec 的三重转述？
- **Necessary adjacent/external contracts:** `deep_research_harness/docs/runtime-architecture.md`（Public Controls / Ordinary Controller Loading 成为唯一行为转述处）；`openspec/specs/deep-research-harness-run-bundles/spec.md`（refine 准入权威，仅被链接不被转述）；`deep_research_harness/COMMANDS.md`（已有"不是第二权威"声明，获得入口链接）；`deerflow/AGENTS.md`（config.yaml 宿主约定的只读出处，只转述不改）。
- **Evidence seam:** 链接完整性走查（新 README 内相对路径解析）+ `check_doc_hygiene.py` 与 `check_project_gate.py --phase closeout`（六组件全绿）+ `UV_OFFLINE=1 make verify` 无关联回归。
- **Not in scope:** `deerflow/`（submodule，绝不修改）；任何 `src/` 运行时代码；spec 目录改名；`openspec/` 治理文件；`_backlog/`。
- **Triggered review policies:** change-admission, authority-and-projections

## Why

以 coding agent 视角复检本仓探索路径后，剩三类摩擦：(1) `runtime/` 是唯一"靠文件名猜"的层——34 个文件 13.8k 行，docstring 质量高但散在文件头，没有 node 包 workflow.md 那样的簇级投影；(2) 根 README 布局表只登记 6 个居民，`config.yaml`/`.env`/`profiles/`/`skills/public/`/`RUN-*.command`/`CONTEXT*.md` 首次 ls 会产生疑问，其中 RUN-010.command 的头注释还指向已不存在的 `_backlog/_local_demo/` 路径，RUN-020.command 处于"被跟踪+被 ignore"的矛盾状态；(3) 根 README 的 Direction Controls 节把 refine/resume 契约与 Agent 加载路线第三次转述（runtime-architecture.md 与 owning spec 已各有一份），是入口文档里现存最大的第二权威漂移源，违反本仓"guide 不是第二权威"的边界。

## What Changes

- 新增 `deep_research_harness/src/deerflow_deep_research/runtime/README.md`：按 5 簇（bundle 生命周期/控制、图/节点执行、work units、观察/评估、调试）的 reader index，头部声明"只是索引、不是第二权威"，沿用 `tests/assets/README.md` 先例。
- `deep_research_harness/docs/README.md` Living References 表加一行，路由到上述 runtime/README.md。
- 根 `README.md` 布局表补 5 行登记：`config.yaml`+`.env`（宿主运行时配置与凭证，gitignored，宿主约定）、`profiles/`（已注册 runtime profiles）、`skills/public/`（spec 物化的公共 controller skill）、`RUN-*.command`（本地双击启动器，gitignored，索引在 COMMANDS.md）、`CONTEXT.md`/`CONTEXT-MAP.md`（词汇边界）。
- `deep_research_harness/README.md` Direction Controls 节收缩为指针块（2-3 句 + 链到 runtime-architecture.md 的 Public Controls / Ordinary Controller Loading + 点名 owning spec），消除三重转述。
- `RUN-010.command:7` 腐烂指针改为指向 `deep_research_harness/docs/runbooks/runbook-010-tui-auto.md`。
- `git rm --cached RUN-020.command` 对齐 `RUN-*.command` ignore 规则（本地文件保留）。
- `deep_research_harness/README.md` Reading Map 给 `COMMANDS.md` 一行入口（消除半孤儿状态）。
- 非目标：不改 `deerflow/`；不改任何 `src/` 行为；不拆 runtime/ 子包；不重写 Direction Controls 的契约内容（它已在 runtime-architecture 与 spec 中拥有）。

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — 纯文档导航、索引与 git 元数据对齐，无 spec 级行为变化；经 `skip_specs: true` 声明。)

## Impact

- 新增：`deep_research_harness/src/deerflow_deep_research/runtime/README.md`。
- 修改：根 `README.md`；`deep_research_harness/docs/README.md`；`deep_research_harness/README.md`（Reading Map 一行）；`RUN-010.command`（本地文件，untracked）。
- git 元数据：`RUN-020.command` 移出跟踪（`git rm --cached`）。
- 归档 change 目录本身。
- 不影响：任何 Python 源码、测试、openspec specs、governance 文件、`deerflow/`。
