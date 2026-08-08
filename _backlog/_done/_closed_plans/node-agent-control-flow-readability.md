# Plan: Node Agent 智力边界与控制流可读性审计

> 类型: 分析 | 更新: 2026-07-29 | 代码快照: 本仓库工作树，2026-07-28
>
> 归档状态: **Closed — v1 方向已由 reader-interface rollout 落地，并由已完成的 cognitive-node-first governance 计划吸收**
>
> 原 Review 状态（2026-07-29）: **已选择 v1 final reader interface；待据此建立 OpenSpec change**
>
> 对齐决定: 每个 LLM-bearing logical node 的说明与实现 colocate；固定只使用
> `graph/nodes/<logical_node>/workflow.md` 作为人和 Coding Agent 共用的维护 interface，
> 不再建立 `workflow_review.py` 第二语义源，也不建立远端 ownership root。
>
> 阅读接口: v1 示例先声明 node 是否承载智力，提供
> `symptom -> exact file::symbol -> responsible test/eval`，再只补充该 node 容易误改的
> 跨模块因果；它不要求所有 node 复刻完整 prompt assembly 或控制流章节。
>
> 快速对齐: 如果正文太抽象，先读
> [workflow card discussion examples](node-agent-control-flow-readability/README.md)，
> 再回到本计划的“Final 实施契约（v1 方法）”。

> **Final 决定（2026-07-29）:**
> [`wave2-synthesis-compact_v1/`](node-agent-control-flow-readability/wave2-synthesis-compact_v1/README.md)
> 是本计划唯一采用的 reader-interface **示例**。最终决定是采用它展示的小型、症状驱动、
> node-local `workflow.md` 方法，而不是让所有 node 复制 Wave2 的内容或章节。后续 OpenSpec
> change、实现和评审应按各 node 自身的认知工作、deterministic authority 与控制流写出等价的
> 最小接口；v0、完整控制流复述、metadata、generated inventory 与 checker 仅保留为历史对照
> 或未来重新评估的备选，不属于本次最终决定。
>
> 本文后续凡是建议 bounded generated region、freshness checker、card identity metadata 或
> 完整 card outcome/inventory 的段落，均记录 v1 决定前的审计推演，不得当作后续实现要求。

## 阅读说明 / 独立上下文

本文是对 DeerFlow Deep Research 子项目的一次静态可读性审计。它不依赖任何聊天
上下文；读者只需从这里开始阅读即可理解问题、证据、结论和建议。

### 要回答的问题

项目把若干 LLM 调用称为 Node Agent，并为它们提供 package-local capability Markdown
和生成的 prompt Markdown。问题不是“模型能不能完成研究”，而是：

> 一个第一次接触仓库的人或 Coding Agent，只看这些 Markdown，能否先识别
> 一个 node 是智力节点还是确定性控制，再准确说出它的输入与反馈、模型承担的
> 认知工作、candidate 如何被接纳、失败如何恢复、为什么进入下一条图边，以及
> 出现质量问题时应该调优智力面还是修改确定性外壳？

本文的回答是“不能直接做到”。本文也说明这不是把更多控制字段塞入 capability
Markdown 就能解决的问题，并提出一个不改变当前 authority 分工的阅读投影方案。

### 系统最小模型

Deep Research 是一个 LangGraph 工作流。其真实实现有 11 个 logical nodes：
`bootstrap`、`hitl1`、`topic_planning`、`wave0`、`wave1`、`wave2_synthesis`、
`targeted_evidence`、`hitl2`、`rerun`、`readiness` 和 `final_delivery`。

下面是帮助定位的主干和两个重要回环，并非完整行为规范；完整的 normalized semantic
edge inventory 在 `agent/src/deerflow_deep_research/graph/topology.py`，实际可执行的
LangGraph wiring 则由 `graph/builder.py` 另行构造：

```text
START -> bootstrap -> [hitl1, when human profile is needed] -> topic_planning
                                                        -> wave0 -> wave1 -> wave2_synthesis
                                                                              |          |
                                                                              |          +-> hitl2 -> readiness -> final_delivery -> END
                                                                              |
                                                                              +-> targeted_evidence --+
                                                                                                      |
                                                                                                      +-> wave2_synthesis
```

图的节点实现可选择 `fake` 或 `real` factory。`fake` 是确定性 fixture 生命周期，
用于拓扑和测试。本文把口语中的“智力节点”规范为 **LLM-bearing logical node**：其
real implementation 至少包含一个可到达 `capabilities.run_agent(...)` 的 direct model
branch。它不是新 runtime 类型。本文不声称某个 real factory 已在任何部署中启用，也不
评估模型、检索或研究结论的质量。

### 术语与 authority

| 术语 | 本文中的含义 |
| --- | --- |
| logical node | LangGraph 中的一个稳定节点名，例如 `wave2_synthesis`；它可由一个 package 实现。 |
| LLM-bearing logical node | 至少拥有一个 direct model branch 的 logical node；这是 reader-interface coverage 分类，不新增 runtime class。 |
| node-local `workflow.md` | 与一个 LLM-bearing logical node colocate、但不参与运行的智力回路与维修说明；这是 v1 的 reader interface。本文早期称它为 “Node Workflow Card”。 |
| workflow ID | v0 历史方案使用的 card ID，不是 v1 的 metadata 或实现要求。 |
| direct model branch | 一个生产 prompt-builder 路径，可直接到达 `run_agent`，例如 `wave0/worker` 或 `wave0/repair`。 |
| cognitive job | 一个 Node Agent 交给模型的有界认知工作；质量调优应先围绕它的 capability、prompt、context、feedback 和 eval。 |
| feedback | 从 parser/validator、controller/gate 或人类产生的信号。card 必须说明 source、实际 recipient、实际传递内容、作用和上限；触发 repair 不等于 signal 已交给模型。 |
| tuning map | 从可观测症状到首要修改 seam 的导航；它防止 Coding Agent 把认知质量问题默认当成 parser、state、gate 或 route 问题。 |
| capability Markdown | `graph/nodes/<node>/capabilities/*.md`。它定义模型的角色、方法、工具姿态与 authority limit。 |
| prompt catalog | `agent/node_prompts/` 下由代码生成的 Markdown，展示一个合成样例的最终提示词和请求级工具姿态。 |
| candidate | 模型返回的未接纳结果。模型只能产生 candidate，不能直接写 route、checkpoint、ledger 或 gate。 |
| control flow | 可信输入、调用、parse/validate/materialize、失败恢复、state 更新，以及 route writer、edge kind、route consumer 与 target 的组合。 |
| authority | 某个事实或动作的唯一决定者。当前控制 authority 是节点/图、gate、ledger、typed state 与 runtime，不是 Markdown。 |

