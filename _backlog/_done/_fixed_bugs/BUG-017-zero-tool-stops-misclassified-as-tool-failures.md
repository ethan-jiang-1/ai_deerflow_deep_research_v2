# BUG-017: Topic planning 的零工具停止被误报为研究工具失败

> 严重级别: P1 | 发现: 2026-08-02 | 状态: 活跃

## 症状

对 real demo 执行以下研究，在确认范围后进入 `topic_planning`：

```bash
cd deerflow_research
make demo-real DEMO_ARGS='--question "比较两种储能路线的成本、风险与适用场景"'
```

保留 run `r_pT1B7bsx-CnWHknsW_HcykxMnQA5ddYDX4sRHSb_Dlk` 在
`model_tool.started` 后约 40 秒终止，并向用户展示“研究工具未能完成请求”。
但 topic planning 的执行策略明确禁用所有工具。

一个无网络内存重放让零工具 agent 抛出
`AgentBudgetError(NodeFinishReason.USAGE_UNAVAILABLE, ...)`，实际结果为：

```text
finish_reason=usage_unavailable
failure_code=tool.execution_failed
```

## 根因

`RuntimeNodeAgentBridge.run_agent()` 对所有 `NodeAgentStop` 无条件写入
`RunFailureCode.TOOL_EXECUTION_FAILED`。`NodeAgentStop` 的子类同时承载
预算超限、usage 缺失和策略拒绝，不能被统一解释为工具执行失败。

这还会丢失安全的停止原因：bundle 事件只保留最终的
`tool.execution_failed`，无法在事后区分 `usage_unavailable`、
`budget_exhausted` 与实际 policy denial。

## 影响

- 零工具阶段会给出错误的故障归因和错误的用户建议（检查工具服务）。
- 支持人员无法仅凭 retained bundle 判断是否应检查模型 usage、预算，还是工具策略。
- 后续的 worker-failure 分类会把非工具故障归入 tool execution，污染恢复与统计。

## 复现

在 `RuntimeNodeAgentBridge` 的 unit seam 中，以 `node_name="topic_planning"`、
`tools_enabled=False` 和空 `allowed_tool_names` 构造请求；让 fake node agent
抛出 `AgentBudgetError(NodeFinishReason.USAGE_UNAVAILABLE, ...)`。断言结果保留
`USAGE_UNAVAILABLE`，且 `problem.code` 不得为 `tool.execution_failed`；当前断言为红。

现有 `tests/unit/test_node_agent_bridge.py::test_missing_usage_metadata_is_terminal`
只断言 `finish_reason`，没有断言用户可见 failure code，因此未覆盖该映射错误。

## 修复关联

尚未创建 OpenSpec change。应建立一个运行时 failure-projection change：按
`NodeAgentStop.finish_reason` 分别投影预算/usage/policy 类别，保留真正的工具失败
分类，并在 retained 诊断中写入安全、有限的 stop reason。该 change 需补齐
bridge-to-presentation 回归测试。
