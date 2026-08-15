# 00 - Policy Gate Injection Layer 原案、审查与架构建议

> 性质: 详细审查依据 | 当前进度 authority: [`../policy-gate-injection-layer.md`](../policy-gate-injection-layer.md)
>
> 本文从主计划迁入以保留原案、审查台账、证据边界和经审查后的建议。它保留形成过程中的历史措辞；
> Change 状态、当前动作和已确认的 Change 3 contract 以主计划为准。

## 阅读说明

这不是一份把原案“改写成答案”的结论稿。它保留三个彼此独立、可追溯的层次，供作者和
reviewer 分别审查：

1. **原案快照**保留提出此 change 时的动机、类比、假设、方案与影响范围；其中的断言是
   作者的输入，不能因后续 review 而被抹掉。
2. **审查台账**逐项记录我核查了什么、怀疑什么、证据能支持到哪里，以及是保留、缩小、
   改写还是排除。未决项明确列为假设，而不是悄悄变成结论。
3. **经审查后的建议**只是在原案和台账基础上给出的 v1 推荐方向；它不覆盖原案，也不把
   设计 policy 伪装成已存在的 runtime contract。

配套的逐卡 bug 证据与外部 session-drift 方案审查位于
[`README.md`](README.md)。主文保留决策与
摘要；配套目录保留能够推翻或限定这些决策的长证据链。

建议 review 顺序：先读 Part I 判断原问题是否值得解决，再读 Part II 复核每个判断是否成立，
最后才评估 Part III 的推荐是否是最小且可验证的回应。

> **路线图检查点（2026-08-02）**
>
> - **Change 1 / V1**：`add-openspec-control-placement-policy` 的 `18/18` 实现任务和最终验证均已完成，
>   已归档到 `2026-08-02-add-openspec-control-placement-policy`，并提交为 `8d8a5f5`。它只创建外置
>   `control-placement` policy、其 proposal record、短路由与机械 shape check；不改变 DeerFlow runtime，
>   也不创建跨 session runner。
> - **Change 2**：`add-openspec-operation-guidance` 的 `20/20` 任务已完成，归档到
>   `2026-08-02-add-openspec-operation-guidance`，并提交为 `ba122b8`。它交付 `rules.tasks` obligation、
>   `operations.apply/archive.guidance`、六项本地 integration probe、`DRC-010` 注册/主规范同步/证据登记。
>   guidance 始终是 advisory，不能执行命令或阻止 apply/archive；probe 保留 selected-change `missing-boundary`、
>   replay `unclosed`，以及全量门禁中三个 boundary-external integration failures，均不得误报为 semantic-review
>   gate 或现有 coordinator。
> - **Change 3**：`add-cross-session-cognitive-guardrails` 尚未提案、尚未实现，但 proposal contract 已经完成
>   文档级 grill。closeout 只能消费调用方显式声明、由 Git 验证的已提交 `base..head` boundary；缺失或失效时
>   只记录 `missing-boundary`，不声称审查覆盖或 semantic clearance，也不触碰 task/archive。未来 coordinator
>   不拥有 native archive 的阻断或替代权。现在可以基于该窄 contract 提案，不能把 advisory guidance 冒充为
>   runner、checker 或 archive authority。
> - 两个 2026-08-02 repair archive 是 V1 的历史回放证据：
>   `fix-topic-planning-provider-outcomes` 与
>   `harden-hitl1-comparison-intake`。它们说明 policy 的适用性，不证明 policy 已经阻止这些
>   bug，也不把 credentialed live replay 的未完成状态伪装成成功。
> - **Change 1 implementation record**：外置 policy、Charter/config 路由、统一的 `Triggered review
>   policies` 字段、结构化 checker、`DRC-009` registry/structure/evidence registration，以及本 V1
>   proposal 归档前的原子迁移均已完成。focused contract、治理/evidence checks、离线 `make verify`、
>   strict OpenSpec validation 与 diff check 均已通过。两个 archive 保持未修改，仅作为有界 replay 输入。
> - **Change 1 closeout**：已完成；没有待做的 V1 实现、验证、归档或提交任务。

## 已确认的三个 OpenSpec Change

“V2”不再作为计划或提案的 canonical 名称，以免把两个不同的可归档交付物混在一起。后续只使用下表的
change name 与序号：每个 change 必须在自己的 OpenSpec proposal、design、specs、tasks、验证、归档和提交
完成后，才进入下一个 change。

| 顺序 | Canonical change | 独立完成边界 | 当前状态 | 下一项的硬依赖 |
|---|---|---|---|---|
| 1 | `add-openspec-control-placement-policy` | 外置 policy、Focus Card record、机械 checker 与证据登记；不创建 runtime 或 guardrail | 已归档并提交 `8d8a5f5` | 已满足 |
| 2 | `add-openspec-operation-guidance` | 仅当 proposal 选择 `control-placement` 时的 `rules.tasks` obligation、apply/archive advisory guidance，以及六项本地 delivery/adapter/side-effect/diff/replay probe 的可复现证据；不创建 `openspec/guardrails/` | 已归档并提交 `ba122b8`（20/20） | 已满足 |
| 3 | `add-cross-session-cognitive-guardrails` | 基于调用方声明、Git 验证的 committed `base..head` boundary，建立有界的 impact/review evidence 与非权威 closeout record；缺失边界只记录 `missing-boundary`，不改变 runtime 或 native archive authority，也不让模型自我批准 | proposal-ready，尚未提案或实现 | Change 2 已归档；遵守下方已确认 proposal contract，且不得把 advisory guidance 当作现有 coordinator 或 diff-boundary proof |

拆分的特别理由是证据依赖，而不是把一个目标拆成更多 ceremony：Change 2 必须先验证 OpenSpec 的实际
delivery、archive 副作用与 selected-change 边界；这些结果决定 Change 3 的 coordinator 接口和可接受
failure mode。probe 已明确 `missing-boundary`，所以先重设 Change 3 的边界来源与 fail/stop posture，不能把
未证实的接口带进 Change 3。

**已确认的 Change 2 决定**：Change 2 是可独立归档的持久交付物。它永久写入简短的
`rules.tasks`、`operations.apply.guidance` 与 `operations.archive.guidance`，并以六项本地 probe 证明
OpenSpec/Codex 对 guidance 的 delivery 边界；它不只是用于决定 Change 3 的一次性 spike，也不创建
`openspec/guardrails/` 或 closeout coordinator。只有选择 `control-placement` 的 proposal 需要在
`tasks.md` 保留跨 session 的 plan-review 与 archive-closeout-review obligation；其它 charter policy
本身不触发该 obligation。Change 2 不新增 checker、不自动写 task，也不因 obligation 缺失阻止 native
archive；它只推送 review posture。selected diff、未完成 finding 与 deterministic verdict 的机械 closeout
仍由 Change 3 的 coordinator 负责。

**Change 2 implementation/probe record（2026-08-02）**：`add-openspec-operation-guidance` 的 authoring
route、focused contracts、`DRC-010` registry/main-spec/structure/evidence metadata 与六项 probe 均已实施，并归档到
`openspec/changes/archive/2026-08-02-add-openspec-operation-guidance/`、提交为 `ba122b8`。`05-operation-guidance-probe-evidence.md`
记录 installed CLI delivery、native archive side effects、selected-change `missing-boundary` 与 ordinary finding 的
resumed-apply `unclosed` replay；没有 guardrail directory、task writer、semantic evaluator、archive wrapper 或
fresh-session claim。归档时主规范已经同步，因此原生 archive 默认重复合并被拒绝；使用原生 `--skip-specs` 后完成
移动，未跳过 validation。focused/governance evidence 均通过；全量 deterministic gate 的三个 runtime/integration
baseline failures 已在 archived task ledger 中如实记录，未由本治理边界修复。Change 3 继续 deferred，直到另一个
proposal 根据这些 observed limits 定义自己的 contract；本状态本身不创建 `openspec/guardrails/`。

### Change 3 Proposal-Contract Reset Gate（2026-08-02）

**当前结论：proposal contract 已确认，可以提案；仍不能在 proposal 之外开始实现。** Change 2 提供的不是
coordinator 的预先实现许可，而是以下不可替代的输入事实：

1. `operations.apply/archive.guidance` 是一般 advisory text；它不写 task、不完成 task、不验证语义质量，
   也不拥有 archive transition。