`ResearchState` 是 checkpointed control authority；多数 logical node 的
`state["route"]` 会被 `graph/builder.py` 的条件边消费，但这不是所有边的统一机制。
`START -> bootstrap` 与 `targeted_evidence -> wave2_synthesis` 是 unconditional edge；
后者虽然当前 handler 返回 `route="next"`，builder 并不读取该值。能力和 prompt
Markdown 是受审阅的投影，不能反向驱动运行时。

### 证据范围与限制

本报告基于以下当前仓库事实，而非模型猜测或历史记忆：

1. `agent/src/deerflow_deep_research/graph/topology.py` 与 `builder.py` 的节点、边和
   wrapper gate 行为。
2. 六个 LLM-bearing node package 的 `node.py`、`subgraph.py`、`prompts.py`、
   `capabilities.py` 与 capability Markdown。
3. 共享的 `graph/components/work_units.py`、`graph/nodes/gate_adapter.py` 和
   `engine/gate_kernel.py` 的接纳、恢复、gate 行为。
4. 当前 node main specs: `hitl1-node`、`topic-planning-node`、`wave0-node`、
   `wave1-node`、`wave2-synthesis-node` 与 `targeted-evidence-loop`。
5. 当前 shared-control/review main specs: `work-unit-kernel`、
   `node-agent-capabilities`、`node-prompt-catalog`、`research-graph-lifecycle` 与
   `project-structure`；以及相关归档 change 的设计意图。

归档 OpenSpec 仅用于解释“为什么已有 Markdown 被设计成这样”，不用于断言当前运行
行为。当前代码说明 implemented behavior，main spec 说明 required behavior，测试说明已被
证明的 observable behavior；三者不能互相替代。本文不修改运行代码、拓扑、状态 schema、
runtime policy 或 OpenSpec；它只提出未来 change 的方向，并单列审计中发现的 conformance
缺口。

### 建议阅读顺序

1. 阅读“背景 / 现状”获得结论和审计对象。
2. 阅读“已有表面与缺口”和“控制实际在哪里”，理解为什么单看 MD 不足。
3. 按“节点级重建结果”选择关心的 node；这部分给出当前真实流程的浓缩答案。
4. 阅读“根因判断”及之后的方案，判断是否应创建后续 OpenSpec change。

## Final 实施契约（v1 方法）

v1 是 Wave2 的**方法示例**，不是向所有 node 分发的固定 card schema。后续 rollout 中，每个
LLM-bearing node 仍只有一份 colocated `workflow.md`，但它只保留该 node 的 reader 必须知道的
事实：

1. node 性质、模型的有界 cognitive job，以及模型不拥有的 deterministic authority；
2. 由 observable symptom 直接到 `file::symbol` 与最低责任测试的 tuning map；
3. 容易误改的跨模块因果，例如模型实际看见的内容、feedback 是否真的抵达模型、route 的 writer
   与 executable consumer 分别是谁。

实现、spec 与测试始终是 authority；`workflow.md` 不进入 runtime。不要把局部 `node.py` 已能
清楚表达的流程再翻译一遍，也不在最终方案引入 card metadata、generated inventory、checker、
远端 index 或固定的全量 outcome table。某个 node 需要额外事实时，按其真实 seam 补一条维修
导航，而不是复刻 Wave2 的章节。验收参考
[Wave2 v1 final example](node-agent-control-flow-readability/wave2-synthesis-compact_v1/README.md)。
实际 rollout 的 change 边界、关口与 stop condition 见
[progressive plan](node-agent-control-flow-readability-progressive-plan.md)。

## 审计结论与历史推演

核心判断成立：当前 capability Markdown 和 prompt catalog 分别适合审阅模型的认知范围
与单次最终 prompt，但它们没有把 logical node 暴露成一个带输入和反馈的智力回路。
当 Coding Agent 只看见 parser、state、gate、route 和大量确定性测试时，它会自然把这些
表面误认为主要调优点。新增 node-level review projection 必须首先修复这个智力导航缺口，
然后才解释确定性控制流；它仍然不获得 execution authority。

原方案不能直接进入实现。下表记录 v1 决定前发现的问题和当时的收紧方向；其中关于
metadata、generated region、checker、全量 load chain 和 outcome table 的具体机制已被上面的
v1 最终实施契约取代：

| 级别 | 问题 | 必须采取的修订 |
| --- | --- | --- |
| Blocker | card 仍以确定性控制与审计字段为首屏，没有让 Coding Agent 先识别 node 的 cognitive job、input/feedback loop 和正确调优 seam。 | 每张 card 首屏固定声明 `node-agent` / `no-agent`，并提供 observable symptom、exact `file::symbol`、why-first 与 responsible test/eval；cognitive job、初始输入和 feedback 紧随其后。 |
| Blocker | `workflow_review.py` 的大 literal 要求读者先学一套新 schema，但没有说明 runtime prompt 如何装配，也没有为具体维修隐藏复杂度。 | 删除该第二语义源。人工语义直接维护在 node-local `workflow.md`；机器只检查或刷新显式标记、可从现有 owner 推导的 inventory 区块。 |
| Blocker | “capability / prompt / context”仍是抽象标签。陌生 Agent 不知道 capability header、body、objective、expected output 和 evidence 哪些对模型可见、分别由谁加载。 | 每张 LLM-bearing card 必须提供真实 runtime assembly/load chain，并把每个 source 标为 model-visible system、model-visible request、runtime enforcement、deterministic admission、graph control 或 review-only。 |
| Blocker | 把 semantic topology、executable builder wiring、`state["route"]` 写入和 route 消费混为一谈；`targeted_evidence` 实际使用 unconditional edge，builder 不消费它返回的 `route="next"`。 | workflow card 的 Exit 必须分别列出 semantic edge、route writer、executable edge kind、route consumer 和 target；不得从 normalized label 推断运行时一定读取 route。 |
| Blocker | 手工重复 branch IDs 和 route labels 会形成 shadow inventory。 | branch 集合从 `prompt_catalog_cases()` 派生，outgoing semantic edges 从 `NORMALIZED_EDGES` 派生，并只写入 `workflow.md` 的 bounded generated region；其余 prose 不由 generator 接管。 |
| Major | Recovery 仍被压成一个“retry/repair bound”，没有区分 model invocation recovery、structured repair、work-attempt retry、phase-gate repair 和 exception propagation。 | 每张 card 必须提供按 failure class 展开的 outcome table，并明确每层 owner、共享预算、terminal disposition、legal next action 和 proof seam。 |
| Major | 证据范围遗漏了 node-specific 与 shared-control main specs，且静态审计已发现 spec/code 不一致。 | 纳入各 node main spec、`work-unit-kernel` 和相关 outcome contract；把实现缺口单列，不能用 workflow 文档替代 conformance 修复。 |
| Major | 远端 `agent/node_workflows/` 会削弱 node-locality；同时“从 capability MD 反向跳转”会诱导修改实际进入 system prompt 的 capability body。 | 每个 authored card colocate 到对应 node package；更新 node-package grammar 与 structure registry。导航由 generated prompt artifact、local card 或派生 index 提供，不修改 runtime-rendered capability body。 |

