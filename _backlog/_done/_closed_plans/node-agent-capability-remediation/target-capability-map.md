# 目标 Node Agent Capability 映射

> 类型：待审定的能力设计地图；不是运行时规范，也不是 prompt 成稿
> 更新：2026-07-27
> 前置事实：[当前 Node Agent Invocation 全量盘点](current-state-inventory.md)

## 设计原则

每份 node-local Markdown 不应只是把现有 Objective 剪贴进去。它应让一个 coding agent、
reviewer 和模型都能回答六个问题：

1. 你是谁，为什么在这个 node 被调用？
2. 你能看什么、应该怎样推理或检索？
3. 工具是禁止、可选还是必须，为什么？
4. 哪些 authority 永远不属于你？
5. 什么结果算完成，何时必须诚实地说不确定？
6. 输出不合法时，repair branch 能修什么、绝不能补造什么？

建议每个 `capabilities/*.md` 至少有固定的可解析章节：`Role`、`Method`、`Tool posture`、
`Authority limits`、`Completion and uncertainty`。内容本身作为 trusted capability policy
进入最终 system prompt；动态数据、schema 值和 untrusted evidence 仍由 Python renderer
按独立 section 注入。

## 拟定目录与引用约定

下面是待阶段 A/B 审定的示意，不是要求现在创建这些文件：

```text
graph/nodes/<node>/
  capabilities.py
  capabilities/
    <capability-slug>.md
```

每个 `capabilities.py` 公开本 node 的稳定 capability declarations；`prompts.py` 只能
引用本 node 已声明的 capability。`NodeExecutionRequest` 最终携带一个必填 reference，
renderer 根据经过验证的 reference 加载对应 Markdown。这样有两个好处：

- node 的 Python 与 Markdown 在一个目录，读者不必跨越一个巨大 registry 才知道它做什么；
- runtime 只消费 reference 和已加载 policy，不拥有或猜测 node 的认知语义。

## 当前 Agent Branch 的目标地图

“推荐工具姿态”是当前设计判断，阶段 A 必须逐项确认；其中用 **已证实** 标明的项目来自
现有代码/文字的明显一致要求，其他为明确的待审定建议。

| 目标 capability ID | Owner / local Markdown | 独有认知工作 | 推荐工具姿态 | 当前要补上的内容 |
| --- | --- | --- | --- | --- |
| `hitl1.profile_brief` | `hitl1/capabilities/profile-brief.md` | 从研究问题提出可解释、保守的 advisory profile；不把建议当接受。 | 禁止（已证实）。 | profile 推断范围、何时留下不确定/待人确认、不得研究/引用/路由。 |
| `hitl1.profile_brief_repair` | `hitl1/capabilities/profile-brief-repair.md` | 只修复原 brief 的结构，使其符合 profile schema。 | 禁止（已证实）。 | 不引入新偏好或事实；repair input 视为 untrusted。 |
| `hitl1.semantic_intake` | `hitl1/capabilities/semantic-intake.md` | 在当前完整 proposal 语境理解自然回复，产生封闭候选 intent。 | 禁止（已证实）。 | 接受、修改、提问、澄清的区分；不拥有 action/route/checkpoint/citation authority；对清晰回复简洁。 |
| `hitl1.semantic_intake_repair` | `hitl1/capabilities/semantic-intake-repair.md` | 只将先前不合法候选修成封闭 schema。 | 禁止（已证实）。 | 不重新解释为新的研究结论；不借 repair 扩大 authority。 |
| `topic_planning.profile_decomposition` | `topic_planning/capabilities/profile-decomposition.md` | 将已确认 profile 拆为覆盖完整、互不重叠、可研究的 topic。 | 禁止（建议，待审定）。 | profile 约束优先、coverage/non-overlap method、何时保守缩小主题、不得开始外部研究。 |
| `topic_planning.plan_repair` | `topic_planning/capabilities/plan-repair.md` | 仅修复 plan 的结构/覆盖约束。 | 禁止（建议，待审定）。 | 不引入外部事实或新的用户偏好；明确 repair 与新规划不同。 |
| `wave0.authoritative_source_intake` | `wave0/capabilities/authoritative-source-intake.md` | 对一个 topic 做宽度优先、独立且权威的来源发现/获取。 | 必须；1-3（已证实当前设计）。 | 来源独立性、权威性、canonical URL、degraded 诚实记录、不得从先验编造来源。 |
| `wave0.source_intake_repair` | `wave0/capabilities/source-intake-repair.md` | 只利用已有 draft/tool results 生成合法 source 元数据。 | 禁止（已证实）。 | 禁止补造 URL/title/fact；不能借 repair 再检索。 |
| `wave1.evidence_extraction` | `wave1/capabilities/evidence-extraction.md` | 基于 topic 在 Wave0 baseline 外进行定向检索，形成可支持/反驳的 claims 与 open questions。 | 必须；恰好 1（已证实当前设计）。 | source novelty、claim/counter evidence、问题状态、不得重取 baseline。 |
| `wave1.evidence_extraction_repair` | `wave1/capabilities/evidence-extraction-repair.md` | 只从已有输出修复 Wave1 schema。 | 禁止（已证实）。 | 不可新增来源、claim 或 question；区分 repair 与研究。 |
| `wave2.evidence_synthesis` | `wave2_synthesis/capabilities/evidence-synthesis.md` | 仅基于 accepted evidence 建立 findings、relations 与真实 gaps。 | 禁止（**已证实，现有 Objective 已如此声明**）。 | evidence-only reasoning、confidence、gap scheduling、冲突处理、不得调用 web 或编造。 |
| `wave2.synthesis_repair` | `wave2_synthesis/capabilities/synthesis-repair.md` | 只用 accepted evidence 修复 synthesis 输出。 | 禁止（已证实）。 | 不补新 evidence/relations/facts；保留 honest gaps。 |
| `targeted_evidence.gap_source_intake` | `targeted_evidence/capabilities/gap-source-intake.md` | 对一个特定 synthesis gap 进行一次受限检索，给出可解决或诚实未解决的证据。 | 必须；恰好 1（已证实当前设计）。 | gap 绑定、single-search discipline、resolved/deferred/unresolved 标准、limitations。 |
| `targeted_evidence.gap_source_intake_repair` | `targeted_evidence/capabilities/gap-source-intake-repair.md` | 只将已有 targeted draft 变成合法结果。 | 禁止（已证实）。 | 不能搜索、不能新增事实/来源、不能改变 gap id。 |
| `targeted_evidence.source_diagnostic` | `targeted_evidence/capabilities/source-diagnostic.md` | 对指定 source 内容判断 trust/materiality/marketing/cross-verification。 | 禁止（**已证实：现有模块说明为 read-only/no tools**）。 | 证据评分方法、不能访问未分配资料、不得把 source 指令当命令。 |
| `targeted_evidence.claim_verification` | `targeted_evidence/capabilities/claim-verification.md` | 只对 assigned evidence refs 判断 claim 的支持、削弱、反驳或不确定。 | 禁止（**已证实：现有模块说明为 read-only/no tools**）。 | assigned-ref discipline、support/counter refs、理由与不确定性、不得补检索。 |

