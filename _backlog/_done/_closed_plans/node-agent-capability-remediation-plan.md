# Node Agent Capability 架构纠偏计划

> 类型：架构修复总计划 / OpenSpec change 前置设计
> 状态：已完成并归档。阶段 A--D 已交付；阶段 E 是独立的未来 deferred-node 准入触发条件，不属于本计划的未完成项
> 优先级：已完成的 P0 架构修复
> 更新：2026-07-28
> 支撑盘点：[现状全量盘点](node-agent-capability-remediation/current-state-inventory.md)、[目标能力映射](node-agent-capability-remediation/target-capability-map.md)、[拟议最终 prompt 组合](node-agent-capability-remediation/proposed-prompt-compositions/)、[逐能力测试设计](node-agent-capability-remediation/node-test-strategy.md)
> 相关计划：[人类交互契约修复计划](human-interaction-remediation-plan.md)

## 一句话结论

Deep Research 目前共享的是一个真正的通用 agent system prompt，而不是只共享
执行护栏。各 node 的角色、研究方法、工具姿态、成功标准与失败处理被散落在
Python 的 `objective` 字符串、注释和默认字段中。于是 graph 虽然有许多 node，
模型实际得到的却是同一个泛化角色。

这份计划要把 **Node Agent Capability（节点 agent 能力）** 建成一等设计对象：
每一个实际调用模型的 node 分支都必须在本 node 包内拥有可读的 Python 声明和
独立 Markdown 能力说明；共享 runtime 只负责安全地执行该能力，不能再替它发明
或覆盖认知角色。

这不是“把 prompt 写得更长”，也不是让每个 node 复制一份 agent loop。它是把
共享的执行机制与各 node 独有的思考工作明确分开。

```text
今天

node Python objective ──> 共享 runtime_policy.md ──> 同一个泛化 phase agent
                         ^
                  角色 / 工具意图 / 方法混在普通消息中

目标

node.py + capabilities.py + capabilities/<branch>.md
                │
                │  NodeAgentCapabilityRef + 动态任务数据
                v
base safety policy + node-local capability policy + output contract
                │
                v
共享 bounded runtime / 模型 / 实际工具 / 预算 / 审计
```

## 当前执行状态

四个 capability cohort 已完成全部十六个 direct branch 的迁移：HITL1 semantic
intake/repair、profile-brief/repair、topic planning plan/repair、Wave0 worker/repair、
Wave1 worker/repair、Wave2 synthesis/repair，以及 targeted worker/repair、SourceDiagnostic
与 ClaimVerifier。它们建立了 local capability resource、closed tool posture、catalog
projection、精确 legacy inventory（现为空）和每 branch 的成功/最高风险证据。

在阶段 E 的下一项 change 创建前：

1. 不把 deferred deterministic node 悄悄标为 agent capability，也不回退已归档 cohort 的已验证边界；
2. 不从 BUG、单条 Objective、catalog diff 或一次 demo 直接开泛化 prompt 修复；
3. 后续 cohort 必须先在本计划中有明确 owner、工具姿态、能力边界和独立 evidence seam；
4. 下一 change 只准入一个有明确认知任务的 deferred node，先定义其 output/admission/failure
   owner 与 independent evidence seam；不得把 readiness 与 final delivery 合并成泛化 writer change。

这是一项设计冻结，不是对既有代码价值的最终裁决。待逐 node 审查结束后，再决定哪些
已有 change 应更新、拆分、撤销、重做或仅保留其可复用证据。

## 为什么这是 P0

本轮真实事故不是孤立的 `确认` 同义词遗漏。用户看到完整 proposal 后自然输入
“确认”，系统把它当 profile 字段，连续失败后终止。这暴露了人类交互能力没有被
明确建模；prompt dump 随后又证明所有 agent-running node 的 system 层完全相同。

更直接的代码证据是：

- `wave2_synthesis` 的任务文字说“没有 web tools”，但请求默认
  `tools_enabled=True`；
- `targeted_evidence` 的 source diagnostic 和 claim verifier 注释为只读、无工具，
  请求同样默认允许工具；
- `hitl1` 的自然语言语义理解虽然已有一个 builder，却仍只是通用 phase agent 的
  一段 user message，没有专属系统级对话能力；