v0 当时建议保留 bounded generated regions 与 freshness checker。最终 v1 只保留
logical-node 粒度、node-locality 和症状直达 owner 的 `workflow.md`；不引入 checker 或 card
identity。远端 ownership root、Python literal 第二语义源和 catalog 的重复枚举仍然不采用。

为了先对齐“最终读者会看到什么”，已增加一组不参与实现的
[workflow card discussion examples](node-agent-control-flow-readability/README.md)：包括
Wave2 普通 gated path、Targeted Evidence 特殊 unconditional path，以及人工维护/自动派生
字段的对照。OpenSpec change 应在这些示例的阅读密度和字段形状确认后再建立。

## 背景 / 现状

结论先行: 不能一眼看出来。作为 Agent，我能通过检索和跨文件追踪把
控制流重建出来，但当前阅读路径会先暴露确定性实现和大量测试，后暴露模型的
认知工作与反馈。这会让 Coding Agent 得到一个错误的相对重要性：它以为 node 主要是
传统程序，LLM 只是一个返回字符串的外部调用。现有 Markdown 说明了单次模型调用的
认知范围和提示词，却没有提供“这个智力节点收到什么、如何思考、收到什么反馈、
哪部分应被调优，以及它如何进入下一条图边”的读者接口。

这不是单纯的文档遗漏。2026-07-27 至 2026-07-28 的归档变更有意把
Markdown 限定为能力政策和提示词的审阅投影：它不得携带 route、checkpoint、
parser、materializer、repair 或 live-tool authority。这个 authority limit 是正确的；若让
能力 Markdown 声明控制，静态提示词资源就会变成第二个控制权威。

本审计把“智力节点”限定为实际调用 `run_agent` 的六个 node package，而不是
所有 11 个图节点：

| Node package | 直接模型分支数 | 现有能力/提示词 Markdown 能回答的事 |
| --- | ---: | --- |
| `hitl1` | 4 | 生成 profile brief，或解释一条人的回复；均为零工具、仅返回候选 |
| `topic_planning` | 2 | 从已确认 profile 产生 topic-plan 候选，或修复候选 |
| `wave0` | 2 | 每 topic 做一次受限检索，或把无效输出修为结构化候选 |
| `wave1` | 2 | 每 topic 做深度证据提取，或修复结构化候选 |
| `wave2_synthesis` | 2 | 仅从已接纳证据综合 findings/gaps，或修复候选 |
| `targeted_evidence` | 4 | 针对一个 gap 检索/修复，或做只读 source/claim critic |

这正好对应 `agent/node_prompts/` 的 16 个 direct catalog cases。`bootstrap`、
`hitl2`、`rerun`、`readiness`、`final_delivery` 是确定性控制、人类中断或
发布表面，不应为了“每个节点都有 MD”而伪装成 Node Agent。

## 已有表面与缺口

| 阅读问题 | 当前最佳入口 | 能否直接得到答案 | 原因 |
| --- | --- | --- | --- |
| 模型在某分支会收到什么指令、可请求什么工具？ | `agent/node_prompts/<node>/<branch>.md` | 可以 | catalog 展示精确提示词、能力绑定和请求级工具姿态 |
| 模型被允许做什么、绝不能做什么？ | `graph/nodes/<node>/capabilities/*.md` | 可以 | metadata 和正文清楚限定认知角色、输出和 authority limit |
| 模型输出无效时会怎样？ | `node.py` 或 `subgraph.py` 加 `prompts.py` | 通常不可以 | repair 次数、provider retry、异常传播和耗尽状态不在 MD 中 |
| 候选何时写入 artifact、ledger 或 checkpoint？ | 节点实现、materializer、共享 work-unit 实现 | 不可以 | 接纳权有意留在确定性实现中 |
| 节点会走到哪一条 route，谁决定？ | `graph/builder.py`、`topology.py`、gate adapter/kernel | 不可以 | route 在 handler、gate wrapper 或图边三处分别拥有 |
| 该节点为何回环、何时终止？ | 上述源文件加当前 capability spec | 不可以 | 没有以 node 为单位的控制流投影 |

现有 `agent/node_prompts/README.md` 明确把 catalog 标为 generated review artifact，
而非 runtime authority。`node-agent-capabilities` 主规范也明确拒绝在能力 metadata
中加入 route、parser、repair 或 evidence selector。这些约束解释了为什么仅阅读
MD 会缺少控制流，而不是说明实现违背了它们。

## 控制实际在哪里

控制在运行时是分层且有意分散的：

```text
Node capability/prompt
        -> model candidate
        -> node-local parser / materializer / worker wrapper
        -> shared work-unit or gate implementation (when applicable)
        -> state["route"]
        -> graph builder conditional edge (most nodes)

targeted_evidence handler -> route="next" (written but not consumed)
                            -> graph builder unconditional edge -> wave2_synthesis
```

宏观语义图在 `graph/topology.py` 中以 40 条 normalized edges 集中表达；实际
`graph/builder.py` 独立构造对应的 LangGraph conditional 与 unconditional edges，并不从
`NORMALIZED_EDGES` 生成 wiring。normalized edge 上的 semantic route label 不等于 builder
必然读取同名 state 字段，semantic inventory 也不能单独证明 executable builder 与它完全
一致。前者解决“设计上节点之间能怎么走”，后者决定实际图如何消费 route；两者都不表达
一个节点内部为何产生该结果。

