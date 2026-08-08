# Plan: Deep Research Harness Agent-Native Progressive Plan

> 类型: 渐进落地计划 / 已收拢 | 状态: **五条 agent-native vertical slice 与共享 deterministic gate repair 均已完成、同步并归档；本计划不再扩张，也没有 active implementation change** | 更新: 2026-08-08

## 这份 Progressive Plan 现在负责什么

`adopt-deep-research-harness-run-bundles` 已于 2026-08-06 完成并归档。filesystem root
已经是 `deep_research_harness/`，Bundle-local State 已经取代旧 session / external-checkpoint
authority，公开工具保留 `deep_research` 名称并提供 `start`、`resume`、`status`、`cancel`、
`refine`。相关实现提交包括 `9ced872` 和 `853eba2`，归档 change 位于
[`openspec/changes/archive/2026-08-06-adopt-deep-research-harness-run-bundles/`](../../../../openspec/changes/archive/2026-08-06-adopt-deep-research-harness-run-bundles/)。

因此，这份文档不再为已经完成的目录和 identity 迁移准入。它现在回答迁移暴露出的下一层
问题：**怎样让 DeerFlow agent workflow 真正拥有 Deep Research 的认知控制，同时让 Python
继续守住状态、权限、预算、准入和副作用；怎样证明用户的自然语言要求确实影响了研究，而
不只是被存进 State 或写进一段测试文本。**

本文是唯一的渐进落地计划与 change admission，不授权代码修改，也不直接修改 main specs。它把
外部一手资料、DeerFlow 本地实现核查和逐项引用
[`deep-research-harness-agent-native-workflow-research.md`](deep-research-harness-agent-native-workflow-research.md)，
以及测试资产的具体落点
[`deep-research-harness-test-asset-audit.md`](deep-research-harness-test-asset-audit.md)，收敛为一个
按顺序推进、每阶段都可停止的 vertical slice。

三份材料已经收敛到一个已完成的 OpenSpec change：
[`2026-08-08-establish-agent-native-research-direction-loop`](../../../../openspec/changes/archive/2026-08-08-establish-agent-native-research-direction-loop/)。
它的实现提交为 `2fcbab6`，spec sync 与归档提交为 `dc91537`。归档中的
[`proposal.md`](../../../../openspec/changes/archive/2026-08-08-establish-agent-native-research-direction-loop/proposal.md)
冻结范围和 authority，
[`design.md`](../../../../openspec/changes/archive/2026-08-08-establish-agent-native-research-direction-loop/design.md)
定义 progressive phases 与 Go/No-Go，
[`tasks.md`](../../../../openspec/changes/archive/2026-08-08-establish-agent-native-research-direction-loop/tasks.md)
记录完成证据。本文继续保留为什么这样收敛的 admission reasoning，不再维护平行 change 顺序。

第二条、小范围的 HITL1 cognitive-program ownership slice 也已完成：它将四份 production-loaded
capability Markdown 变成各自 bounded cognitive method 的唯一 owner，保留 Python 对 candidate
admission、correlation、State、route、budget 与 recovery 的确定性责任；并以版本化 control corpus
区分 deterministic handoff 与 credentialed live-quality evidence。change 已同步主规格并归档于
[`2026-08-08-establish-hitl1-cognitive-program-ownership`](../../../../openspec/changes/archive/2026-08-08-establish-hitl1-cognitive-program-ownership/)，
实现、spec sync 与归档提交为 `e6b742f`。

下文“当前真正的问题”至“五个渐进闸门”保留为该 change 在 apply 前的诊断和承诺，不能当作
当前实现事实阅读；本文件末尾的“已完成的 slice 与下一次准入”才是 2026-08-08 后的现状与
后续决定。

## TODO List（唯一进度清单，按依赖顺序）

本节是这份计划中**唯一**使用 checkbox 的地方。所有项均已完成或被明确收拢；不必从后面的
设计、历史 Focus Card 或归档说明中再找待办。

- [x] 1. Run Bundle 基础迁移：Bundle-local State 成为唯一 lifecycle authority，公开工具具备
  `start` / `resume` / `status` / `cancel` / `refine`。
- [x] 2. Direction-loop：完成 Phase 0--4（可信启动、如实准入、同 Bundle round、agent-native slice、
  校准与关闭），`2026-08-08-establish-agent-native-research-direction-loop` 已同步并归档。
- [x] 3. HITL1 cognitive-program ownership：Focus Card、实现、deterministic corpus 与 `16/16` tasks
  已完成，归档提交 `e6b742f`。
