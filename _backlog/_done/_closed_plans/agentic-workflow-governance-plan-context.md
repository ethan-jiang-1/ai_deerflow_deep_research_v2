# Context: 为什么需要 Agentic Workflow 治理与 Node-Agent 契约

> 配套计划：[Agentic Workflow 治理与 Node-Agent 契约](agentic-workflow-governance-plan.md)
> 用途：让不了解本次讨论或仓库历史的 reviewer 理解这份计划为何存在、哪些事实支撑它、以及应提出什么建设性意见。
> 状态：背景与评审材料，不是运行时 authority、OpenSpec delta 或实现任务清单。
> 更新：2026-07-27

## 如何使用这份背景

先读本文件，再读配套计划。计划拥有拟议机制、职责分工、change train 和待确认的架构
决定；本文件只提供理解这些决定所需的事实、历史和阅读地图。两份文件都不是当前
runtime behavior 的第二权威，具体行为仍由 accepted specs、active delta、代码和测试按
各自主题拥有。

请区分三类陈述：

| 陈述类型 | 在材料中的含义 | 应到哪里核实 |
| --- | --- | --- |
| **已核实事实** | 当前源码、生成 catalog、测试或 OpenSpec 状态已经能证明的行为或缺口。 | 下文的 inventory / active change 路径。 |
| **架构判断** | 为什么此前的投入没有释放 DeerFlow 的 agentic 价值，以及应怎样重新分工。 | 配套计划的“DeerFlow 的魅力与本次方向纠偏”。 |
| **待审定提案** | `NodeAgentCapability`、目录形状、能力地图、change 顺序和工具姿态。 | 配套计划“实施目标”以后及关联 remediation plan。 |

结论不是“确定性实现错了”，也不是“所有 node 都应该让模型主导”。确定性实现和节点
智力都需要；此前的问题是两者被投入到了错误职责上。图已经承担了它应承担的控制工作，
下一步需要把真实 LLM-bearing node 的认知工作变成一等、可验证的系统对象。

## 术语速览

| 术语 | 在本材料中的准确含义 | 不等同于 |
| --- | --- | --- |
| **Graph / node handler** | LangGraph 生命周期编排、状态读写、route、retry、checkpoint 与 artifact promotion 的确定性 owner。 | 一个拥有研究判断权的万能 agent。 |
| **Node Agent** | 在一个 node 的一个明确 branch 中执行 bounded cognitive work 的 LLM 角色。 | node 本身、通用聊天机器人或 route controller。 |
| **Node Agent Capability** | Node Agent 的小执行 interface：稳定 ID、node-local policy、工具姿态、assignment/output 与 typed candidate contract；候选采纳者和 evidence seam 由 node-owned governance projection 关联。 | 一段自由 prompt、YAML 配置、全局 agent profile，或把 parser/catalog/test selector 塞进 runtime request 的大而全 registry。 |
| **Candidate** | LLM 产生但尚未被系统接受的结构化结果、建议、检索结果或修复草案。 | 已写入 checkpoint 的事实、graph route 或最终研究结论。 |
| **Runtime bridge** | 唯一的受控执行 adapter，负责模型、实际工具、sandbox、预算、取消与安全失败投影。 | 为 node 决定研究方法或替换其认知角色的第二 controller。 |
| **`no-agent` node** | 其当前工作可以并且应该完全确定性地完成的 node / branch。 | 一个“以后再补 prompt”的漏项。 |

## 前因后果：问题怎样被看见

1. Deep Research 先建立了确定性骨架：显式 node、typed state、checkpoint、HITL
   correlation、retry / terminal handling、artifact materialization 和测试资产。这些工作是
   必要的，它们让研究流程有可恢复、可审计的骨架。
2. 在这个骨架上，模型调用逐步被接入各个节点，但接入方式是把角色、方法、工具意图、
   输出限制和 repair 规则继续塞进每个 Python builder 的 `objective` / `expected_output`
   字符串，再交给一份共享 `runtime_policy.md`。于是流程“能跑”，却没有可审查的节点
   智力分工。
3. 人类交互的“自然确认”事故暴露了这类错位：用户面对完整 proposal 输入自然语言确认，
   系统却把它当传统 profile 字段解析。问题不是少一个同义词，而是没有一个明确的
   `hitl1.semantic_intake` Node Agent 专门理解 proposal 语境，同时又不拥有 graph action
   authority。
4. 随后的 prompt catalog 盘点进一步给出系统性证据：当前 16 条可达模型 branch 的最终
   system 层都来自同一份通用 node-agent policy；不同节点的智力差异散落在动态字符串里。
   catalog 使这个事实可见，却没有改变它。
