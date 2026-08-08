# Plan: Agentic Workflow 治理与 Node-Agent 契约

> 类型：架构设计 / OpenSpec change 前置计划
> 状态：已完成并归档；治理准入、capability foundation 与行为闭环分别由连续 OpenSpec changes 完成，deferred node 的未来准入保持独立
> 更新：2026-07-28
> 关系：保留 [Node Agent Capability 架构纠偏计划](node-agent-capability-remediation-plan.md) 的 inventory、target map 和 test seams；本轮修订其“单个 foundation change 批量迁完 16 branch”的交付假设

> 背景导读：[为什么需要这份计划：独立评审上下文](agentic-workflow-governance-plan-context.md)。
> 机制参考：[DeerFlow digest 精选机制地图](agentic-workflow-governance-plan-deerflow-digest-source-map.md)；它是上游机制借鉴，不是本计划的运行时 authority。

## 本轮评审结论（2026-07-27）

方向**有条件通过**：确定性图编排受约束的 Node Agent 是正确的目标；阶段 1 的治理
change 可以继续收尾，但阶段 2 不应在下面的设计门关闭前开工。

本轮把五个容易混淆的判断拆开：

| 判断 | 评审结论 |
| --- | --- |
| 架构方向 | 接受“graph 保有生命周期与采纳权，Node Agent 只做 bounded cognitive work”。 |
| 能力 interface | 修订为小的执行契约；parser、materializer、catalog case、evidence seam 等保留为 owning node / governance projection，不作为 runtime caller 必须理解的字段。 |
| 工具与副作用 | 必须区分 request 声明、model-visible 工具、实际调用和 attempt-scoped 副作用；只写 prompt 不能证明权限。 |
| 证据主张 | 测试数量不能代表 agentic 能力。当前 pytest catalog 收集 2037 个 case；排除 `requires_llm`、`release_e2e`、`postgres` 后有 2027 个 deterministic case，fast lane 选中 1857 个并全部通过。中心 evidence registry 只有 162 条 claim（141 code correctness、16 workflow、4 live、1 release），而生产 `run_agent()` 有 16 条 branch、workflow owner inventory 只有 6 个。integration lane 当前 19 failed、131 passed、4 skipped、15 deselected，完整 gate 仍未通过。 |
| 交付切片 | 最终仍覆盖 16 条 branch，但不能先批量铺完声明/Markdown 再补行为证据；foundation 必须以代表性纵向 cohort 验证 kernel，单个 diff 无法独立审查时先拆 change。 |

这些数字证明了控制面和传统程序的成熟度，不证明模型会研究、选源、理解自然确认或诚实
综合。后文的 foundation 退出条件与后续 eval 必须按这两类证据分别记账。

## 测试资产审计（2026-07-27）

本轮把“收集到的 pytest case”“被 evidence registry 声明的 claim”和“真实模型行为”分开
记账。2037 是参数展开后的测试 case 数，不是 2037 个 scenario，也不是 2037 个 agent
判断。仅 `contract`、`domain`、`engine`、`unit` 四个传统确定性目录就有 1608 个 case，
占总收集的 78.9%，占 fast lane 的 86.6%。这解释了为什么 1857 这个数字很大，却不能
回答节点是否真的会研究。

| 资产口径 | 当前基线 | 能证明什么 / 不能证明什么 |
| --- | ---: | --- |
| pytest 全量收集 | 2037 cases | 仓库可收集；不是能力覆盖率 |
| deterministic aggregate | 2027 cases | 确定性控制面、契约和回归的候选集合 |
| fast lane (`contract/domain/engine/unit/graph/eval`) | 1857 selected；1857 passed，2 deselected | 传统正确性和局部 node seam；不能证明真实模型质量 |
| integration lane (`integration/blocking_io`) | 154 selected；131 passed、19 failed、4 skipped、15 deselected | 跨 runtime/lifecycle seam；当前不是绿门 |
| workflow lane | 16 selected；15 passed、1 failed | 仅 16 个显式 workflow case（14 scripted-real、2 real-node/fake-capability）；不能覆盖 16 branch 的全部语义 |
| live lane | 8 collected；6 个 canary scenario | 真实依赖入口与少量行为切片；4 条 central live claim 仍不等于质量基线 |
| release lane | 1 selected | 一条 full-real acceptance；不能代表研究分布 |
| central evidence registry | 162 claims：141 correctness、16 workflow、4 live、1 release | 可追踪的证明声明；不是 pytest 总数的别名 |