- [x] 4. Wave0 source-intake cognitive-program ownership：Focus Card、最低责任 test assets、实现与
  `18/18` tasks 已完成，归档提交 `797c9b6`。
- [x] 5. Wave1 extraction/repair cognitive-program ownership：两份 runtime-loaded method、closed corpus、
  `13/13` tasks 及 `WON-010` / `EVH-028` spec sync 已完成，归档提交 `db8677e`。
- [x] 6. 共享 deterministic gate 修复：`2026-08-08-restore-deterministic-gate-contracts` 已归档；
  focused tests、`UV_OFFLINE=1 make test-assets`、`UV_OFFLINE=1 make test-fast` 与完整 verify 均通过。
- [x] 7. Wave2 synthesis cognitive-program ownership：初始 synthesis 与一次 zero-tool repair 的
  runtime-loaded method、closed deterministic corpus、`17/17` tasks，以及 `WSN-008` / `EVH-029`
  main-spec sync 均已完成；change 已归档为
  [`2026-08-08-establish-wave2-synthesis-cognitive-program-ownership`](../../../../openspec/changes/archive/2026-08-08-establish-wave2-synthesis-cognitive-program-ownership/)，
  提交 `3a1cde1`。
- [x] 8. **收拢决定：**credentialed live cognitive case 是补充性 release-quality research，不是
  deterministic ownership migration 的完成条件。本计划有意不执行它，也不把它保留为未完成工作；只有
  独立、重新获批的研究或发布评估才可重新考虑。
- [x] 9. **计划终止：**不在本计划中选择或准入下一项功能，不创建 successor OpenSpec change，也不进行
  猜测性代码修改。

### 已完成 Focus Card：HITL1 Cognitive-Program Ownership

| 项目 | 已准入的决定 |
| --- | --- |
| Primary module / causal owner | `deep_research_harness/src/deerflow_deep_research/graph/nodes/hitl1/`；该 module 已拥有 brief、semantic intake、candidate repair 与 graph-side admission 的组合。 |
| Question | 如何让现有四个 runtime-loaded HITL1 capability Markdown 成为 brief 与 semantic-reply interpretation/repair 的唯一认知方法 owner，同时保留既有的 typed candidate、human correlation、profile acceptance、Bundle-local persistence 和 route owner？ |
| Trusted input projection | 原始研究问题、当前 checkpointed proposal、受限 validation fact 和当前 human reply 作为有界 data 进入 `NodeExecutionRequest`；能力 Markdown 不接收 State writer、route、request id、path 或 tool 权限。 |
| Deterministic owners | `domain/profile.py` 和 `domain/human_interaction.py` 保留 schema/validation；HITL1 node 保留 correlation、调用上限、recovery、checkpoint/profile materialization 与 route；runtime renderer/bridge 保留 exact resource loading、zero-tool posture、budget 和 safe failure。 |
| Lowest responsible evidence seam | 四条 production renderer/resource tests 证明实际 system policy 读取 exact capability method；prompt-builder tests 证明 objective 只携带本次 bounded facts；scripted HITL1 node/integration tests 证明 candidate 仍必须经过 parser/materializer，且 ambiguity、invalid-output repair、provider exhaustion 和 cancellation 不越权。 |
| Cognitive-quality evidence | 新的 versioned HITL1 corpus 覆盖 normal confirmation、complete revision、question、ambiguity、prompt-injection、malformed candidate/repair；deterministic lane 只证明 handoff/constraint，获批 credential 后的 live review 才能主张语言判断质量。 |
| Necessary adjacent contracts | `agents/phase_prompt.py` 只回答“production renderer 是否加载该资源”；`runtime/node_agent_bridge.py` 只回答“zero-tool posture/budget 是否强制”；`domain/profile.py` 只回答“接受的 profile 如何持久化”；它们不扩展为 change 的新 owner。 |
| Triggered review policies | `human-interaction-integrity`, `node-agent-workflow-integrity`, `workflow-outcome-review`, `control-placement`。 |
| Not in scope | 不改 `ResearchProfile` / `SemanticCandidate` schema、pending-response correlation、Bundle lifecycle、profile-to-topic-planning canonical projection、tool posture/call ceiling、public controller、`wave0`/`wave1`/synthesis/final delivery、`backend/` 或 `frontend/`。 |

这张卡的关键取舍已经由归档实现验证：profile-to-topic-planning 的 `profile_ref` consumer chain 已在
上一条 change 落地，不能再被包装成 HITL1 的“投影工作”。HITL1 只收紧其内部的认知 owner，保持深
module 的小 interface：输入是有界 assignment，输出是闭集 candidate；复杂的自然语言 method、分支
与 repair 留在 runtime-loaded Markdown，所有可见或持久化 effect 继续藏在确定性 implementation 后面。

