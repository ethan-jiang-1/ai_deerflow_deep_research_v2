## Why

BUG-068：`check_project_req_coverage.py` 在**干净工作树**上即红，报
`uncovered requirement: LDD-005` 与 `LDO-008`；`--phase closeout` 因此退出 1，任何
change 都无法按仓库流程归档。根因不是运行时缺陷，而是 archived changes
`2026-09-02-add-local-workflow-debug-driving` / `-observation` 关闭时证据登记丢失：
LDD-005 的 topology guard 已在 `runtime/debug_driver.py:290` 实现但**没有任何测试**，
LDO-008 的 typed-adapter 证据存在但未标 `@impl` 且缺少 spike 退休断言。

## What Changes

- **LDD-005**：在 `tests/integration/test_debug_driver_matrix.py` 新增 driver 级
  guard 测试 `test_topology_guard_fails_closed_on_multi_visit_superstep`——用注入的
  两节点 superstep 证明 driver 抛出 `DebugDriverError("topology_guard_multi_visit")`
  而非漂移推进；模块 docstring 补 `@impl LDD-005`。
- **LDO-008**：在 `tests/integration/test_demo_run_update_adapters.py` 补
  `@impl LDO-008`，并新增
  `test_read_side_tui_trace_spike_is_retired`，断言前尖刺
  `scripts/experiments/tui_trace.py` 已不存在（对应 requirement 的 spike 退休 scenario）。
- 无生产代码、规范、错误码或运行时行为改动。

## Capabilities

### New Capabilities

（无——仅补既有 requirement 的确定性证据。）

### Modified Capabilities

（无。`.openspec.yaml` 声明 `skip_specs: true`；LDD-005 与 LDO-008 的 requirement
文本与运行时行为均不变，本 change 只补齐其 `@impl` 证据缝。）

## Impact

- `deep_research_harness/tests/integration/test_debug_driver_matrix.py`（+1 测试，
  +`@impl LDD-005`）
- `deep_research_harness/tests/integration/test_demo_run_update_adapters.py`
  （+`@impl LDO-008`，+1 spike 退休断言）
- `_backlog/bugs/BUG-068-debug-requirement-evidence-uncovered.md`（登记）
- 无 `src/`、无 spec、无 `deerflow/` 改动。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/tests/integration/` 的两条
  evidence seam（`test_debug_driver_matrix.py`、`test_demo_run_update_adapters.py`）——
  修复 requirement 与证据之间缺失的登记，不触碰被证明的实现。
- **Seam classification:** deterministic-guardrail —— 为既有确定性 guard/typed-adapter
  行为补齐确定性证据；无认知面、无人工决策面、无运行时行为变化。
- **Question:** 能否在不改任何运行时行为、不伪造证据的前提下，为 LDD-005 与 LDO-008
  恢复真实可执行的确定性证据，使 `check_project_req_coverage.py` 与 `--phase closeout`
  在干净树退出 0？
- **Necessary adjacent/external contracts:** `runtime/debug_driver.py`（guard 实现，只读
  证据对象，本次不改）；`openspec/specs/local-workflow-debug-driving/spec.md` 与
  `local-workflow-debug-observation/spec.md`（requirement 所有者，本次不改）；
  `openspec/governance/check_project_req_coverage.py`（证据检查器，本次不改）。
- **Evidence seam:** 新测试直接执行 `topology_guard_multi_visit` 失败闭合与 spike 退休；
  `check_project_req_coverage.py` exit 0 且 `check_project_gate.py --phase closeout`
  exit 0（六组件全绿）。
- **Not in scope:** 任何运行时/规范行为改动；LDD/LDO 的实现；`check_project_specs.py`
  对 `skip_specs` 的忽略（发现 #1，另开 change）；`work_unit_storage_probe` 重命名；
  `deerflow/`。
- **Triggered review policies:** none: 仅补既有 requirement 的确定性测试证据，无新代码路径、无认知面、无 workflow outcome、无 node-agent 面。
