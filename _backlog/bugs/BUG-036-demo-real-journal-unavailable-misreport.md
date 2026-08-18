# BUG-036: demo_real 终端显示 "Bundle 内 Event Journal 记录不可用" 但 journal 实际存在且 complete

> 严重级别: P2 | 发现: 2026-08-18 | 状态: 活跃

## 症状

两次真实 003 run 的 `demo-real-scripted` 终端输出，在 blocked 终态都打印：

```
  诊断引用: diag_xxx
  Bundle 内 Event Journal 记录不可用。
```

但同一 bundle 的 `diagnostics/` 实际存在（`events.jsonl` / `run-summary.json` /
`journal-manifest.json` 齐全），且 `soft-bundle inspect` 对同一 bundle 显示
`Journal health: complete`、`Observed summary: ...@...`。同一 bundle，两个
入口（demo_real 终端 vs soft-bundle inspect）对 journal 可用性的结论矛盾。

## 根因

（定位到呈现/诊断投影层，未深挖到具体字段）`demo_real.py` 的
`_failure_lines` / `_provider_failure_lines` 依据 `RunFailure` 的
`journal_record_created` / `diagnostic_location` 字段渲染 "Event Journal:
已创建/不可用"。blocked 终态经 `ResearchRunExperience` 投影时该字段为 false /
`unavailable`，而 bundle 磁盘上的 diagnostics 是完整的——**呈现层字段与
磁盘事实不同源**。需要核对 blocked 终态的 journal 字段投影路径
（`gate_result_to_state_update` → terminal incident → `RunFailure` 投影）。

## 复现

```bash
cd deep_research_harness
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run <root> --mode 003"   # run 停在 wave2 blocked
# 同一 bundle 再跑：
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="inspect <root>"          # Journal health: complete
```

## 修复关联

无关联 change（BUG-035 的观测副产物）。修复方向：让 demo_real 的 journal
可用性渲染与 bundle 内 diagnostics 实际存在性一致（或明确区分"运行期未写入"
与"进程内观察不到"两种语义）。