`make test-assets` 通过只说明 selector、claim、scenario 和 inventory 的引用关系闭合，
不说明这些测试的行为都通过，更不说明模型聪明。当前 6 个 model-workflow owner 也不能
替代 16 条生产 branch 的逐 branch 证据；有些 real-node/fake-capability 测试被登记为
正确性资产，不能因为它们调用了 bridge 就自动升级为 workflow 或 live evidence。

因此本计划以后以 **branch × behavior × authenticity** 而不是测试数量作为 agentic foundation
的分母：

1. 16 条 branch 各自必须有 capability identity、成功路径和最高风险的 scripted real
   workflow path；repair、required/forbidden tool、exhausted 和 candidate admission 要有
   明确的断言。
2. 六个 owner 的聚合 inventory 只能作为导航；阶段 2 必须产出可逐项审计的 branch matrix，
   不得用一个 node 的“成功 + 失败”替代其多个 branch。
3. live/eval 只为语义理解、来源选择和研究质量提供证据；deterministic fake、catalog 或
   `make test-assets` 通过不能升级为这些主张。
4. workflow marker、claim registry 和 scenario id 必须互相对齐；若真实 workflow 测试仍
   被放在 fast/integration，需明确标注其真实性等级，而不是靠总数掩盖分层。
5. 不为“改善比例”删除有效的控制面 regression；但新增 fast/contract case 必须指出新的
   failure class 或 seam。相同风险的参数扩张不能计入 agentic 进度。

## 结论

Deep Research 不应被理解为“许多 Python node 串起来，再在几个地方调用一下模型”。
它应是一个有明确分工的 agentic workflow：确定性程序控制整个生命周期，节点内的
LLM 在受限任务中完成真正的语义工作，结果必须经过确定性契约才可影响下一步。

当前缺口不只是 prompt 文案，而是这条机制没有成为可审查、可执行、可防回退的
系统契约。先补这一层，再迁移每个 node 的专属能力；不要继续以单点 Objective、
HITL parser 或 catalog diff 代替架构设计。

## DeerFlow 的魅力与本次方向纠偏

DeerFlow 的魅力不在于“把一个聊天模型挂到一条传统流程末端”，也不在于让模型接管
整个图。它提供的是一种可组合的混合工作方式：图把研究过程拆成有状态、可恢复、可
观测的工作节点；每个需要判断、检索、比较、归纳或受限修复的节点，都可以拥有自己
的 Node Agent 智力；统一 runtime 再把模型、工具、sandbox、预算和取消收敛到同一条
受控执行路径。这样，研究流程既不会失去确定性，也不会把最需要语义推理的工作硬塞
回传统程序。

此前的努力方向有偏差。我们持续强化了 node handler、typed state、route、parser、
HITL 输入分支和 prompt 文本可见性，却没有把真实 LLM-bearing node 的“智力部分”定义
出来：它没有明确自己在研究中要理解什么、采用什么方法、何时能使用什么工具、产出
何种候选，以及其候选由谁采纳。结果是 LLM 只像传统程序中的一个通用字符串函数，
而 Python 分支试图承担本应由受限认知完成的语义工作。问题不在于确定性程序太多；
问题在于把它用在了错误的职责上。

本计划的纠偏原则是：

1. **让图继续做它擅长的事。** 生命周期、状态、并发、route、checkpoint、retry、
   人类输入关联和 artifact promotion 必须由确定性程序拥有。
2. **让 Node Agent 做它不可替代的事。** 在一个明确 capability 内理解任务、判断
   证据、选择受许可的检索策略、综合或提出受限修复；它不是被动填充 JSON 的模板。
3. **让候选结果回到确定性闭环。** 模型的智力可以改变研究内容，却不能自行宣布
   完成、改变 route 或写入事实；parser/evaluator/materializer 决定是否采纳。
4. **让每个节点的智力可被审查和演进。** 不再依赖一个泛化 Objective 或全局 system
   prompt 猜测角色，而是以 node-local capability 明示角色、方法、工具姿态、边界和
   证据 seam。

这不是“多加几个 prompt”的计划，而是把 DeerFlow 从“确定性流程里偶尔调用 LLM”校正
为“确定性工作流编排多个受约束的节点智力”的计划。不是每个 node 都要变成 agent；
但每个真实模型调用都必须是一个有目的、有能力边界、会对研究结果产生可审计影响的
Node Agent。

