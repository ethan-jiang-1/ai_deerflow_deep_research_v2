# BUG-003: 真实 CLI 不清楚地区分运行中、已结束与可恢复性

> 严重级别: P1 | 发现: 2026-07-22 | 状态: 已修复

## 症状

真实 CLI 在每次 dispatch 时只显示一次“正在等待生命周期返回结果（仅返回结果模式）”。liveness 心跳实际被 CLI 去重器压掉；用户看不到耗时、正在执行的阶段、最近进展、该进程是否仍存活、终态是否已经写入 bundle，也不知道 Ctrl-C 后是仅停止本地等待还是会取消研究。

现场 run 最终在 2026-07-22T03:59:53Z 以 `blocked` 结束，但交互片段停在“正在等待”，导致用户合理地以为仍在后台运行。核验时没有发现该 real demo 的存活 `demo_real.py` 进程；该 run 的持久性本来就是 `same_process`，不能跨进程继续。

## 根因

`ResearchRunExperience` 生成工作中更新，但 `demo_real._dispatch_observer()` 按 `(action, message)` 去重，所有同文案心跳只显示一次。展示层没有定义清晰的 run-state 摘要或统一的结束回执；“same_process”也没有转化为用户可操作的生命周期语义。

## 复现

```bash
cd /Users/bowhead/ai_deerflow_deep_research/agent
make demo-real DEMO_ARGS='--question "比较锂电池和液流电池在电网储能中的成本、风险与适用场景"'
```

在模型/网页工作阶段观察输出：只会出现一次等待文案，不能从 CLI 判断进程状态或最近阶段；随后只能靠另一个终端手工 inspect run ID。

## 修复关联

新建 focused OpenSpec change。CLI/TUI 必须在不泄露原始异常的前提下提供持续的状态行（run ID、阶段、elapsed、最后事件时间）、明确的 terminal 回执与 inspect 命令；文档必须区分 retained inspection、same-process continuation 和 restart-durable operation。测试应覆盖心跳可见、终态可见、Ctrl-C 语义与不含敏感信息。