2. OpenSpec instruction contract 未提供可靠 selected-change code-diff boundary；广泛扫描 worktree 会过度声称
   review coverage，因此观察结果为 `missing-boundary`。
3. replay 仅证明普通 unchecked finding 能跨 resumed apply 保留；它没有证明 fresh-session identity、semantic
   evaluator 或 finding 已闭合。
4. Change 2 的确定性 governance/focused evidence 通过；完整 deterministic gate 的三个 runtime/integration
   baseline failures 属于本 change 之外，不能被 guardrail proposal 伪装为已通过的 release evidence。

**已确认的 proposal contract（文档级 grill）：**

1. **boundary posture**：任何 closeout coverage claim 都需要可靠的 selected-change boundary。边界缺失时，
   只能产生 `missing-boundary` 记录；不得声称已审查代码、给出 semantic clearance，或影响 task/archive。
2. **事实 owner**：调用 closeout 的人或适配器显式提供 boundary fact；Git 是 commit identity、ancestor
   relation 与 diff 的事实来源；coordinator 只验证并记录，绝不从共享 worktree、路径名单或分支名推断归属。
3. **selected-change binding**：attestation 必须同时含 canonical `change_name`、repository identity、
   `base_commit`、`head_commit`，并声明范围语义为 `base..head`。coordinator 机械验证仓库匹配和祖先关系，
   其 coverage claim 只能精确指向该已声明 range。
4. **最小确定性证明**：只接受 committed range，且执行时 `HEAD == head`、worktree clean。测试须覆盖一个
   valid range 及缺字段、错误仓库、非祖先、`HEAD` 漂移、dirty worktree 等拒绝路径。成功记录 commits 与
   diff 摘要，不生成 semantic pass；失败不写 task、不运行 archive。
5. **authority boundary**：Change 3 不包装、替代或阻止 native archive。它至多输出可审计的
   `review-required` / `inconclusive` evidence record；真实 finding 仍须是普通 `tasks.md` 未完成 task。
   在存在不可绕过的 admission attach point 及其证据前，不能把任何 outcome 写成 hard archive gate。

这些决定解除的是**提案**前置条件，不是对完整 guardrail 设计的预批准。proposal 必须把它们转成可测试的
requirement、明确支持的调用方式及其不支持的情形；在 proposal 获批前，不创建 `openspec/guardrails/`，不假设
dossier、fresh-session challenger、task writer 或 blocking coordinator 已经存在，也不让 advisory guidance 代替
这些能力。

## Part I：原案快照（保留为审查输入，不等于已采纳结论）

> 原始标题：`Plan: Policy Injection Layer for Deep Research Change Governance`
> 来源：本文件在本次 review 前的 Git `HEAD` 版本。正文按原案保留，仅把 Markdown 标题下调一层
> 以嵌入本审查文档。特别是“2000+ regression”“PPT Maker 可直接借鉴”“prompt 拥有判断”等
> 说法均是需要审查的主张，**不是本文件认可的既定事实**。

### 问题：为什么会有 2000+ regression？

DeerFlow Deep Research 的 regression 一直在涨。我的判断是根因不在单个 bug，而在**设计阶段的决策惯性**：
团队一碰到问题就改传统代码（LangGraph flow、gate engine、runtime adapter、checkpoint plumbing），
而不是先问："这段逻辑应该放在 prompt/MD 里，还是放在 graph handler 代码里？"

Node agent 的 prompt 层才是真正做认知判断、语义解释、创意合成的地方。但当前没有任何机制在设计阶段
强制人去想这件事。Charter 里的 policy 写了一堆，但 `config.yaml` 的 rules 没有把它们变成 proposal
必须过的检查点。Policy 是参考读物，不是强制入口。

### 借鉴对象：PPT Maker 的 OpenSpec 怎么做

`/Users/bowhead/ai_tool_ppt_maker/openspec/` 这个项目很有意思——它的 controller 是 MD，传统程序 (JS/CLI)
是 gate。和 DeerFlow 刚好反着（DeerFlow 是 flow+gate 做传统程序，MD 只是治理层），但它的 **policy
注入机制** 完全可以直接借鉴。

#### 三层自强化架构

**第一层：`config.yaml` 作为中央宪法**

一打开就声明 ownership matrix：

| 控制面 | 所有权 |
|--------|--------|
| Python control / Agent | 流程、节点、依赖、路径选择、创意判断与用户交互 |
| JS / CLI | 解析、校验、自愈、状态、证据、产物转换和结构化诊断 |
| 人类 | 隐喻、主张、案例可信度、视觉与最终内容判断 |

然后是大段的 `rules:` —— proposal、specs、design、tasks 各自要遵守什么规则。
**关键**：这些规则不是建议，是强制引用具体 policy 的要求。

**第二层：三个跨切面 Policy**

1. **`human-centered-gates.md`** — 把每个质量/流程边界分类为 `guide`（可自动修复）、
   `confirm`（需要人类给出 bounded reason）、`hard-stop`（不可绕过的 invariant）。
   定义 continuation 为 auditable version-scoped waiver（不是 approval）。

2. **`agent-assistance-and-control.md`** — 管责任移交：哪个 source 拥有事实、哪个 evaluator
   做检查、diagnostic 报什么、recovery 怎么走。防止创建 "第二 authority"。

3. **`simple-reliable-control.md`** — 核心原则：**Quality control SHALL be simpler than
   the work it validates.** 加任何 blocking rule 之前必须说明删掉了什么复杂度，否则降级为
   advisory 或缩 scope。

**第三层：Specs 作为 Capability Contract**

每个 `specs/<capability>/spec.md` 定义可测试的 requirement + scenario，显式区分 MD 责任 vs
JS 责任。Gate-sensitive 的 requirement 必须分类为 guide/confirm/hard-stop。

#### 注入怎么生效的

`config.yaml` 的 proposal rules 里写死了：

> "涉及 gate、readiness、validation、diagnostic 或 override 时，必须引用
> `openspec/policies/human-centered-gates.md`，说明 guide/confirm/hard-stop 结果"

> "涉及 controller handoff、Agent 自动执行、state/recovery 时，必须引用
> `openspec/policies/agent-assistance-and-control.md`"

> "涉及任何新的或修改后的质量控制路径时，必须引用
> `openspec/policies/simple-reliable-control.md`"

不是"建议参考"——是"必须引用并说明"。这就是注入机制。

### DeerFlow 已有的基础（不需要推倒重来）

DeerFlow 其实已经有不少原材料，只是没串起来：

1. **显式的 ownership layer**：`runtime`, `domain`, `engine`, `agents`, `graph` 在
   `project-structure.toml` 里已经定义好了，每个有自己的职责。

2. **运行时的 failure 分类**：`domain/failure_codes.py` 已经把 failure 分为 `hard`、
   `semantic`、`degradable`、`repairable`、`system`。`engine/gate_kernel.py` 产出
   `PhaseVerdict`（PASS, REPAIR, BLOCKED, NEEDS_HUMAN）。这些和 guide/confirm/hard-stop
   是自然对应的。

3. **Node-agent 分类已经存在**：`node-agent-workflow-integrity.md` 已经要求每个 LLM-bearing
   node surface 回答 bounded cognitive question、tool posture、candidate admission owner、
   failure owner and bound。

4. **Prompt 可审计**：`graph/prompt_catalog.py` 和 `node_prompts/` 提供了确定性的 prompt
   fixture，不用跑模型就能 review prompt 内容。

5. **Focus Card 已经存在**：每个 proposal 必须写 primary module、question、adjacent contracts、
   evidence seam、not-in-scope、triggered policies。这是注入新规则的完美入口。

#### 缺了什么

- **没有** gate 分类词汇（guide/confirm/hard-stop）在设计阶段强制执行
- **没有** 规则说"碰到 gate 必须分类"
- **没有** 规则说"碰到 prompt vs code 边界必须说明 ownership"
- **没有** 规则说"加质量检查必须说明净简化"
- **没有** 显式的 ownership matrix 让人一眼看到 prompt 管什么、code 管什么

Charter policy 是参考读物。`config.yaml` rules 没有把它们串成必过的检查点。

### 方案：三个新 Policy + config.yaml 注入

不做大重构。在现有的 charter 框架里加三个 policy，然后改 `config.yaml` rules 让它们被强制引用。

#### Policy 1: Gate Classification（gate-classification.md）

从 PPT maker 的 `human-centered-gates.md` 改编。引入设计阶段的 gate 分类词汇，
与运行时的 `failure_codes.py` 分类是两层不同的东西：

