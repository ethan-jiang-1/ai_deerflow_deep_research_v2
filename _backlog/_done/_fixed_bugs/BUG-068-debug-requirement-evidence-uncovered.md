# BUG-068: 归档的两条调试 requirement 缺少确定性证据，closeout 门在干净树即红

> 严重级别: P1 | 发现: 2026-09-12 | 状态: 活跃

## 症状

干净工作树上运行 OpenSpec 治理门即失败，任何 change 都无法按仓库流程归档：

```
$ python3 openspec/governance/check_project_gate.py --phase closeout
[check_project_req_coverage.py] exit=1
  uncovered requirement: LDD-005
  uncovered requirement: LDO-008
```

## 根因

`check_project_req_coverage.py` 要求每条 active main requirement 至少被一个测试文件
（含 `test_*` 函数）或 OpenSpec 治理脚本的 `@impl` 引用。两条 requirement 在
archived changes `2026-09-02-add-local-workflow-debug-driving` /
`2026-09-02-add-local-workflow-debug-observation` 关闭时，代码/规范已落地，但证据
登记随归档丢失：

- **LDD-005（topology guard）**：guard 已在
  `runtime/debug_driver.py:290` 实现（`DebugDriverError("topology_guard_multi_visit")`），
  但全仓**没有任何测试引用该符号**；`tests/integration/test_debug_driver_matrix.py`
  只覆盖 LDD-001..004。这不是「少标 `@impl`」，而是确定性证据**从未存在**。
- **LDO-008（adapter 只消费 typed view + spike 退休）**：
  `tests/integration/test_demo_run_update_adapters.py` 已证明第一半（adapter 只消费
  共享 typed view），但漏标 `@impl LDO-008`；`scripts/experiments/tui_trace.py` 尖刺
  已删除，但无「spike 已退休」的断言。

这是证据/登记漂移，不是运行时缺陷。

## 复现

```bash
python3 openspec/governance/check_project_gate.py --phase closeout   # exit 1
python3 openspec/governance/check_project_req_coverage.py           # exit 1
```

## 修复关联

OpenSpec change `2026-09-12-repair-debug-requirement-evidence`：补 LDD-005 的 driver
guard 测试（multi-visit superstep → typed fail-closed）与 LDO-008 的证据标注 + spike
退休断言；`check_project_req_coverage.py` 与 `--phase closeout` 恢复绿。