5. 因而不断增加 parser、branch condition、HITL alias、单点 Objective 或 catalog diff
   没有解决根因：它们能补传统控制路径，却不能声明“这个 node 的 LLM 到底要怎样做研究、
   能调用什么、何时必须保留不确定性、谁采纳结果”。

方向纠偏不是废弃已有 deterministic work，而是把它从“代替认知”的位置放回“编排、
约束、验证和采纳认知”的位置。

## 已有工作、它解决了什么、它还没有解决什么

| 已有工作 | 已提供的价值 | 不能替代的下一步 |
| --- | --- | --- |
| 确定性 graph / lifecycle / checkpoint 实现 | 把状态、route、retry、HITL correlation、artifact 与终态留在可验证的 owner 手中。 | 不回答一个 LLM-bearing node 的研究角色、方法或工具姿态。 |
| `make-node-prompts-auditable` | 生成无需模型调用的 prompt catalog，使 16 条 branch 的实际 prompt 形状可审计。 | 它的明确 non-goal 是改变 prompt 语义，不能把 catalog 当成 capability 定义或运行时 authority。 |
| `establish-human-interaction-contract` | 定义自然语言 reply 的候选 intent、图拥有的接受权、可见 control 与安全绑定。 | 它解决“人如何表达、谁能接受”；尚不能替所有节点定义“模型如何理解和研究”。其 `semantic_intake` 是后续 capability foundation 的重要使用者，而不是 foundation 本身。 |
| `node-agent-capability-remediation` 盘点与目标地图 | 记录当前 16 条 branch、工具矛盾、拟定 capability 名称和测试分层。 | 复用其 inventory/map；本轮评审不接受“单个 foundation change 先批量迁完 16 branch、再做行为闭环”的交付假设。 |
| `define-node-agent-workflow-governance` | 把“节点智力需要明确 review”变成 Agent Charter 的条件准入与 checker。 | 它不创建 `NodeExecutionRequest` capability、prompt resource、bridge 行为、工具 enforcement 或任何模型质量结论。 |

## 测试资产分布：为什么 1857 是危险的分母

本轮重新运行当前仓库的 collection、asset checker 和三个 deterministic lane。结果支持
“大量投入仍在测传统程序”的担心，但需要把结论说准：这些资产多数不是无用，而是它们
证明的对象与项目下一步最缺的对象不相同。

| 观察口径 | 当前事实 | 评审含义 |
| --- | --- | --- |
| pytest collection | 2037 个参数展开后的 case；deterministic aggregate 为 2027 | case 数不是 scenario 数，更不是 agent 判断数 |
| 传统确定性核心 | `contract/domain/engine/unit` 共 1608 个，占总收集 78.9% | 控制面很厚；不能由此推断模型会研究 |
| fast lane | 1857 selected，全部通过 | 证明契约、domain、engine、unit、局部 graph/eval seam；不是 agentic score |
| integration lane | 154 selected；131 passed、19 failed、4 skipped，另有 15 workflow deselected | 完整 deterministic gate 当前不绿 |
| workflow lane | 16 selected；15 passed、1 failed | 显式 workflow 资产只占总收集约 0.8% |
| live / release | 8 / 1 collected；其中 registry 只有 4 条 live claim、1 条 release claim | 真实模型分布与研究质量证据非常薄 |
| central evidence registry | 162 claims：141 correctness、16 workflow、4 live、1 release | 可审计声明的 87.0% 仍是 code correctness |
| capability 分母 | 16 条 production `run_agent()` branch；现有 workflow inventory 只按 6 个 owner 聚合 | node 有测试不等于该 node 的每条认知 branch 被验证 |

仓库另有 10 个 first-wave deterministic scenario case 和 6 个 live canary scenario。它们是
比 pytest 总数更有意义的资产，但仍未形成 16 branch × 成功/高风险行为 × 真实性等级的完整
矩阵。尤其是 repair、tool-required、tool-forbidden、semantic intake、source selection 和
synthesis 不能被同一 node 的另一个 happy path 代替。

`make test-assets` 当前会报告通过：13 incidents、11 real nodes、7 critical faults、6
model-workflow nodes、162 central claims，以及各 lane 的 selector 数。这个通过只证明引用
闭合和分类规则成立；它既不执行这些行为，也不会发现本轮 integration/workflow 的失败。
因此不能把“asset checker 绿”写成“agent workflow 绿”。

当前失败也不是模型质量失败。至少有两组清晰的契约漂移：adapter/workbench 仍读取当前
`PromptView` / `PendingSessionInput` 上不存在的 `action_ids`，多条 lifecycle 测试仍把 LangGraph
`Command` 当可下标的旧字典结果；TUI 和 session view 随之投影成 fault 或旧状态。workflow
lane 唯一失败也是同一 `Command` shape 不匹配。这些失败说明传统集成面尚未收口，却不能
反过来证明或否定 Node Agent 的研究能力。

