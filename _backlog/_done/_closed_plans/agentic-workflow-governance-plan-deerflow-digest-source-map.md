# DeerFlow Digest Source Map: Node-Agent Capability Foundation

> 配套材料：[Agentic Workflow 治理与 Node-Agent 契约](agentic-workflow-governance-plan.md)；[评审上下文](agentic-workflow-governance-plan-context.md)。
> 用途：为后续 `establish-node-agent-capabilities` OpenSpec change 提供一份经过筛选的 DeerFlow 机制阅读地图，而不是把 `_ln_deerflow_digest/` 变成第二份计划或运行时 authority。
> 范围：2026-07-27；阅读了 digest 的顶层目录和下列源码路径明确的分析笔记。

## 使用边界

`_ln_deerflow_digest/` 是指向 DeerFlow 研究摘要的符号链接；其同步说明显示，内容锚定于
上游 `4915b5e`（2026-07-07），而不是本仓库的 Deep Research runtime 规范。它适合借鉴
已经被上游实现验证的**机制和问题形状**，不适合直接复制类名、目录、配置或事实结论。
实际 change 仍须以 Deep Research 的 accepted spec、active delta、当前代码和最低责任测试
seam 为权威。

这份地图只回答四个问题：Node Agent 如何有明确能力；确定性工作流如何包住 LLM 认知；谁
实际拥有工具、sandbox、运行和持久化权力；怎样验证和观察这些边界。下表中的“影响”是对
后续 change 的约束，不是本次材料授予的实现授权。

优先目录是 `concepts/lead-agent/`、`concepts/subagent/`、`concepts/skills-tools/`、
`concepts/sandbox/`、`internals/agent-loop/`、`internals/middleware/`、`internals/runtime/`、
`internals/persistence/`、`operations/security/`、`operations/it-ops/` 与 `testing/`。其余目录
已按下文的排除规则审阅，不应因“与 DeerFlow 有关”而默认进入 capability foundation 的范围。

## 先读什么

1. 先读配套计划的“拟审定的控制模型”和“阶段 2”，再读
   [graph nodes and state](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/concepts/lead-agent/03-graph-nodes-and-state-design.md>)、
   [agent-loop code trace](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/internals/agent-loop/03-code-trace.md>)。
2. 再读 [subagent lifecycle](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/concepts/subagent/dual-threadpool-and-lifecycle.md>) 和
   [skills/tool assembly](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/concepts/skills-tools/skill-md-and-tool-assembly.md>)，把“角色说明”和“实际可用工具”分开看。
3. 然后读 [policy enforcement](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/operations/it-ops/03-policy-enforcement.md>)、
   [trust boundary](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/operations/security/04-trust-boundary.md>) 和
   [sandbox abstraction](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/concepts/sandbox/abstract-interface-and-three-impls.md>)。
4. 最后读 [agent test patterns](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/testing/04-agent-test-patterns.md>)、
   [workflow testing](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/testing/05-testing-skills-and-workflows.md>)、
   [record/replay](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/testing/07-record-replay.md>) 和
   [RunJournal](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/internals/runtime/04-journal.md>)。

## 1. Node Agent 的角色、提示与能力契约

| 推荐资料 | 它实际说明什么 | 为什么对 Deep Research 有用 | 对 `establish-node-agent-capabilities` 的具体影响 |
| --- | --- | --- | --- |
| [concepts/subagent/dual-threadpool-and-lifecycle.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/concepts/subagent/dual-threadpool-and-lifecycle.md>) | 上游 subagent 的可发现性同时来自 tool schema 和动态 system prompt；`SubagentConfig` 分别声明 description、system prompt、工具 allow/deny、skills、model、turn/timeout，并由运行时限制并发、取消和终态。 | 它把“一个角色被模型看到”与“该角色实际可以做什么”拆开，也暴露三套描述漂移的维护风险。 | 每个 `NodeAgentCapability` 应有稳定 ID、单一 local policy resource、工具 posture 和预算/结果契约；renderer 只从该声明组合 prompt。**不要**把 Node Agent 实现成 subagent 或复制其独立 loop/checkpointer。 |
| [concepts/lead-agent/02-soul-md-guide.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/concepts/lead-agent/02-soul-md-guide.md>) | SOUL.md 的示例把角色、原则、工作步骤、约束和输出格式分层表达；文件本身是注入 system prompt 的 lead-agent 人格资源。 | 可借鉴 node-local Markdown policy 的可审查写法，尤其是角色、方法、限制和输出形状分开写。 | capability Markdown 可以稳定采用 `Role`、`Method`、`Tool posture`、`Authority limits`、`Completion and uncertainty` 等章节；但不能把 SOUL.md 的 per-user/lead-agent 生效模型带入 node capability。 |
| [concepts/skills-tools/skill-md-and-tool-assembly.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/concepts/skills-tools/skill-md-and-tool-assembly.md>) | Skill 同时有 prompt guidance 与 `allowed-tools`；`get_available_tools()` 再按 config/MCP/builtin 等来源装配真实工具。request-scoped secrets 不进入 prompt、trace 或 checkpoint。 | 直接说明“文案说不能用工具”不是权限机制，真正的工具集合由运行时装配；也说明敏感运行时数据不应塞入 capability policy。 | capability 声明工具姿态，`NodeExecutionRequest` 声明数值约束，bridge 对实际 tool resolver 做 fail-closed 交集校验。不要把 node role、凭证或 provider 配置写回 root `config.yaml` 或 Markdown。 |

