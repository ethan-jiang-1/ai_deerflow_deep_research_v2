# BUG-026: Gate fatigue 没有区分失败的工作单元

> 严重级别: P0 | 发现: 2026-08-15 | 状态: 活跃（修复实现待验证）

## 症状

2026-08-15 的真实研究在 Wave1 三次访问后终止为 `research.blocked`。三次 gate failure 分别
关联不同的工作单元（`w0000`、`w0004`、`w0008`），但第三次仍被判为相同失败的 fatigue，导致
研究在仍有新证据路径时被不可重试地阻断。

## 根因

`gate_kernel` 的 fatigue fingerprint 仅由 `(failure_code, rule_name)` 构成，遗漏
`Failure.ref`。因此“相同规则、不同 WorkSpec”的失败被错误合并为重复失败；它把进展误判成
无效重试。

## 复现

构造同一失败码和规则、但 `Failure.ref` 依次为三个不同工作单元的 gate 结果。第三次在旧实现
达到 fatigue 阈值并进入 blocked，而不是重置计数。真实 Bundle 的 terminal 事件为
`diag_38b9cfc7957fce5289930885`。

## 修复关联

实现已将 fingerprint 扩展为 `(failure_code, rule_name, ref)`，并新增
`tests/engine/test_gate_kernel.py::test_different_failed_reference_resets_fatigue`。本卡保持活跃，
直到该测试和相关 Wave1 测试在当前工作树通过。