评审后的证据口径是：

1. 控制面正确性继续保留，避免为了调比例删除有价值的 regression。
2. 新增 agentic 资产时以 branch、scenario 和真实性等级计数，不追求 pytest case 总量。
3. scripted model/tool 证明 wiring、权限、轨迹和 candidate admission；只有 live/eval 才能
   支持自然语言理解、来源判断和综合质量主张。
4. 未来 snapshot 必须同时报告 fast、integration、workflow、live、release 和 branch matrix，
   禁止只报最大的那个绿色数字。
5. 16 条 branch 是最终覆盖分母，不是一次 bulk edit 的理由；先用 zero-tool semantic、
   required-tool research 和 evidence-only synthesis 三种纵向切片证明共同 kernel，再决定后续
   cohort 是否能留在一个 change 中。

## 评审快照（2026-07-27）

| Change | 当前进度 | 作用 | 与配套计划的关系 |
| --- | --- | --- | --- |
| `make-node-prompts-auditable` | 8/9 | 让现有 prompt 结构可见。 | 是事实盘点和以后 catalog 的基础；不是 node capability 迁移。 |
| `establish-human-interaction-contract` | 8/13 | 让 HITL1 的自然语言输入只产生候选 intent，并维持图的控制权。 | 是 `hitl1.semantic_intake` 的行为闭环；其 adapter 迁移尚未完成，不能据此声称通用 agentic foundation 已完成。 |
| `define-node-agent-workflow-governance` | 9/10 | 增加 Node Agent Review 的治理准入、policy 和 checker。 | 是配套计划的阶段 1；change-local 治理证据已通过，但 task 5.2 的完整验证尚未通过：integration lane 有 19 个失败，workflow lane 有 1 个失败。 |

这个快照有两个重要含义：治理 change 已经给未来 runtime change 建立入口，但还没有改变
任何模型 branch；当前工作树中出现的 HITL / adapter 实现只说明一个局部行为 change 正在
进行，不能倒推出全系统已经拥有 node-local capability。

## 参考项目：借鉴什么，不复制什么

本轮设计阅读了 `ai_tool_deepresearch/guidelines/` 的 agentic workflow / execution guidance，
以及 `ai_tool_bsimulation/openspec/` 的 policy 和 `config.yaml` 组织方式。它们提供的是
机制设计上的启发，不是要被移植的产品架构。

| 借鉴的思路 | 在 Deep Research 中的落点 | 明确不复制的内容 |
| --- | --- | --- |
| 稳定的 agent / deterministic control 分工应在实现前被明确表达。 | Node Agent Review、capability policy、candidate -> evaluator -> graph handoff。 | 对方的 Agent/Engine/Markdown runtime、phase chain、queue、subagent 或 gate 术语。 |
| policy 有具体触发条件，指导 change admission，但不创造运行时权限。 | Agent Charter 的 `node-agent-workflow-integrity` 和 OpenSpec proposal review。 | 用 policy 文档直接定义 Deep Research state、route、writer、tool permission 或 retry。 |
| authoring config 提供短而明确的阅读/审查路由。 | `openspec/config.yaml` 的 change authoring context。 | 把 `openspec/config.yaml`、root `config.yaml` 或任何 YAML 变成 node role / prompt / runtime authority。 |
| 复杂行为需要可验证的 contract lineage，而不是只靠说明文档。 | capability declaration -> local resource -> renderer -> bridge -> catalog -> deterministic evidence。 | 为了模仿另一套 framework 而增加第二个 workflow controller 或平行状态系统。 |

Deep Research 是 LangGraph/Python 的下游 research product，图、状态和 checkpoint 已是可执行
runtime；模型智力需要作为受限 node capability 嵌入其中，而不是把整个系统改造成
Markdown-first agent runtime。任何建议引入参考项目概念的意见，都应先指出它在本项目中
替代的现有 owner、带来的 interface 和最小可验证收益；“名称相似”不是引入新机制的理由。

## DeerFlow Digest：定向机制参考

`_ln_deerflow_digest/` 不是要整体搬进本项目的资料库。已将真正会影响 capability
foundation 的内容收敛为[DeerFlow digest 精选机制地图](agentic-workflow-governance-plan-deerflow-digest-source-map.md)：
它按 Node Agent role、确定性编排、tool/runtime/sandbox 权威，以及测试/可观测性四组列出
精确文件、可借鉴的机制和对后续 OpenSpec change 的约束，也明确排除了 frontend、部署、
通道、泛用 overview 与不适用的 subagent 调度细节。