- 当前 `RuntimeNodeAgentBridge.system_prompt` 可以替换整个 system policy，说明
  node capability 甚至没有不可绕开的组合位置。

这些都不是单点 prompt 质量问题，而是“能力没有系统实体”的症状。若不先修正这
一层，继续改 HITL 文案、JSON parser、一个 worker 的 objective 或一条工具默认值，
只会在下一个 node 重演同样的错位。

## 范围与非范围

### 在范围内

- 盘清当前所有实际模型调用分支及其调用者、输入、输出、工具姿态、repair 路径和
  测试证据；
- 定义 node-local capability policy 的目录、引用、加载和审计约定；
- 把共享 base safety policy 与 node-specific cognitive policy 分离；
- 使请求、渲染器、bridge、catalog 与测试都必须携带一个明确 capability；
- 逐项纠正已确认的工具姿态矛盾；
- 为 HITL1 的语义 intake、研究规划、检索、证据判断与综合分别建立可审查能力；
- 让未来启用 agent 的 node 无法悄悄落回 generic prompt。

### 不在范围内

- 不复制 DeerFlow agent loop 到每个 node；模型、sandbox、工具解析、预算、
  middleware、调用和结果投影仍由共享 runtime 拥有；
- 不在本计划中直接决定每条研究 prompt 的最终措辞或声称研究质量已经提升；
- 不把尚未调用模型的 deterministic node 伪装成 agent；它们应被显式记录为
  `no_agent_capability`，未来真的引入模型时再走同一准入；
- 不修改 `backend/` 或 `frontend/`；
- 不把生成的 `agent/node_prompts/` 变成运行时权威；它始终只是源码的审计投影。

## 核心定义

### Node Agent Capability

一个 Node Agent Capability 是“一个 node 在一次 bounded model invocation 中承担的
独立认知工作”，而不是 node 名称、工具列表或一段自由文本。每个能力必须同时有：

1. 稳定 ID：包含 owner node 与 branch，不能有生产默认 generic capability；
2. node-local Python 声明：让调用者明确选择该能力，并构造其动态任务和输出契约；
3. node-local Markdown policy：说明角色、输入解释、方法、工具姿态、权威边界、
   完成条件和不确定性处理；它是最终 system prompt 的能力层来源；
4. 明确的 output/result contract、parser 与 repair owner；
5. 声明的工具姿态：`forbidden`、`optional` 或 `required`，以及可适用的最小/最大
   调用约束；
6. 一条 deterministic catalog case 和最低责任的行为证据。

这六项缺任一项，不能称为已实现的 agent capability。

### 四层输入模型

必须把目前混在 `objective` 中的东西按来源与权威拆开：

| 层 | Owner | 内容 | 是否可被外部数据覆盖 |
| --- | --- | --- | --- |
| Base safety policy | `agents/` + runtime | sandbox、预算、工具只可由 runtime 提供、untrusted data 规则 | 否 |
| Capability policy | owning node | 该 node 的角色、方法、工具姿态、成功/失败标准 | 否 |
| Assignment / output contract | owning node Python | 本次 topic、proposal、gap、schema、已验证任务数据 | 否；但可包含明确标记的外部字段 |
| Evidence / raw reply / draft | source artifact 或用户输入 | 要分析的外部内容 | 必须被明确 delimit 为 untrusted |

runtime 仍拥有实际可用的工具、模型、预算和 host/sandbox 事实。Capability policy
只能声明策略，不能虚构或枚举当前机器配置出的工具名称。

## 目标结构（待 OpenSpec 设计确认）

对于一个确实调用模型的 node，目标是让源码树本身说明它正在做什么：

```text
graph/nodes/wave0/
  node.py                    # phase 编排、结果处理、route
  capabilities.py            # WAVE0_SOURCE_INTAKE / WAVE0_OUTPUT_REPAIR 的稳定声明
  prompts.py                 # WorkSpec -> 动态 assignment / output contract
  capabilities/
    source-intake.md         # source-intake 的完整 trusted capability policy
    output-repair.md         # repair 的完整 trusted capability policy
  contracts.py               # node 的可验证输入/输出语义
```

不是每个文件都要机械存在：没有模型调用的 node 不需要 `capabilities/`；有多个认知
branch 的 node 必须有多个 Markdown 文件。关键是读者能顺着下面这条链直接找到能力：

