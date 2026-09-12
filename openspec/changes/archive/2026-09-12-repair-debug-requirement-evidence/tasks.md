# Tasks: repair-debug-requirement-evidence

## 0. 背景（BUG-068）

- [x] 0.1 确认 LDD-005 非「漏标」而是**缺测试**：`runtime/debug_driver.py:290` 的
      `topology_guard_multi_visit` 全仓无测试引用
- [x] 0.2 确认 LDO-008 的 typed-adapter 证据存在（`test_demo_run_update_adapters.py`），
      缺 `@impl`；spike `scripts/experiments/tui_trace.py` 已删除但无退休断言
- [x] 0.3 登记 `_backlog/bugs/BUG-068-debug-requirement-evidence-uncovered.md`；
      活跃/fixed README 的 Next ID 推进到 BUG-069

## 1. LDD-005 证据

- [x] 1.1 `tests/integration/test_debug_driver_matrix.py` 新增
      `test_topology_guard_fails_closed_on_multi_visit_superstep`：注入两节点 superstep，
      断言 driver 抛 `DebugDriverError("topology_guard_multi_visit")`（未改生产代码，
      现有 guard 通过该测试被锁定）
- [x] 1.2 模块 docstring 补 `@impl LDD-005`（import 补 `SimpleNamespace` 与 `DebugDriverError`）
- [x] 1.3 该文件 9 passed

## 2. LDO-008 证据

- [x] 2.1 `tests/integration/test_demo_run_update_adapters.py` docstring 补 `@impl LDO-008`
- [x] 2.2 新增 `test_read_side_tui_trace_spike_is_retired`，断言
      `scripts/experiments/tui_trace.py` 不存在
- [x] 2.3 该文件 20 passed

## 3. 验证与收口

- [x] 3.1 `python3 openspec/governance/check_project_req_coverage.py` exit 0
- [x] 3.2 `python3 openspec/governance/check_project_gate.py --phase closeout` exit 0
      （六组件全绿；AGENTS.md 120 行 warning 为既有非阻断提示）
- [x] 3.3 `UV_OFFLINE=1 make verify` exit 0（2694 fast + 327 integration + 35 workflow；
      integration 由 325 增至 327 即本 change 的两个新测试）
- [x] 3.4 `--phase plan` 通过——发现 #1 已由
      `2026-09-12-honor-skip-specs-in-plan-gate` 修复，delta-less change 合法
- [ ] 3.5 按 openspec-archive-change 流程归档本 change