### 已完成 Focus Card：Wave0 Source-Intake Cognitive-Program Ownership

| 项目 | 已准入的决定 |
| --- | --- |
| Primary module / causal owner | `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave0/`；`prompts.py` 目前拥有 worker 与 repair 的大量可复用认知方法，`subgraph.py` 只编排其已有确定性 handoff。 |
| Question | 如何让现有两个 runtime-loaded Wave0 capability Markdown 成为 source-intake worker 和其一次 pre-candidate structural repair 的唯一认知 method owner，同时保留 web-tool、source admission、ledger、gate 与 route 的既有 owner？ |
| Trusted input projection | 仅 topic assignment（`topic_id`、title、scope、must-answer bindings）和闭集 output contract 作为 worker/repair 的可信 data；repair 另收严格 validation category。工具结果、retrieved page/snippet 与 model draft 均保持 untrusted data，不能改写 instruction authority。 |
| Deterministic owners | runtime node-agent bridge / `ExecutionPolicy` 强制 allowed web tools、attempt root、1--3 tool-call bound 与 cancellation；`domain.work_units` parser/schema、artifact writer、submit validator 与 ledger 决定 source admission；work-unit controller/gate 决定 retry、degraded coverage、terminal outcome 和 route。 |
| Lowest responsible evidence seam | production renderer/resource regression 观察 exact capability body；prompt-builder test 证明 objective 只留下 assignment/output data；`test_real_wave0_worker_binds_the_required_capability_before_artifact_admission` 以 fake capability 驱动真实 worker/controller；repair 与 post-candidate validation tests 证明一次 repair 和不回流 repair 的边界。 |
| Cognitive-quality evidence | 新增 versioned Wave0 corpus 必须覆盖正常 bounded retrieval、retrieved prompt injection、retrieval shortfall、malformed initial candidate/one repair、以及 post-candidate rejection；deterministic lane 只证明 loaded method、tool/candidate handoff 和 authority limits。真实 web/model judge quality 仍需受控 live evidence，不能由 fixture 代替。 |
| Necessary adjacent contracts | `agents/phase_prompt.py` 仅验证/加载 exact local resource；`runtime/node_agent_bridge.py` 仅执行 configured tools/budget；`engine`/`domain.work_units` 仅解析、验证、提交和记录 source candidate；这些都不成为新的 cognitive method owner。 |
| Triggered review policies | `node-agent-workflow-integrity`, `workflow-outcome-review`, `control-placement`。 |
| Not in scope | 不改 `WorkSpec`、`Wave0WorkerOutput`/`wave0.source-intake` contract、URL/content validation、artifact path/ledger、gate/source floor、retry budget、graph edges、topic registry、Wave1、synthesis、final delivery、public controller、`backend/` 或 `frontend/`。 |

Wave0 比 HITL1 多了 web tools，但这不授权 capability 选择工具、绕过 attempt root 或承认 source
evidence。这个 change 的唯一认知迁移是“如何在许可 retrieval 下筛选、处理不确定性、输出 candidate
和做一次结构 repair”；任何 candidate 必须继续经过既有 parser、artifact writer 和 submit validation
才可能进入 ledger。若实现中发现 capability method 需要改动 tool policy、source-floor 或 gate，必须
停止该 change 并重新准入，而不是把新 controller 塞进 Markdown。

## 仍然成立的系统边界

| 主题 | 冻结决定 |
| --- | --- |
| Run Bundle | 一件持续打磨的 Deep Research 对应一个 opaque `bundle_id` 和一个可独立删除的 Bundle；Bundle-local State 是该 Run 唯一生命周期 authority。 |
| Active / ended | 一个 trusted conversation scope 同时至多一个 active Bundle；ended Bundle 仍可检查，显式 refinement 可在同一 Bundle 开启后续 round。 |
| Current Bundle Handle | Handle 只是短期 locator，不能证明 Bundle 存在、可用或处于某状态；缺失时只能在 trusted scope 内按 Bundle-local State 发现。 |
| Deletion | Bundle 不可用后不得由 session、checkpoint、日志、诊断或缓存恢复；新建独立 Run 仍合法。 |
| Human input | correlated pending response 只能由 `resume` 消费；独立的 run direction 只能由 `refine` 接收，两者不能互相冒充。 |
| 上游边界 | 不修改 `backend/` 或 `frontend/` 来放宽 Harness boundary；需要的 DeerFlow 能力应先通过现有公开 agent/skill 接口使用。 |