```text
trusted graph state / typed input
             |
             v
deterministic node handler ---- constructs bounded assignment ----+
             |                                                    |
             | route, retry, state, artifact promotion           v
             |                         Node Agent (LLM cognitive loop)
             |                        understand -> reason -> use permitted
             |                         tools -> synthesize/repair candidate
             |                                                    |
             +<---- typed candidate result / declared artifacts --+
                              |
                              v
                 deterministic parser, evaluator, materializer
                              |
                              v
                     typed state update and graph route
```

这里的 agentic 不等于让 LLM 决定图怎么走，也不等于每个 node 都必须调用模型。它的
含义是：在确实需要理解、检索、判断、综合或受限修复的 node 内，LLM 以清晰角色执行
有界工作；传统程序负责把这项工作放进正确的生命周期、权限和验证闭环。

### 不再继续的错误方向

- 把 LLM-bearing node 视为“先写完传统逻辑，再补一个 prompt”的附属步骤；
- 用通用 `objective`、字符串约定或 adapter alias 让模型猜测它的研究角色；
- 让 parser 和 branch condition 承担开放式证据判断、来源取舍或内容综合；
- 以 prompt catalog、JSON 可 parse 或一次 fake 调用通过，误报节点已经具备 agentic
  能力；
- 为了看起来 agentic，反过来给本应确定性的 lifecycle node 随意加模型。

正确的推进方向是：先明确每一个真实模型 branch 的节点智力是什么，再让确定性代码
负责调度、约束、验证和采纳这份智力。

## 已核实的现状

- 图已有 11 个显式 logical node 和确定性 typed route；拓扑、retry 上限、checkpoint、
  artifact materialization 与 terminal outcome 不应交给模型决定。
- 当前只有 `hitl1`、`topic_planning`、`wave0`、`wave1`、`wave2_synthesis` 和
  `targeted_evidence` 真实调用 `run_agent()`，共 16 个可达 branch。`bootstrap`、
  `hitl2`、`rerun`、`readiness`、`final_delivery` 目前是确定性或 deferred node，不能
  为了“看起来 agentic”而伪造模型角色。
- `NodeExecutionRequest` 当前只有 Objective、Expected output、artifact refs 和工具
  数值；它没有“这是哪个 node agent、该 agent 的方法与权限是什么”的可验证声明。
- 所有 16 条 branch 当前共用同一份 `runtime_policy.md` system policy。它正确表达了
  sandbox、预算、untrusted data 和不可越权的安全护栏，但不表达每个 node 的研究角色。
- `RuntimeNodeAgentBridge.system_prompt` 还能整体替换 system policy；这使 node 能力没有
  一个不可绕开的组合位置。
- 已在进行的 `make-node-prompts-auditable` change 正确暴露了上述事实：catalog 可审计
  最终 prompt，但它的 non-goal 是改变 prompt 语义。它是后续工作的证据基础，不是
  capability 机制本身。

现有 [Node Agent Capability 架构纠偏计划](node-agent-capability-remediation-plan.md)
已经完成了 16 条 branch 的盘点、目标能力地图和测试分层。本计划复用这些事实与目标，
不重新发明 capability 名称；但本轮评审修订其交付边界和证据分母：16 条是最终覆盖，
不是先做 bulk migration、后补行为证据的理由。

## 拟审定的控制模型

| 角色 | 拥有的职责 | 明确不拥有的职责 |
| --- | --- | --- |
| Graph / node handler | 生命周期、状态、route、attempt/retry bound、HITL admission、artifact promotion | 研究判断、来源选择、自然语言理解、内容综合 |
| Node Agent | 一个 capability 内的理解、检索策略、证据判断、受限修复或综合；输出候选结果 | route、gate verdict、checkpoint、用户意图接受、ledger、跨 attempt 状态 |
| Runtime bridge | 已配置模型、实际工具、sandbox 继承、预算、调用、取消和安全失败投影 | 选择 node 认知角色、解释业务语义、替节点决定 retry 或下一 route |
| Parser / evaluator / materializer | schema、provenance、硬约束、artifact 写入和候选结果的采纳 | 以确定性规则假装完成开放式研究判断 |

每次模型调用都应遵守以下四层输入，而不是继续把所有东西塞进一个 `objective` 字符串：