## 2. 确定性编排与 LLM 认知的分工

| 推荐资料 | 它实际说明什么 | 为什么对 Deep Research 有用 | 对 `establish-node-agent-capabilities` 的具体影响 |
| --- | --- | --- |
| [concepts/lead-agent/03-graph-nodes-and-state-design.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/concepts/lead-agent/03-graph-nodes-and-state-design.md>) | LangGraph state 由 node 返回局部 update、再由 reducer 合并；model/tools 与 middleware hook 的执行位置不同，subagent 也不是父图中的普通 node。 | 能把“图/状态/route 的 owner”与“模型生成文本或 tool call”的 owner 分开，避免让 prompt 直接变成 state 或 route authority。 | Deep Research graph/node handler 继续拥有 checkpoint、typed state、retry、route 和 materialization；Node Agent 只返回 typed candidate，既不能写 checkpoint，也不能宣布 gate 或 route。 |
| [internals/agent-loop/03-code-trace.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/internals/agent-loop/03-code-trace.md>) | 将 `run_agent()` 定位为启动、context/checkpoint/journal/SSE 生命周期外壳；实际 superstep loop 在 LangGraph `PregelLoop.tick()`，middleware 和条件边构成确定性外围。 | 这是“DeerFlow 的魅力”最直接的上游佐证：运行框架不必替模型做研究判断，但可确定性地调度、记录、中断和恢复其工作。 | 不为 capability 再造 controller 或平行 state。把 four-layer prompt renderer 接入现有 runtime bridge；保留 graph 的 deterministic candidate admission，而不是让 LLM 决定下一 node。 |
| [internals/middleware/01-hooks-and-flow.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/internals/middleware/01-hooks-and-flow.md>) | 精确区分 graph-node hook 与 model/tool 内联 wrapper；tool wrapper 可在不调用 handler 时阻止执行，`Command(goto=...)` 才有路由中断能力。 | 说明 prompt、middleware、graph node 不是可互换的实现位置。 | capability policy 只能指导认知；工具拦截、失败投影、取消和 route 仍留在 runtime/graph 的已命名 owner，不把这些控制语义下放到 `capabilities/*.md`。 |
| [operations/it-ops/03-policy-enforcement.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/operations/it-ops/03-policy-enforcement.md>) | 明确给出四层：system prompt 是概率性约束，Guardrail、sandbox audit、循环/并发/超时才是确定性 enforcement。 | 它正好反驳“写一段更强 prompt 就等于实施 policy”的旧方向。 | proposal/design 必须把 policy 文字与对应 mechanical enforcement、failure mode 和 evidence seam 一一列出；没有 runtime enforcement 的约束只能如实标为行为指导。 |

## 3. 工具、运行时、sandbox 与持久化权威边界