Canonical model 位于 [`deep_research_harness/CONTEXT.md`](../../../../deep_research_harness/CONTEXT.md)，
durable decision 位于
[`ADR-0028`](../../../../deep_research_harness/docs/adr/0028-deep-research-harness-is-the-downstream-module-root.md)。
旧 session 模型只作为迁移历史，不再是下一 change 的设计依赖。

## 当前真正的问题

### 不是“prompt 还不够长”，而是认知 owner 放错了位置

当前 Harness 已经调用真实 DeerFlow agent loop，也已经支持 package-local capability Markdown，
但认知程序仍主要由传统 Python prompt builder 拥有：

| 当前事实 | 证据 | 判断 |
| --- | --- | --- |
| 20 个 runtime-loaded capability Markdown 合计只有 114 行 | `graph/nodes/*/capabilities/*.md` | 它们目前多是短 policy supplement，还没有完整表达方法、分支、检查和 repair workflow。 |
| 11 个 `workflow.md` 合计 427 行 | `graph/nodes/*/workflow.md` | main spec 明确把它们定义为 non-runtime reader projection；它们不能控制模型执行。 |
| 方法、步骤、禁止项、repair 和输出格式大量拼在 `prompts.py` | `hitl1`、`topic_planning`、`wave0`、`wave1`、`wave2_synthesis`、`targeted_evidence` | 修改认知行为仍迫使 coding agent 像改传统程序一样改字符串和分支。 |
| `NodeExecutionRequest` 的主要认知接口仍是自由文本 `objective` / `expected_output` | `domain/context.py` | capability 虽已可加载，但 Python 仍能临时重写大部分方法；认知程序没有单一、可版本化的 owner。 |
| `RuntimeNodeAgentBridge` 每次建立无 checkpointer 的 ephemeral full-takeover agent | `agents/factory.py`、`runtime/node_agent_bridge.py` | 当前只保留 budget 和 tool-policy middleware；这是合理的 bounded phase-agent 安全姿态，但不等于充分利用 DeerFlow 的 skill/workflow 能力。 |

DeerFlow lead agent 已经提供正确的分层样板：SOUL / activated `SKILL.md` 负责让模型识别任务、
选择 workflow 和解释结果；middleware、tool schema、ThreadState 与 runtime owner 负责执行边界。
充分利用 DeerFlow 不意味着给每个内部 phase agent 打开 memory、subagent、todo 或 clarification，
而是让 **Markdown 成为认知方法的 runtime source**，再按每个角色的风险显式选择能力和
middleware。full-takeover 可以继续存在，但必须是经过说明的 capability posture，而不能成为
“既然都关掉了，就继续把认知写回 Python”的理由。

### Public controller 只有动作协议，没有 conversational workflow

[`config/public-skill/deep-research-controller/SKILL.md`](../../../../deep_research_harness/config/public-skill/deep-research-controller/SKILL.md)
只有 14 行，contract 还强制其不超过 1400 bytes。它列出了五个 action 和若干限制，却没有
完整规定模型如何从自然语言、pending interaction、Current Bundle Handle 和 typed lifecycle
result 中选择唯一合法动作，也没有规定歧义、冲突、unavailable 和 ended 后 refinement 的
对话策略。

这与 DeerFlow 自带的
[`skills/public/deep-research/SKILL.md`](../../../../skills/public/deep-research/SKILL.md)
形成明显对比：后者用 Markdown 明确写 phases、研究方法、检查项和迭代策略。DeerFlow runtime
会真实发现、加载或注入 `SKILL.md`，所以 public controller skill 应该是一段可执行的对话
workflow，而不只是工具参数速记。

现有 `tests/integration/test_public_entry_replay.py` 也没有证明这项 UX：fake model 的 tool call
已经由测试作者预先写成 `start` / `resume`，模型根本没有根据用户自然语言或 tool result 作
选择。该测试能证明 schema、tool loop 和结果投影接得上，不能证明 controller 会做对决定。

### `note` 的两个含义都需要收紧

若这里的 “note” 指 **graph node**，问题是：我们是否把传统程序中的每一个处理步骤都做成了
node，而没有先证明它是 durable orchestration boundary。若它指 **用户备注 / 运行中意见**，
当前实现同样没有形成效果闭环。

已确认的 `custom_notes` 数据流如下：

```text
HITL1 识别并确认 custom_notes / scope_boundaries
            |
            v
     profile.json 持久化完整 ResearchProfile
            |
            +--> Bundle-local State 只投影短字段
                         |
                         v
              topic planner / 后续 node
              未读取 custom_notes 或 scope_boundaries
```