| Gate posture | 什么时候用 | 映射到运行时 | DeerFlow 例子 |
|---|---|---|---|
| `guide` | 确定性修复，不需要人类接受风险 | PASS / repairable, degradable | schema 校验错误自动重试；content hash mismatch 在 budget 内重取 |
| `confirm` | 可逆的质量/流程风险属于人类 | NEEDS_HUMAN / semantic | 证据不够，人类判断 "够不够好"；话题覆盖缺口，人类决定 scope trade-off |
| `hard-stop` | identity、integrity、security、authorization、recoverability 不确定 | BLOCKED / hard | research identity mismatch；missing work spec；cancelled work；fatigue escalation；unauthorized state mutation |

核心概念：
- **Continuation**：auditable version-scoped waiver，带 normalized human reason。不是 approval。
  映射到 DeerFlow 的 HITL1/HITL2 semantic-intake flow。
- **Protected invariants**：research identity（research_id, generation, work_id）是精确的；
  checkpointed state 不会被 continuation 覆盖；provider work 需要显式 authorization；
  ledger entries append-only。

#### Policy 2: Prompt/Code Ownership Boundary（prompt-code-boundary.md）

从 PPT maker 的 `agent-assistance-and-control.md` 改编。声明 DeerFlow 的三栏 ownership matrix：

**Node Prompts / MD 拥有：**
- 用户意图的语义解释
- 研究方法论和搜索策略
- 来源质量判断（相关性、可信度、独立性）
- 内容合成和创意呈现
- 模糊判断（"覆盖够不够好？"）
- 修复策略（"哪里出错了，怎么改"）

**LangGraph Code / Engine / Domain 拥有：**
- 确定性校验（schema、hashes、identity、gate rules）
- State transition 和 checkpoint 持久化
- Artifact promotion（candidate → accepted）
- Route logic（根据 verdict 选哪条边）
- Budgets、retry bounds、fatigue detection
- Tool posture enforcement（可用工具、sandbox）
- I/O、persistence、lifecycle binding

**Human 拥有：**
- 语义确认（HITL1: adopt/amend research plan; HITL2: adopt deliverable）
- 不能用确定性规则表达的内容质量判断
- Cost/scope trade-off
- Authorization boundary

**Direct Control Path**（5 步操作原则）：
1. 读 owning source of record
2. 对同一个 fact 在 inspect/gate/submit 路径上复用一个 evaluator
3. 在最早可行动的失败前提处短路
4. 返回 bounded root cause + nearest legal next action
5. 通过 owner 修复，然后 rerun 同一个 checkpoint

**Change Admission**（加任何 blocking 逻辑之前必须回答）：
1. 哪个 direct source of record 拥有这个 fact？
2. 现有 checkpoint 抓不住的 real failure 是什么？
3. 删掉/合并/避开了什么冗余检查或特殊情况？
4. 每个独立失败后的唯一最近合法动作是什么？
5. 哪个 focused negative test 证明不会 block 合法路径？

#### Policy 3: Simple Reliable Control（simple-reliable-control.md）

从 PPT maker 的 `simple-reliable-control.md` 改编。核心原则：**Quality control SHALL be
simpler than the work it validates.**

8 条规则映射到 DeerFlow：
1. **Direct facts first** — checkpoint state、typed contract、ledger entry、content hash
   是 authority；summary/diagnostic 是 projection
2. **One truth path** — `gate_kernel.py` 是 canonical evaluator，不要加第二个 pass/fail loop
3. **Prerequisites before implications** — identity/schema 失败就短路，不报一堆派生症状
4. **Smallest actionable root set** — 遵循已有的 `_build_inspect()` / `_build_advice()` 模式
5. **Strict authority, tolerant presentation** — 对 bytes/schema/identity 严格；
   formatting 偏好是 advisory
6. **Fail closed or unknown** — 不确定就 fail closed，不猜
7. **Same-check repair** — 修复后 rerun 同一 checkpoint（已有 wave0/repair, wave1/repair 模式）
8. **One next action** — 每个根因一个最近合法动作，不给菜单

**Blocking-Rule Burden**：加任何 blocking rule、validator、persistent field、retry、fallback、
recovery command 之前必须回答上述 5 个 change admission 问题。答不上来就缩 scope 或降级为 advisory。

#### 注入机制：改 `config.yaml`

这是最关键的一步。改 `openspec/config.yaml`：

**A. Context 里加 Ownership Matrix**

在 `context:` 段加三栏 ownership 表（Prompt | Code/Engine | Human），让每个人一打开 config.yaml
就知道"这段逻辑该放哪"是有明确答案的。

**B. Change Focus Card 加 `Ownership decision` 字段**

现有 Focus Card 要求里加一个必填字段：
`Ownership decision: prompt | code | both | human-interaction`
当选 `both` 时，必须加 `## Ownership Boundary` 表，列出每个跨边界决策及其 owning side 和
enforcing evaluator。

**C. Proposal rules 加三条强制引用**

```
- 涉及 gate、validation、readiness、diagnostic 或 override →
  必须引用 gate-classification.md，分类 guide/confirm/hard-stop，说明 protected invariant

- 涉及 prompt 内容修改或 "这段逻辑该放 prompt 还是代码" 的决策 →
  必须引用 prompt-code-boundary.md，说明 direct Source of Record、evaluator、
  human/Agent/runtime responsibility

- 涉及新的或修改后的质量控制路径 →
  必须引用 simple-reliable-control.md，说明净简化，答不上来就缩 scope 或降 advisory
```

**D. Specs/Design rules 加对应要求**

Specs 要求 gate-sensitive requirement 分类 guide/confirm/hard-stop，质量控制 requirement
比被验证工作更简单。Design 要求每个关键决策标 owner，gate-sensitive design 说明每种结果的
分类和 protected invariant。

**约束**：`config.yaml` 有 140 行 warning / 180 行 hard limit。新增内容必须精简（context ~25 行，
rules 尽量合并现有条目）。

### 为什么这样能防止 Regression

具体链条：

1. 开发者想改进 "source quality detection"，本能地在 `engine/` 加一个新 gate rule 和新 state field
2. **之前**：写 Proposal + Focus Card，触发 `control-and-recovery`，写 Workflow Outcome Review 表，
   开始写代码。gate rule 和 state field 加进去。后来发现 prompt 的 `source-diagnostic` branch
   已经产出了同样的 quality signal。多余的代码变更 = regression
3. **之后**：`config.yaml` rules 强制 `Ownership decision: code`。`prompt-code-boundary.md`
   被触发。Admission question "Which direct source owns the fact?" 让开发者发现 prompt 的
   `source-diagnostic` output 已经有 quality signal。Gate rule 降级为消费已有的 typed result
   而不是加并行检查。不需要新 state field。没有 regression

防止机制：
- `Ownership decision` 是第一个设计阶段检查点
- `prompt-code-boundary.md` 的 admission question 强制 "复用还是加新" 的分析
- `simple-reliable-control.md` 的 blocking-rule burden 问 "删了什么"
- Gate classification 强制每个质量决策有明确的 posture

### 实施步骤

#### Step 1: 创建 gate-classification.md
`openspec/governance/agent-charter/policies/gate-classification.md`
- 定义 guide/confirm/hard-stop，带 DeerFlow 具体例子
- 映射到 `failure_codes.py` 和 `gate_kernel.py` 的运行时分类
- 定义 protected invariants 和 continuation 语义
- 声明 boundary：只管 outcome classification，不管 runtime schema

#### Step 2: 创建 prompt-code-boundary.md
`openspec/governance/agent-charter/policies/prompt-code-boundary.md`
- 三栏 ownership matrix（Prompt | Code/Engine | Human）
- Direct Control Path 5 步循环
- Durable state discipline
- Change admission 5 个问题

#### Step 3: 创建 simple-reliable-control.md
`openspec/governance/agent-charter/policies/simple-reliable-control.md`
- 核心原则 + 8 条规则（映射到 DeerFlow 已有模式）
- Blocking-rule burden（5 个 justification 问题）
- State and recovery discipline

#### Step 4: 更新 Charter Route Table
`openspec/governance/agent-charter/README.md`
- Policy Route 表加 3 行（trigger → policy → what it answers）

#### Step 5: 更新 Charter Principle
`openspec/governance/agent-charter/charter.md`
- 加一条原则："Prompts Own Judgment, Code Owns Determinism"

