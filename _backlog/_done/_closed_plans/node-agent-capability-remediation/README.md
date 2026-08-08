# Node Agent Capability Remediation — 支撑盘点

> 这是一组支撑 [Node Agent Capability 架构纠偏计划](../node-agent-capability-remediation-plan.md) 的事实盘点和目标映射；它们不是运行时权威，也不授权实现。
> 更新：2026-07-27

## 阅读顺序

1. [current-state-inventory.md](current-state-inventory.md)：先看今天到底有哪些 node、哪些真的调模型、每个 branch 实际给了模型什么，以及已确认的不一致。
2. [target-capability-map.md](target-capability-map.md)：再看每个 agent branch 应拥有的独立能力、目标 local Markdown 和待审定的工具姿态。
3. [proposed-prompt-compositions/](proposed-prompt-compositions/)：逐 node 审阅拟议最终 system + human prompt 组合；它是待审定原文，不是当前运行时事实。
4. [node-test-strategy.md](node-test-strategy.md)：逐 capability 审阅 zero-API fake model/tool、bridge 和真实 node seam 的测试设计。
5. 返回主计划：决定 capability contract、迁移顺序和 OpenSpec change 边界。

## 盘点口径

“智能 node”在本目录中有一个可复核的技术口径：它是指生产路径上经
`NodeExecutionCapabilities.run_agent()` 到达 `RuntimeNodeAgentBridge` 并建立模型 agent
的一次 branch，而不是名称听起来像 planner / critic / writer 的任意 Python 文件。

截至 2026-07-27：

- graph 有 11 个注册逻辑 node；
- 6 个 node 包拥有实际 model invocation；
- 13 个顶层 `NodeExecutionRequest` builder 对应 16 个初始或 repair 执行 branch；
- 5 个注册 node 目前是 deterministic 或明确 deferred agent，已在现状盘点中记录，
  但不应被强行加 prompt。

这一定义防止两种相反的错误：漏掉隐藏在 subgraph 的真实 agent branch，或为了“每个
node 都有 prompt”的形式要求而给不应调用模型的状态/格式化节点增加不必要风险。

## 共同证据

当前所有 16 个 branch 都由
`agents/phase_prompt.py::render_phase_agent_prompt()` 组合相同的
`resources/node_agent/runtime_policy.md` system text；node-specific 内容在 `Objective` 和
`Expected output` 的 human message 中。现有生成审计目录 `agent/node_prompts/` 已把这个
事实逐项展示出来。

本目录的“目标”列不是已经批准的代码设计。它们是进入 OpenSpec proposal 前必须审查的
能力清单，避免未来只看一个 generic prompt 又重新失去全局视野。
