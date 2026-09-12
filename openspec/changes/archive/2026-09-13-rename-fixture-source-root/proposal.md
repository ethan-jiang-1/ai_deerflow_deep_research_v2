## Why

coding-agent 友善度审查确认一处会误导 agent 的命名不一致：同一个"确定性非生产适配器"概念
在仓库里有三套词——目录叫 `fake`（`src_fake/`），包名与 spec 叫 `fixture`
（`deerflow_deep_research_fixtures`、`fixture_root`、`fixture-source-isolation`），
证据真实性等级又叫 `FAKE`（`FAKE_GRAPH`、`REAL_NODE_FAKE_CAPABILITIES`）。agent 走进
fixture 源根时读到的最响亮、也最不权威的词是 `fake`，容易把它误读为"一次性假货 / 测试替身"，
而它实际是受 spec 治理、只允许 import 白名单生产契约的一等非生产源根。本 change 只做目录
重命名与引用同步，不改变任何导入包名、行为、公开符号、错误码或持久化事实。

## What Changes

- `deep_research_harness/src_fake/` → `deep_research_harness/src_fixtures/`（`git mv` 整棵
  树，保留内部包 `deerflow_deep_research_fixtures/` 不变）。
- **不改导入包名**：`deerflow_deep_research_fixtures` 保持，所有 `from
  deerflow_deep_research_fixtures...` import 不变；仅把父目录名对齐权威词汇 "fixture"。
- 同步 `pyproject.toml` 的 `pythonpath`、`Makefile` 的 `PYTHONPATH=src_fake` 全部引用、
  `scripts/_demo_core.py`。
- 同步 `.github/workflows/agent-entry-environment-regression.yml` 的 `src_fake/**` 路径过滤。
- 同步 5 个测试对 `src_fake` 字面路径的引用。
- 同步治理：`project-structure.toml` 的 `fixture_root`、`check_project_architecture.py` 的
  字面量 `"src_fake"`、`required-paths.toml` 的 6 条 fixture 路径、`req-registry.yaml` 的
  FSI-001 描述；并按注册表重新渲染 `deep_research_harness/AGENTS.md` 生成块。
- 更新 4 份现行文档中的路径（根 `README.md`、harness `README.md`、
  `docs/runtime-architecture.md`、`docs/local-operations.md`）。
- **不改真实性词汇**：`FAKE_GRAPH`、`REAL_NODE_FAKE_CAPABILITIES`、`tests/fixtures/`
  测试辅助、`make demo-fixture-graph` / `--fixture` 等既有语义名不变（属另一根轴）。
- **不改历史**：`_backlog/` 与 `openspec/changes/archive/**` 保留旧路径（历史证据）。

## Capabilities

### New Capabilities

（无——纯结构重命名，无 spec 级新行为。）

### Modified Capabilities

- `fixture-source-isolation`：FSI-001、FSI-003 的需求语句中把 `src_fake/` 更新为
  `src_fixtures/`；隔离语义（物理/包级分离、生产不得 import、Docker/wheel 排除）不变。
- `project-structure`：PRS-001（canonical package ownership）、PRS-017（one canonical
  downstream filesystem root）、PRS-019（scripted-real debug 路径）中的 fixture 源根字面
  路径更新；一个非生产源根、唯一 canonical Harness 根、结构注册表枚举等语义不变。
- `evaluation-hardening`：EVH-005 的 entry-environment CI 路径过滤面把 `src_fake/**` 更新为
  `src_fixtures/**`；门禁语义、lane 身份、证据类别不变。

## Impact

- `deep_research_harness/src_fake/` → `src_fixtures/`（整棵树；内含
  `deerflow_deep_research_fixtures/` 包名不变）
- `deep_research_harness/pyproject.toml`（`pythonpath`）
- `deep_research_harness/Makefile`（10 处 `PYTHONPATH=src_fake`）
- `deep_research_harness/scripts/_demo_core.py`
- `.github/workflows/agent-entry-environment-regression.yml`（`src_fake/**` 路径过滤）
- `deep_research_harness/tests/{contract/test_demo_commands,contract/test_docker_compose,contract/test_entry_environment_regression_workflow,integration/test_demo_cli,unit/test_checkpoint_msgpack}.py`
- `openspec/governance/{project-structure.toml,check_project_architecture.py,required-paths.toml,req-registry.yaml}`
- `openspec/specs/{fixture-source-isolation,project-structure,evaluation-hardening}/spec.md`（经本 change 的 delta）
- `deep_research_harness/AGENTS.md`（生成块重渲染）、harness/根 `README.md`、`docs/{runtime-architecture,local-operations}.md`
- `deerflow/` 不修改、不 source-browse。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src_fake/`（重命名为 `src_fixtures/`）——非生产 fixture 源根身份命名的唯一语义决策面。
- **Seam classification:** wiring —— 仅目录/路径重命名与引用同步，无认知面、无人工决策面、无运行行为、状态、路由或契约变化。
- **Question:** 能否在不改变导入包名（`deerflow_deep_research_fixtures`）、隔离语义、公开符号或任何运行事实的前提下，让非生产 fixture 源根的目录名与仓库权威词汇 "fixture" 对齐，从而不再被 agent 误读为一次性假货？
- **Necessary adjacent/external contracts:** `openspec/governance/project-structure.toml` / `required-paths.toml`（结构注册表精确枚举 `fixture_root` 与 fixture 路径，必须同步）；`openspec/governance/req-registry.yaml`（FSI-001 描述含字面路径）；`pyproject.toml` / `Makefile` / CI workflow（`src_fake` 在 import 路径与 CI 路径过滤中生效，重命名必须原子覆盖）；无外部 DeerFlow 契约。
- **Evidence seam:** 仓库根 `python3 openspec/governance/check_project_architecture.py` 于干净工作树 exit 0（含生成块匹配）；`deep_research_harness` 下 `UV_OFFLINE=1 make verify` 全绿；`make demo` 与 `make demo-scripted` 零凭据 fixture 图仍可运行。
- **Not in scope:** 包名 `deerflow_deep_research_fixtures` 的重命名；`FAKE_GRAPH` / `REAL_NODE_FAKE_CAPABILITIES` 真实性词汇；`tests/fixtures/` 测试辅助目录；`work_unit` / `storage` 等其它命名；任何行为、状态、路由、错误码、diagnostic 字段；`_backlog` 与归档 change 的历史路径；`deerflow/`。
- **Triggered review policies:** none: 纯目录重命名与引用同步，无新代码路径、无认知面、无 workflow outcome、无 node-agent 面、无 control placement 决策。