```text
node.py -> build_*_request() -> local capability constant -> local Markdown policy
       -> shared renderer -> RuntimeNodeAgentBridge
```

`agents/` 应只拥有深的 **prompt composition module**：以一个小 interface 把 base
safety policy、已验证 capability reference、assignment 和 output contract 组合成最终
消息。它不再拥有所有 node 的认知文字。`runtime/` 是该 module 的执行 adapter，不能
选择或替换 capability 语义。这个划分保留共享执行的 leverage，同时让知识与改动在
owning node 有 locality。

## 与现有工作关系

| 现有工作 | 这份计划的判断 | 后续处置 |
| --- | --- | --- |
| `make-node-prompts-auditable` | 它正确地暴露了事实，但其明确 non-goal 是不改变 prompt semantics。 | 作为证据和 catalog 基础完成；不要悄悄扩 scope 成能力架构重写。新 capability work 必须令 catalog 展示 base 与 node policy 的真实组合。 |
| `establish-human-interaction-contract` | 它对人类 intent / graph admission 的方向正确，但 semantic intake 仍运行在 generic capability 上。 | 暂停扩展 adapter 层；基础 capability contract 完成后，更新该 change 的设计/tasks，使 HITL1 使用自己的 local semantic-intake policy 与相应 evidence。 |
| `human-interaction-remediation-plan` | 它回答“人能如何表达、谁准入”。 | 本计划回答“哪个 agent 如何理解”。两者必须在 HITL1 交汇，但不能相互替代。 |

## 工作阶段与建议 Change 边界

以下是建议的最小依赖序列，不是现在已批准的 change 数量。每个阶段完成后都应重新
审查是否需要拆分，而不是为了计划而强行创建所有 change。

### 阶段 A：能力盘点与架构决定（已完成）

- [x] A.1 固化本子目录中的全量 invocation inventory、target capability map、逐 node
  拟议最终 prompt 组合与逐能力测试设计；任何新增模型调用先补入这四项。
- [x] A.2 审定上面的能力定义、目录约定、static/dynamic 数据分层和 deterministic-node
  例外。
- [x] A.3 决定 capability reference 的最小 interface：它必须是必填、稳定、可验证的，
  但不能把任意 system prompt 文本开放给 runtime caller。
- [x] A.4 决定本地 Markdown 是用约定资源路径解析，还是经受限 manifest 解析；两种方案都
  必须不依赖 `agents -> graph` 的 Python import cycle，也必须让 node-locality 可见。
- [x] A.5 为每条目标能力写出最小行为 scenario，尤其是自然确认、无工具 synthesis、只读
  critic、检索 worker 和 repair。
- [x] A.6 复审阶段 A 的未知项和证据，确认可以创建或修订阶段 B 的 change 边界。
- [x] A-exit 每个当前 agent branch 都有“当前状态”“目标能力”“最终 system + human prompt
  形状”和“fake/bridge/node 测试思路”；任何未知项被标成明确设计问题而非默认沿用；没有人
  再需要从长 objective 字符串推测该 agent 的职责。

### 阶段 B：Change 1：建立 node agent capability contract（首个 cohort 已完成）

建议 change 名：`establish-node-agent-capabilities`。

当前的 `establish-node-agent-capabilities` 已收敛为首个垂直 cohort：迁移六个直接 catalog
branch，并将其余十个明确保持为封闭 `legacy` 集合。全部 16 个 branch 的迁移仍是本计划的
总体目标，但必须在该 cohort 完成后按顺序重新审查和拆分，不能错误计入本 change。

- [x] B.1 新建 capability reference / declaration contract；生产
  `NodeExecutionRequest` 不再允许没有 capability 的 generic request，过渡期仅允许封闭
  `legacy` 集合无 reference。
- [x] B.2 在 `hitl1`、`wave0` 和 `wave2-synthesis` 建立 node-local capability Python +
  Markdown 资产，迁移六个首批 direct branch；其余十个 branch 保持显式 `legacy`，不推断
  generic capability。
- [x] B.3 让 renderer 组合 `base safety + local capability + dynamic assignment`；删除或
  严格封死 bridge 的任意完整 `system_prompt` 替换入口。
- [x] B.4 将工具 posture 变为 capability contract 的可验证部分，纠正当前已确认的不一致。
- [x] B.5 升级 prompt catalog：显示 capability ID、node-local source、base safety、node
  capability、assignment、output contract 和 request/runtime tool-policy 区别。
