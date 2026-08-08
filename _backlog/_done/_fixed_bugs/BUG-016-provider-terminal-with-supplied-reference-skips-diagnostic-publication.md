# BUG-016: 带既有 diagnostic_ref 的 provider 终态跳过诊断落盘

> 严重级别: P1 | 发现: 2026-07-31 | 状态: 已修复（2026-07-31）

## 症状

现场 run `r_O9XU_UbsEE1LIm6utC4kmXF4gcxVG94bVd8QYFuyaSs` 返回
`provider.timeout`，并将 `diag_1b9f964333956fb6422de6c6` 标为 `session_bundle`。
正确的只读检查能找到 retained bundle、`run-summary.json`、`events.jsonl` 与
`lifecycle.jsonl`，三者都引用该 ID；但 bundle 缺少
`diagnostics/records.jsonl`，全局 support journal 也没有该引用。

因此终态声称“诊断位置: 保留会话 bundle”，而其唯一诊断引用在实际存储中不存在。
这是 `BUG-015` 修复后用户仍会遇到的真实 runtime 缺陷，而不是打印命令的后续文案问题。

## 根因

`RunSessionStore._publish_sync()` 仅在 `fact.diagnostic_ref is None` 时派生引用并写入
`diagnostics/records.jsonl`。provider terminal 已由上游提供稳定的 diagnostic reference，
于是跳过整个写入分支；之后同一引用仍被写到 event、trace、summary 和返回的
`RunSessionView.terminal_diagnostic_ref`。见
[`run_session.py`](../../../deerflow_research/src/deerflow_deep_research/runtime/run_session.py#L349)。

`ResearchRunExperience._provider_diagnostic_location()` 只根据 returned session view 的
available 状态和引用相等判断 `session_bundle`，没有验证 diagnostic record 已成功发布。见
[`run_experience.py`](../../../deerflow_research/src/deerflow_deep_research/runtime/run_experience.py#L864)。

这直接违反 `RER-009`：声明 `session_bundle` 前必须以同一 opaque reference 将诊断记录
发布到 retained bundle；否则必须诚实降级为 `support_journal` 或 `unavailable`。

## 影响

- provider 故障终态携带不可解析的引用，支持与开发者无法核对分类记录。
- UI 误导用户诊断已被保留，掩盖实际的记录发布失败/遗漏。
- `BUG-014` 所要求的更丰富但安全的运维事实即使加入，也会沿同一分支丢失。

## 复现

以 provider-terminal fixture 构造一个带预先提供 `diagnostic_ref` 的 record-bearing terminal，
通过真实 `RunSessionStore.publish()` 发布后断言：

1. `RunSessionView` 只能在 `diagnostics/records.jsonl` 已存在且含完全相同 reference 时报告
   terminal diagnostic reference；
2. 文件不存在或写入失败时，`ResearchRunExperience` 必须报告 `support_journal` 或
   `unavailable`，不得报告 `session_bundle`。

现场只读证据也可复核：

```bash
cd deerflow_research
make demo-sessions DEMO_ARGS="inspect r_O9XU_UbsEE1LIm6utC4kmXF4gcxVG94bVd8QYFuyaSs"
```

输出列出 `diagnostics/events.jsonl` 和 `diagnostics/lifecycle.jsonl`，但不会列出
`diagnostics/records.jsonl`；在该 bundle 与
`deerflow_research/.reports/deep-research-diagnostics/records.jsonl` 搜索该 reference 都无结果。

## 修复与验证

由 `harden-research-run-diagnostics-and-hitl-intake` 修复。`RunSessionStore` 现在对所有带
reference 的 record-bearing terminal 先原子写入并重验同一个 bounded diagnostic record，才
允许 event、trace、summary、manifest 或 session view 引用它。冲突、重复、畸形或写入失败时
不会声称 bundle 可用；`ResearchRunExperience` 仅基于 exact-record 验证设置 `session_bundle`，
否则保留原 reference 并使用既有 support-journal / unavailable 真相。没有存储层 category
registry，也没有替代 reference。

- `tests/unit/test_run_session_store.py::test_supplied_provider_terminal_reference_is_published_before_every_projection`
  和 `test_diagnostic_write_failure_prevents_terminal_reference_projection` 覆盖发布顺序与失败。
- `tests/contract/test_run_experience_failures.py::test_provider_terminal_falls_back_to_support_journal_with_same_reference`
  覆盖同 reference 的 fallback 与来源角色。
- `tests/integration/test_session_operations_lifecycle.py::test_broker_republishes_provider_timeout_origins_into_exact_retained_diagnostic`
  覆盖 broker 再发布不丢失 exact record。
- 2026-07-31 的本 change focused suite 通过 228 项测试。
