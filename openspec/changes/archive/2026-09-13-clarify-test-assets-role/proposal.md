## Why

coding-agent 友善度审查确认一处目录直觉误导：`deep_research_harness/tests/assets/` 位于
`tests/` 下，却几乎不是测试——14 个模块、约 8568 行里只有
`test_main_spec_requirement_sources.py` 一个被 pytest 收集，其余是 test-owned 证据/清单词汇
与校验器（`evidence.py`、`requirement_evidence.py`、`inventory.py` 等），被 34 个测试和
`scripts/checks/check_test_assets.py` import。agent 按 `tests/` 的通用直觉会期望这里是测试或
测试夹具，从而误判该打开哪个模块。本 change 只把该目录的角色做成结构上和视线上都清楚，
不改任何测试语义、治理词汇或运行事实。

## What Changes

- 把目录内唯一被收集的测试 `tests/assets/test_main_spec_requirement_sources.py` 移到
  `tests/contract/test_main_spec_requirement_sources.py`（它本就 import
  `openspec/governance/check_project_reqs.py`，是治理契约测试），使 `tests/assets/` 不再包含
  任何被收集的测试。
- 从 `tests/assets/selection.py::FAST_PATHS` 与 `Makefile::test-fast` 的路径列表中移除
  `tests/assets`（该条目当初正是为收集这个测试而加），并同步
  `tests/contract/test_verification_gate_contract.py` 对 Makefile 路径列表的精确断言。
- 新增 `tests/assets/README.md`：一屏说明"这不是测试；是 test-owned 证据/清单词汇与校验器，
  被 tests 与 `check_test_assets.py` 引用，受 EVH/WFO/CPE 需求治理；pytest 在此不收集任何测试"。
- 在 `deep_research_harness/AGENTS.md` 的 Information Map 增加一行指向该 README，让角色在
  coding-agent 焦点门即可见。
- 同步 `docs/testing-and-evaluation.md` 中相关 lane 描述。
- **不改**：目录名 `tests/assets`（"asset" 是仓库自洽的治理词汇）、`AssetClass` /
  `make test-assets` / `check_test_assets.py` 名称、目录内证据与校验器的内容或行为、
  任何 pytest marker 或 lane 表达式。

## Capabilities

### New Capabilities

（无——纯目录角色显性化、单文件搬迁与 lane 路径同步，无 spec 级行为变化。）

### Modified Capabilities

（无。`.openspec.yaml` 声明 `skip_specs: true`。测试语义、治理词汇、覆盖范围与运行事实均不变；
fast lane 的具体路径成员不属于 spec 拥有的行为，既有先例 `restore-deterministic-gate-contracts`
在新增同一个 `tests/assets` 路径条目时同样未改 spec。）

## Impact

- `deep_research_harness/tests/assets/test_main_spec_requirement_sources.py`
  → `deep_research_harness/tests/contract/test_main_spec_requirement_sources.py`（`git mv`；
  `parents[3]` 深度不变，索引 `openspec/governance/check_project_reqs.py` 的逻辑不变）
- `deep_research_harness/tests/assets/selection.py`（`FAST_PATHS` 移除 `tests/assets`）
- `deep_research_harness/Makefile`（`test-fast` 路径列表移除 `tests/assets`）
- `deep_research_harness/tests/contract/test_verification_gate_contract.py`（精确路径列表断言）
- `deep_research_harness/docs/testing-and-evaluation.md`（lane 描述）
- 新增 `deep_research_harness/tests/assets/README.md`
- `deep_research_harness/AGENTS.md`（Information Map 一行）
- `openspec/governance/required-paths.toml` 未枚举 `tests/assets`，无需改动。
- `deerflow/` 不修改。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/tests/assets/` 的角色与
  `tests/assets/selection.py::FAST_PATHS` 的路径成员——目录"是测试还是 test-owned 支持库"的
  唯一语义决策面。
- **Seam classification:** wiring —— 仅目录角色显性化、单文件搬迁与 lane 路径同步；无认知面、
  无人工决策面、无测试语义、状态、路由或契约变化。
- **Question:** 能否在不改变任何测试语义、治理词汇、`AssetClass` / `make test-assets` 名称、
  覆盖范围或 lane 表达式的前提下，让 `tests/assets/` 一眼可辨为 test-owned 支持库而非测试目录？
- **Necessary adjacent/external contracts:** `tests/contract/test_test_lane_selection.py` 与
  `tests/contract/test_verification_gate_contract.py`（断言 fast lane 路径划分与 Makefile 精确
  列表，搬迁测试与移除路径条目必须同步）；`docs/testing-and-evaluation.md`（登记 fast lane 内容）；
  `scripts/checks/check_test_assets.py`（import 该支持库，搬迁不得破坏其解析）；无外部 DeerFlow 契约。
- **Evidence seam:** `deep_research_harness` 下 `make test-fast`（搬迁后的测试仍被 contract lane
  收集执行）、`make test-assets`（支持库与其 selector 仍可解析）、`UV_OFFLINE=1 make verify` 全绿。
- **Not in scope:** 重命名 `tests/assets` 目录或 `AssetClass` / `make test-assets` /
  `check_test_assets.py`；`tests/assets/` 内证据与校验器的内容、行为或治理；`tests/fixtures/`
  测试辅助；任何 marker、lane 表达式或覆盖分母；`deerflow/`。
- **Triggered review policies:** none: 目录角色与文档显性化加单文件搬迁，无新代码路径、无认知面、无 workflow outcome、无 node-agent 面、无 control placement 决策。