`profile_state_fields()` 没有把 `custom_notes` 或 `scope_boundaries` 投影进 Bundle-local State，
`planner_inputs_from_state()` 也不读取 `profile_ref`。因此备注虽然保存在 `profile.json`，却没有
进入 topic planning、retrieval、synthesis 或 final delivery 的 runtime prompt。当前不能声称
它会约束研究结果。

已确认的 `refine` 数据流也不完整：

- active Bundle 的 `refine` 只把单个 `admitted_refinement` 写入 State；第二次输入会覆盖第一次，
  没有 queue、history 或 explicit supersession。
- 生产 graph 没有读取或调用 `consume_admitted_refinement()`；所谓 “next safe point” 目前只在
  reducer 名称和规格中存在。
- ended Bundle 的 refinement 会立即清空该字段并增加 `refinement_round`，但
  `BundleControl._refine()` 不调用 `BundleGraphExecutor`，所以它不会实际启动下一 round。
- 当前测试证明了 bounded text、durable write、不误消费 pending response 和 pure reducer，
  没有证明 refinement 改变 planner、retrieval、synthesis、report 或用户可见结果。

结论是：当前 `custom_notes` 与 `refine` 的处理 **不恰如其分**。问题不是再增加一个 `note`
action，而是建立 typed direction 的生命周期、应用点和结果证据。

## Target: 四层 agent-native program

| 层 | 应拥有的内容 | 不应拥有的内容 |
| --- | --- | --- |
| Public controller skill | 从自然语言和 typed lifecycle result 选择 `start/resume/refine/status/cancel`；歧义处理；truthful user response；何时停下来等待用户 | Bundle 状态推断、path/identity 构造、graph phase、checkpoint、内部 gate 或 retry topology |
| Graph orchestration | durable checkpoint、human interrupt、fan-out/join、safe point、独立 admission/gate、恢复和不可逆副作用边界 | 研究方法的逐步自然语言、如何判断来源、如何修复一份模型草稿 |
| Node cognitive capability | 一个角色的完整 method、输入解释、工具策略、分支、self-check、repair 和 completion condition；以 package-local runtime-loaded Markdown 为 canonical source | phase route、State mutation、artifact admission、权限、预算上限和“成功”最终裁决 |
| Deterministic owners | typed State、schema、trusted projection、tool allowlist、budget、candidate validation/admission、route、store 和 publish | 用大量 if/else 和拼接 prompt 代替模型该承担的判断，或用 fake model output 宣称 UX 正确 |

原则仍是 Charter 的 `Cognition proposes; deterministic owners validate, admit, and route`。
这里所谓 Markdown control flow 不是把所有 Python 搬进 `.md`，而是让认知方法只有一个真正被
runtime 加载的 owner；Python 只投影可信数据并执行不可绕过的约束。

### Public controller 的最小决策表

| 对话事实 | controller 行为 |
| --- | --- |
| 用户提出一项新的研究，当前没有 active Bundle | 以本轮唯一 tool call 调用 `start`，不复制问题到参数，也不构造 id。 |
| tool result 要求一个 correlated response，用户给出匹配回答 | 调用 `resume`；回答留在最新 user message，不塞入 tool arguments。 |
| 用户给的是独立研究方向而非 pending subject 的回答 | 调用 `refine`，保留用户原意的 bounded text；不得用 `resume` 偷渡。 |
| 同一句话既可能回答 pending subject，也可能是 run direction | 不猜；先用自然语言澄清它要回答当前问题还是修改研究方向。 |
| 用户询问进度、状态或上次结果 | 调用 `status`，按 typed result 说明事实和合法下一步。 |
| 用户要求停止 | 调用 `cancel`，不把“已发起”说成“已取消”，必须按结果回应。 |
| 用户对 available ended Bundle 提出新方向 | 使用明确 `bundle_id` 调用 `refine`；成功只意味着 runtime 真正启动或排定了下一 round，不能只回报字段已保存。 |
| Bundle unavailable、target ambiguous 或 transition conflict | 如实说明不可用或需要显式选择；不得从旧 session、日志或猜测恢复。 |

`SKILL.md` 应拥有这张表背后的 workflow、优先级和停止条件，SOUL 只保留稳定人格/产品原则，
tool docstring 只保留 schema 级事实。相同规则不应复制成三个必须人工同步的 prompt owner。

## Direction 已怎样收敛

单一 change 已冻结三个不同含义，并同步写入
[`deep_research_harness/CONTEXT.md`](../../../../deep_research_harness/CONTEXT.md)：

1. **Correlated Research Response**：只回答当前 human subject，由 `resume` 按 request/message
   correlation 精确消费。
