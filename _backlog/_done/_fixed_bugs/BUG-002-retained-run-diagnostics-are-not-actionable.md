# BUG-002: 保留 run bundle 缺少可诊断的失败证据与摘要

> 严重级别: P1 | 发现: 2026-07-22 | 状态: 已修复（观察性）；Wave0 根因分类见 BUG-005

## 症状

现场 run 已在 `wave0` 终止，但 `demo-sessions inspect` 只列出若干“Available”文件，不能直接说明最后状态、最后阶段、失败分类、诊断引用、失败 work attempt 或下一步。`diagnostics/records.jsonl` 仅有 `research.blocked` 这一类别；三次 Wave0 attempt 只留下 `work-spec.json`，没有可供操作者定位的、经过脱敏的失败事件。

现场 bundle：

```text
agent/.deep-research-demo-runs/workspace/deep-research/r_SnrIKUGQhUwUIAWyht4dq_zJLGNftutorg24_bhX62E
```

其 `diagnostics/lifecycle.jsonl` 的最后记录是 `status=blocked`、`phase=wave0`、`diagnostic_ref=diag_b32706968b70e9c6af20a1b2`；CLI 却打印全局 journal 的另一引用 `diag_WUApFmNjkJUkMjR2anjrAqg1`。两者没有关联说明，且都不能定位 Wave0 attempt 失败类别。这些关键信息没有在 inspect 输出中汇总。

更根本地，bundle 没有按时间排序的执行日志：不能看到 Python runtime、图 node、worker attempt、模型调用、网页工具、校验、ledger submit、retry 和 terminal gate 的开始/结束/耗时。没有这样的 per-run log，开发者和操作者都无法从现场还原一个“Wave0 失败三次”的实际因果链。

## 根因

run-session 契约保存的是窄 lifecycle trace 与 failure category，session inspection 的呈现层只暴露固定文件列表。运行体验又为同一 terminal result 另写全局 diagnostic journal，未保留两个引用的关联。work-unit 生命周期只保存终态代码/哈希，不保存可关联的、脱敏且有界的失败事件。现有“有 bundle”不等于“有可诊断现场”。

## 复现

```bash
cd /Users/bowhead/ai_deerflow_deep_research/agent
make demo-sessions DEMO_ARGS='inspect r_SnrIKUGQhUwUIAWyht4dq_zJLGNftutorg24_bhX62E'
```

当前输出只显示 bundle 路径和文件名；无法从该输出判断该 run 已终止于 `wave0`、为何 blocked、哪些 attempt 失败、应读取哪个诊断记录。

## 修复关联

新建 focused OpenSpec change，建立脱敏、有界、可关联的 run diagnosis 投影：run 摘要必须包含 terminal/suspended 状态、阶段、时间、诊断引用、证据路径和下一步；每个 run 必须有按 sequence/timestamp 排序的 JSONL 执行事件日志，覆盖 Python runtime、图 node、worker attempt、模型/工具调用、校验、提交、retry/exhaustion 和 terminal；失败 attempt 必须能按 run/phase/work/attempt 关联到安全类别与摘要。未来 sandbox/pod 侧事件沿用同一 correlation 字段并由 runtime 收集/关联。原始异常、密钥、用户原文、模型/工具正文、绝对主机路径不得进入公开 CLI/TUI 投影。