#### Step 6: 改 config.yaml（注入机制）
`openspec/config.yaml`
- Context 里加 Ownership Matrix
- Change Focus Card 规则加 `Ownership decision` 字段
- Proposal/Specs/Design rules 加三条 policy 强制引用
- 控制行数在 180 行以内

#### Step 7: 验证
- `openspec validate` — config.yaml 合法性
- `python3 openspec/governance/check_agent_charter.py` — charter 一致性
- 拿 active change `harden-research-run-diagnostics-and-hitl-intake` 回溯测试新规则
- 确认 `backend/` 和 `frontend/` 没被碰

### 涉及文件

| 文件 | 操作 |
|---|---|
| `openspec/governance/agent-charter/policies/gate-classification.md` | **Create** |
| `openspec/governance/agent-charter/policies/prompt-code-boundary.md` | **Create** |
| `openspec/governance/agent-charter/policies/simple-reliable-control.md` | **Create** |
| `openspec/governance/agent-charter/README.md` | **Modify** — Policy Route 表加 3 行 |
| `openspec/governance/agent-charter/charter.md` | **Modify** — 加 ownership 原则 |
| `openspec/config.yaml` | **Modify** — 加 ownership matrix + 强化 rules |

## Part II：审查台账（证据、疑点、判定均显式保留）

以下不是对原案的事后删改，而是本次审查的可复核记录。**证据能证明**与**我据此建议**
刻意分列：前者是当前仓库中可检查的事实，后者仍然可以被 reviewer 推翻。

| 原案主张或机制 | 审查时的疑点 / 需反证的问题 | 已核查的证据 | 判定 | 对推荐方案的处理 |
| --- | --- | --- | --- | --- |
| `2000+ regression 一直在涨` | `2150` 是否真是 regression 数，而非测试量或泛称？bug 的重复 lineage 是否足以支持“先问 boundary”的架构诊断？ | `deerflow_research/.reports/test-fast.xml` 报告的是 `2150` 个 test cases；但 BUG-001→013、BUG-006→007、BUG-008→010→014、BUG-011、BUG-012→016 等记录了反复出现的 semantic/authority/projection/control 边界错位。详见配套 [bug evidence](01-bug-boundary-evidence.md)。 | **接受为有案例支撑的定性架构诊断**；不接受 `2150` 为 regression 数，也不声称该模式已量化为全部或主要根因。 | 以 lineage 而非卡片数建立 replay baseline，记录触发 policy 能否提前提出正确问题和哪些 case 是反例；不用 test count、policy 引用次数或表格数量声称 regression 已下降。 |
| 借鉴 PPT Maker 的 policy 注入机制 | controller ownership、runtime abstraction、waiver 语义是否可直接迁移？ | PPT Maker 是 MD-first controller；本仓库是 LangGraph、typed state 与 deterministic gate/admission。两者都需要 source/evaluator/recovery 思考，但 owner 与运行时语义不同。 | **借原则，不直接移植 contract/术语**。 | 借鉴“强制写明适用 policy、direct fact、控制要简单”的方式；不搬 `confirm` waiver、controller ownership 或 MD/JS matrix。 |
| `guide / confirm / hard-stop` 可自然映射 `PASS / REPAIR / BLOCKED / NEEDS_HUMAN` | 当前 gate 是否真的产生 `NEEDS_HUMAN`？`semantic` 是否走 confirm？ | `gate_kernel.py` 当前只以 failure class、budget 等产出 PASS/REPAIR/BLOCKED；`PhaseVerdict.NEEDS_HUMAN` 是保留枚举，现有 failure path 不产出它。 | **否决 runtime 映射**；原分类最多可作为设计讨论的灵感。 | 外置 policy 使用不与 runtime 枚举绑定的四个 design posture；不定义新的 failure taxonomy。 |
| continuation/waiver 可映射到 HITL1/HITL2 | 现有 HITL 是否有可审计 waiver schema、version scope、state effect？ | 当前 HITL1/HITL2 有各自的 typed interaction/lifecycle contract，但没有被 policy 接管的 waiver/continuation schema。 | **排除**，不能由 policy 凭空创建 runtime human-action contract。 | 只有 owning capability 新增 schema、interpreter、graph admission 后，才可讨论实际 human decision；policy 本身不授权 continuation。 |
| `Prompts Own Judgment, Code Owns Determinism` 与三栏 ownership | “判断”是否等于接受、写 state、改变 route，`both` 是否足以描述 handoff？ | `node-agent-workflow-integrity.md` 要求 bounded question、candidate result 与 deterministic admission owner；prompt/model 输出是 candidate，parser/evaluator/materializer/graph 才能 validate、admit、persist、route。 | **改写**：原句有 authority 歧义，`both` 会掩盖 source、evaluator、admission 的不同 owner。 | 原 `Ownership decision` 字段和 matrix 不进入 config；采用逐行 `Control Placement Review`，原则改为“Cognition proposes; deterministic owners validate, admit, and route.” |
| 三个新 Charter policy | 是否已和现有 Charter policy 同义重叠，形成第二治理 authority？ | `control-and-recovery`、`authority-and-projections`、`node-agent-workflow-integrity`、`human-interaction-integrity`、`workflow-outcome-review` 已覆盖 recovery、projection、candidate handoff、human input 与 lifecycle outcome。 | **缩为一个补缝 policy**，既有 policy 保持 route owner。 | 仅新增 `openspec/policies/control-placement.md`；通过组合表引用既有 policy，不复制三套近义正文。 |
| `config.yaml` 放完整 ownership matrix，作为“中央宪法” | 当前 config 的 information-map 限制是否允许承载详细设计教程？ | `openspec/config.yaml` 当前约 80 行；`agent-information-map.md` 对入口文档有 `140` 行 warning / `180` 行 hard limit，并要求深度内容走局部文档。 | **保留短路由，否决完整 matrix 注入**。 | config 只写触发/必填 record/组合提示及 non-authority boundary；详细问题进入 `openspec/policies/control-placement.md`。 |
| checker 可以把 policy 从“参考读物”变成“必过检查点” | 机械 checker 能否可靠地从 prose/code 推断 policy 应不应该触发、答案是否语义正确？ | `check_agent_charter.py` 已校验 Focus Card、声明 policy、heading/table shape；它没有也不应成为 source analyzer 或 LLM quality judge。 | **部分接受**：可强制“已声明时 record 完整”，不能自动证明“应该选择 / 选择正确”。 | registry + deterministic table validator 只检查 canonical name、存在性、组合和表格 shape；语义适用性由 review/guardrail/human 复核。 |
| `source-diagnostic` 已有 quality signal，因此能替代新 gate/state | 该 output 是 authority 还是仅为 downstream candidate/materialized input？是否每个 source-quality problem 都能复用？ | prompt catalog、capability 与 board 证明存在该 branch 及其 candidate/admission seam；未证明它是普适质量 authority，也未证明每个 gate 所需事实皆已 materialize。 | **保留为设计审查问题，否决为通用证明**。 | Control Placement Review 要求作者给出 direct fact + deterministic owner，并明确复用或避免的复杂度；不得仅写“prompt 已判断”。 |
| “这样能防止 regression” | policy 表是否能实际在实现前发现重复 control 或错误 authority？ | 尚未有前后对照、replay 结果或首批 change 使用数据。 | **待验证效果假设**。 | V1 加 baseline、回放和首五个 change 的使用记录；发现盲点就扩 policy 的反例，而不是修改分类以迎合结论。 |
| 三个 policy 放 Charter/governance 内 | policy、governance checker、未来跨 session 检查是否是同一职责层？ | 用户明确要求 policy 位于 `openspec/` 下的独立子目录，未来 `guardrails` 也需独立；governance 当前拥有零依赖 checker。 | **采纳目录边界调整**。 | v1 policy 位于 `openspec/policies/`；未来跨 session pre-submit 机制位于 `openspec/guardrails/`；本 change 不创建空 guardrails 目录。 |
| 原案的六文件影响范围足够 | 外置 policy、checker、registry、evidence、真实 migration 是否需要更多契约性改动？ | 新机制若要被 active-change checker 可靠验证，至少涉及 policy registry、requirements、structure、focused tests、evidence 与一个真实 active change。 | **范围扩大但仍限定为治理层**。 | Part III 列出完整文件清单；不改 `backend/`、`frontend/`、runtime route、checkpoint schema 或 prompt runtime 行为。 |

### 历史 bug 不是背景噪声：它定义这项工作的纠正对象