2. **Accepted Profile Note**：HITL1 确认的 `scope_boundaries`、`custom_notes` 等持久约束；
   `profile_ref` 指向的 canonical profile 是内容 authority。
3. **Run Refinement**：active 或 ended Run 上独立提交的 `refine`，不改写 profile，也不冒充
   pending response。

MVP 不采用 append-only queue/history。每个 Bundle 最多一个 pending refinement：同一 trusted
delivery 幂等；相同 pending text 不重复 admission；不同的第二条 direction 返回 typed conflict
并完整保留第一条，绝不 silent overwrite。应用后只保留当前 round 的 bounded refinement fact，
更早方向由其已经产生的 round/artifacts 体现，不建立无限历史。

本 change 的 active safe point 也故意收窄为**当前 refinement round 已提交 terminal graph
snapshot 的边界**。suspended subject 必须先由 `resume` 正常解决，pending refinement 继续显示为
waiting；显式 ended refinement 已处于边界，可在同一 Bundle 立即准备下一 full rerun。跨 Bundle
State 与 Bundle-contained graph checkpoint 的提交使用 deterministic round token、prepare-before-
publish、CAS 和 crash reconciliation；只有 Bundle State commit 后才能向外报告 applied。

第一条 cognitive effect 只打到 `topic_planning`：它从 canonical profile 读取完整 notes/scope，
再叠加 current-round refinement 形成 bounded assignment。direction 不能选 route、topic id、path、
tool 或 State writer；现有 rerun controller、zero-tool bridge 和 topic materializer 继续拥有这些
确定性效果。

## Node Admission Review

一次 LLM 调用、一个 prompt 文件或一个“看起来像阶段”的名词都不足以成为 graph node。每个
现有 node 只有在至少承担一个下列边界时才应保留：

- human interrupt / resume correlation；
- durable checkpoint 或 crash-recovery boundary；
- bounded parallel fan-out / join；
- 独立 candidate admission、gate、retry budget 或 failure outcome；
- 需要隔离和幂等的外部副作用；
- direction safe point 或明确的 round boundary。

初步审计不是删除决定，而是给下一 proposal 的逐项问题：

| 当前 node | 初步存在理由 | change 必须回答 |
| --- | --- | --- |
| `bootstrap` | 原子创建 Bundle 内容和初始 durable State | 只保留初始化/发布；不要在这里藏研究判断。 |
| `hitl1` | human interrupt、profile confirmation 和 correlation | profile 的完整有效约束如何成为后续 trusted projection；语义 intake/repair 是否应是一个 Markdown workflow 内的分支。 |
| `topic_planning` | 产生 fan-out 前的 durable accepted plan | 保留 plan admission boundary；decomposition 与 repair 应由同一 capability workflow 拥有。 |
| `wave0` | per-topic fan-out、工具使用、candidate source admission | source intake/diagnostic/repair 的认知步骤是否应合并为一个 agent workflow，而不是多个 Python prompt call。 |
| `wave1` | per-source evidence work、claim admission 和并发 | extraction、verification、diagnostic、repair 的内部循环由 capability 表达；controller 只保留 work/gate 状态。 |
| `wave2_synthesis` | 跨 topic join 和 accepted synthesis artifact | synthesis/repair 是一个 cognitive program；必须接收 effective direction。 |
| `targeted_evidence` | 缺口驱动的新一轮 bounded retrieval | 只有在独立 work/budget/recovery 边界成立时保留 node；否则成为 evidence workflow 的分支。 |
| `readiness` | 决定继续补证、进入 HITL2 或交付的 gate | 确定性 readiness 和 model critic 的责任要拆清；route 不能由 critic 自证。 |
| `hitl2` | 最终 human decision / interrupt | 保留 interaction boundary；不得复制 final quality workflow。 |
| `rerun` | 新 generation / retry control | 若只做状态路由，应是 deterministic controller，不应伪装成 cognitive node。 |
| `final_delivery` | 最终 compose、publish 和用户可见 artifact | composition method 可在 capability；publish/admission 必须留在 deterministic owner，并消费有效 directions。 |

`workflow.md` 继续作为给人看的 route/owner map，不直接拼进 system prompt，因为它混有维护导航、
graph topology 和 authority 说明。真正运行的 capability Markdown 应足以独立回答“该角色如何
工作”，并从 `NodeExecutionRequest` 接收结构化 task data，而不是让 Python 再拼一份平行方法。

## Runtime Markdown 的准入契约

每个被迁移的 cognitive program 至少需要：