```text
1. Base safety policy       agents/runtime: 不可绕过的安全与隔离规则
2. Capability policy        owning node: 该次认知工作的角色、方法和限制
3. Assignment/output        owning node: 本次可信任务数据、输出契约、工具数值
4. Untrusted evidence       source/user/model draft: 仅供分析，绝不成为指令
```

模型的结果始终是 candidate。只有 node 的既有 parser/evaluator 接受后，graph 才写入
state 或选择 route。这既保持 LLM 的智力位置，也避免回到“模型自我宣布 phase 完成”的
伪 agentic workflow。

### 工具姿态必须落到执行层

capability resource 中的工具姿态只是对 Node Agent 的行为指导，不是权限本身。阶段 2 必须
让同一份已验证声明穿过一条可检查的链：`NodeAgentCapability` ->
`NodeExecutionRequest` 的数值约束 -> 模型实际可见的工具集合 -> runtime bridge 的
middleware / guardrail / sandbox enforcement -> typed candidate result。任何“声明允许”与
“实际可用”不一致、required tool 未满足或禁止工具可见的情况，都应 fail closed，而不能
依赖模型自我约束。

这不是新增第二个 agent loop、tool resolver 或 guardrail。runtime bridge 应接入 DeerFlow
既有的模型、工具和 middleware 执行路径；graph 仍是唯一拥有 checkpoint、route 和候选采纳
权的确定性 owner。

## 最小治理层

不复制参考项目的一整套宪法、Chain/Queue 名词或 Markdown runtime。我们只借鉴其做法：
稳定原则要短、触发条件要明确、policy 不能偷偷变成 runtime authority、行为仍须落到
OpenSpec specification 和 executable evidence。

第一步建议只增加一个 Deep Research charter policy，暂定名
`node-agent-workflow-integrity`。它的触发条件是新增或改变以下任一事项：

- 一个 `run_agent()` branch、node agent prompt、capability resource 或 output parser；
- 工具 posture、模型预算、repair/retry 边界或 node agent 的 artifact 权限；
- 从 deterministic node 启用 LLM，或把模型调用改回 deterministic path。

该 policy 应要求 change author 在 proposal/design 中回答：

1. 这个 node 是 `no-agent` 还是哪一个明确的 Node Agent Capability？
2. LLM 要回答的有界语义问题是什么，哪些输入可信、哪些是不可信数据？
3. LLM 可以怎样使用工具，什么工具姿态由 runtime 强制？
4. 哪个 typed result、parser/evaluator 和 graph owner 决定候选是否被采纳？
5. LLM 明确不能改变哪些 deterministic fact，失败后谁以什么 bound 处理？
6. 最低责任的 deterministic evidence seam 在哪里，哪些质量主张只能由 live/eval
   evidence 支持？

这个 policy 只指导设计和审查。它不创建 node、state、route、writer、retry、permission
或 schema。它会被加入 Agent Charter 的 route table，并在 `openspec/config.yaml` 中作为
LLM-bearing change 的 authoring route；新行为仍必须通过对应的 capability spec/delta。

不在第一步新增第二份“agent workflow handbook”。现有 Agent Charter 已有 local-context、
authority/projections、control/recovery 和 workflow-outcome-review。只有当这个单一 policy
反复无法表达一个真正跨 capability 的问题时，才审查是否需要拆分，而不是预先堆叠文件。

## 配置与权威边界

`config.yaml` 是 DeerFlow 的部署和 operator 配置：模型、端点、可安装工具、sandbox、
token budget 等。它不应成为 node 角色、研究方法、route 或 prompt 语义的第二权威；
这些内容若放入可运行环境任意替换的 YAML，会把产品行为和 operator 环境混在一起。

| Surface | 应拥有 | 不应拥有 |
| --- | --- | --- |
| Root `config.yaml` / profiles | provider、可用工具、宿主 sandbox、全局运行额度 | node identity、研究方法、graph route、用户语义 |
| `openspec/config.yaml` | change authoring 的短路由和 policy admission | 当前 runtime prompt、node 行为或执行权限 |
| Node-local typed declaration | capability ID、owner、resource ref、tool posture、result/evaluator binding | 真实 provider credential 或可变 runtime truth |
| Node-local Markdown resource | reviewed LLM role、method、authority limits、completion/uncertainty | graph state、gate verdict、任意运行时配置 |
| Runtime `ExecutionPolicy` | 实际可提供的工具、路径和预算的 fail-closed enforcement | 代替 node 选择认知语义 |
| Prompt catalog | 从同一 renderer 得出的 review projection | 运行时 authority |