该地图的资料锚定于上游 `4915b5e`（2026-07-07）。因此它只能提供机制启发和源码导航，
不能证明当前 Deep Research runtime 的事实，更不能成为第二个 policy 或实现 authority。
准备 `establish-node-agent-capabilities` 时，必须回到当前 `agents/`、`graph/`、`runtime/`、
accepted OpenSpec delta 与测试 seam 逐项核实。

## 推荐阅读顺序

1. 本文件的“前因后果”“已有工作”“评审快照”，再读配套计划的“拟审定的控制模型”、
   “建议的交付顺序”和“待确认的架构决定”。
2. [Node Agent Capability 架构纠偏计划](node-agent-capability-remediation-plan.md) 的“一句话结论”、
   “核心定义”“与现有工作关系”和“总验收标准”。
3. [当前 Node Agent Invocation 全量盘点](node-agent-capability-remediation/current-state-inventory.md)，
   尤其是 16 条 branch 表和三处工具 posture 矛盾。
4. [目标 Node Agent Capability 映射](node-agent-capability-remediation/target-capability-map.md)，
   用来审查 capability 粒度、`no-agent` 例外与拟定工具姿态。
5. `openspec/changes/make-node-prompts-auditable/`、
   `openspec/changes/establish-human-interaction-contract/` 和
   `openspec/changes/define-node-agent-workflow-governance/` 的 proposal/design/tasks，
   用来区分已接受范围、待实现行为和配套计划提出的后续基础迁移。
6. `agent/tests/assets/selection.py`、`evidence.py`、`workflow_nodes.py` 和
   `agent/tests/scenarios/`，用 `check_test_assets.py` 的输出核对 collection、claim、scenario
   和 branch denominator，不从 1857 这个总数反推能力。
7. 需要审查“prompt 是否真的被执行层兑现”或验证策略时，再读
   [DeerFlow digest 精选机制地图](agentic-workflow-governance-plan-deerflow-digest-source-map.md)；
   它是上游机制借鉴，不覆盖前五步的 Deep Research 一手事实。
8. 最后沿 `agent/src/deerflow_deep_research/graph/nodes/<node>/prompts.py` ->
   `NodeExecutionRequest` -> `RuntimeNodeAgentBridge` 读一个具体 branch，验证材料事实是否
   与代码一致，而不是反向从一个 branch 推翻或放大整个架构判断。

## 希望 Reviewer 重点挑战的假设

1. **问题诊断是否成立？** “16 条 branch 共享通用 system policy、角色散落在 Objective”
   是否足以说明当前缺的是 node capability，而不是某个更小的 renderer / testing 改进？
2. **职责切分是否正确？** Graph/node handler、Node Agent、runtime bridge 与
   parser/evaluator/materializer 的 owner 是否清晰？是否有任何职责被错误地下放给 LLM，
   或相反仍被传统分支错误地承担？
3. **Capability 是否是足够深的 module interface？** 稳定 ID、local policy、工具 posture、
   assignment/output contract、candidate admission owner 和 evidence seam 是否足够小且有
   leverage？是否遗漏了 caller 必须知道的约束，或泄漏了本应隐藏在 renderer/runtime 内的
   实现细节？
4. **16 条 branch 的粒度和 `no-agent` 分类是否合理？** 特别应审查 repair 是否应独立
   capability、topic planning 的工具 posture 是否真应禁止，以及 Wave2 / targeted critics
   的“文字无工具、请求却允许工具”矛盾该如何收敛。
5. **治理层是否恰当？** 条件性的 Node Agent Review 是否足以防止未来悄悄插入 generic
   `run_agent()`，同时又不会把纯确定性或无关 change 变成仪式性表格？checker 的“只校验
   结构、不推断语义”边界是否正确？
6. **change train 是否正确？** 先治理、再 capability foundation、最后 HITL / research
   behavior evidence 的顺序，是否比直接重写 prompt 或完成局部 adapter 更能降低返工？
   foundation 是否真的以纵向 cohort 交付，还是仍在一个 diff 里先批量迁移 16 条 branch、
   最后才补行为证据？哪些部分必须拆成独立 OpenSpec change，哪些不应过早抽象？
7. **证据主张是否诚实？** 配套计划是否清楚地区分了静态结构、prompt composition、执行边界、
   节点行为与真实模型质量？是否有地方把 fake / deterministic test、`make test-assets` 或
   1857 个 fast case 误说成了模型“聪明”的证据？
8. **测试分母是否正确？** 16 条 production branch 是否各有成功与最高风险的 evidence row，
   还是仍用 6 个 owner、11 个 node、162 条 claim 或 2037 个 pytest case 互相替代？新增资产
   是否真正增加 workflow/live 行为证据，而不是继续扩张 contract/unit 参数组合？
