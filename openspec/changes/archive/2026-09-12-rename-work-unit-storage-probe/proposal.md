## Why

coding-agent 友善度审查确认一处会误导 agent 的文件名歧义：`runtime/work_unit_storage.py`
与 `runtime/work_unit_store.py` 仅差 `storage` / `store`，但两者职责完全不同。前者是存储
**就绪分类与 POSIX 能力探测**（`classify_work_unit_storage`、
`check_prelaunch_work_unit_storage`、`probe_posix_primitives`、
`verify_runtime_work_unit_storage`），不提供任何作业存储写入；后者才是真正的原子
submission ledger store（`WorkUnitStore`）。不读代码无法从名字判断该打开哪一个，是
agent 最容易静默改错模块的点。本 change 只做文件重命名与引用同步，不改变任何行为、
公开符号、错误码、diagnostic 字段或持久化事实。

## What Changes

- `runtime/work_unit_storage.py` → `runtime/work_unit_storage_probe.py`（`git mv`）。
- `tests/unit/test_work_unit_storage.py` → `tests/unit/test_work_unit_storage_probe.py`
  （同一测试单元随其被测模块改名）。
- 同步全部 import / 路径引用（`src/`、`tests/`、`scripts/`）。
- 同步 `openspec/governance/required-paths.toml` PRS-001 中该路径条目。
- 同步 `tests/assets/evidence.py` 的 correctness claim selector 与
  `docs/regression-descent.md` 的对应行（登记的是改名后的测试 selector）。
- **不改符号名**：`classify_work_unit_storage`、`check_prelaunch_work_unit_storage`、
  `verify_runtime_work_unit_storage`、`WorkUnitStorageCheck`、`WorkUnitStoreError` 全部保留。
- **不改语义名**：diagnostic 字段 `work_unit_storage` 与错误码
  `work_unit_storage_unavailable` 保持不变（它们是规范级事实，不是模块文件名）。

## Capabilities

### New Capabilities

（无——纯结构重命名，无 spec 级行为变化。）

### Modified Capabilities

（无。`.openspec.yaml` 声明 `skip_specs: true`。模块角色、导入边界、公开符号、
错误码与持久化事实均不变，仅文件枚举路径变化，由 `required-paths.toml` 承载。）

## Impact

- `deep_research_harness/src/deerflow_deep_research/runtime/work_unit_storage.py`
  → `work_unit_storage_probe.py`
- `deep_research_harness/src/deerflow_deep_research/runtime/{bootstrap_bundle,request_bundle,work_unit_store,diagnostics}.py`（import 更新）
- `deep_research_harness/tests/unit/test_work_unit_storage.py`
  → `test_work_unit_storage_probe.py`
- import 引用更新：`tests/{unit/__init__ 相关, blocking_io, integration, graph, eval}` 中 import 该模块的测试
- `deep_research_harness/scripts/_demo_core.py`（import 更新）
- `deep_research_harness/tests/assets/evidence.py`、`deep_research_harness/docs/regression-descent.md`（selector 同步）
- `openspec/governance/required-paths.toml`（PRS-001 路径同步）
- `deerflow/` 不修改。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/work_unit_storage.py`（重命名为 `work_unit_storage_probe.py`）——模块身份命名的唯一语义决策面。
- **Seam classification:** wiring —— 仅文件名/路径重命名与引用同步，无认知面、无人工决策面、无行为、无状态或契约变化。
- **Question:** 能否在不改变任何运行时行为、公开符号、错误码、diagnostic 字段或持久化事实的前提下，让存储就绪探测模块的文件名不再与真正的作业存储 `work_unit_store.py` 相混？
- **Necessary adjacent/external contracts:** `openspec/governance/required-paths.toml`（PRS-001 精确枚举该路径，必须同步）；`tests/assets/evidence.py` 与 `docs/regression-descent.md`（登记改名测试的精确 selector）；无外部 DeerFlow 契约。
- **Evidence seam:** `check_project_architecture.py` 于干净工作树 exit 0；`UV_OFFLINE=1 make verify` 全绿；`scripts/checks/check_test_assets.py` 能解析改名后的 selector。
- **Not in scope:** `work_unit_store.py` 或任何其他模块的重命名（含 `debug_driving`、`run_observation`、`run_experience`——审查判定它们属刻意的分层约定或另列 follow-up）；`classify_work_unit_storage` 等符号名；`work_unit_storage` diagnostic 字段与 `work_unit_storage_unavailable` 错误码；registry 的 imports/ignore/gitlink 等其他事实；`deerflow/`。
- **Triggered review policies:** none: 纯文件重命名与引用同步，无新代码路径、无认知面、无 workflow outcome、无 node-agent 面。