因此不建议新建一个泛用 `agent_policy.yaml` 再把同一规则复制到 Python、Markdown 和
catalog。应使用 node-local typed capability declaration 作为小 interface，renderer、
bridge 和 catalog 共同消费它的已验证结果。

## 实施目标：Node Agent Capability

在治理 policy 审定后，沿用既有 remediation plan 的目标：每一个实际模型调用 branch
成为一个一等的 `NodeAgentCapability`。它的 runtime execution interface 应保持小，只声明：

- stable capability ID、owning node 和 branch；
- node-local trusted capability resource；
- Role、Method、Tool posture、Authority limits、Completion and uncertainty 的 validated resource；
- 动态 assignment / output contract 的构造入口和 typed candidate result contract；
- runtime 必须执行的工具与数值约束。

node-owned governance projection 另行记录 candidate result 的 parser/evaluator/materializer、
repair owner、catalog source/case 和 deterministic evidence seam，用于 admission、审计和测试
寻址。它们不是 capability execution interface，也不进入每次 `NodeExecutionRequest`。
production request 只携带执行本次认知工作所需的稳定 capability reference、可信 assignment、
output contract 和数值执行约束；其余实现细节留在 owning node、renderer 和治理 projection 内。

推荐目录形状如下，具体 field 名称留给 OpenSpec design 决定：

```text
graph/nodes/<node>/
  capabilities.py             # typed declarations, stable IDs, policy refs
  capabilities/<branch>.md    # local cognitive policy
  prompts.py                  # dynamic assignment/output; selects declaration
  node.py / subgraph.py       # orchestration, parser, evaluator, route
```

`agents/` 保持深的 prompt-composition module，负责组合 base safety policy、已验证的
capability policy、assignment 和 untrusted-data envelope；它不再收集所有 node 的认知
文字。`runtime/` 保持唯一 execution adapter，不能接收任意 full-system-prompt override。
这使共享执行仍有 leverage，同时让每个 node 的知识和改动保持 locality。

## 建议的交付顺序

## 执行追踪

- [x] **阶段 0：机制计划审查**。控制模型、权威边界、测试资产分母与 cohort 策略已完成评审。
- [x] **阶段 1：治理-only OpenSpec change**。已由 `define-node-agent-workflow-governance` 完成并归档。
- [x] **阶段 2：能力基础**。已由 `establish-node-agent-capabilities` 及后续纵向 cohort 完成。
- [x] **阶段 3：行为闭环**。已由 HITL1 lifecycle 与两个研究能力 calibration changes 完成。

勾选规则：只有本阶段的退出条件和所有列出的 checklist 均满足时，才勾选阶段；测试数量、
catalog 或单次 demo 不能替代退出条件。

### OpenSpec Change Train

1. **`define-node-agent-workflow-governance`（当前 change）**：只修改
   `deep-research-agent-charter` 的准入机制。它增加 policy、proposal review、checker 和
   deterministic evidence，明确 Node Agent 的 candidate handoff，但不创建任何 runtime
   authority。它校正“节点智力必须被设计”的方向，不能单凭治理文字宣称 DeerFlow 已经
   用好了节点智力。
2. **`establish-node-agent-capabilities`（后续 change，必要时按 cohort 拆分）**：在阶段 1 被接受后，才修改
   `node-agent-runtime`、prompt catalog 和被明确列出的 node owners，建立可执行的
   node-local capability contract 并迁移已盘点的 LLM-bearing branches。这是把上述方向
   变成整个系统实际能力的第一个 runtime change：每个模型分支从通用调用点变成有专属
   认知职责、方法、工具姿态和候选采纳路径的 Node Agent。最终完成条件仍是 16 条全部迁移，
   但实施不得成为一个“先铺 16 份资源、最后统一验收”的 bulk prompt project。
3. **行为闭环 changes（后续）**：human interaction、研究质量和未来 deferred node 的
   LLM admission 分别以自己的 capability delta 和 evidence 处理，不能由阶段 1 的
   governance prose 自动获得实现授权。

### [x] 阶段 0：审查这份机制计划

确认上面的控制模型、权威边界和“不把所有 node 变成 agent”的原则。此阶段不改 runtime，
也不把 `make-node-prompts-auditable` 的剩余验证问题混入 capability 语义改造。