`builder.py::_node_wrapper` 是另一个容易遗漏的控制所有者：对于 Wave0、Wave1、
Wave2 和 final delivery，它在节点返回后评估 gate，并把 gate 的结果写成 route。
因此仅看这些节点的 `node.py` 会找不到成功路径的 `route` 写入。共享的
`graph/components/work_units.py` 还负责 fan-out、候选校验、提交、重放和 drain；
`engine/gate_kernel.py` 负责 repair budget、疲劳和 blocked 判定。它们具有深 module
的结构意图，但本审计不把“结构集中”当作行为正确性的证明；当前缺少的是一个面向
阅读者、通过现有 owner 串联这些行为的 review interface。

`ResearchState` 是 checkpointed control authority。MD 既不应也不能成为它的替代品。

## 节点级重建结果

| Node | 实际内部控制流 | 仅读 MD 时丢失的关键信息 |
| --- | --- | --- |
| `hitl1` | 初次 brief -> checkpoint proposal -> 人类 interrupt；人的 action/text 经过确定性解析或 semantic-intake 候选分类；结果可 accepted、revise/follow-up、cancel 或 exhausted。brief 的 provider recovery 与 structured repair 共用最多 2 次 model invocation；semantic transient retry 与 repair 共用最多 3 次；人的 accepted-answer 与 rejected-response rounds 另有独立上限。 | 人类中断、proposal 持久化、多层共享预算、响应轮次和 `needs_followup` 自环；MD 只说明两类模型候选没有 route authority。 |
| `topic_planning` | 读取 confirmed profile -> 初次 plan 调用；初次可恢复 provider failure 的一次 retry 与 parse/materialize failure 的一次 repair 共用 2-call ceiling，不是两个可叠加预算；成功写 topic registry 并 `next`，terminal failure 写 `exhausted`。 | provider recovery 与结构修复是互斥消耗同一 ceiling 的控制分支；coverage/materialization 是决定 `next` 的确定性接纳门。 |
| `wave0` | 按 topic materialize work intents -> fan-out worker；每 worker 检索、parse，必要时一次 repair -> 写候选 artifact -> 共享 validator/ledger 接纳 -> shared gate 将 phase 导向 `repair`、`pass` 或 `exhausted`。 | 不是“一个 prompt 调用后进入 Wave1”；worker 失败、提交校验、重试和 phase route 都在 local subgraph + shared work-unit/gate 中。 |
| `wave1` | 与 Wave0 使用同一工作单元骨架，候选含 sources/claims/open questions；worker 接受 `wave0_urls` baseline，但当前 real node 传入空集合，因此 implemented path 并未实际识别 Wave0 duplicate；最终由 shared gate 决定 phase route。 | 与 Wave0 的共同控制骨架、不同 candidate materialization，以及 required behavior 与当前 baseline 接线的差距都不在 prompt/capability MD 中。 |
| `wave2_synthesis` | 读取已接纳证据 -> synthesis；初次 parse/backing-ref semantic failure 可做一次 repair；成功写 synthesis 并产生 gate preview；wrapper gate 决定 `evidence_needed`、`pass` 或 `exhausted`。已归类的 invocation failure 会写 `exhausted`，但 repair 后再次 parse/semantic failure 以及 bundle I/O 当前可直接传播 exception。 | 成功 route 由 preview + gate 决定；typed terminal update、一次 repair 与 exception propagation 是不同 outcome，不能概括成统一的“失败 exhausted”。 |
| `targeted_evidence` | 从 gate-owned searchable gaps fan-out retrieval worker；每 worker parse/gap-id failure 可 repair 一次并经过 shared validator/ledger。若 state 中存在 `critic_work_items`，还会顺序 dispatch source/claim critics，materializer 校验引用集合后写 artifact。handler 返回 `route="next"`，但 builder 通过 unconditional edge 回 Wave2，并不消费该 route。 | 四个模型角色的条件可达性、gap 身份校验、critic exception propagation、route 非消费语义，以及当前 wrapper gate-view contract 缺口。 |

所以，现有信息的可读性不是均匀差：

- 宏观拓扑: 找到 `topology.py` 后清楚。
- 单次模型行为: 找到 `node_prompts/` 后清楚。
- 节点内部控制: 需要人工跨 3 到 6 个实现文件重建，且部分 route 在 wrapper/gate
  中而不在 node package 的主函数中。
- 全链路失败和恢复: 还要理解 `ResearchState`、work-unit 和 gate kernel；对没有
  先验的人或上下文受限 Agent 都不够直接。

归档 OpenSpec 不是这个问题的合适入口。它们解释了某次变更为何把 prompt/能力做成
可审计投影，但按历史 change 组织、且不是当前行为权威；用它们补全当前控制流会迫使
读者做时间上的反向推理。

### 审计中发现的 conformance 缺口

这些问题不是 workflow projection change 可以“文档化解决”的，应分别由 owning
capability 澄清或修复。workflow card 在它们解决前只能如实标注 implemented behavior，
不能把 main spec 的 required behavior 写成已实现事实。

