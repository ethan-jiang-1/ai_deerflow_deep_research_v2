# BUG-030: 真机 demo 长时间运行没有实时人类可读轨迹

> 严重级别: P1 | 发现: 2026-08-15 | 状态: 已修复（2026-08-16）

## 症状

真实 demo 在约 35 分钟研究期间，控制台只显示一次“正在等待生命周期返回结果”和
`本地等待: 0.0s（非执行流）`，直到终态才输出结果。Run Bundle 实际保留了 176 条安全事件，
但操作者在运行中看不到阶段推进、模型调用完成、校验失败、gate 决定或心跳，因而无法判断是
正常慢、卡住、还是已进入错误修复循环。

## 根因

`demo_real.py` 通过 result-only 的 `ResearchRunExperience.handle()` 等待最终结果；其 observer
只渲染少量 `Working` 更新，并没有订阅 event recorder 或把 Journal 事件投影为实时文本日志。
现有 JSONL 是受限的机器证据，不是可 tail、可扫读的操作者日志。

## 复现

执行真机 demo：

```bash
cd deep_research_harness
make demo-real
```

在长模型/检索阶段观察控制台。另在运行结束后读取 selected Bundle 的
`diagnostics/events.jsonl`，可看到期间已有大量事件而终端没有逐条可读投影。

## 修复关联

`_backlog/plans/runtime-operator-logs-and-live-trace.md` 定义了 Bundle 内人类可读 operator log
和实时控制台投影的双轨方案。实施前需要一个专属 OpenSpec change，以保持日志、Journal 和
生命周期权威的边界。

2026-08-16 验证：runtime-observability 三件套已归档（`instrument-deep-research-runtime-observability`
/ `add-deerflow-native-live-event-projection` / `wire-harness-observability-entrypoints`）；
默认真实 CLI（Gateway 路由）的 `demo_real.py` 现有 `_gateway_progress_observer` 逐条渲染
`deep_research.progress.v1`（阶段/校验/gate 事件）与心跳/错误行；`tests/unit/test_gateway_observer.py`
与 `test_events.py` 68 例通过，CLS-041 记录了公开 SSE `custom` 通道的真实探针成功。
embedded smoke 仍为明确标注的 result-only 本地校准路由。
