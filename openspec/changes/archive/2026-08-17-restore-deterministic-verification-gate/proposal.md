## Why

`UV_OFFLINE=1 make verify`（README、AGENTS.md、CI 共同声明的确定性 gate）在 HEAD 上三处独立失败：已提交测试文件里的 E501 让 lint 挂；PRS-019/SCR-001 两个 alive 需求缺确定性 `@impl` 让 test-assets 挂；integration 里一个非封闭测试依赖本机 gitignored 的 `profiles/` 状态。`.github/workflows/agent-tests.yml:26` 跑的就是 `make verify`，所以 CI 同样是红的。测试内容本身健康（test-fast 2812 个全绿），坏的是验证系统自己——这是 coding agent 每天第一脚就踩的坑。

## What Changes

- 修复 `tests/contract/test_import_boundaries.py:391-392,404-405` 的 4 处 E501：超长字符串字面量改相邻拼接（不关 lint 规则、不降 line-length）。
- 给 PRS-019、SCR-001 补确定性 `@impl` docstring，放在各自归属的确定性测试文件（SCR-001 → `tests/contract/test_scripted_real_debug_command.py`；PRS-019 → 归属 canonical-path 契约的确定性测试），使 `make test-assets` 绿。
- 修复 `tests/integration/test_local_entry_environment.py` 非封闭性：测试在拷贝出的项目里**自行构造**被检的 demo profile（含隔离的 sqlite_dir），不再依赖本机 gitignored 的 `profiles/` 状态，干净 checkout 上可绿。
- 退役 `postgres` marker：移除 pyproject marker 注册与 `make test-postgres` target；从全部 lane 表达式（Makefile 四处 `-m`、`scripts/benchmark_fast.py`）与 exact-string 断言（`tests/assets/selection.py` 三常量、`tests/contract/test_test_lane_selection.py`、`tests/contract/test_verification_gate_contract.py`、`tests/assets/inventory.py` 的 VerifiedLane 数据行）中移除引用。`postgres-test` extra 保留（Postgres 服务仍被 tech-stack 决策推迟）。
- `release_e2e` 从「靠文件名不可收集的隐身态」改为「可收集但被 marker 排除」：`tests/scenarios_suspended/evh_024_release_acceptance.py` 改名 `test_evh_024_release_acceptance.py`；同步所有「release_e2e 收集为空」断言（`tests/contract/test_test_lane_selection.py:112-113`、`tests/contract/test_test_structure_retirement.py:63`、`tests/contract/test_release_suspension.py:18,32-33` 的旧文件名常量与 SUSPENDED_SELECTOR），使其期望 suspended 材料被收集但被 lane 排除。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `evaluation-hardening`: 新增 EVH-031——确定性测试选择只引用活 marker，suspended 材料保持可收集可见性，确定性 gate 在干净 checkout 上为绿。

## Impact

- `deep_research_harness/Makefile`（删 `test-postgres` target 及注释；改 4 处 `-m` 表达式）
- `deep_research_harness/pyproject.toml`（移除 postgres marker 注册；`postgres-test` extra 不动）
- `deep_research_harness/scripts/benchmark_fast.py`（FAST_EXPRESSION）
- `deep_research_harness/tests/assets/selection.py`（DETERMINISTIC_EXCLUDE/FAST_EXPRESSION/WORKFLOW_EXPRESSION）、`tests/assets/inventory.py`（VerifiedLane 两行）
- `deep_research_harness/tests/contract/test_import_boundaries.py`、`test_scripted_real_debug_command.py`、`test_test_lane_selection.py`、`test_verification_gate_contract.py`、`test_test_structure_retirement.py`、`test_release_suspension.py`
- `deep_research_harness/tests/integration/test_local_entry_environment.py`
- `deep_research_harness/tests/scenarios_suspended/`（文件名改名，路径不变）
- `openspec/specs/evaluation-hardening`（delta）
- 无运行时 `src/` 改动；`deerflow/` 不修改。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/tests/` 与验证接线面（Makefile 测试目标、pyproject marker 注册）——语义核心是「测试选择与验证 gate 的行为」，不是任何运行时模块。
- **Seam classification:** deterministic-guardrail 只修改验证/选择机制及其 exact-string 契约测试；不触碰运行时行为、LLM 行为、持久化契约或任何生产路径。
- **Question:** 文档与 CI 共同声明的确定性 gate 能否在干净 checkout 上真实为绿，且 lane/marker 语义与它的 exact-string 契约测试保持单一来源一致？
- **Necessary adjacent/external contracts:** `evaluation-hardening`（lane 选择与证据机制的归属 capability，EVH-031）；`project-structure`（scenarios_suspended 与测试路径注册不变——仅文件名改名、路径不动，不触发 toml 改动，但需核对 PRS 路径清单无遗漏）；`scripted-real-workflow-debug`（PRS-019/SCR-001 的 `@impl` 补位，不改需求文本）。
- **Evidence seam:** `UV_OFFLINE=1 make verify` 全绿（含 lint、test-assets、test-integration）；`make test-postgres` 目标不存在；suspended 目录的收集/排除断言；`openspec validate <name> --strict` + `git diff HEAD --check` + gitlink/submodule 状态证据。
- **Not in scope:** `postgres-test` extra 的移除、其他 lint/风格债务、`release_e2e` marker 本身与 conftest 逃生口的改动、其他测试目录重构、`tests/fixtures/` 命名问题、任何 `src/` 或 `deerflow/` 改动。
- **Triggered review policies:** change-admission, authority-and-projections