| 缺口 | 当前代码证据 | 影响 | 建议 owner |
| --- | --- | --- | --- |
| Wave1 baseline 与 critic 接线不完整 | `wave1/node.py` 构造 `wave0_urls` 时两个读取循环均为 `pass`，并最终传入空集合；生产源码中也没有 Wave1 accepted submission 后创建 critic work 的路径。 | `is_new_vs_wave0` 无法反映真实 Wave0 duplicate，`wave1-node` spec 的 baseline/new-source 与 critic 要求不能据此视为已证明。 | 独立 `wave1-node` conformance change。 |
| Targeted critic 分支缺少正常图内 producer | `targeted_evidence/node.py` 读取可选 `critic_work_items`，但当前生产源码没有该 state key 的 writer。 | 两个 critic prompt branches 存在且可被直接调用，但不能未经限定地描述为当前正常 graph journey 可达。 | `wave1-node` / `targeted-evidence-loop` 共同澄清唯一调度 owner。 |
| Targeted real node 丢失 wrapper 所需 gate view | `targeted_evidence` 的 `NODE_SPEC` 声明 `WORK_UNIT_CONTROLLER`；`_node_wrapper` 因此要求 `WORK_UNIT_GATE_VIEW_KEY`。`run_gap_workers()` 取得 component result 后只返回 `parent_update`，real node 未返回 `gate_view`。 | compiled real journey 到达该 node 时会在 wrapper validation 阶段失败；direct factory tests 绕过了该 seam。 | 独立 `targeted-evidence-loop` / `work-unit-kernel` bug change，并增加 compiled-graph proof。 |
| Wave2 local validation failure 没有交给 repair model | `wave2_synthesis/node.py::build_real` 使用 `except ValueError:` 丢弃 exception，再调用 `build_synthesis_repair_prompt(result.summary, evidence)`；repair request 只有 draft、accepted evidence 和通用 schema。 | 不能把它画成“validator 把具体 feedback 送回模型”；`WSN-005` 要求的 validation facts 当前未实现，repair 可能重复同一语义错误。 | 独立 `wave2-synthesis-node` cognitive-feedback conformance change；补 request-content assertion。 |
| Wave2 focused live canary 未走专用 Wave2 bridge | `tests/scenarios/canaries.py::_execute_focused_wave2_core` 调用 `_build_hitl1_capabilities`，生产 `ResearchActionHandler._context` 对 Wave2 调用 `_build_wave2_synthesis_capabilities`。 | canary 可观察真实 node/prompt/admission 的一部分行为，却不能证明专用 Wave2 execution policy、预算和 bridge wiring 的 authenticity。 | `evaluation-hardening` / `node-agent-runtime` 澄清或修复 canary construction，并保留分层证据说明。 |
| Wave2 repair 后的无效 candidate 没有统一 typed outcome | 第二次 `_validate_synthesis_semantics(parse_synthesis_output(...))` 不在异常转换内。 | card 必须写 exception propagation，不能承诺所有 repair exhaustion 都得到 `route="exhausted"`；是否收敛为 typed outcome 由 `wave2-synthesis-node` 决定。 | 独立 outcome conformance decision。 |

## 根因判断

当前设计提供了两个有价值但不同的模块接口：

1. capability interface: “该模型候选可以思考什么，不能拥有何种 authority”。
2. prompt-review interface: “这一直接分支的最终提示词和请求级工具姿态是什么”。

一个拥有大量确定性测试的仓库仍可以缺少第三个接口。测试能证明 parser、state、
ledger、gate 和 route 的 observable behavior，但它们不会自动告诉 Coding Agent：
“当研究判断、证据选择或综合质量不对时，首要调优面是认知任务、context、feedback 和 eval。”
因此测试数量不能替代智力导航。

用户真正需要的是第三个接口：

3. node-agent loop interface: “该 node 承担什么有界认知工作，从哪种可信输入开始，
   收到哪些反馈且反馈交给谁，如何产生 candidate，由哪个确定性 owner 接纳，
   失败如何有界恢复，最后可能写出哪些 route，以及不同症状应该从哪个 seam 开始修改”。

前两个接口以 direct branch 为粒度，这是对 capability posture 和测试证据最合适的
粒度。第三个接口必须以 logical node 为粒度，因为 repair、fan-out、gate、human
interrupt 和 route 的关系跨越多个 branch。`workflow.md` 应在一张 card 中 join 前两个现有
owner 的引用与 node-level 语义，但不复制 capability/prompt 正文，也不把它们的
authority 转移给 card。这样人和 LLM 读同一份 interface，仍不会误以为模型拥有控制权。

## 已搁置的 v0 方案推演

> 以下内容解释为何曾考虑 metadata、generated inventory 和 checker。它是审计历史，不是 v1
> 的实现任务；与“Final 实施契约（v1 方法）”冲突时，一律以该契约为准。

建议另建一个受检验的 **node-agent maintenance-map projection**，而不是扩写 capability
metadata 或把完整控制语义塞进 prompt catalog。每张 card 的 ownership seam 固定在对应
node package 内，不再使用远端 `agent/node_workflows/` 作为 owner。

### Reader-first Node Agent loop

每张 card 不应以 Scope/Admission/Outcome 审计字段开场。第一层先给维修导航，再给人和
LLM 共用的一个智力回路。回路必须允许“failure 只触发 repair、但没有送给模型”的真实状态：

```text
initial input + re-entry context
              |
              v
      cognitive work (LLM) <---- model-visible feedback, only if implemented
              |
           candidate
              v
 deterministic judgment/admission
       | accepted             | rejected
       v                      +-> bounded repair trigger
 artifact/state                  (may or may not carry failure details)
       |
       v
 gate / human / controller -> next route or indirect re-entry
```

该层回答七件事：

1. `classification`: 它是 `node-agent` 还是 `no-agent`。
2. `maintenance map`: 每个 observable symptom 对应的 exact `file::symbol`、why-first 与 test/eval。
3. `cognitive job`: 模型承担的有界判断是什么。
4. `input`: 首次进入与再次进入时各收到什么。
5. `prompt assembly`: capability header/body、request、evidence 和 runtime policy 分别由谁读取，
   哪些内容模型可见。
6. `feedback`: 每条反馈的 source、recipient、实际 signal、effect 和 bound；特别区分
   “具体 failure 交回模型”“failure 只触发 repair”与“只改变图路径的 gate feedback”。
7. `deterministic judgment/output`: 谁接纳 candidate，什么成为 artifact/state/route。

Outcome rows、exact source/spec/test refs 与现有 owner keys 仍然保留，但放在第二层
Technical Trace。它们用于证明和防漂移，不得把智力回路挤出首屏。

### Canonical node-package grammar

每个 LLM-bearing logical node 只 colocate 一个 reader-facing review file：

```text
graph/nodes/<logical_node>/
├── __init__.py            # public export 仍然只有 NODE_SPEC
├── node.py                # runtime implementation
├── prompts.py
├── capabilities.py
├── capabilities/
└── workflow.md            # authored reader interface；只含 bounded generated regions
```

`workflow.md` 由人和 Coding Agent 直接维护，也是二者共用的唯一语义 interface。第一行
metadata 与 `BEGIN/END GENERATED` inventory region 可由 documentation checker 读取；其余 prose
不要求机器解析。package root、node factory、builder、runtime、prompt renderer 和 capability
loader 均不得读取它。该文件必须加入 `project-structure` node-package grammar 和 exact-path
registry。

第一批 exact inventory：