| 推荐资料 | 它实际说明什么 | 为什么对 Deep Research 有用 | 对 `establish-node-agent-capabilities` 的具体影响 |
| --- | --- | --- |
| [operations/security/04-trust-boundary.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/operations/security/04-trust-boundary.md>) | 从认证和 user context 到 Guardrail、路径 containment、输出清洗和 sandbox provider 的逐层边界，且区分 Browser/Internal/IM 的 trust boundary。 | 提醒 capability input 中的用户、来源、模型草案和可信 graph data 必须显式分层；tool permission 不能靠模型自行判断。 | renderer 必须有 trusted assignment 与 untrusted evidence envelope；bridge/runtime 负责实际工具、用户隔离、路径和安全失败投影，capability 不获得新的权限。 |
| [operations/security/03-guardrail.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/operations/security/03-guardrail.md>) | `GuardrailMiddleware` 在 tool call 上 evaluate allow/deny，配置可 fail-closed；文章也列出 raw arguments、thread/subagent identity 等局限。 | 能避免把 capability tool posture 错当作完备安全策略，也为审查“实际 enforcement 能观察到什么”提供问题清单。 | change 只为每个 capability 建机械可比较的 posture；不能声称它解决了上游 guardrail 尚无的信息。对 Deep Research 的 bridge，要测 capability permit 与 runtime tool availability 的交集，而不是只测试 prompt 文案。 |
| [concepts/sandbox/abstract-interface-and-three-impls.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/concepts/sandbox/abstract-interface-and-three-impls.md>) | sandbox 统一了 command/file 操作接口，但 provider 的隔离强度不同；local host bash 默认关闭，工具注册本身也有能力门控。 | 说明 Node Agent 的“工具可用”是具体 execution environment 的事实，不是 static Markdown 事实。 | `RuntimeNodeAgentBridge` 保持唯一的 sandbox/tool adapter；capability 不直接取得 Sandbox 或文件路径权力。tool posture mismatch 应在 bridge 构造时失败，而非由 LLM 自我约束。 |
| [internals/runtime/01-run-manager.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/internals/runtime/01-run-manager.md>) 和 [internals/persistence/db-checkpointer-store-backends.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/internals/persistence/db-checkpointer-store-backends.md>) | 前者区分活跃 run control、取消、并发策略、store fallback 和 orphan reconciliation；后者区分 checkpointer、run event store 和 stream bridge。 | 支持计划中“候选不是 checkpoint fact”的边界：活跃控制与持久化状态都不属于节点认知角色。 | capability result 经 parser/evaluator/materializer 后才写 graph state/artifact；不要让 capability resource 或 LLM output 直接承担 run status、checkpoint、thread history 或 retry ownership。 |

## 4. 评估、测试与可观测性

| 推荐资料 | 它实际说明什么 | 为什么对 Deep Research 有用 | 对 `establish-node-agent-capabilities` 的具体影响 |
| --- | --- | --- |
| [testing/04-agent-test-patterns.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/testing/04-agent-test-patterns.md>) | 提供 FakeToolCallingModel、记录 bind_tools、prompt composition、middleware assembly、tool result 和 filesystem-boundary 的确定性测试模式。 | 与计划的前四层机制证据直接对应；第五层 branch coverage 是跨这些 seam 的完整性约束。 | 新 change 至少覆盖：缺 capability/resource/generic fallback 的静态失败；renderer/catalog 一致；工具可见性和 required/forbidden tool 的 bridge 行为；scripted model 通过真实 node 后的 parser/repair/route。 |
| [testing/05-testing-skills-and-workflows.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/testing/05-testing-skills-and-workflows.md>) | `interrupt_before=["tools"]` 可在实际工具执行前检查模型决策；trajectory 测试可检查调用顺序；文档也把更正式的 `AgentEvals` 作为可选外部库。 | 适合测试“系统没有阻止正确行为”和“工具 posture 生效”，同时不把它误报为模型质量证明。 | 将 scripted/fake 测试定位为 contract/evidence；把真实研究质量、语义理解和来源取舍留给后续 scenario/live eval change，不作为 foundation 完成条件。 |
| [testing/07-record-replay.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/testing/07-record-replay.md>) | 通过归一化输入、caller-aware key 和 golden event shape 做 Gateway regression；为稳定回放而刻意排除 system message。 | 可以守住 SSE/state/middleware shape 漂移，但不能直接评估 node-local policy 的好坏。 | 将 replay 放在 integration regression 层；另建 renderer/catalog 断言，不能以 replay 未变或 golden 通过声称 prompt/capability 质量已验证。 |
| [internals/runtime/04-journal.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/internals/runtime/04-journal.md>) 和 [operations/it-ops/04-audit-observability.md](</Users/bowhead/ai_deerflow_deep_research/_ln_deerflow_digest/operations/it-ops/04-audit-observability.md>) | RunJournal 将 LLM/tool/run 事件、latency、caller 分桶 token 和 middleware audit 写入 event store；可观测性材料也明确指出 guardrail deny 不入 journal、没有 operation-completeness verification 或聚合 dashboard。 | 使“可审计”成为具体而克制的主张：能记录什么、缺少什么都要说清楚。 | 若变更添加 capability ID 到 catalog/trace/journal，应把它视为可选且需单独 contract；在没有运行时事件字段前，不承诺 capability-level audit 或模型行为完整性。 |

### 当前 Deep Research 资产基线

下面是 2026-07-27 对本仓库的独立快照，不是 digest 的上游数字：pytest 共收集 2037 个
case，其中 deterministic aggregate 为 2027，fast lane 为 1857。大数字主要来自传统
correctness 层；仅 `contract/domain/engine/unit` 就有 1608 个 case。必须继续保留这些测试，
但不能让它们成为 agentic capability 的完成分母。

