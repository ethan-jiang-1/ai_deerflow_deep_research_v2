# BUG-014: provider.timeout 保留诊断无法标识超时责任方

> 严重级别: P1 | 发现: 2026-07-31 | 状态: 已修复（2026-07-31）

## 症状

真实 `make demo-real` 运行在 `hitl1` 返回 `provider.timeout` 后，保留事件只记录
闭合类别 `provider.timeout`、`no_response`、尝试序号和时间戳。现场记录显示第一次尝试约
30.48 秒、一次 1000 ms 重试、第二次尝试约 30.04 秒后耗尽。

这些信息足以确认策略曾重试并终止，但不足以回答运维处置所需的基本问题：是本地 bridge 的
wall-time 预算到期、OpenAI SDK 抛出超时，还是服务端在客户端期限内没有响应。因而不能将
该结果归因于已配置的 provider，也无法决定应该调整本地预算、检查网络/SDK，还是联系服务商。

## 根因

`NodeAgentBridge` 同时拥有至少两条可到达的 timeout 路径：它以
`asyncio.timeout(self.policy.budget.wall_time_seconds)` 包裹 `agent.ainvoke()`，并单独分类
`openai.APITimeoutError`。两条路径最终都可投影为相同的 `provider.timeout` / `no_response`
安全观察。见
[`node_agent_bridge.py`](../../../deerflow_research/src/deerflow_deep_research/runtime/node_agent_bridge.py#L355)
和 [`node_agent_bridge.py`](../../../deerflow_research/src/deerflow_deep_research/runtime/node_agent_bridge.py#L414)。

`RunEvent`、生命周期 trace 和终端 `ProviderObservation` 未保留一个闭合、脱敏的
timeout-origin 事实。现有诊断契约优先避免原始异常、provider body 和 URL 泄露是正确的，
但没有提供足以区分这些本地可判定分支的最小运维事实。

## 影响

- 现场支持会把本地超时误报为“某模型服务无响应”，或在真实服务故障时盲目调整本地设置。
- 自动重试耗尽后，用户只有“检查服务状态并新启动”的泛化建议，无法从保留记录验证该建议。
- 诊断系统无法帮助下一位开发者缩小根因范围，本身构成 DevOps 可观测性缺陷。

## 复现

在 `deerflow_research/` 运行真实 demo，待终态出现 `provider.timeout` 后使用可用会话检查命令：

```bash
make demo-sessions DEMO_ARGS="inspect <run-reference>"
```

检查 `diagnostics/events.jsonl`。它会给出 `provider.timeout`、retry 和耗尽的时间线，却没有
bridge wall-time、SDK/provider timeout 或等价安全 origin 字段。该断言应使用确定性注入的
bridge deadline 和 SDK timeout 两个 fixture，而不是依赖实际 provider 发生超时。

## 修复与验证

由 `harden-research-run-diagnostics-and-hitl-intake` 修复。`RuntimeNodeAgentBridge` 只在它
能直接观察到的分支产生闭合来源：自身 deadline 为 `bridge_wall_time_budget`，受支持的 SDK
异常为 `provider_sdk_timeout`；transport、legacy 与 generic no-response 不臆造来源。触发重试
与最终观察分别保留、关联、落盘并经精确记录验证后投影，未引入原始异常或 provider body。

- `tests/unit/test_node_agent_bridge.py::test_admitted_hitl_bridge_deadline_has_only_bridge_timeout_origin`
  和 `test_admitted_hitl_timeout_wrappers_are_classified_before_connection_wrappers[openai]`
  覆盖两个正向 owner 分支；`[httpx]` 保持来源缺失。
- `tests/domain/test_workflow_outcomes.py::test_controller_provider_diagnostic_reference_uses_the_shared_timeout_origin_identity`
  证明 controller-derived 路径复用共享安全身份。
- `tests/integration/test_demo_sessions.py::test_inspect_renders_only_the_exact_verified_terminal_diagnostic_projection`
  只从 exact verified projection 呈现两个角色的来源。
- 2026-07-31 的本 change focused suite 通过 228 项测试。
