# Tasks: single-source-runtime-identifiers-and-retire-dead-code

## 1. 红测护栏（先红后绿）

- [x] 1.1 新建 `tests/contract/test_identifier_single_sourcing.py`：断言 src 内每个 canonical 正则（bundle-id/content-hash/sandbox-path）与 11 个 phase 列表**仅一处定义**；断言 `make_attempt_id`、`project_lifecycle_status`、`GATED_FIELDS`、`MAX_FAKE_TRACE_ENTRIES`、`MAX_FAKE_REPAIR_ATTEMPTS`、`dedupe_source_urls` 与模块 `graph/routing`、`engine/work_units/reducers` 在 src 中不存在。先跑确认对现状红（4/4 红），重构完成后绿（4/4 绿）。apply 修正：phase 检查只统计 Tuple/Literal 的**直接元素**（`topology.py` 的 `NORMALIZED_EDGES` 嵌套边端点属误报，已排除）；`serialize_research_state`/`validate_research_state` 经 apply 复核后**从删除范围撤出**（它们是 state serde 的规范测试缝，支撑 `test_state_bounds` 的边界不变量，非误导性死重），故也从 DEAD_NAMES 移除
- [x] 1.2 对每项删除出 grep 零调用清单（`project_lifecycle_status`/`GATED_FIELDS`/`dedupe_source_urls`/`_request_id`/`_pending_interrupt`/`route_typed`/`reduce_candidates`/`reduce_accepted_refs`：仅 `__all__` 与测试消费；`MAX_FAKE_*`：仅 `__all__`），清单随提交记录

## 2. 标识符单一来源

- [x] 2.1 新建 `domain/identifiers.py`：`LogicalPhase` 枚举（自 `lifecycle.py` 迁入，lifecycle 重导出保持 17 个消费点零改动）、`LOGICAL_PHASE_NAMES`（由枚举派生）、`BUNDLE_ID_PATTERN`/`BUNDLE_ID_RE`/`CONTENT_HASH_RE`/`SANDBOX_PATH_RE`
- [x] 2.2 替换全部重复定义：bundle-id（`bundle.py:55`→`import as _BUNDLE_ID_RE`、`run_observation.py:33`→`import as _BUNDLE_ID_PATTERN`、`lifecycle.py:28`→import、`work_units.py:57`→import、`state.py:97`→import、`tool.py:33`→经 `runtime/bundle_control` 转发——tool 层 import 边界只允许 runtime 内部模块）、content-hash（`work_units.py:58`、`state.py:99` + 删除 `WORK_UNIT_HASH_RE` 别名）、sandbox-path（`state.py:100`、`work_units.py:68`→`import as BUNDLE_REF_RE`）；5 处 phase 列表（`lifecycle.py` 枚举迁入 identifiers、`topology.py LOGICAL_NODES = LOGICAL_PHASE_NAMES`、`registry.py` 由 `LOGICAL_NODES` 派生、`run_experience.py`/`run_observation.py` 用 `Literal[*LOGICAL_PHASE_NAMES]`——Python 3.12 运行时验证可用）
- [x] 2.3 `make_attempt_id` 改名 `make_node_visit_id`（`domain/lifecycle.py` 及其消费点 `graph/builder.py`、`graph/nodes/targeted_evidence/node.py`），产出格式不变；`lifecycle.py` 与 `engine/work_units/ids.py` 补两处 scheme 边界注释；`tests/domain`/`tests/graph` 无回归
- [x] 2.4 `graph/builder.py` 的 registry 顺序检查移除——`RESEARCH_NODE_PACKAGES` 已由 `LOGICAL_NODES` 派生，顺序按构造恒等，原检查成为恒真死代码，替换为注释说明

## 3. 投影退役与死代码删除

- [x] 3.1 删除 `project_lifecycle_status`（`domain/state.py`，连同 `_control_field`）与其测试消费（`tests/unit/test_state_persistence.py`、`tests/unit/test_state_contracts.py` 相关用例）
- [x] 3.2 **apply 决策修正：保留** `serialize_research_state`/`validate_research_state` 及其测试（`test_state_bounds.py` 的 `MAX_CHECKPOINT_STATE_BYTES` 边界不变量依赖它们；二者是 state serde 规范缝，非误导性死重）——从本 change 范围撤出，已同步 proposal 口径与 contract DEAD_NAMES
- [x] 3.3 删除 `engine/work_units/reducers.py`、`graph/routing.py` 整文件；`project-structure.toml` 中两处 `[[required_paths]]`（PRS-001/PRS-003）同步移除；`check_project_architecture.py` 通过
- [x] 3.4 删除 `GATED_FIELDS`（`state.py`，连同 `test_state_contracts.py`/`test_gate.py` 相关用例）、`MAX_FAKE_TRACE_ENTRIES`/`MAX_FAKE_REPAIR_ATTEMPTS`（`lifecycle.py` + `__all__`）、`dedupe_source_urls`（`bundle.py` + `test_bundle.py` 用例）、`bundle_control._request_id`/`_pending_interrupt`；同步 `__all__`

## 4. 去重与注释修正

- [x] 4.1 `runtime/research.py` 合并 WAVE0/WAVE1 worker policy 为参数化 `_worker_policy(policy_name=..., graph_context=...)` + 共享 `WORKER_TOOL_NAMES`；`_wave0_worker_policy`/`_wave1_worker_policy` 保留为薄包装（`tests/unit/test_research_runtime_capabilities.py` 仍 import 它们）；`tests/graph`/`tests/unit` 无回归
- [x] 4.2 修正误导注释：`agents/middleware.py:69` docstring（None→实际 `-1`）、`domain/gate.py:142` 注释（参数实为 gate-state Mapping）、`domain/state.py` 模块 docstring（移除 change-01/skeleton_state.py 引用）；`engine/real_gates.py:139` 改用 `FINAL_DELIVERY_GATE_VIEW_KEY`

## 5. 验证与收尾

- [x] 5.1 `UV_OFFLINE=1 make verify` 全绿；`tests/contract/test_identifier_single_sourcing.py` 绿；每项删除的 grep 零调用清单随提交记录
- [x] 5.2 `openspec validate single-source-runtime-identifiers-and-retire-dead-code --strict` 过；`git diff HEAD --check` 无输出；记录 `git status --porcelain=v1 --untracked-files=all`、`git ls-files --stage deerflow`、`git submodule status -- deerflow`、`git -C deerflow status --porcelain=v1 --untracked-files=all`，review `git diff --submodule=short`