| Evidence 层 | 当前资产 | 对后续 change 的约束 |
| --- | --- | --- |
| Code correctness | 141 条 central claim；fast lane 1857/1857 passed | 保护 graph、schema、parser、store、预算和权限；不得据此宣称认知质量 |
| Deterministic workflow | 16 条 central claim / 16 个 selected case；14 个 scripted-real、2 个 real-node/fake-capability | 从 6 个 model owner 扩为 16 production branch 的逐项 matrix；成功、高风险、repair/tool posture 不得互相代替 |
| Live behavioral | 8 个 collected test、6 个 canary scenario、4 条 central claim | 为语义理解、选源和综合建立可重复基线；preflight 或一次 provider 成功不等于质量通过 |
| Release acceptance | 1 个 full-real case / 1 条 claim | 只证明完整系统协作，不承担 branch 诊断或统计分布证明 |

当前 `make test-assets` 会通过，说明 asset/selector/claim 引用闭合；实际 lane 并非全绿：
integration 为 131 passed、19 failed、4 skipped、15 deselected，workflow 为 15 passed、1
failed。地图中的测试模式只能帮助补正确的 seam，不能把 inventory checker、marker 或
record/replay 的通过转换成模型能力结论。

因此使用上游 testing 资料时，coverage unit 必须写成
`branch × behavior × authenticity`。如果一个新增测试没有增加某条 branch 的 trajectory、
tool exposure/call、副作用、candidate admission 或 live quality 证据，它只是控制面回归，
不应计入 capability foundation 的完成率。

## 已查看但不推荐作为本 change 的设计依据

| 区域/资料 | 不推荐原因 |
| --- | --- |
| `getting-started/`、`overview/` 的一般部署/请求导览、`frontend/`、`operations/deployment/`、`operations/channels/` | 它们用于安装、进程拓扑、UI 和通道适配，不回答 Node Agent capability 的语义、candidate admission 或工具 posture。必要时只作运行环境定位，不应进入 capability foundation 的 primary scope。 |
| `concepts/lead-agent/02-soul-md-guide.md` 的 per-user SOUL 路径和模板细节 | 仅保留其“分层写角色/方法/约束/输出”的表达方式；SOUL 是 lead-agent personality，复制其存储、热加载和 user override 会制造第二权威。 |
| `concepts/subagent/` 的线程池、后台轮询、独立 checkpointer、`task` delegation 协议 | 它证明 subagent 与 Node Agent 是不同层次；后续 change 不需要新增并发 agent loop 或任务调度器。仅借鉴稳定角色、工具实际强制和预算边界。 |
| `internals/middleware/03-catalog.md` 的具体顺序/编号 | 可作为上游 middleware 覆盖面参考，但不应把它的“29 个 middleware”和编号视为本仓库的稳定 API；同 digest 内安全材料与 catalog 的位置编号已有不一致。应以当前 Deep Research runtime 代码和 tests 判断真正 hook owner。 |
| `concepts/memory/`、MCP、configuration、model-layer 的实现细节 | 这些分别处理跨会话 memory、外部工具协议、operator configuration、provider compatibility；它们不应该决定 node-local role 或让 `config.yaml` 变为 prompt/route authority。仅当 change 触及对应 interface 时再按 Agent Charter 的 focus gate 定向阅读。 |
| `testing/07-record-replay.md` 作为能力质量评估 | 它排除了 system message 才能稳定回放，验证的是 event/state shape 及由行为改变带来的回放 miss，不是 policy 完整性或研究结论质量。 |

## 给 Review 的结论

建议把 digest 的价值压缩为五条可执行判断：

1. 每个 Node Agent 的角色说明、工具 posture 和动态 assignment 需要分离，但只有 runtime
   能兑现工具、sandbox、预算和取消。
2. 确定性 graph 不是要被模型替代的“旧逻辑”；它正是 candidate -> evaluator -> state/route
   这一安全、可恢复闭环的 owner。
3. Prompt 中的约束是行为指导，不能替代 fail-closed tool enforcement、路径隔离、预算或
   deterministic parser/evaluator。
4. Foundation change 可用 deterministic fake/fixture 证明 wiring 和边界；模型理解、来源选择
   与研究质量必须留给后续专门的 scenario/live evaluation change。
5. 2037/2027/1857 这些 collection 数只能描述测试体量；能力验收必须同时给出 16-branch
   matrix、workflow/live/release 分布和各 lane 的真实结果。

每次实际使用本地图中的观点前，都应回到当前 Deep Research owner：`agents/` 的 capability
contract、`graph/` 的 node seam、`runtime/` 的 bridge，以及对应 OpenSpec delta 和测试。