- stable `capability_id`、role、method version 和 source digest；
- 明确的 trusted input projection 与 untrusted evidence 分隔；
- task method、decision branches、tool-use policy、uncertainty handling、self-check、repair 和停止条件；
- 输出 candidate schema 与 authority limit，明确模型不能提交、route、写 State 或宣称 gate 通过；
- 对应的 normal、ambiguity、adversarial、tool failure、invalid output/repair eval cases；
- renderer test 证明生产 runtime 读取的正是这份资源，而非测试副本或 reader projection。

capability 内容可以比当前 4-8 行更完整，但不以长度为目标。`objective` 应逐步收缩为本次 task
的 typed/bounded facts，`expected_output` 应收缩为 schema/contract reference；可复用方法和
repair policy 不应继续动态拼接。

## 必须证明的产品行为

| 风险 | 最低责任证据 |
| --- | --- |
| Controller 能理解用户意图 | 真实 DeerFlow skill injection + real model 的 bounded controller eval；fake typed `deep_research` tool 只替代外部生命周期，不预写模型 action。 |
| Controller 接得上生产工具 | scripted real lead-agent workflow，保留 skill activation、middleware、tool schema 和 loop，断言 trajectory 与 truthful result projection。 |
| `custom_notes` / scope 真正生效 | deterministic projection test + affected cognitive-program eval；断言运行时 prompt digest/输入包含 canonical bounded direction，并以对照 case 检查输出行为变化。 |
| active refinement 不丢失 | domain concurrency/state tests 证明多条输入不覆盖、pending response 不被消费、safe-point exactly-once apply 和 crash recovery。 |
| refinement 改变研究 | mixed workflow 从 public refine 到下一 safe point，再到至少一个真实 planner/retrieval/synthesis/composer，比较 admitted direction 前后的 observable plan/artifact。 |
| ended refinement 真正继续 | integration test 证明显式 target 启动同一 Bundle 的下一 round、graph 有进展、旧材料保留，不能只断言 `refinement_round += 1`。 |
| Node cognition 改对 | 以 capability/cognitive program 为 subject 的 versioned eval corpus，记录硬不变量、质量 rubric、成本、延迟、模型/provider 和人工 review。 |
| Graph 边界仍可靠 | 最短 scripted mixed/full pipeline 验证 checkpoint、fan-out、gate、failure 和 publish；它不替代 controller 或 node 的局部认知 eval。 |

关键字存在、byte-size cap、prompt snapshot、预写 fake tool call、字段已写入 State 都可以保留为
静态或 wiring 证据，但不得再被表述成上述 UX / semantic quality 的证明。

## 一个 Change，五个渐进闸门（实施前承诺，现已完成）

这里最终选择的不是四个 change，也不是一个同时开工的巨包，而是**一个 change 内的 gated
vertical slice**：

| Phase | 先交付什么 | Go 条件 |
| --- | --- | --- |
| 0. Trustworthy start | 只修 13 个 requirement id declaration；证明真实 DeerFlow skill activation；用 fixture adapters 组合生产 `StateGraph` 的 topology/reducers/rerun writer/edge，证明同一 Bundle 的现有 rerun 能回到 `topic_planning`，且不调用外部 API | `make test-assets` 绿；真实 composed context 看到 committed skill；feasibility test 不创建第二 Bundle/external checkpoint，也不以全真实 provider 调用冒充 graph API 证据 |
| 1. Truthful admission | 一个 pending/current-round refinement、幂等、typed conflict/result | reducer/lifecycle/reopen/concurrency/pending-response matrix 全绿，且没有 applied overclaim |
| 2. Same-Bundle round | terminal-round safe point、crash-consistent prepare/commit、ended lazy graph start | 一次 operation 只产生一次 generation；restart/stale writer 不能重复或覆盖；真实到达 `topic_planning` |
| 3. Agent-native slice | public `SKILL.md` workflow、SOUL 责任收缩、canonical profile notes、topic-planning capability Markdown | actual loader + scripted handoff + prompt/bridge/materializer + 最短 direction-effect workflow 全绿 |
| 4. Calibrate/close | controller/topic-planning versioned cognitive cases、全量 deterministic gate、review closeout | implementation finding 全闭合；live evidence 只按其真实性报告，不冒充 deterministic proof |

每个 No-Go 都要求后续 task 保持 unchecked，在同一 change 内修订 design/spec；不得用另一个
change、外部 checkpoint、copied loader 或第二 Bundle 悄悄绕过。广泛 registry 清扫、其余 19 个
capability program、finer-grained mid-round safe point 和 full-real release 继续明确不在本 change。

## 已完成的 slice 与下一次准入

