# BUG-008: 真实 demo 的模型超时没有可恢复路径或可操作诊断

> 严重级别: P1 | 发现: 2026-07-24 | 状态: 已修复并通过确定性验收（2026-07-25）

## 症状

真实模式研究在 HITL1 的模型调用耗尽 30 秒后终止。终端只显示“模型服务在限定时间内未响应”和泛化的“稍后重试”，没有说明失败类别、模型调用已尝试几次、是否已执行自动重试、下一次重试的等待策略，也没有可直接执行的重新开始命令。

现场 run `r_8DBlE7o5W6l7KwxxlrsOm7LJeGvJxSgRnzBT11_7cuc` 的 `run-summary.json` 已确认 `provider.timeout` 于 `hitl1` 终止。`diagnostics/events.jsonl` 记录一次 `model_tool.started`，然后在约 31 秒后终止，所有 `retry_count` 均为 `null`。

## 根因

HITL1 的 `ExecutionPolicy` 将单次模型调用 wall-time 限制为 30 秒；`RuntimeNodeAgentBridge` 在超时后投影 `provider.timeout`。`_generate_brief()` 的两轮循环只用于结构化输出修复，收到任何非成功 `NodeExecutionResult` 都立刻返回，因此瞬态 provider timeout/unavailable 的有效自动重试次数为零。已有运行事件 schema 支持 `retry_count`，但 HITL1 没有产生 provider-attempt、retry/backoff 或 exhaustion 事件；CLI 的失败投影也没有把重试处置或可执行的 fresh-run 命令显示给用户。

## 复现

```bash
cd /Users/bowhead/ai_deerflow_deep_research/agent
make demo-real DEMO_ARGS='--question "OpenSpec 的普及程度、正面与负面影响；只采用有影响力团队或社区的一手资料，并给出引用。"'
make demo-sessions DEMO_ARGS='inspect r_8DBlE7o5W6l7KwxxlrsOm7LJeGvJxSgRnzBT11_7cuc'
```

预期修复后，短暂 provider timeout/unavailable 在受限次数内自动重试；耗尽后，终端和 inspect 都显示安全的类别、尝试摘要、重试已耗尽的事实和不承诺 resume 的重新开始命令。认证、配置、结构化输出及取消不得被错误重试。

## 修复关联

OpenSpec change `harden-real-demo-provider-recovery`。该变更在最低责任层为可重试分类、退避、取消语义和运行事件建立确定性测试，并增强 CLI/TUI/inspect 的安全反馈；不修改 `backend/`、`frontend/`，不显示原始异常、请求、响应、URL、路径或凭据。

## 解决

HITL1 现在只对首个、直接分类且带安全 `ProviderObservation` 的
`provider.timeout` / `provider.unavailable` 执行一次图层自动恢复：固定等待
1 秒后重复完全相同的零工具 brief 请求，整次 visit 最多两次 bridge/model 调用。
认证、配置、未知、结构化输出和取消仍然 fail-closed。耗尽或 repair 槽已用尽时，
终端保留安全类别、服务标签/endpoint authority/HTTP 状态（如有）、尝试与处置摘要、
一个相关诊断引用和唯一的静态 `make demo-real` fresh-start 命令；inspect 只标为只读诊断，
不会冒充恢复或 resume。

运行事件与 retained session 保留有因果顺序的 bridge/model 调用、退避和耗尽观察，
并只在终端投影中传播既有诊断引用。`harden-real-demo-provider-recovery` 已通过完整
离线验证：快速测试 1767 项、集成测试 139 项和工作流测试 15 项全部通过；`backend/`
与 `frontend/` 未被修改。