| Logical node | Workflow ID | Authored card |
| --- | --- | --- |
| `hitl1` | `node-workflow/hitl1` | `graph/nodes/hitl1/workflow.md` |
| `topic_planning` | `node-workflow/topic_planning` | `graph/nodes/topic_planning/workflow.md` |
| `wave0` | `node-workflow/wave0` | `graph/nodes/wave0/workflow.md` |
| `wave1` | `node-workflow/wave1` | `graph/nodes/wave1/workflow.md` |
| `wave2_synthesis` | `node-workflow/wave2_synthesis` | `graph/nodes/wave2_synthesis/workflow.md` |
| `targeted_evidence` | `node-workflow/targeted_evidence` | `graph/nodes/targeted_evidence/workflow.md` |

这个表是当前 rollout expectation，不是长期手写 inventory authority。checker 应从 prompt
catalog 的 canonical logical-node set 推导 required package paths；新增 LLM-bearing node 时，
缺少 local card 必须失败。no-agent node 默认不得为了整齐而添加空 card。

### Identity 与检索键

第一版只新增 card-level stable ID：`node-workflow/<logical_node>`。不要再给 cognition、entry、
feedback、outcome 和 tuning prose 各制造一套 record schema；那会迫使读者先学 ID grammar，
却没有改善具体维修。

其余检索直接复用已有 owner 的键：

- direct branch 使用 prompt `case_id`；
- cognitive capability 使用 `capability_id`；
- semantic edge 使用 `<source>:<route>`；
- implementation 使用 exact repo-relative `file::symbol`；
- evidence 使用 exact pytest selector、scenario ID 或 metric ID。

这些键已经能被 `rg`、测试和 review 引用，不再制造别名 ID。

每个 card 第一行固定为机器可读 metadata：

```markdown
<!-- node-workflow-card: {"schema_version":1,"workflow_id":"node-workflow/wave2_synthesis","logical_node":"wave2_synthesis","classification":"node-agent"} -->
```

系统因此既可按固定 path 找文件，也可用 `rg 'node-workflow/wave2_synthesis'` 找 card。
metadata 与 path、`NODE_SPEC.logical_name` 不一致时 check 必须失败。

建议的导航方向是从 review surface 指向 runtime owner，而不是要求 runtime-rendered
capability Markdown 反向链接文档：

```text
graph/nodes/<logical_node>/node.py <-> workflow.md
        -> generated prompt cases + package-local capability sources
        -> source-owned symbols + current main specs + responsible tests
        -> normalized semantic topology

generated prompt case -> owning node package/workflow.md
optional derived index -> all node-local workflow.md files
```

任何全局 index 都只能从 local cards 派生，不能保存第二份 prose 或 ID inventory。

不要求 `capabilities/*.md` body 加 backlink。loader 会把 metadata 后的正文放进 system
policy；为了文档导航修改它，会改变模型实际收到的 prompt。若未来确实要求从 capability
source 反向导航，应先设计一个不进入 renderer 的独立 source-index seam，而不是偷偷扩展
capability schema 或正文。

每张 card 固定回答以下问题，避免没有维修方向的自由散文：

| 区块 | 必须包含 | 数据来源 / 维护方式 |
| --- | --- | --- |
| Identity | card `workflow_id`、logical node、`node-agent` / `no-agent`、real factory | authored metadata + `NODE_SPEC` existence check |
| Maintenance map | observable symptom、first inspect、exact `file::symbol`、why-first、responsible test/eval | 人工对照 source/test 审阅；这是首要 reader interface |
| Cognitive job | 模型的有界判断、请求工具姿态、不拥有的 authority | capability/prompt exact refs |
| Runtime assembly | shared system policy、capability header/body、objective、expected output、evidence、runtime enforcement 的 reader 与可见性 | loader、renderer、request builder、bridge exact refs |
| Entry / feedback | 可信输入；每条 feedback 的 source、actual recipient、actual signal、effect、bound 和 re-entry | node/controller/gate/human exact refs |
| Candidate paths | direct branch、builder、capability、请求工具姿态 | 从 `prompt_catalog_cases()` 派生到 bounded region |
| Admission / outcomes | parser、validator、materializer、ledger/checkpoint owner；每个 failure 的 recovery、bound、terminal/exception 与 legal next action | 人工语义 + exact owner/test refs |
| Exit semantics | semantic route/target、route writer、executable edge kind/target、route consumer | semantic inventory 派生；executable control 人工引用 builder/node/gate |
| Worked repair | 至少一个真实 symptom 到 causal chain、edit set、test/eval 的完整例子 | 人工维护；优先选择高风险或已知 conformance gap |

Recovery 必须按层级写。例如 Wave0/Wave1 至少区分一次模型 structured repair、共享
work-attempt retry、phase gate repair；HITL1/Topic Planning 必须说明 provider recovery 与
structured repair 共用 model-call ceiling。不要把这些不同 owner 都写成“retry once”。

该投影应显示控制所有者，而非把流程画成模型自主决策。例如 Wave2 卡应写成：
“model returns synthesis candidate -> node validates assigned refs -> node writes canonical
synthesis and creates typed gate preview -> wrapper invokes gate -> gate writes route”；同时另列
repair 后无效 candidate 的当前 exception outcome。还必须写明 initial `ValueError` 当前只触发
repair、没有把具体 failure 送给 repair model。不能写成“模型决定下一步”或“validator 已反馈”。

### Documentation checker 的接口

不再建立读取人工 Python schema 的 central catalog。建议由
`agent/scripts/node_workflow_docs.py`（拟议名称）提供两个窄动作：

```python
def render_inventory(logical_node: str) -> str:
    """Join prompt cases and normalized semantic edges for one generated region."""


def check_workflow_docs() -> tuple[str, ...]:
    """Check card coverage, identity, generated bytes, and exact source links."""
```

checker 从 prompt catalog 得到 canonical LLM-bearing node set，按固定 path 找
`nodes/<logical_node>/workflow.md`，只读取第一行 metadata 与 exact
`BEGIN/END GENERATED` region。它不解析 cognitive job、feedback、outcome 或 maintenance
prose，也不生成它们。package root 的 public interface 仍然只有 `NODE_SPEC`。

具体 join 规则：

1. direct branches 通过 prompt catalog 的 canonical logical-node identity join。目前
   `PromptCatalogCase.node_name` 是输出路径 slug（如 `wave2-synthesis`），不是
   `LOGICAL_NODES` identity（`wave2_synthesis`）；应增加显式 `logical_node` 字段或一个受测的
   closed mapping，不能依赖全局 `-` -> `_` 字符串猜测。
2. branch builder、capability ref 和 request tool posture 从 built `NodeExecutionRequest` 派生，
   只进入 generated inventory，不在 prose 中维护第二份枚举。