对 BUG-001～016 的审计说明，当前工作不是抽象地“防未来 regression”，而是把最近不断显露的
错误着力点变成可复用的 design review 问题。详细根因、原卡链接、fixing commit 与不可推导边界在
[`01-bug-boundary-evidence.md`](01-bug-boundary-evidence.md)；主文只保留
对 v1 有直接影响的压缩版：

| Lineage | 已观察到的“努力使错层” | 这项 policy 应迫使作者先回答什么 |
| --- | --- | --- |
| BUG-001 → BUG-013 | 中文 parser / 精确 typed-action 改善了协议，却仍把自然的“确认”当 profile 字段；问题不是再加 alias，而是语义 intent 与 graph admission 被混同 | 这是不是 bounded semantic candidate？谁只解释意图、谁仍拥有 correlation/state admission？ |
| BUG-006 → BUG-007 | 把错误投影修正后，用户仍被要求选择 graph 内部 route；问题不是菜单文案，而是人根本不该替已验证状态做该决定 | 人类真正贡献的是偏好/授权还是 route？Agent/graph 已经拥有什么 direct fact？ |
| BUG-008 → BUG-010 → BUG-014 | 一个 node 的 retry/terminal 表现修好后，相邻 node 又丢失 provider observation，最终连 timeout origin 都无法判断 | direct fact 在哪个 shared owner 产生？哪些 consumer 应复用它、不得各自重分类？ |
| BUG-011 | 为 direct terminal 加“任意 `terminal_status` 跳过 gate”的 broad guard，吞掉 final-delivery 的 repair/pass route | 改的是哪一个具体 decision？既有 gate owner / legal route 是什么？新 guard 会吞掉什么相邻情形？ |
| BUG-012 → BUG-016 | 统一 diagnostic reference 后，带既有 reference 的分支仍跳过 record publication；同一 ID 被误当成已存在证据 | 事实是“有引用”还是“该引用的 record 已发布”？唯一 writer 和 projection precondition 是什么？ |
| BUG-004 / BUG-009 / BUG-015 | warning、fixture、字符串断言都曾让测试看似通过，但没有覆盖真实 checkpoint、合法 predecessor 或用户实际运行的 command | 最低 evidence seam 是否真的运行在 consumer / legal input / 声明环境，而不是只比对文本？ |

这些案例的共同点不是“把一切移到 prompt”，而是**先停止继续叠加**：将认知候选、人类决定、direct
fact、deterministic evaluator、route 和 presentation 拆开，再选择最小 owner。BUG-011 / BUG-012 / BUG-016
甚至要求把逻辑收回到更窄的 deterministic owner；BUG-001 / BUG-013 则要求给语义解释一个受限而不越权的位置。

### 仍未解决、必须由后续证据回答的疑点

| 未决问题 | 为什么目前不能下结论 | V1 / 后续如何获得证据 |
| --- | --- | --- |
| “重复 control / 错误 authority”占历史问题的比例是多少？ | 没有把 regression findings、BUG 卡和具体修复按同一分类复盘。 | 为可重放样本建立 baseline，并保留无法归类的比例和反例。 |
| 哪些 prompt/candidate 改动需要 live calibration，而不仅是 deterministic proof？ | “有 prompt 改动”并不自动等于“改变认知质量”；影响程度取决于 branch、candidate semantics 与用户意义。 | 用 branch inventory、Cognitive Program Board、normal/highest-risk rubric 决定；未覆盖时先扩 owning evaluation capability。 |
| fresh session 是否真的独立？ | 无可信 orchestration identity 时，不能根据“新对话”声称安全级别的独立性。 | 后续 guardrail 记录 author/reviewer session identity、diff digest 和 provenance；未满足时只称 fresh review record。 |
| 能否把认知质量变成自动 blocking threshold？ | provider/model drift、样本覆盖与 rubric 可靠性不足；单一 LLM judge 会自证。 | 先使用 paired baseline、counterexample、bounded calibration 与 human escalation；只有累积足够历史数据且单独批准后才考虑阈值。 |

## Part III：经审查后的推荐方向

### Review 结论

保留原方案的目标：在写实现前，强制把「这是谁的认知判断、谁拥有事实、谁能接受
结果、谁能改变 route」说清楚，避免把一个已有的候选信号又做成第二套 gate/state。

但原方案不能原样实施，原因如下：

1. `deerflow_research/.reports/test-fast.xml` 中的 `2150` 是测试用例数，不是
   `2000+ regression` 数；不能拿它充当 regression KPI。但对 BUG-001～016 的逐卡和 Git-history
   审计已给出重复的 boundary/authority/control 错位案例，足以支持「先问 placement，再继续叠加实现」
   的**定性架构诊断**。尚未被证明的是它占全部或主要 regression 的比例，以及本 policy 是否会改善它；
   这些仍需 baseline、replay 和反例检验。
2. PPT Maker 是 Markdown-first controller；Deep Research 是 LangGraph + typed
   admission 的确定性工作流。PPT Maker 的 MD/JS ownership matrix、`confirm` waiver 和
   continuation 语义不能直接搬过来。
3. Deep Research 已有 `control-and-recovery`、`authority-and-projections`、
   `node-agent-workflow-integrity`、`human-interaction-integrity` 和
   `workflow-outcome-review`。再复制三份同义 policy 会制造第二个治理 authority。
4. `PhaseVerdict.NEEDS_HUMAN` 目前只是保留枚举；`semantic` failure 当前会进入
   bounded repair 或 budget-exhausted block，不存在原方案所说的 `confirm -> NEEDS_HUMAN`
   映射。HITL1/HITL2 也没有可由 policy 凭空定义的 waiver/continuation contract。
5. Prompt 不是事实或 route 的 owner。Node Agent 只产生受限 candidate；parser、
   evaluator/materializer、graph 和 typed state 才能验证、接纳、持久化和路由它。

因此 v1 只新增一个**外置 OpenSpec policy**与一个可检查的 proposal record；不新造运行时
taxonomy、不把 prompt 提升为 controller，也不宣称它已经消灭 regression。

### 已验证的现有基础

| 已有资产 | 已经能证明 | 不能替代什么 |
|---|---|---|
| `failure_codes.py` + `gate_kernel.py` | 闭合 failure 分类、bounded repair、唯一 gate route writer | 人类判断、prompt 质量或设计时 policy applicability |
| `node-agent-workflow-integrity.md` | bounded cognitive question、tool enforcer、candidate admission owner | 一个 change 为什么需要新增/复用 control 的跨层说明 |
| `control-and-recovery.md` | direct fact、bounded recovery、最近合法动作、控制应简单于被控制工作 | 新 policy 的目录、proposal record 和跨 session 复核 |
| prompt catalog + `node_prompts/` | 最终 prompt 的确定性 review diff | 模型判断质量、prompt 的运行时 authority |
| Cognitive Program Board / capability evidence | 20 个直接模型分支、candidate/admission seam、已知限制 | 某次模型输出「足够好」 |
| 四套 live calibration corpus | 有边界的 rubric、normal/highest-risk case、真实 provider judgment evidence | 通用质量分数、一次运行后的永久结论 |
| BUG-001～016 + fixing-change Git history | 多条真实 lineage 在 semantic interpretation、direct fact、projection、gate owner、legal route 或实际 evidence seam 上发生错位 | 该模式的全量比例、单一根因，或“prompt 总是正确落点” |

外部 PPT Maker policy 仅借鉴三个思想：先找 direct fact、控制路径要净简化、把可逆人类
判断和不可绕过 invariant 分开。具体术语、controller ownership 和 waiver 行为不迁移。

### 目录与职责边界

这次的 policy 不放进 `openspec/governance/agent-charter/policies/`。物理布局和职责如下：

| 目录 | 职责 | 不负责 |
|---|---|---|
| `openspec/policies/` | 跨 OpenSpec change 的设计/admission policy；v1 放 `control-placement.md` | 运行时 route、state、权限，或执行提交检查 |
| `openspec/guardrails/`（后续 change 创建） | 提交前、跨 session 的 impact/evidence/review orchestration 与 closeout coordinator | 取代 capability spec、test asset 或人类质量判断 |
| `openspec/governance/` | 零依赖的结构、追踪与 proposal-shape checker | 承载 policy 内容或推断模型质量 |
| `openspec/governance/agent-charter/` | Deep Research 的本地路由；链接到适用的外置 policy | 复制外置 policy 正文 |