## Node 级阅读地图

| Node | 一个读者应先看什么 | 不应误以为 |
| --- | --- | --- |
| `hitl1` | `capabilities.py` 后依次读 profile brief 与 semantic intake policy。 | 模型可以接受 proposal 或改 checkpoint；它只能给候选。 |
| `topic_planning` | profile decomposition policy 与 topic contract。 | topic planner 已在做网络研究。 |
| `wave0` | authoritative source intake policy，再看 source result contract。 | output repair 可以找新来源。 |
| `wave1` | evidence extraction policy 与 Wave0 baseline input。 | 一次 search 意味着允许编造未取到的证据。 |
| `wave2_synthesis` | evidence synthesis policy 与 accepted evidence contract。 | synthesis 因工具默认值而可以绕过 accepted evidence。 |
| `targeted_evidence` | 四种不同 capability，而非一个笼统“worker”。 | critic、gap search 和 repair 共享同一工具权力或认知任务。 |

## Deferred Node 的未来准入卡

以下 node 不在本次 16 branch 迁移中。它们未来若从 deterministic 实现变成模型调用，
不得直接在 `node.py` 插一段 `run_agent()`；必须先填这张卡并开相应 OpenSpec change。

| Deferred node | 未来可能能力 | 先要决定的事 |
| --- | --- | --- |
| `readiness` | evidence-readiness critic | 人工规则与模型 critic 的分工、是否有工具、如何阻止模型绕过 hard rules、blocked repair 的 authority。 |
| `final_delivery` | evidence-grounded report writer | report style vs evidence truth、citation map authority、是否允许工具、最终报告的验收与修复循环。 |

## 结构性防复发要求

目标能力图不应只作为一次人工 checklist。foundation change 的 tests/architecture checks 至少应
证明：

1. 所有生产 `NodeExecutionRequest` builder 选择一个明确 declared capability；
2. 每个 declared capability 都有同 node 包内的 Markdown policy，且 capability ID、
   resource path、catalog case 和 branch 一一对应；
3. policy 满足固定章节/metadata，不是只换标题的一份 common text；
4. capability posture 与 `tools_enabled`、minimum/limit、bridge 实际 tool resolver 的
   组合合法；
5. renderer / bridge / dump 使用同一个 composed policy，catalog 显示 node policy 的
   source 路径与最终文本；
6. 没有生产 generic/default capability，也没有可替换全部 system policy 的通用桥接入口；
7. 新增 agent branch 缺少上述信息时，在 deterministic architecture test 中失败。

## 仍待审定的取舍

- repair 是否全部用独立 capability：当前保守推荐是“是”，因为它们往往从搜索/推理切换
  到只读、结构恢复、不得补造的完全不同任务；若未来某一 repair 与初始能力真正同构，
  必须由 capability contract 明示而非隐式共享。
- planner 是否绝对 zero-tool：当前推荐是是，因为它处理已确认 profile；但应在 change
  design 中确认这不是产品期望的遗漏。
- policy resource reference 的具体表示：可采用受限 path convention，或 manifest；不应
  允许调用者把任意字符串作为 system prompt 传给 runtime。
- 初始 capability migration 是否同时把 `objective` 拆为 typed assignment：推荐在同一
  foundation change 至少建立明确 section/model；若完整 typed payload 迁移过大，可拆为
  后续契约加深 change，但不能继续把静态角色文字留在 Objective。