- [x] B.6 添加机械防线：builder 的 capability binding、policy asset、封闭 legacy
  inventory、catalog 一致性和 posture/request 矛盾均可确定性验证。
- [x] B.7 为六个迁移 branch 建立每 branch 的成功与最高风险行为证据；不得用聚合 pytest
  数量或其他 branch 的证据代替。
- [x] B.8 复审剩余十个 legacy branch 的风险、证据边界和合理分组，再决定后续 cohort，
  不自动扩大本 change。
  - 已决定：下一 cohort 只覆盖同一 HITL1 family 的 `profile-brief` 与
    `profile-brief-repair`；topic planning、targeted evidence 与 Wave1 保持 legacy。
- [x] B-exit 六个首批 branch 的 capability admission、组合边界、工具 posture、catalog 和
  branch-by-behavior-by-authenticity evidence 全部通过；十个 legacy branch 保持封闭且不带
  inferred capability；人类 state/adapter 行为未被本阶段改变。

**不应塞入此 change：** 真正的 report writer/readiness critic agent、HITL state
transition、adapter UI overhaul、或“调到研究结果很好”的开放式 prompt tuning。

### 阶段 C：建议 Change 2：完成 HITL1 profile-brief capability family（migration 已完成，lifecycle evidence 待 follow-up）

建议 change 名：`migrate-hitl1-profile-brief-capabilities`。这是已归档
`establish-human-interaction-contract` 的聚焦 follow-up，而不是重开 interaction
state/adapter 设计。

- [x] C.1 `hitl1/semantic-intake` 与 repair 已在阶段 B 获得专属 capability policy。
- [x] C.2 迁移 `hitl1/profile-brief` 与 `hitl1/profile-brief-repair`；保持零工具和 advisory
  profile 边界，并在初次 proposal 与 malformed-output repair/exhaustion seam 证明它们。
- [x] C.3 保留已经设计正确的“语义解释只产生候选 intent，graph 才准入”的 authority seam。
- [x] C.4 对现场 `确认`、带一手资料/引用限制的修改、提问、歧义、模型失败后的 fallback
  做真实 lifecycle transcript。
- [x] C.5 验证用户收到的是听懂后的简短反馈或聚焦澄清，而不是 schema/JSON 教学。
- [x] C-exit HITL1 的 profile-brief 与 semantic-intake capability family 在真实 lifecycle
  中共同受审查；模型仍没有 graph admission authority，且未迁移 branch 保持 explicit legacy。

> 原阶段 C 的 broader human-interaction UX transcripts 保留为 profile-brief cohort 的
> lifecycle acceptance evidence，不授权改变 graph transition、adapter 或 public interface。

**阶段 C follow-up 建议边界：** 建议 change 名
`harden-hitl1-profile-interaction-lifecycle`。它只为 C.4/C.5 增加真实
confirmation、带来源/引用约束的 revision、question、ambiguity 与 model-failure fallback
的 scripted lifecycle evidence，并在现有确定性 owner 不满足这些 acceptance contract
时做最小修复；不迁移其余八个 legacy branch，不改 graph transition、adapter、public
interface 或研究质量语义。完成 C-exit 后，才按 D.7 重新审查 research calibration 的拆分。

阶段 B 保证它有真正的“理解人类 proposal interaction”的 agent；阶段 C 才验证这个
能力与 human interaction contract 一起交付可用 UX。

### 阶段 D：研究能力的行为校准与评估（已拆分为两个连续 Change）

阶段 D.7 已审查并决定拆分。单一 change 会同时改变三种工具 posture（zero-tool、
bounded retrieval、read-only critic）、12 个 direct branch 和两条实际图闭环；失败或证据
不足时无法把责任收敛到 research intake 或 evidence evaluation。因此两个 change 按生产
闭环切分，repair 始终跟随它修复的 producer，而不是按测试目录或 prompt 文件归类。

**Change 3：`calibrate-planning-and-intake-capabilities`（已完成并归档）**

- 覆盖 `topic_planning/{plan,plan-repair}`、`wave0/{worker,repair}` 与
  `wave1/{worker,repair}`，即确认 profile 后的 topic decomposition、baseline source intake
  与 Wave1 evidence expansion。