不要在本 change 创建一个空的 `openspec/guardrails/`。空目录会伪装成已有能力；它应由单独的
`add-cross-session-cognitive-guardrails` change 在有明确 contract、runner 和 evidence model 时创建。

### V1：`control-placement` OpenSpec Policy

#### 触发条件

当 change 有下列任一种行为时，作者必须选择 `control-placement`：

- 新增或改变 gate、validator、readiness check、candidate admission、retry/fallback/recovery，
  或能决定下一动作的 diagnostic；
- 新增 durable control fact、checkpoint/state writer，或把现有 fact 投影成新的 pass/fail authority；
- 在 Node Agent、human decision 和 deterministic owner 之间移动一个认知/控制边界；
- 为已经存在的 prompt/model candidate 新增并行 quality rule、state field 或 gate。

下列情形不触发：不改变 bounded question、candidate contract、admission 或 control 行为的纯文案
调整；只刷新由已有 source 生成且内容语义未变的 catalog；普通运行时重构且控制边界不变。
遇到不确定时选择该 policy 并写 `none` candidate，而不是假设 prompt 或 code 自动拥有全部责任。

#### 语义边界

`control-placement.md` 只指导 proposal/design review，不创建 runtime contract。它使用四个**设计
posture**，并明确它们不是 `FailureCode`、`PhaseVerdict`、HITL action 或 waiver schema：

| Posture | 含义 | 必须说明 |
|---|---|---|
| `advisory` | 只提供信息或候选，不得改变 lifecycle/route | 谁消费它，以及为何不是第二 authority |
| `bounded-repair` | 已有合法 owner 可在明确 bound 内修复并重跑同一 checkpoint | owner、bound、terminal disposition、next action |
| `human-decision` | 一个已存在或本 change 明确定义的 typed human decision 必须处理不可确定的取舍 | subject、interpreter、graph admission；不得把它说成 waiver |
| `non-bypassable` | identity、integrity、authorization、recoverability 等事实不能靠 prompt、policy 或人类文本跨越 | protected invariant 和唯一合法恢复路径 |

`human-decision` 不等于「人可以继续」。如需要实际的用户 action，必须同时选择
`human-interaction-integrity` 并由 owning capability 定义 schema、可见 control 和 state effect。
`non-bypassable` 可有修复路径，但不能有 force/waive 后门。

#### Proposal record

选择 `control-placement` 时，proposal 必须恰有一个 `## Control Placement Review`，每一项受影响
的 decision/fact 一行，使用此精确表头：

```text
| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
```

约束：

- 第二列填写 `none`，或一个有限的 Node Agent question / human subject；它不可以宣称 prompt
  拥有 state、route、permission 或 accepted artifact。
- 第三列必须给出 direct source of record 和唯一的 deterministic owner/evaluator，不能写
  「prompt output」或「review table」。
- 第四列只能是四个闭合 posture；`human-decision` 要同时列出
  `human-interaction-integrity`。其他现有 policy 仍按自己的 trigger 选择。
- 第六列必须写明复用了什么，或者明确说明避免了什么新增 control；「新增 helper」不是净简化。
- 每行给出最低负责的 deterministic seam。模型质量 claim 另走 calibration/guardrail，不伪装成
  unit test 已证明。
- 当 direct fact 跨越 producer/consumer owner，evidence seam 必须覆盖该真实 handoff，不能只由
  consumer fixture 手造事实；当 fact 会持久化，evidence 必须覆盖 write/reload/direct-consumer
  链路。
- 同一 feature 若同时包含人类输入和不可绕过 invariant，必须拆成不同 row，分别声明
  `human-decision` 与 `non-bypassable`，不得用一个 posture 掩盖两种 effect。
- 这是一个**跨层 delta record**，不是第二份 Node Agent Review、Workflow Outcome Review 或全仓
  semantic-object inventory。既有 review 已经保存的细节必须以稳定 heading/row reference 指向，
  不得复制成另一组同义答案；checker 接受这种 reference，但不追踪或裁决它的语义。

该表替代原方案的 `Ownership decision: prompt | code | both | human-interaction`。后者把多方
协作误压成一个二元选择，且会诱导「prompt owns judgment」的错误 authority 模型。

#### 与既有 policy 的组合

| 变化 | 必选组合 | 各自仍回答什么 |
|---|---|---|
| LLM role、prompt 的 bounded question、tool posture 或 admission 改变 | `control-placement` + `node-agent-workflow-integrity` | 前者放置 decision/fact；后者记录 Node Agent handoff |
| 人类语义输入、visible control 或授权改变 | `control-placement` + `human-interaction-integrity` | 前者说明 posture；后者记录 subject、interpretation、action binding |
| retry、terminal、diagnostic 或 lifecycle projection 改变 | `control-placement` + `workflow-outcome-review`，按需再加 `control-and-recovery` | 前者避免重复 control；后者记录 failure/recovery 事实 |
| state、summary、cache、diagnostic 投影改变 | `control-placement` + `authority-and-projections` | 前者说明 evaluator/reuse；后者保护 source of truth |

这张表是补充，不合并或替代现有 `Node Agent Review` 与 `Workflow Outcome Review`。

### 注入机制与可执行边界

#### 统一 policy 名称

现在的字段名 `Triggered charter policies` 只能准确描述 Charter 内的 policy。v1 外置 policy
后，将其一次性迁移为 `Triggered review policies`：同一字段列出 charter policy 和
`openspec/policies/` policy 的 canonical name。这样不会新增两个必填字段，也不会把外置 policy
伪装为 Charter 所有物。

`check_agent_charter.py` 维护一个小的 policy registry：canonical name → path → record validator。
它仍然只校验已声明 policy 的存在、文件 anchors、Focus Card 和 table shape；**不扫描 source、
不从 prose 推断 policy 是否应该被选择、不判断语义答案是否正确**。这正是可机械化的上限。

#### 精简的 `openspec/config.yaml` 规则

`openspec/config.yaml` 只增加短路由，而不增加三栏 ownership matrix：

- Focus Card 使用 `Triggered review policies`，列出 canonical names，或 `none: <rationale>`；
- 涉及 control-placement trigger 时选择 `control-placement`，并补 `Control Placement Review`；
- 提醒与 Node Agent、human interaction、workflow outcome 的组合关系；
- 明确 config、policy、prompt 和 review record 都不授予运行时 authority。

当前文件约 80 行，必须保持在 information-map policy 的 140 行 warning / 180 行 hard limit 内。
深度解释只存在于 `openspec/policies/control-placement.md`，不是默认 authoring context。

#### 2026-08-02 archived repair replay

当前 V1 change 已归档；不得假设
`harden-research-run-diagnostics-and-hitl-intake` 曾是或仍是迁移对象。V1 已将以下两个已归档
repair 保留为历史回放样本，而不是改写 archive：

1. `fix-topic-planning-provider-outcomes`：回放 closed stop classification、default-deny
   provider-observation admission、bridge 与 topic-planning 之间的 retry owner，以及 terminal
   projection。它检验 policy 是否能在代码前指出“共享 direct fact 的 owner 不能被 node-name
   predicate 或 presentation inference 替代”。
2. `harden-hitl1-comparison-intake`：回放 typed comparison/language profile facts、明确确认的
   local action path、相关联的 language option 和非交互路径不得虚构事实。其 design 中已有自愿
   的 Control Placement Review，可作为七列表格的输入，不是已符合未来格式的证明。

回放必须记录 policy 本会提出的问题、无法提出的问题和任何反例；不得声称它已经阻止这些 bug。
本 V1 proposal 已在归档前原子迁移到 `Triggered review policies` 并接受新 checker。未来 active
change 采用该字段；已 archive 的 change 一律不做字段 rename 或批量重写。

### 认知题的解法：分层证据，而不是更多 Test Asset

传统程序的正确性常可归约为 input/output、invariant 和 deterministic replay；Node Agent 的「判断是否
有用、保守、贴题」不能。测试资产仍必要，但只能证明边界，不足以证明认知质量。

| 证据层 | 现有/应复用资产 | 能给出的结论 | 不能给出的结论 |
|---|---|---|---|
| 确定性 guardrail | typed schema、parser/materializer、gate、prompt catalog、capability/board/test assets | candidate 不越权、未漏分支、route/state/ledger 不被模型控制 | 输出是否高质量、覆盖是否有洞见 |
| 有界行为评价 | 四套 calibration corpus、normal/highest-risk rubric、live report 与 provider provenance | 在给定 case/model/config/bound 下的 rubric evidence | 跨时间、跨模型、跨主题的一般质量结论 |
| 独立审查 | fresh-session challenger + human review | 发现作者上下文未见的 counterexample、错误 scope、无依据的 quality claim | 取代 human 的价值取舍或成为 runtime authority |

