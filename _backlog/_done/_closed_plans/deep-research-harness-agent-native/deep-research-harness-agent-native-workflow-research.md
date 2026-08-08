# Deep Research Harness Agent-Native Workflow 研究记录

> 类型: 研究记录 / change 准入输入 | 快照: 2026-08-07 | Git: `1a8a594`
>
> 范围: DeerFlow lead-agent workflow、Deep Research public `SOUL.md` / `SKILL.md`、
> Run Bundle `resume` / `refine` 语义与相关测试资产。本文只使用仓库源码、已接受规格和
> LangChain 官方文档；它不是运行时 authority、OpenSpec change 或实施授权。
>
> 落地: 本研究先由
> [`deep-research-harness-agent-native-progressive-plan.md`](deep-research-harness-agent-native-progressive-plan.md)
> 收敛为唯一渐进计划，再由单一 OpenSpec change
> [`establish-agent-native-research-direction-loop`](../../../../openspec/changes/archive/2026-08-08-establish-agent-native-research-direction-loop/)
> 承接；其 `design.md` / `tasks.md` 是实施工件，本文继续作为证据来源。

## 结论先行

1. **当前 UX 的主要缺口不是再加一个生命周期动作，而是缺少一段真正的 cognitive
   control program。** Run Bundle 已经有 `start`、`resume`、`status`、`cancel`、
   `refine` 五个闭集动作；但 public `SOUL.md` / `SKILL.md` 只罗列调用协议，没有教
   lead agent 如何把自然语言 follow-up 识别为 pending answer、run-level refinement、
   status、explicit cancel、ambiguous feedback 或 unrelated request。
2. **DeerFlow 的正确利用方式不是把 lifecycle 搬进 Markdown。** `SOUL.md`、skill 和
   prompt 负责让模型理解语境、分类意图并提出一个工具动作；middleware、严格 tool
   schema、trusted context、Bundle-local State 和 runtime handler 继续负责权限、关联、
   持久化与副作用。这与本项目 Charter 的 `Cognition proposes; deterministic owners
   validate, admit, and route` 一致（`openspec/governance/agent-charter/charter.md:63-67`）。
3. **`note` 不应成为第六个 lifecycle action 或通用 durable authority。** 用户口中的
   “note/补充/记一下”只是未经信任的自然语言：回答当前 pending subject 时走 `resume`；
   对同一个 Run 提交独立方向时走 `refine`；含义不清时先 clarification；明确停止才走
   `cancel`。现有 `custom_notes` 只是 HITL1 Research Profile 的有界字段，不是一个 Run
   refinement inbox。
4. **现有实现还不能宣称 active refinement 已经做对。** active `refine` 只写入单个
   `admitted_refinement`；生产代码没有在 graph safe point 消费它，第二次 admission 还会
   覆盖第一条。规格却要求在下一 durable safe point 消费。这个 implementation/spec gap
   必须在 agent UX change 之前或同一批准 change 中闭合。
5. **现有 public-entry replay 证明的是 plumbing，不是 prompt 决策质量。** 测试中的
   model response 已经预写 `start` / `resume` tool call，因此即使删除 Markdown 的意图判断
   规则也可能继续通过。下一轮需要同时具备确定性 action/state 测试、真实 DeerFlow skill
   加载与 handoff 测试，以及用真实模型重复运行的认知选择评测。

## 一手资料给出的 Agent Workflow 模型

### Deep Agents / LangGraph 的框架基线