- 迁移仍为 legacy 的 topic-planning 与 Wave1 branch；Wave0 保留既有 capability binding，
  只补其 source strategy、tool-call、independence 与 honest-degradation 的行为 evidence。
- 验收 coverage/non-overlap/profile constraints、Wave0 1--3 次 retrieval、Wave1 恰好一次
  新来源检索、repair 不补造事实/来源/claim/question，以及 deterministic admission、ledger/
  artifact 边界。
- 不包含 Wave2 synthesis、targeted gap loop、source diagnostic、claim verifier、graph
  topology/public interface 或 live research-quality 宣称。

**Change 4：`calibrate-synthesis-and-evidence-review-capabilities`（已完成并归档）**

- 覆盖 `wave2_synthesis/{synthesis,repair}` 与
  `targeted_evidence/{worker,repair,source-diagnostic,claim-verifier}`，即 accepted-evidence
  synthesis、gap-driven targeted retrieval 与 read-only evidence judgment。
- 迁移仍为 legacy 的四个 targeted-evidence branch；Wave2 保留既有 zero-tool capability
  binding，补证据约束、gap honesty 和 repair 的行为 evidence。
- 验收 synthesis 只能使用 assigned accepted evidence、gap 才能授权一次 targeted search、
  critic 只能引用 assigned refs 且无工具、repair 不扩展 evidence/claim/gap authority。
- 不回改 Change 3 已验收的 planner/Wave0/Wave1 行为，也不改变 graph admission 或 public
  interface。

两个 change 共同完成阶段 D；第一个只建立研究启动链的独立 acceptance evidence，不能代表
后一个 evidence-evaluation 闭环已经通过。

- [x] Change 3 已完成并归档：`calibrate-planning-and-intake-capabilities`
  （`2026-07-28-calibrate-planning-and-intake-capabilities`）。
- [x] Change 4 已完成并归档：
  `2026-07-28-calibrate-synthesis-and-evidence-review-capabilities`；Wave2 与 targeted
  evidence 闭环的 capability、行为 evidence、catalog 和 strict verification 已完成。

它按目标能力映射逐组定义实际质量与边界证据：

- [x] D.1 为 topic planning 定义覆盖、互斥和 profile 约束遵循的 evidence。
- [x] D.2 为 Wave0/Wave1/targeted intake 定义来源策略、工具调用、独立性和诚实退化的
  evidence。
- [x] D.3 为 critics 定义只读、证据归因和无越权工具的 evidence。
- [x] D.4 为 Wave2 定义仅基于给定 evidence 综合、显式报告缺口而非编造的 evidence。
- [x] D.5 为 repairs 定义只修结构、不补造事实或来源的 evidence。
- [x] D.6 用 scripted model/tool transcript、artifact fixture 和必要的评估集实施这些
  evidence；不得用 prompt 文本或一次 live demo 宣称完成。
- [x] D.7 按评估边界和风险复审并拆为两个 change：
  `calibrate-planning-and-intake-capabilities`（topic planning、Wave0、Wave1）和
  `calibrate-synthesis-and-evidence-review-capabilities`（Wave2、targeted evidence、critics）；
  repair 跟随所属 producer，两个闭环分别验收。
- [x] D-exit 每个研究能力组都有可重复、可审查的质量与边界 evidence，而非仅有结构或
  parse 测试。

### 后续触发条件：未来 agent 启用的准入（不属于本计划完成范围）

`readiness` critic 与 `final_delivery` writer 当前明确是 deterministic fallback /
deferred agent。未来启用它们时：

- 未来 E.1：为候选 agent 完成能力盘点行和 node-local policy。
- 未来 E.2：定义工具 posture、结果契约和 failure table。
- 未来 E.3：添加 catalog case 和 eval evidence，并以独立 change 审查准入。
- 未来 E-exit：不在原 node 中直接增加 `run_agent()`；每个新 agent 都先满足与现有 capability
  相同的准入规则。

**下一项建议 Change：先探索单一 readiness decision capability 的必要性。** 只有当
`readiness` 需要在现有确定性规则不能表达的证据权衡中产生候选判断时，才应提出一个
只覆盖该 node 的 admission change；它必须保持 gate/route/terminal authority 在 graph，
且与 `final_delivery` writer 分开审查。若没有该明确认知问题，阶段 E 保持 deferred，
不为完成计划而新增 agent。