**退出条件：** 审查者能对任一 node 明确判断：它是否是 LLM-bearing、该节点的智力
要完成什么研究工作、结果如何回到确定性流；并认同“补传统控制逻辑”不能替代“定义
节点认知能力”。

### [x] 阶段 1：治理-only OpenSpec change

当前 change：`define-node-agent-workflow-governance`。

- [x] 加入并路由 `node-agent-workflow-integrity` policy；
- [x] 更新 `openspec/config.yaml` 的短 authoring route，而不把它膨胀成项目手册；
- [x] 以现有 16-branch inventory 作为已核实 baseline，登记 no-agent/deferred node 的准入卡；
- [x] 为 policy route 和文档边界添加最小治理测试。
- [x] 完成 focused charter test、direct checker 与 strict OpenSpec validation。
- [x] 完成 OpenSpec task 5.2：`UV_OFFLINE=1 make verify`、完整 deterministic gate、
  `git diff --check` 与工作树/模块边界核验均通过，并记录结果。

**不包含：** 修改 `NodeExecutionRequest`、资源加载、bridge、真实 prompt、HITL 行为或
research output。这一 change 只建立之后每一次实现必须遵守的设计入口。

**阶段 1 验收边界：** change-local charter test、checker 和 strict OpenSpec validation 可以
证明治理准入已实现；它们不能用 1857 个 fast test 或 `make test-assets` 通过替代完整 gate。
归档前 task 5.2 与完整 deterministic gate 已通过；治理 change 的完成不替代后续 runtime
capability 或行为 evidence 的独立验收。

### [x] 阶段 2：能力基础 OpenSpec change

后续 change：`establish-node-agent-capabilities`，由 `agents/` 作为 primary module /
causal owner，`graph`、`runtime`、每个具体 node contract 作为被明确命名的相邻 interface。

**开工门：** 阶段 1 的 task 5.2 和完整 deterministic gate 先变绿；小 execution interface /
node-owned governance projection 的边界被审定；16-branch inventory 与工具姿态重新对照当前
源码；每条 branch 的成功和最高风险 evidence row 已在 change design 中命名。任一项缺失时
不得以“先写 capability type 再补测试”启动实现。

**纵向 cohort：** 第一批只用三组代表性 path 证明共同 kernel：
`hitl1.semantic_intake`（零工具语义理解）、`wave0.authoritative_source_intake`（required tool
与 artifact/ledger 副作用）、`wave2.evidence_synthesis`（无工具、accepted-evidence-only
综合）。每组都必须连同自己的 repair / failure boundary 和真实 renderer/bridge/node journey
验收，再按 zero-tool/repair、retrieval worker、critic/synthesis family 迁移其余 branch。
如果一个 OpenSpec change 无法让每批独立 review、green、stop/rollback，应在实现前拆成多个
顺序 change；不得用“避免 legacy 状态”作为放弃纵向验证的理由。

- [x] 为当前 16 个 branch 建立 local capability declaration、resource 和逐 branch evidence row；
- [x] 让 production `NodeExecutionRequest` 必须带 capability reference，并将静态角色规则
  从 dynamic objective 中分离；
- [x] 由唯一 renderer 组合四层输入，bridge 不再允许任意完整 system prompt 替换；
- [x] 使 tool posture 与 `tools_enabled`、minimum/maximum call、模型实际 tool binding 以及
  runtime middleware / guardrail / sandbox enforcement 可机械对照；不一致、required call
  缺失或禁止工具可见时 fail closed，优先修正已证实的 Wave2 和 targeted critics 工具矛盾；
- [x] 扩展 catalog，显示 capability ID、source path、四层 prompt 组成和 request/runtime
  tool policy 的差异；
- [x] 对缺 capability、缺 local resource、generic fallback、catalog drift、posture 不一致
  建立 deterministic failure；
- [x] 将 6-owner workflow inventory 扩展为 16-branch matrix；每条 branch 至少有一次成功和
  一次最高风险的真实 renderer/bridge/node scripted journey，且 repair、tool call 和禁止效果
  不能由同一个泛化 happy-path selector 代替。

**不包含：** 把 `readiness` 或 `final_delivery` 改成 LLM node、重写 HITL state machine、
或以“prompt 已不同”宣称研究质量已被证明。

### [x] 阶段 3：按行为闭环拆分后续 changes