`establish-agent-native-research-direction-loop` 已完成、通过 strict validation、同步 main specs 并于
2026-08-08 归档。它以 `runtime/` 的 Bundle lifecycle/graph-execution boundary 为 primary causal
owner，覆盖 Run Bundle、graph lifecycle、runtime integration、deployment configuration、rerun 和
`topic_planning` 的最小必要 delta。Control Placement、Workflow Outcome、Node Agent Review，以及
plan-review / archive-closeout-review 均已完成。

五个闸门均已通过：真实 public skill 的 runtime loading 与 handoff、refinement 的有界准入与
同 Bundle round、canonical profile direction 到 topic planning 的 effect、版本化 controller/planner
评测资产、以及全量 deterministic verification。最终 `UV_OFFLINE=1 make verify`、strict OpenSpec
validation 和受保护的 `backend/` / `frontend/` 路径检查均为绿。唯一必须保留的证据边界是：没有
获批 live credential，因此两组 live cognitive case 的结论是 `limited`；它不是 deterministic
pass，也不是 full-real release 证据。

Wave0 已完成、同步并归档于
[`2026-08-08-establish-wave0-source-intake-cognitive-program-ownership`](../../../../openspec/changes/archive/2026-08-08-establish-wave0-source-intake-cognitive-program-ownership/)。
它证明了下一层 pattern：runtime-loaded Markdown 可以成为 tool-bearing worker 与 zero-tool repair 的
唯一认知 method owner，而 runtime 仍拥有 tool posture，validator/controller/ledger/gate 仍拥有
admission 与 lifecycle。

### 已完成：Wave1 Extraction/Repair（已同步并归档）

本条只处理了 `graph/nodes/wave1/` 中的 `wave1-evidence-extraction` 与
`wave1-evidence-extraction-repair`。此前 Wave1 的初始 prompt 曾在 Python 中重复 retrieval、baseline
newness、candidate-source/claim、counterevidence/open-question 与 authority-limit 方法；repair prompt 也
重复 baseline 与 no-invention 方法。这与 Wave0 问题同构，但 Wave1 多了一条不能突破的
事实：accepted Wave0 baseline URL 不能被表示为新的 Wave1 coverage。

- **Focus Card（已完成）：**已确认 primary owner 为 Wave1 worker/repair prompt seam；可信输入仅为 topic
  projection 与 accepted Wave0 baseline，新 retrieval/draft 均为 untrusted data。
- **Test-asset decision（已完成）：**现有 evaluator 并非可直接容纳 Wave1 的 generic fixture；但 HITL1/Wave0
  的 typed cognitive-program pattern 可以在同一 change 内按最小 Wave1 sibling 扩展。它必须覆盖 normal
  handoff、adversarial retrieval、baseline duplicate、parser/local-semantic repair、post-validation isolation，
  且 selected-live 必须在创建任何运行证据前拒绝。
- **Change scope（已完成）：**已归档
  [`2026-08-08-establish-wave1-evidence-extraction-cognitive-program-ownership`](../../../../openspec/changes/archive/2026-08-08-establish-wave1-evidence-extraction-cognitive-program-ownership/)；
  它包含 Wave1 与 `evaluation-hardening` 双 delta，仍不改 `Wave1WorkerOutput`、two-source floor、
  new-vs-baseline validation、artifact/ledger、retry/gate、graph route、source diagnostic、claim verifier 或 Wave2。
- **Polish / archive（已完成）：**proposal 的三份 review、双 delta、design 和可勾选 tasks 已一致；`13/13`
  task、strict OpenSpec、Agent Charter、lint/format、test assets、requirement coverage、相关 `148` 项回归、
  diff 与受保护目录 checks 均通过。两份 main spec delta 已同步，并按 OpenSpec recommended workflow 归档。
- **共享门禁恢复（已完成）：**`2026-08-08-restore-deterministic-gate-contracts` 已以 `skip_specs` 修复 registry、
  lane-selection、Wave0/Wave1 capability-resource 和两处 HITL1 renderer 测试契约，并以完整 `make verify`
  收口归档；它未改变 Wave1 的 approved owner。Wave2 随后已完成、同步 main specs 并归档，未留下 active
  implementation change。

credentialed live 补证没有启动：它只能补齐既有 deterministic handoff 的 release-quality research，
不能替代任何 authority proof，也不是本计划的完成条件。除非另有独立、明确获批的研究或发布评估，
本计划到此结束。

到这里为止，这份 plan 的结论不是“少写 Python、多写 Markdown”，而是：**把认知方法写在
真正被 DeerFlow runtime 执行并能独立评测的 Markdown program 中；把持久化、权限、准入、
预算和副作用留给 deterministic deep modules；再用观察真实决策和实际结果变化的测试证明
用户体验，而不是证明字符串与字段存在。**