## 已通过实现回答的设计问题（历史记录）

1. Capability policy resource 的可验证引用如何表示，才能同时保持 node-locality、避免
   任意 system prompt 注入，并不产生 Python import cycle？
2. `NodeExecutionRequest` 应怎样把 static capability、dynamic assignment、output
   contract 和 untrusted evidence 区分，才能避免下一次又把角色规则塞进 `objective`？
3. capability 的工具 posture 如何与 runtime 实际可用工具、minimum/maximum call
   requirement 组合，既不虚构配置也不允许“声明无工具却拿到工具”？
4. repair 是 owner node 下的独立 capability，还是同一 capability 的 repair mode？
   当前计划的保守默认是独立 Markdown branch，因为其认知工作与权限都不同。
5. 如何定义“能力不同”的测试？不能只比较 Markdown 字节不同；至少要检查每份 policy
   都有角色、方法、工具姿态、权威边界、完成条件与失败处理，且每条行为 scenario 走
   真实 bridge/request seam。
6. 现有 `agents/` 的 ownership rule 要怎样修改为“组合机制在 agents，认知 policy 在
   owning node”，才能让后续 coding agent 不再按旧规则把所有 prompt 收回集中目录？

## 总验收标准

只有同时满足下列条件，才能说这轮架构纠偏完成：

1. 从任意实际 `run_agent` 调用，读者可在一个小跳转链内找到其 node-local Python 声明
   和 Markdown 能力说明；
2. 最终系统消息明确由 base safety policy 与该 local capability policy 组成，不能被
   generic default 或 bridge override 悄悄替换；
3. 所有当前 16 个 branch 都有显式 capability，新增 branch 在缺失该项时 deterministic
   failure；
4. capability 声明、request tool policy、runtime enforcement 和 dump 中的展示一致；
5. generated catalog 能让审查者看见真正不同的能力层，而不是 16 份相同 system policy；
6. HITL1 的自然语言 confirmation/revision/question/clarification 在真实 lifecycle 上
   可用，且没有给模型 graph authority；
7. research workers、critics、synthesis 与 repairs 各有能证明其方法与限制的 deterministic
   evidence，不是只验证 JSON 能 parse；
8. deferred deterministic node 没有被伪造为 agent；新 agent 加入受同一准入规则约束；
9. OpenSpec specs、项目结构规则、catalog、tests 和 operator docs 共同表达这套模型，
   不只靠一次人的记忆。

## 风险与取舍

| 风险 | 缓解 |
| --- | --- |
| 把 16 个分支一次性重写成巨型 prompt project | 先以 capability contract 拆静态与动态层，再分 HITL UX 与研究质量两个 evidence change。 |
| local Markdown 使 runtime 形成 graph import cycle | 用纯 resource reference / resolver seam；runtime 只消费已验证 reference，不 import node Python。 |
| 每个 node 复制 agent factory 与安全逻辑 | 明确共享 runtime 是唯一 execution adapter；locality 只用于 cognitive policy 和任务构造。 |
| 为了“每个 node 有 prompt”给 deterministic node 加无用模型调用 | inventory 公开标注 no-agent 节点；未来启用时才建 capability。 |
| capability Markdown 变成不被执行的说明书 | renderer、bridge、catalog 使用同一解析结果；测试捕获最终 system policy。 |
| 改善了结构却没有改善用户体验或研究质量 | 后续 change 必须有真实 HITL lifecycle transcript 和各能力行为 eval；结构迁移本身不能宣称产品修复。 |

## 本计划的下一步

阶段 C 已由 `harden-hitl1-profile-interaction-lifecycle` 完成：真实 lifecycle acceptance
保留 graph-owned admission，且 deterministic presentation/fallback 不教授 schema、JSON 或
隐藏 action token。阶段 D 的 `calibrate-planning-and-intake-capabilities` 已完成并归档，
建立了 planner/Wave0/Wave1 的行为 acceptance；
`calibrate-synthesis-and-evidence-review-capabilities` 也已完成并归档，建立了 Wave2/
targeted evidence 闭环的行为 acceptance。下一步仅在明确存在 deterministic owner 无法表达的
bounded cognition 时，为一个 deferred node 提出独立 change；不要直接从 BUG、单条 objective、
catalog diff 或一次 demo 开泛化 prompt 修复。