3. semantic route labels/targets 从 `NORMALIZED_EDGES` 按 source node 派生，并使用
   `<source>:<route>` 作为显示键；不得由 card 创建 edge。
4. route writer、executable edge kind/target 和 route consumer 仍是带 exact source refs 与
   test selector 的人工语义，因为当前 `TopologyEdge` 不编码 conditional/unconditional，
   builder 也不是由 topology data 自动装配。
5. checker 可验证 repo-relative path、Python symbol 和 pytest file/selector 的静态存在性，
   但 owner、bound、feedback 是否真正对模型可见、failure 含义和 why-first 仍由 code review
   负责。

runtime、capability loader、prompt renderer、builder、state reducer 和 production node
factories 均不得调用 checker 或读取 `workflow.md`。

### 防漂移方式

纯手写 inventory 会过时；纯 AST 又无法从任意 Python 推断 failure 的产品含义。推荐一个
更窄的混合方案：

1. 每个 node-local `workflow.md` 直接保存不可推导的 maintenance semantics 与
   source/spec/test refs；同一文件的 bounded region 保存派生 inventory。
2. 提供与 `prompt-dump-check` 同类的只读 freshness check。写入命令只能原子替换已验证文件中
   exact generated region；不得覆盖整份 MD、递归清理 node package，必须拒绝 symlink、
   duplicate/missing marker、unexpected file kind 与 path escape。
3. 检查集合相等：prompt-catalog canonical logical-node set 与 local `workflow.md` set 完全相同；
   每个 case 恰好归属一张 card、每张 card 至少有一个 case、no-agent package 没有空 card。
   当前 `6 nodes / 16 cases` 只作为摘要，不是硬编码上限。
4. 检查 identity：workflow ID 由 containing directory 唯一派生；metadata、path 与
   `NODE_SPEC.logical_name` 必须一致。direct branch/capability/edge keys 复用现有 owner。
5. generated region 必须与 `prompt_catalog_cases()`、built requests 和 `NORMALIZED_EDGES`
   byte-for-byte fresh；每个 Exit 另有 exact builder wiring ref 与 responsible test selector。
6. focused tests覆盖 region parser/path safety、coverage/identity、freshness、source-link
   existence、navigation、purity/non-import 与 project-structure registration。
7. checker 只能证明 inventory、identity、link 和 freshness，不能证明人工 feedback/recovery
   prose 与 implementation 语义一致。设计与 code review 仍必须核对 referenced owner。

这样形成有 locality 的维护 interface：读者在 node package 内只学一张 card；branch/topology
从已有 owner 聚合，shared work-unit/gate 逻辑仍维护一次，人工只承担机器无法可靠推导的
因果含义。删除 checker 只会失去 freshness enforcement，不会让维修语义散回 Python literal；
这说明 checker 是 adapter，而不是另一个需要读者学习的产品 module。

### 不推荐的方案

| 方案 | 不采用的原因 |
| --- | --- |
| 向 `capabilities/*.md` metadata 加 route/parser/retry 字段 | 直接违反 `node-agent-capabilities` 的 authority limit，静态资源会成为第二控制权威。 |
| 在每个 `node_prompts/*.md` 重写完整流程 | 16 个 branch 文档会重复六个 node 的控制，且 prompt catalog 的 synthetic case 不是生命周期执行记录。 |
| 用 `workflow_review.py` 大 literal 保存人工语义，再生成整份 MD | 引入一套陌生 Agent 必须先学的 schema；Python record 与 Markdown 重复表达同一语义，却仍不能证明 runtime loading/feedback。 |
| workflow prose 再手写 branch IDs、route labels 和 targets | freshness check 只能发现两份 inventory 不一致，却不能消除重复维护；应只在 bounded region join 现有 owner。 |
| 只放一张全局大图 | 能回答拓扑，不能回答 candidate 如何被接纳、repair 谁拥有、gate 为什么改 route。 |
| 从 Python AST 自动生成全部流程 | 能抽取函数和部分调用，无法可靠表达异常、state ownership、gate policy 和产品级 recovery 语义；容易制造看似精确但错误的图。 |
| 为所有 11 个 node 强制建立同样的 card | 会把 no-agent controller 伪装成“智力节点”，增加噪声。先覆盖六个 LLM-bearing packages，其他只在需要时加确定性操作卡。 |

## 风险 / 取舍（v0 历史推演）

- [projection inventory 漂移] -> branch 与 semantic route/target 直接从 prompt catalog 和
  topology 派生；generator + completeness/freshness check 只校验每张 authored card 的
  bounded generated region。
- [人工 outcome 语义漂移] -> 每个 failure row 必须带 owner/bound/evidence refs，并在 owner
  行为变化的 change 中列为 review surface；明确 freshness 不能证明语义正确。
- [人工 runtime trace 漂移] -> 每一跳使用 repo-relative `file::symbol`，checker 做 existence
  check；验收用具体 symptom 要求陌生 Agent 重走 source/test，而不是只检查 Markdown 格式。
- [卡片过度简化共享控制] -> 按 invocation/structured-repair/work-attempt/phase-gate 分层标注
  owner；链接 shared module 的 interface，不复制其 implementation。
- [读者误认为模型控制流程] -> 固定采用 “candidate -> deterministic admission -> route owner”
  的写法，并把模型 capability、admission owner、route writer 与 route consumer 分栏。
- [Coding Agent 误认为 node 只是传统程序] -> card 首屏先给 symptom-to-owner map，再展示
  cognitive job、model-visible prompt assembly 与 input/feedback loop；认知质量导向
  capability/request/context/eval，结构、authority 和 route 问题导向确定性 seam。
- [spec/code divergence 被文档掩盖] -> 已发现的 Wave1/targeted/Wave2 outcome 缺口单独进入
  owning change；Wave2 必须明确“validation failure 只触发 repair、未送达模型”；card 区分
  required 与 implemented，不把 main spec 文本冒充运行证据。
- [导航污染 runtime prompt] -> generated prompt case 和 workflow index 可互链，但不修改
  capability Markdown body 或 metadata 来添加 review backlink。
- [文档量反而变成负担] -> 一 node 一 card；首两屏必须完成症状定位和智力识别，完整 load
  chain、outcome 与 worked example 放在后续可跳过区块。不在 `AGENTS.md` 或 README 复制正文。