- [x] 更新或续接 `establish-human-interaction-contract`：用 `hitl1.semantic_intake` 的
   专属 capability 验证“确认”、修改、提问、歧义和 provider failure 的真实 lifecycle；
   模型仍只产生 candidate intent，graph 才能接受它。
- [x] 开启研究能力校准：按 topic planning、Wave0/Wave1、Wave2、targeted critics、repair
   分组建立 scenario/eval evidence，证明方法与限制，而非只验证 JSON 可 parse。
- 未来要为 `readiness` critic 或 `final_delivery` writer 启用模型时，先做独立 capability
  admission，不允许在 `node.py` 直接插入 `run_agent()`。

## 证据与验收

阶段 2 的基础迁移必须至少有五层证据，避免把“文档写得好”误报为 agentic behavior：

| 层 | 证明内容 |
| --- | --- |
| 静态结构 | 每个 production branch 有 capability、local resource、明确 no-agent 例外和合法 tool posture |
| Prompt composition | renderer、bridge、catalog 得到同一 base + capability + assignment + untrusted-data 结构 |
| 执行边界 | declaration、request 与实际 model-visible tool binding 一致；禁用工具的 capability 拿不到工具；required tool 未调用失败；模型无法写 graph/gate/ledger |
| 节点行为 | scripted/fake model 与 recording tool binding 经真实 node seam 后，parser、repair、artifact、route 与禁止效果都符合契约 |
| Branch coverage | 16 条 production branch 都有独立 evidence row；6 个 owner 聚合项、pytest 数量或同 node 的其他 branch 不能代替 |

真正的模型质量、对自然语言“确认”的理解、来源选择和综合质量还需要后续 scenario/eval
或受控 live evidence。确定性 fake 只能证明系统没有阻止正确行为，也不能证明某个模型
永远聪明。

record/replay 可以作为 event/state shape 的回归证据，但不能替代 capability renderer、
tool binding 或研究质量的证据；若为稳定回放而归一化或排除 system prompt，它尤其不能被
当作 node-local policy 的质量评估。

## 风险与取舍

| 风险 | 缓解 |
| --- | --- |
| 复制参考项目，得到不适合 LangGraph 的大型 guideline suite | 只新增一个有触发条件的 policy；不复制其 Markdown/JS runtime 或术语体系 |
| 政策成为一份没有执行力的说明书 | capability spec、typed declaration、renderer、bridge、catalog 和 test 使用同一条引用链 |
| 用 YAML 配置解决语义，形成多份权威 | 保持 operator config 与 reviewed node semantics 分离；不新增 generic prompt config |
| 为了 agentic 给 deterministic node 加模型 | no-agent 是正式分类；新增模型必须经过同一 admission |
| 一次迁移 16 条 branch 变成无验收的 prompt 大项目 | 先用三组代表 path 做纵向 cohort，每批 renderer/bridge/node evidence 变绿再扩；单个 diff 无法独立审查时拆 change |
| LLM 被赋予 graph authority | candidate -> parser/evaluator -> graph route 的闭环写入 policy、types 和 tests |
| 1857 个 fast test 制造“能力已经充分”的错觉 | 发布 evidence snapshot 时同时给出 branch、workflow、live、release 分母；禁止以 pytest 总数作为 agentic 完成指标 |

## 待确认的架构决定

1. 是否接受 DeerFlow 的核心优势是“确定性工作流编排多个受约束的节点智力”，而不是
   “传统程序流程中偶尔调用模型”？
2. 是否接受“确定性图控制整体流程，Node Agent 完成不可替代的 bounded cognitive work”
   的分工，并停止让传统分支承担开放式语义判断？
3. 是否接受一个最小 `node-agent-workflow-integrity` policy 先行，而不是直接复制大量宪法？
4. 是否接受 node-local typed declaration + Markdown resource 为认知语义的主入口，
   root `config.yaml` 仅保留 operator/runtime 配置？
5. 是否接受以纵向 cohort 迁移已盘点的 16 条模型 branch，并用逐 branch evidence matrix
   验收，而不是一次 bulk edit 或用 6-owner inventory、1857 个 fast test 代替；同时保持
   当前 deterministic/deferred node 不变，后续再各自准入？

阶段 1 完成并被接受后，下一步是以
`establish-node-agent-capabilities` 或按上述 cohort 拆出的顺序 OpenSpec changes 推进 runtime
foundation；
在那之前不应修改 runtime、node prompt 语义或现有生命周期行为。
