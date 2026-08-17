# BUG-034: `soft-bundle inspect` 对 mode 002（scripted-real）bundle 永远报 unavailable

> 严重级别: P2 | 发现: 2026-08-18 | 状态: 已修复

## 症状

按 [runbook-002](../_local_demo/runbook-002-easy-scripted-real.md) 第 3 步执行：

```bash
cd deep_research_harness
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="inspect $ROOT"
```

失败并退出码 2：

```
Run Bundle or its contained Event Journal is unavailable for safe inspection.
make: *** [soft-bundle] Error 2
```

runbook 第 3 步的检查点（`Observed summary: completed@final_delivery generation 0`、`Journal health: complete`）因此永远无法满足。

同时确认：run 本身 `RESULT: PASS`；`status` / `path` / `phases` / `verify` 全部正常；bundle 的
`diagnostics/events.jsonl`（48 个事件）、`diagnostics/run-summary.json`
（`journal_availability: complete`）、`final/report.md` 均完好。即 bundle 健康，是 inspect 找不到它。

## 根因

`scripts/soft_bundle.py` 的 `cmd_inspect` 把 root 解析成 `current_bundle_id` 后委托：

```bash
make demo-sessions DEMO_ARGS="inspect <bundle_id>"
```

`scripts/demo_sessions.py` 用 `DemoAdapter(bundle_root=.deep-research-demo-runs)` 的**默认
fixture-graph scope**（`demo-user` / `demo-thread-<profile_hash>`），scope bucket =
`s_f03ba8558dfae1fbbdab`，只在
`.deep-research-demo-runs/workspace/deep-research/scopes/<bucket>/` 下按 bundle_id 解析。

而 mode 002 的 bundle 由 `debug-scripted-real-workflow` 创建在**独立的 run workspace**：

```
.deep-research-demo-runs/workspace/scripted-real/run-<ts>-<hex>/workspace/deep-research/scopes/s_5MTRx…/<bundle_id>
```

scope 是 `debug-operator` / `thread-<token>`（`debug_scripted_real_workflow.py:_local_envelope`），
与 demo_sessions 的固定 scope 完全不同。

`BundleLifecycle.resolve()` 是 scope 封闭的（`runtime/bundle_lifecycle.py`：scope 外的 Handle
必须不可见，只是"unavailable"），所以 inspect 对 002 bundle 永远找不到。对 mode 001
（fixture-graph，bundle 落在同一 demo scope 下）恰好匹配，能正常工作——这也是为什么该委托
从 001 沿用至今没暴露问题。

## 复现

```bash
cd deep_research_harness
ROOT=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="create --name 002-demo --mode 002" | sed -n 's/^soft_bundle_root=//p')
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run $ROOT --mode 002"    # RESULT: PASS
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="inspect $ROOT"           # 报 unavailable，退出码 2
```

## 修复关联

候选方向（不直接改 Harness 核心，按 `_backlog` 流程先定方案）：

- `cmd_inspect` 按 mode 分流：mode 002 时把 run workspace / scope 传给 demo_sessions（例如让
  demo_sessions 支持显式 workspace root 或 scope），而不是用固定 demo scope。
- 或由 `debug-scripted-real-workflow` 输出 bundle 的 event journal 路径，`soft-bundle inspect`
  对 002 直接渲染该 bundle 的 diagnostics（只读，不引入控制 authority）。
- 需要补一个 process-level 回归：真实跑一次 002 后 `inspect` 能输出 summary + journal health。

> 修复: 已修复（`fix-local-demo-tooling`：`soft-bundle inspect` 按 mode 分流，002 直接渲染记录 bundle 的只读 diagnostics；`debug-scripted-real-workflow` 补发终态观察，run-summary 到达 terminal）。
