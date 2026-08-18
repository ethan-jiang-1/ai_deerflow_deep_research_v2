# BUG-036: demo_real 终端显示 "Bundle 内 Event Journal 记录不可用" 但 journal 实际存在且 complete

> 严重级别: P2 | 发现: 2026-08-18 | 状态: 已修复（openspec/changes/honest-delivery-and-real-run-diagnostics）

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

已修复：`openspec/changes/honest-delivery-and-real-run-diagnostics/`。根因即
上述投影层字段与磁盘事实不同源：`runtime/run_experience.py::
_failure_for_terminal` 只在 provider-diagnostic 分支解析
journal 可用性字段，gate-blocked incident（无 provider observation）恒投影
`unavailable`。修复把"观测已确认的 terminal diagnostic ref 已发布进 bundle
journal"检查泛化到**任何** blocked 终态（helper 更名
`_incident_diagnostic_location`），渲染层零改动。确定性证据：
`tests/unit/test_retained_terminal_result_cutover.py`（gate-blocked 三例：
已发布→created、未确认→unavailable、无观测→unavailable；provider 无 ref
仍在契约层 fail-closed）。原"无关联 change"段落系修复前状态。

## 修复后真机验证（2026-08-18，tasks.md 6.1）

修复后 003 run（bundle `b_T0Pu…`）终端渲染：run 输出明确打印
`诊断引用: diag_68670e0507bcfa723e4e401f`；`soft-bundle inspect` 对同一
bundle 显示 `Journal health: complete` 与
`Diagnostic reference: diag_68670e0507bcfa723e4e401f`，事件流完整可读（至
terminal #81）。修复前的"Event Journal 记录不可用"误报消失，gate-blocked
incident 的 journal 可用性如实投影——两个入口结论一致。