- [历史 OpenSpec 与当前行为混淆] -> card 只链接 main spec 和当前符号；归档 change 只在
  背景中引用，不作为行为证据。

## 历史 v0 验收标准（不属于 final）

1. 每个 LLM-bearing node 只有一个 node-local `workflow.md` reader interface，不存在必须同时
   学习的 `workflow_review.py`、JSON/Python semantics record 或远端 prose owner。
2. 每张 card 首两屏明确 `node-agent` / `no-agent`，并提供
   `symptom -> first inspect -> exact file::symbol -> why -> responsible test/eval`。给定认知质量、
   feedback、结构、admission、budget 或 route 症状，陌生 Coding Agent 能先选中正确 owner，
   并看见专门 quality eval 缺失时的 `MISSING`，而不是被测试总量误导。
3. 每张 LLM-bearing card 列出真实 runtime assembly/load chain，并把 sources 标为
   model-visible system policy、model-visible request content、runtime enforcement、deterministic
   admission、graph control 或 review-only。特别证明 capability header 被剥离、body 进入 system
   policy、objective/expected output 进入 user message、generated prompt/card 不被 runtime 加载。
4. 给一个完全不熟悉 DeerFlow 的 Agent **只提供 Wave2 `workflow.md`** 和症状
   “`synthesis_findings_required` 后 repair 重犯”，它必须定位到
   `node.py::build_real`、`prompts.py::build_synthesis_repair_prompt`、prompt catalog synthetic case
   与 real-node request test，并说明当前 validation error 被丢弃、不能先改 parser/gate/builder。
5. `agent/node_workflows/README.md`（若保留）一跳到达每张 local card；每个 generated prompt
   case 一跳到达所属 card；card 回链 exact capability source。不得为 backlink 修改会进入模型的
   capability body。
6. `prompt_catalog_cases()` 的 canonical logical-node/case 集合与 workflow cards 完全相等；
   current snapshot 是六个 LLM-bearing nodes、16 个 direct branches。每张 card 的 bounded
   generated region 与 built requests、`NORMALIZED_EDGES` 完全 fresh，没有 orphan/stale/extra。
7. 每个 branch 能回答 trusted input、candidate、deterministic admission owner 和工具姿态；
   每条 feedback 能回答 actual recipient、actual signal 与 bound，并明确区分 model-visible
   feedback、trigger-only repair 和 graph-only feedback。
8. 每个 Exit 分别给出 semantic route、route writer、edge kind、route consumer 和 target。
   `targeted_evidence` 明确 handler 的 `next` 不被消费，实际返回 Wave2 依赖 unconditional edge；
   Wave0、Wave1、Wave2 明确 successful route 由 wrapper gate 产生。
9. HITL1 card 说明 proposal checkpoint、interrupt、人的响应、semantic candidate、共享调用预算
   与 `needs_followup` 自环；Targeted card 区分 gap worker/controller/ledger 与 conditional critic，
   不把缺少 producer 的 `critic_work_items` 描述成已证明的正常旅程。
10. 已列 conformance 缺口在各自 owning change 中修复，或在 card 中标为 implemented
    limitation；尤其不得把 Wave2 trigger-only repair 写成 validation feedback 已送达，也不得把
    repaired-invalid exception 写成统一 typed `exhausted`。
11. checker 在 coverage/identity、generated-region bytes、source/spec/test links、unsafe markers/path
    或 structure 漂移时失败；写入只替换 exact generated region。它明确不宣称验证
    semantic/executable parity、why-first 或人工 feedback/outcome prose。
12. `project-structure` registry/spec/checker、generated `agent/AGENTS.md` locator（若结构提示受影响）
    和 focused architecture fixtures 同步；runtime、capability loader、prompt renderer、graph
    builder、state reducer 和 production node factories 均不读取 workflow docs/checker。

## 历史 v0 落地关联（不属于 final）

这份分析建议独立建立一个 OpenSpec change，例如
`make-node-agent-control-flow-reviewable`，并新增一个明确 owning 的 documentation capability
（名称可为 `node-workflow-maintenance-map`），而不是把要求散放进
`node-agent-capabilities` 或 `research-graph-lifecycle`。

该 change 的 admission 至少应写清：

- **Primary module / causal owner:** 各 `agent/src/deerflow_deep_research/graph/nodes/<node>/workflow.md`
  是 node-local reader interface；`agent/scripts/node_workflow_docs.py` 是派生 inventory/check 的
  adapter。二者引用 prompt cases、semantic topology 与 wrapper/gate owners，但不接管这些事实。
- **Necessary adjacent contracts:** `node-prompt-catalog` 提供 canonical branch identity 并承载
  generated case -> card link；六个 node main specs 与 `work-unit-kernel` 提供 behavior owners；
  `project-structure` 注册新 paths；`node-agent-capabilities` 只作为不被修改的 authority limit。
- **Evidence seam:** region renderer/freshness/path-safety tests、coverage/identity/link/purity tests、
  architecture registry tests、每张 card 引用的最低责任 behavior test，以及至少一个
  symptom-driven newcomer repair exercise。
- **Exclusions:** graph topology behavior、checkpoint schema、Node Agent capability metadata/body、
  runtime tool policy、`backend/`、`frontend/`。若要让 topology 数据直接驱动 builder 或修复上述
  conformance 问题，分别建立 owning change。
- **Triggered charter policies:** `authority-and-projections`、
  `node-agent-workflow-integrity`、`workflow-outcome-review`。Proposal 必须包含完整
  `## Node Agent Review` 与 `## Workflow Outcome Review` tables，不能只在本分析里出现。

结构范围必须显式包括六个 authored local `workflow.md`、checker/region renderer、focused tests
和可选的 derived `agent/node_workflows/` index，并同步 `project-structure.toml`、owning delta/spec
与 architecture checker。
若 `PromptCatalogCase` 增加 canonical `logical_node` 或 generated prompt files 增加 workflow
link，`node-prompt-catalog` delta 与其现有 tests 也必须同步。

第一批仍只覆盖由 prompt catalog 派生出的 LLM-bearing logical nodes；是否为 no-agent
controller 增加 operation card，留待真实读者需求出现。Wave1 baseline/critic、targeted
gate-view、Wave2 validation-feedback delivery、focused-canary bridge authenticity 与
repaired-invalid outcome 应作为独立、先行或并行的 conformance work，不混进纯
documentation tasks，也不能在它们未解决时写成已通过的全链路事实。