任何「认知改进」proposal 必须先声明它属于哪一层：

- 只改确定性边界：执行最低 seam、prompt catalog diff 和相关 workflow proof；不得声称质量提升。
- 改 bounded cognitive question、prompt constraint 或 candidate semantics：定位受影响 branch，复用或
  先扩展其 normal/highest-risk calibration case 与 rubric，记录 live 结果的 model/config/日期/bounds。
- 新增高风险认知 role、用户意义解释或会影响 deliverable quality 的判断：除上述外，需要独立 session
  的 challenge 和人类审查；`limited` / `inconclusive` 是诚实结果，不可被单次 LLM judge 伪装成 pass。

现有 calibration corpus 已故意把 deterministic conformance 与 live judgment 分开。新设计应消费这
套资产，不能再建立一个平行的「quality score」或让一段 prompt/一个 agent judge 自动批准自己。

### Change 3 deferred：跨 Session Cognitive Guardrails（独立 change）

这个后续不是 Change 1 或 Change 2 的隐含实现，而是
`add-cross-session-cognitive-guardrails` 的独立 OpenSpec change。
它在 `openspec/guardrails/` 下实现提交前的**证据编排与 feedback loop**，而不是新 runtime controller。

#### 借鉴 session-drift 分析后的职责分层

对 `ai_tool_deepresearch` 的 [session-drift analysis](02-session-drift-borrowing.md)
进行本地适用性核实后，后续 guardrail 采用以下分工，而不是新增一个“万能智能检查器”：

| Surface | 未来职责 | 不得冒充 |
| --- | --- | --- |
| `openspec/policies/control-placement.md` | 触发条件、review 问题、既有 policy 的组合方式 | runtime authority、跨 session runner、machine verdict |
| `openspec/config.yaml` 的 `rules.tasks` | 在 change artifact 中留下 plan/closeout review obligation | 命令执行、semantic proof、archive authority |
| `operations.apply/archive.guidance`（由 Change 2 验证并配置） | 在 apply/archive 事件把 risk-led review 重新推到当前 Agent | hard gate 或自动 checker |
| `openspec/guardrails/` | review protocol、impact packet、fresh-session challenge、dossier、finding 编排与 guardrail-owned closeout coordination | graph route、模型自我批准、平行 governance registry 或 policy 正文 |
| `tasks.md` | 跨 session 保存 review finding 与最小修复工作 | 触发器、质量证明或 source of truth |
| `openspec/governance/` | 输出既有 deterministic check result，供 guardrail coordinator 消费 | policy 正文、cognitive-quality judge 或 guardrail coordinator |

**instruction 是 push channel，task 是 durable work ledger，deterministic check/finalizer 才能闭合
机械前提。** 这三者不能互相冒充。外部方案也给出三个明确反例：不做 SessionStart banner、不把
semantic reasoning 填成可机检 schema、不让单一 LLM judge 自动给 quality pass。职责借鉴与反模式详见
[`02-session-drift-borrowing.md`](02-session-drift-borrowing.md)；OpenSpec 1.7
两个 operation guidance 的实际契约、时机分工和配置草案详见
[`03-openspec-1.7-operation-guidance.md`](03-openspec-1.7-operation-guidance.md)。

#### Guardrail 输入与流程

Change 3 只有在 Change 2 完成配套文档列出的 local attach-point / archive-side-effect probes 后，才采用
如下流程；它不是今天的隐式 hook：

1. 对触发 cognitive/control review 的 change，`operations.apply.guidance` 在第一次 target edit 前和
   resumed apply 时推送 plan review。Agent 读取 Focus Card、Control Placement Review、适用 spec delta、
   prompt catalog diff、Cognitive Program Board 与相似 historical lineage；这一步只提出问题，不自动判定
   质量。
2. 发现需要工作的 semantic / authority / scope 问题时，立即写成未完成 `tasks.md` task，包含被保护的
   requirement 或 reader question、direct owner、最小修复和诚实 done condition。它不能只留在聊天、
   challenger 散文或 dossier 中。
3. 在 archive 前，`operations.archive.guidance` 绑定 selected change 的 merge-base / approved baseline /
   actual diff。若无法把该 change 与无关 worktree 改动可靠分离，报告 `missing-boundary` 并停止 closeout；
   不扫描整个 worktree 后声称已完成 review。
4. 构建 impact packet：受影响的 branch/capability/candidate admission owner、相邻 consumer、已有
   deterministic claim、calibration case/rubric、相似 bug lineage 以及明确的 unknown。已知
   source→branch mapping 与作者声明不一致时 fail closed；未知映射要求显式扩大 scope，不能猜。
5. 在不携带作者聊天上下文的 fresh session 运行 challenger。它只提交结构化 objection：被质疑的
   claim、直接证据、反例/遗漏影响、所需下一证据；不能用自由散文或自己的偏好替代 source of truth。
6. 对认知语义变更选择受影响 branch 的现有 normal/highest-risk calibration；不覆盖新 hypothesis 时
   先在 owning evaluation capability 中新增带 provenance 的 corpus/rubric，再运行有界 live evaluation。
7. 由人或指定 reviewer 对 baseline-vs-candidate evidence 作结论。比较必须记录 change/diff、case id、
   model/config、时间、预算、rubric 与 `pass|limited|inconclusive`；provider drift 时不得把旧分数当
   当前事实。
8. 产生一个提交 admission 结果：`clear`（无质量 claim 的确定性变更）、`review-required`、
   `inconclusive` 或 `blocked`。只有缺少必需 deterministic contract、保护 invariant 被跨越、impact
   packet 不完整，或 closeout finding 仍有未完成 task 时才可自动 `blocked`；认知质量本身不由单次 LLM
   自动裁决。

#### Guardrail 的持久化与边界

- change-local dossier 应保存 review input digest、影响集合、objection、evidence references 和最终
  disposition；不保留 prompt、secret、原始 provider body 或用户敏感内容。
- dossier 记录“审查过什么、得到了什么证据”；`tasks.md` 记录“还必须做什么”。一条需要修复的 finding
  必须同时有 ordinary pending task，不能以一个 `pass` 文本、聊天总结或 dossier 结论自行闭合。
- 跨 session runner 应验证 dossier 绑定当前 diff，且 reviewer session 与 author session 可审计地不同。
  没有可信 orchestration identity 时，只能声称「fresh review record」，不能声称安全级别的独立性。
- current code/spec/test/corpus 仍是各自事实源；guardrail dossier 是提交证据，不是 lifecycle、模型或
  quality authority。
- 不能用平均分或单个 golden answer 当硬 gate。先以 rubric、paired baseline comparison、counterexample
  和 human escalation 建立可信度；阈值只在有足够历史数据和单独 approval 后才可能升级。

这解决了「每个 change 只看自己」的问题：guardrail 读取当前 change 之外的 branch inventory、既有
calibration 与 merge-base，但不把这些投影变成第二套 runtime state。

### 量化已观察模式，并检验干预

历史 bug 语料已经证明 boundary/authority drift **存在**；这里建立 baseline 不是为了把它降回
“尚无证据的猜测”，而是为了量化适用范围并检验本 policy 是否真的改变早期决策。不要把 policy
compliance 当成功代理：

1. 以配套 [bug evidence](01-bug-boundary-evidence.md) 的 six lineage 为首批
   replay corpus，再把 `regression-descent.md` 的可重放发现和其余 BUG 卡按「重复 control / 错误
   authority / 未声明 cognitive boundary / evidence-seam mismatch / provider-only or unrelated」分类。
   一个祖先问题与残留问题按同一 lineage 计，记录无法归类的比例。
2. 对每个适用样本回放 Control Placement Review：记录它在实现前会提出哪一个正确问题、不能提出什么、
   是否会诱导多余表格。未抓到的样本是 policy 的反例，不得被改写为“无关 bug”。
3. 在首五个符合 trigger 的 change 上记录：table 是否改变 scope/复用决策、是否保护了已存在的
   evaluator/route、是否造成仪式化行，以及哪些 semantic question 仍只能由 calibration /
   fresh-session challenge / human review 处理。