LangChain 官方 [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)
把 agent harness 描述为工具、文件系统、context management、delegation 和 human-in-the-loop
等能力的组合，并明确其 durable execution 建立在 LangGraph 上。官方
[Skills 文档](https://docs.langchain.com/oss/python/deepagents/skills) 更直接说明：

- skill 用来封装 workflow、best practices、scripts、references 和 templates；
- 启动时只加载 name/description，相关时才读取完整 `SKILL.md`，再按需读取 supporting
  resources，即 progressive disclosure；
- 有效 skill 应包含 step-by-step procedures、decision criteria、expected input/output
  examples 和 edge cases，而不是只做工具名目录；
- 官方建议 `SKILL.md` 保持聚焦并低于约 5,000 tokens，而不是用极小的 byte ceiling
  阻止它表达工作流。

官方 [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) 与
[interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) 文档说明，checkpointed
state 和 thread identity 支撑暂停/恢复，resume value 必须回到对应 interrupt；节点恢复时会
从节点开头重新执行，因此副作用与 correlation 仍需确定性、幂等的 owner。官方
[LangGraph test guide](https://docs.langchain.com/oss/python/langgraph/test) 也建议用 fresh
checkpointer 测完整 stateful graph，并可通过 state + interrupt 做 partial execution 测试。

这些官方资料支持“Markdown 是认知程序、runtime 是状态与副作用 owner”的分工，但**不替代
本项目更严格的 Bundle-local lifecycle authority**。本项目明确规定 Bundle-local State，而
不是外部 LangGraph checkpoint，才是 pending request 和 continuation 的权威
（`openspec/specs/research-graph-lifecycle/spec.md:215-221`）。

### DeerFlow 当前实际组合方式

DeerFlow lead agent 不是一段大 prompt，而是分层组合：

| 层 | 当前事实 | 对 Deep Research 的意义 |
| --- | --- | --- |
| Lead composition | `_make_lead_agent` 将 model、filtered tools、middleware、system prompt 和 `ThreadState` 绑定成一个 agent（`backend/packages/harness/deerflow/agents/lead_agent/agent.py:595-625`）。 | UX 必须在真实组合中验证，不能把某个 Markdown 直接当作完整 system prompt 来模拟。 |
| `SOUL.md` | custom Agent 的 SOUL 被加载并作为 `<soul>` 追加进 lead system prompt（`backend/packages/harness/deerflow/config/agents_config.py:252-274`；`backend/packages/harness/deerflow/agents/lead_agent/prompt.py:817-822`）。 | 放稳定身份、诚实性和行为 guardrails，不复制详细 action state machine。 |
| Skills | base prompt 告诉模型按相关性读取完整 skill，并支持显式 slash activation（`backend/packages/harness/deerflow/agents/lead_agent/prompt.py:730-750`）；activation middleware 会安全读取完整 `SKILL.md` 并注入 hidden context（`backend/packages/harness/deerflow/agents/middlewares/skill_activation_middleware.py:129-199`）。 | `SKILL.md` 应承载具体 follow-up decision procedure、examples 和 edge cases。 |
| Durable context | middleware 捕获 skill/delegation 摘要，并把历史值作为 untrusted data 注入，而非 instruction authority（`backend/packages/harness/deerflow/agents/middlewares/durable_context_middleware.py:1-7,145-187`）。 | `bundle_id` 和工具结果可以帮助后续判断，但不能绕过 runtime 再验证。 |
| Middleware enforcement | middleware chain 加入 skill activation、durable context、summarization、tool filtering、loop/token limits、safety 和 clarification（`backend/packages/harness/deerflow/agents/lead_agent/agent.py:304-405`）。 | Markdown 选择动作；middleware 限制执行形态并处理失败/澄清。 |
| Clarification | 模型调用 `ask_clarification`，middleware 构造 typed human-input payload 并结束本轮（`backend/packages/harness/deerflow/agents/middlewares/clarification_middleware.py:25-36,67-99,195-238`）。 | ambiguity 不应被强行猜成 `resume`、`refine` 或 `cancel`。 |
| Subagents | task tool 创建隔离 cognitive worker，status contract 使用 closed typed states（`backend/packages/harness/deerflow/tools/builtins/task_tool.py:217-259,342-388`；`backend/packages/harness/deerflow/subagents/status_contract.py:35-63,87-114`）。 | 子 agent 适合研究工作，不应成为 public lifecycle authority 或另一个 Bundle controller。 |

因此，“agent-native”在这里有一个严格含义：**让模型通过 Markdown workflow 做只有模型擅长的
语义判断，然后只提交一个闭集 action candidate；让代码继续做只有确定性 owner 才能做的
admission。**

## Harness 内已有可复用的 Markdown 模式

Harness 实际上已经区分了两类 Markdown：

- node 的 `workflow.md` 明写为 reader interface，不是 runtime resource；例如 HITL1 文件声明
  model 只能提出 candidate，parser/domain/graph 才能 admit 和 route
  （`deep_research_harness/src/deerflow_deep_research/graph/nodes/hitl1/workflow.md:1-15,24-28`）。
- capability Markdown 才是 model-visible cognitive policy。loader 校验 metadata、body size
  和 exact capability id（`deep_research_harness/src/deerflow_deep_research/agents/capabilities.py:15-29,50-67`），
  renderer 把 body 追加进 system policy（`deep_research_harness/src/deerflow_deep_research/agents/phase_prompt.py:27-54`），
  runtime bridge 再强制其 tool posture 和执行预算。`hitl1-semantic-intake.md` 也明确要求模型只
  返回 semantic candidate，ambiguity 必须保留为 clarification
  （`deep_research_harness/src/deerflow_deep_research/graph/nodes/hitl1/capabilities/hitl1-semantic-intake.md:1-7`）。

public Run Bundle controller 应复用同一思路：`SKILL.md` 是 lead agent 的 cognitive program，
tool/runtime 是 deterministic admission owner。不要把 reader-only `workflow.md` 写得越来越长，
也不要在 Python 中重新实现自然语言意图分类。

## 当前 Public Agent Surface 的缺口

当前 `SOUL.md` 和 `SKILL.md` 都只用了几行描述五个 action 的 wire protocol
（`deep_research_harness/config/agent-template/SOUL.md:1-7`；
`deep_research_harness/config/public-skill/deep-research-controller/SKILL.md:1-14`）。配置确实把该
skill 与唯一 public tool 交给 `deep-research` Agent
（`deep_research_harness/config/agent-template/config.yaml:1-6`），configure 也会逐字安装
`SKILL.md`（`deep_research_harness/scripts/configure.py:301-324`）。因此缺的不是另一套装载系统，
而是把已有 skill 写成真正可执行的认知工作流。

目前至少有四个具体问题：

1. 没有 follow-up intent table，也没有 ambiguity、negative feedback、active conflict、ended target
   和 mixed answer/refinement examples。
2. tool runtime 要求**每一个** lifecycle action 所在的 AI message 只能有一个
   `deep_research` call（`deep_research_harness/src/deerflow_deep_research/tool.py:69-76,102-107`），
   但 surface 只明确说 `start` 是 sole tool call。
3. contract test 用 `<= 1400` bytes 强制 skill 保持“thin”并主要检查字符串存在
   （`deep_research_harness/tests/contract/test_public_skill.py:55-80`）。这会直接抑制官方 skills
   文档所要求的 decision criteria、examples 和 edge cases。
4. public replay 在模型响应中预写 tool call，再把单个 surface 直接作为 `system_prompt`
   （`deep_research_harness/tests/integration/test_public_entry_replay.py:64-145`）。它能证明 schema、
   tool execution 和 result projection，但不能证明真实 DeerFlow 会发现/加载 skill，也不能证明
   模型因该 workflow 而选对动作。

## `note` 的恰当语义

当前 codebase 没有 generic `Note` domain object。最接近的两个概念必须继续分开：

- `custom_notes` 是 HITL1 的 profile field，最大长度由 profile/human-interaction contract 限制
  （`deep_research_harness/src/deerflow_deep_research/domain/human_interaction.py:73`；
  `deep_research_harness/src/deerflow_deep_research/domain/profile.py:202`）。它随 profile proposal /
  acceptance 被 materialize，不是整个 Run 的任意消息收件箱。
- `RefinementInput` 是有界的 run-level direction，类型注释已经明确它不同于 HITL response
  （`deep_research_harness/src/deerflow_deep_research/domain/lifecycle.py:237-246`）。

建议把自然语言的处理规则冻结为：

| 用户表达及当前 subject | Lead agent candidate | 确定性 owner 必须保证 |
| --- | --- | --- |
| 正面回答当前展示的 pending question/choice | `resume`；答案只留在 latest HumanMessage，不放 tool args | Bundle-local pending id/correlation、exact-once consumption |
| “顺便重点看监管风险”“补充比较 X/Y”等同一 Run 的独立方向 | `refine(refinement=...)`；即使正在 suspended 也不冒充 answer | target/scope、bounded input、durable admission、pending request 保持不变 |
| “现在到哪了”“结果出来了吗” | `status` | read-only projection，不推断进度 |
| “先停掉/取消这次研究” | `cancel` | legal transition 与 idempotency |
| “方向不太对”“记一下这个”但无法判断 subject | `ask_clarification`，不做 lifecycle mutation | clarification payload；非交互 context 按现有 typed denial/degradation |
| HITL1 open-text response 同时给出 profile constraints | `resume`，由 bounded HITL1 semantic candidate 决定是否进入 `custom_notes` | profile parser/materializer 才能接受字段 |
| 已结束 Run 的明确继续打磨 | `refine` 必须在 tool call 中带已验证、无歧义的 `bundle_id` | ended target validation；不能凭 stale Handle 猜目标 |
| 单纯负面评价、抱怨或批评 | 不得推断 `cancel`；按是否含清晰 direction 选择 `refine` 或 clarification | 无显式 stop 就不产生 terminal effect |

“用户用了 note 这个词”本身不决定 action。决定因素是**当前展示给用户的 semantic subject**，
这也符合 Human-Interaction Integrity Policy 要求先识别 subject、candidate interpreter 和 effect
owner（`openspec/governance/agent-charter/policies/human-interaction-integrity.md:8-28`）。

## 必须先承认的 Refinement 实现缺口

接受的规格要求 active Bundle 的 refinement 在“下一 durable safe control point”被消费并记录
round transition（`openspec/specs/research-graph-lifecycle/spec.md:610-620`；
`openspec/specs/deep-research-harness-run-bundles/spec.md:93-124`）。当前实现并未完整满足：

- active `refine` 只调用 `admit_bundle_refinement`
  （`deep_research_harness/src/deerflow_deep_research/runtime/bundle_lifecycle.py:369-400`）；
- `admit_bundle_refinement` 是单槽 replacement，新的 input 直接替换旧值
  （`deep_research_harness/src/deerflow_deep_research/domain/state.py:474-480`）；
- `consume_admitted_refinement` 虽然存在，但本快照的 production search 只发现 ended-Bundle
  reactivation 在 `bundle_lifecycle.py:421` 调用；active graph safe point 没有调用者；
- ended Bundle 路径反而会立即 admit + consume 并递增 round
  （`deep_research_harness/src/deerflow_deep_research/runtime/bundle_lifecycle.py:402-423`）。

现有测试只证明 pending response 与 admitted value 能并存、pure reducer 能被手工调用、ended
Bundle 能 re-open（`deep_research_harness/tests/unit/test_state_reducers.py:31-73`；
`deep_research_harness/tests/integration/test_research_lifecycle_tool.py:112-176`）。它们没有让 active
graph 到达真实 safe point，因此不能作为 REG-021 已满足的证据。

下一 change 必须明确多条 refinement 在 safe point 前的政策：bounded FIFO、显式 reject/conflict，
或带可见 supersede 语义的 typed coalescing 三者择一。**当前 silent last-write-wins 不可保留。**
从“用户可以连续补充 note”的 UX 看，优先研究 bounded ordered admissions + exact-once batch
consumption；若成本不接受，至少返回 typed pending/conflict，不能悄悄丢掉前一条。

## 目标 Agent-Native Control Flow

```text
latest user turn + visible pending subject + retained typed tool outcomes
                              |
                              v
          SOUL: stable identity / truthful outcome posture
          SKILL: classify intent, ambiguity and target
                              |
                              v
       one candidate: start | resume | refine | status | cancel
                    or ask_clarification / no action
                              |
                              v
       exclusive tool call + strict schema + trusted runtime scope
                              |
                              v
       Bundle lifecycle validates, admits and persists the effect
                              |
                              v
          typed result returns to lead agent for truthful UX
```

建议的 surface responsibility：

- `SOUL.md`: Deep Research identity、truthfulness、不伪造结果、服从 typed lifecycle outcome。
- `SKILL.md`: qualification、state/action decision table、pending-vs-refine rule、target selection、
  clarification criteria、result handling、positive/negative examples。
- tool schema/runtime: closed actions、exclusive-call shape、trusted scope、authorization、correlation、
  idempotency、persistence 和 typed denial。
- Bundle-local State: 唯一 durable lifecycle truth；不保存“agent 猜测的 intent”。
- subagent: 只做 Bundle 内部的研究 cognition，不参与 public follow-up routing。

当前 configure 只复制一个 `SKILL.md`（`deep_research_harness/scripts/configure.py:301-324`）。第一版
decision program 完全可以留在一个聚焦的 skill 内；只有实测超过可维护大小时，才新增一个被
`SKILL.md` 明确引用、configure 同步安装的 supporting resource，不能先写一个 runtime 根本不会
部署的 `workflow.md`。

## 能证明“做对了”的测试资产

没有一种测试可以单独证明 prompt workflow。应按 claim 选真实性层级：

| 要证明的 claim | 最低负责资产 | 明确不能证明什么 |
| --- | --- | --- |
| 五个 action 的字段、权限、correlation、idempotency、deletion/isolation | domain/runtime deterministic matrix | 模型会不会从自然语言选对 action |
| skill 被 configure 安装、被真实 DeerFlow discovery/activation 读取，SOUL 进入实际 lead prompt | downstream integration against real DeerFlow loader/middleware | 模型会遵循内容 |
| 一个已选择 action 能经 real middleware/tool/runtime/Bundle State 返回 typed result | `SCRIPTED_REAL_WORKFLOW`，只替换外部 model response | prompt 导致了该选择；研究质量 |
| follow-up 语义被模型稳定分类为正确 action/clarification | versioned live cognitive evaluation，真实 lead prompt + SOUL + skill + tool schemas，重复运行 | lifecycle mutation 本身安全；由 deterministic tests 证明 |
| active refinement 在 restart 后于真实 safe point exact-once 生效 | partial/full graph test + Bundle-local persisted State + restart | 模型分类质量 |
| 用户看见的提示、pending subject、denial 和 next action 可恢复 | typed transcript/rubric review，必要时真实 UI projection | 底层 authorization |

现有真实性阶梯已经支持这种分工：scripted workflow 保留真实 bridge、middleware、policy、store、
gate；live 才能证明实际 model/provider behavior
（`deep_research_harness/docs/testing-and-evaluation.md:50-89`）。但 Cognitive Evaluation Suite
当前只有 `hitl1-brief@v1` 和 `wave0-worker@v1` 两个 subject
（`deep_research_harness/evals/control/registry.json:1-16`；
`deep_research_harness/docs/cognitive-evaluation-suite.md:52-59`），还没有 public controller。

### 最小场景语料

下一 change 至少应版本化以下 cases；每条记录 prompt/skill version、model/provider、完整输入、
期望 tool/clarification、禁止副作用、token/cost/latency 和失败诊断：

| Case | 输入摘要 | 硬不变量 |
| --- | --- | --- |
| New research | 新的多源研究诉求，无 active Bundle | 只调用 `start`，无 caller id/question args |
| Correlated answer | 当前 pending subject 的直接回答 | 只调用 `resume`；不把 answer 放进 args |
| Mid-suspension direction | “顺便重点看监管风险” | `refine`，pending request 保持原样 |
| Status inquiry | “现在到哪了” | `status`，不编造进度 |
| Explicit stop | “先停掉这次研究” | `cancel`；重复 delivery 不产生第二次 effect |
| Ambiguous criticism | “这个方向不太对” | clarification；Bundle 无 mutation |
| Active conflict | active Run 期间提出另一件新研究 | 不创建第二个 Bundle；说明 continuation/conflict |
| Ended refinement | 明确继续打磨一个已知 ended Bundle | `refine` 带已验证 id；目标不明则 clarification |
| Unavailable Bundle | 已知 Bundle 被删除 | 不恢复、不假装完成；只报告 typed unavailable/next action |
| Repeated notes | safe point 前两条独立方向 | 第一条保持 pending；相同 delivery 幂等，不同第二条返回 typed conflict，绝不 silent overwrite |

offline replay 应继续存在，但名称和 assertion 要诚实表达它只证明 handoff。真正的 action selection
case 必须让实际模型看到真实 composed prompt 后自己产生 tool call；否则只是把期望答案写进 fake
model。live defect 若可稳定重放，再按现有 regression-descent policy 下沉到最小 deterministic
seam（`deep_research_harness/docs/testing-and-evaluation.md:139-143`）。

## 统一落地

三份 backlog 材料不再各自提出 change：

| 材料 | 继续负责 | 不再负责 |
| --- | --- | --- |
| 本研究记录 | DeerFlow/LangGraph 一手资料、现状缺口、`note` 语义与 evidence claim limits | 实施顺序或 change scope |
| [`deep-research-harness-agent-native-progressive-plan.md`](deep-research-harness-agent-native-progressive-plan.md) | 唯一落地顺序、目标边界、domain/control placement、一个 vertical slice 的 phase/Go-No-Go | 平行 change 的排期 |
| [`deep-research-harness-test-asset-audit.md`](deep-research-harness-test-asset-audit.md) | 资产事实、真实性分层、缺失 evidence families 与长期治理风险 | 当前 change 的 task ledger |

唯一落地 change 是
[`establish-agent-native-research-direction-loop`](../../../../openspec/changes/archive/2026-08-08-establish-agent-native-research-direction-loop/)。
它先以 Phase 0 修复当前 gate 并验证真实 loader/同 Bundle rerun 可行性，然后依次完成单槽
direction admission、terminal-round safe point、public controller + `topic_planning` Markdown vertical
slice，最后增加 bounded cognitive cases。任一 Go 条件失败，后续阶段不展开。

这也冻结了 `note` 的处理：Accepted Profile Note 只属于 canonical profile；Correlated Research
Response 只走 `resume`；独立 Run Refinement 只走 `refine`；语义不清先 clarification。第一版
只允许一个 pending refinement，不做 queue/history/merge；不同的第二条明确 conflict。

## Source Index

外部一手资料：

- LangChain, [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)
- LangChain, [Customize Deep Agents](https://docs.langchain.com/oss/python/deepagents/customization)
- LangChain, [Deep Agents Skills](https://docs.langchain.com/oss/python/deepagents/skills)
- LangChain, [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- LangChain, [LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- LangChain, [Test LangGraph applications](https://docs.langchain.com/oss/python/langgraph/test)

仓库内 primary owners：

- DeerFlow lead composition: `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
- DeerFlow prompt/skills/SOUL: `backend/packages/harness/deerflow/agents/lead_agent/prompt.py`、
  `backend/packages/harness/deerflow/config/agents_config.py`
- DeerFlow skill/durable/clarification middleware: `backend/packages/harness/deerflow/agents/middlewares/`
- Public Deep Research surfaces: `deep_research_harness/config/agent-template/SOUL.md`、
  `deep_research_harness/config/public-skill/deep-research-controller/SKILL.md`
- Tool/lifecycle/state: `deep_research_harness/src/deerflow_deep_research/tool.py`、
  `runtime/bundle_lifecycle.py`、`domain/lifecycle.py`、`domain/state.py`
- Accepted behavior: `openspec/specs/deep-research-harness-run-bundles/spec.md`、
  `openspec/specs/research-graph-lifecycle/spec.md`、`openspec/specs/runtime-integration/spec.md`