4. 只有完成上述前后对照后，才评估该 policy 是否降低重复 control、错误 authority 或 evidence-seam
   mismatch；不得以 test count、table 数量或 policy 被引用次数声称 regression 已下降。

### 实施步骤

#### 1. 立项并冻结 v1 边界

创建 `openspec/changes/add-openspec-control-placement-policy/`，其 Focus Card 的 primary owner 是
OpenSpec review-admission route/checker，修改 capability 为 `deep-research-agent-charter`。新增
`DRC-009`：外置 policy、`Triggered review policies`、conditional Control Placement Review 以及
checker 的机械边界。它不定义任何 DeerFlow runtime 行为。proposal/design 同时必须引用一份有界的
historical replay evidence note：以 BUG-011、BUG-001→013、BUG-012→016 等 lineage 说明“为什么此
policy 存在”，但不把它们伪装成全量统计或新的 runtime requirement。

#### 2. 建立外置 policy 层

- 创建 `openspec/policies/README.md`，说明该层与 `governance/`、Charter 和未来 guardrails 的边界；
- 创建 `openspec/policies/control-placement.md`，写入触发条件、四个 design posture、table 问题、
  组合规则和 non-authority boundary；
- 只在 Charter 路由表增加到该外置文档的链接；不复制 policy 内容，也不移动现有 Charter policy。

#### 3. 迁移 review-policy 入口

- 将 Focus Card 的 `Triggered charter policies` 统一改为 `Triggered review policies`；
- 同步 `deerflow_research/AGENTS.md`、`openspec/config.yaml`、change-admission、node-agent 和
  workflow-outcome policy 中的作者指引；
- 在 Charter 加入精确原则：**Cognition proposes; deterministic owners validate, admit, and route.**
  它不说「prompt owns judgment」；
- 不在 `openspec/config.yaml` 注入完整 ownership matrix，保持它是路线图。

#### 4. 扩展确定性 admission check

- 将 `check_agent_charter.py` 的 policy registry 从「Charter path 假设」改为 canonical name/path mapping；
- 增加 `control-placement` 及 `Control Placement Review` 的 heading、精确七列表头、非空 row、闭合
  posture 和 `human-decision` 组合校验；
- 保持现有 Node Agent Review 与 Workflow Outcome Review 的独立强制，不做 source/prose 语义推断；
- 在 `test_agent_charter_governance.py` 先加 red fixture：外置 policy 缺失、未知 policy、缺 table、
  错表头、空 cell、非法 posture、遗漏 human-interaction 组合、三种 review 同时选择均被正确处理。

#### 5. 同步结构与需求证据

- 在 `req-registry.yaml` 登记 `DRC-009`，给 policy、checker 与 focused test 添加 `@impl DRC-009`；
- 在 `openspec/specs/deep-research-agent-charter/spec.md` 和本 change delta 写完整可观察 requirement/
  scenarios；
- 在 `project-structure.toml` 注册 `openspec/policies/`、`README.md` 和 `control-placement.md`，path
  owner 使用 `DRC-009`；不为一个目录位置凭空新增新的 project-structure capability；
- 在 `tests/assets/evidence.py` 和 `tests/assets/requirement_evidence.py` 增加一个 collected
  deterministic DRC-009 claim/impact，证明 table 不会吞掉既有 review。

#### 6. 回放已归档 repair 并做假设审计

- 使用 `fix-topic-planning-provider-outcomes` 和
  `harden-hitl1-comparison-intake` 的 archive 作为首两个真实 replay；不改写 archive；
- 为每个 repair 写出未来七列表格会提出的 placement question、对应的实际设计决定、未覆盖的
  问题和反例。特别核对 shared producer-to-consumer handoff，以及 profile/checkpoint 的
  write/reload/direct-consumer 链路；
- 运行 checker 对 V1 自身和后续新 active change；新 change 迁移
  `Triggered review policies`，archive 保持历史原样；
- 将 lineage baseline/replay 结果放入 V1 design 或明确的 evidence note。若某类 case 不受 policy
  影响，保留其反例、缩小 policy 的承诺，不扩大 checker。

#### 7. 验证与归档

- 先跑 `cd deerflow_research && uv run --extra operations python -m pytest tests/contract/test_agent_charter_governance.py -q`；
- 再跑 `python3 openspec/governance/check_agent_charter.py .`、
  `python3 openspec/governance/check_project_reqs.py .`、
  `python3 openspec/governance/check_project_specs.py .`、
  `python3 openspec/governance/check_project_architecture.py .`；
- 运行 `openspec validate add-openspec-control-placement-policy --strict`、
  `cd deerflow_research && UV_OFFLINE=1 make verify`、`git diff HEAD --check`；
- 记录 `git status --porcelain=v1 --untracked-files=all`，确认 `backend/`、`frontend/`、root
  `AGENTS.md` 和 root `CLAUDE.md` 没有改变。

#### 8. 先完成 Change 2，再另开 Guardrails change

这是明确的 **Change 3 deferred checkpoint**，不是 Change 1 的可选尾项。先通过
`add-openspec-operation-guidance` 完成并归档 [session-drift borrowing](02-session-drift-borrowing.md)
中的六项本地 probe：OpenSpec operation-guidance delivery、supported archive adapter、archive side effect、
selected-change diff boundary、historical replay 和 guardrail-owned closeout coordinator interface。只有这些
前提成立，才提案 `add-cross-session-cognitive-guardrails`，由它定义 impact-packet/dossier schema、
`openspec/guardrails/`、跨 session runner、review provenance 和 risk-tier admission；不得把它夹带进
Change 2。

### 已创建的审查附件

以下文件是本计划的 review/evidence material，不是本计划所提议的 runtime 或 OpenSpec implementation
交付物；它们保留长证据链，避免未来 reviewer 只能看到一个压缩结论：

| 文件 | 当前作用 |
| --- | --- |
| [`README.md`](README.md) | 导航、证据边界与阅读顺序 |
| [`01-bug-boundary-evidence.md`](01-bug-boundary-evidence.md) | BUG-001～016 与 Git history 的 lineage/replay 证据 |
| [`02-session-drift-borrowing.md`](02-session-drift-borrowing.md) | 对外部 session-drift feedback loop 的选择性借鉴、本地适用性与反模式 |
| [`03-openspec-1.7-operation-guidance.md`](03-openspec-1.7-operation-guidance.md) | OpenSpec 1.7.0 两个 operation guidance 时机、`rules.tasks` 组合、advisory 边界与 Guardrails 接入前 probes |

### 涉及文件

| 文件 | 操作 | 目的 |
|---|---|---|
| `openspec/policies/README.md` | Create | 外置 policy 层的职责与导航 |
| `openspec/policies/control-placement.md` | Create | 唯一新增的 control-placement policy |
| `openspec/changes/add-openspec-control-placement-policy/` | Create | proposal、delta specs、design、tasks 与 evidence note |
| `openspec/governance/agent-charter/README.md` | Modify | 路由到外置 policy |
| `openspec/governance/agent-charter/charter.md` | Modify | 加入 candidate 与 deterministic authority 原则 |
| `openspec/governance/agent-charter/policies/{change-admission,node-agent-workflow-integrity,workflow-outcome-review}.md` | Modify | 迁移字段名称并说明组合边界 |
| `openspec/config.yaml` | Modify | 精简注入规则，不放完整 matrix |
| `deerflow_research/AGENTS.md` | Modify | 同步 Focus Card 字段名称 |
| `openspec/governance/check_agent_charter.py` | Modify | 外置 policy registry 与 table validator |
| `deerflow_research/tests/contract/test_agent_charter_governance.py` | Modify | red/green admission fixtures |
| `openspec/specs/deep-research-agent-charter/spec.md` | Modify | 归档后的 `DRC-009` requirement |
| `openspec/governance/req-registry.yaml` | Modify | 追加 DRC-009 |
| `openspec/governance/project-structure.toml` | Modify | 注册外置 policy 路径 |
| `deerflow_research/tests/assets/evidence.py` | Modify | DRC-009 collected claim |
| `deerflow_research/tests/assets/requirement_evidence.py` | Modify | DRC-009 smallest-sufficient impact |
| `openspec/changes/harden-research-run-diagnostics-and-hitl-intake/proposal.md` | Modify | 真实 active-change migration |

`openspec/guardrails/` 是后续独立 change 的目标目录，**不在本 change 创建**。不修改
`backend/`、`frontend/`、DeerFlow root runtime config、graph route、checkpoint schema、provider policy 或
prompt runtime behavior。
