# Alignment Audit 55 - Cleanup Decision Record

> 类型: 清理判定记录 / alignment deliberation record
> 决策日期: 2026-08-12
> 原始审计证据快照: `65df2571108cc6b4b81f55d3ba8542786a810b39`
> 决策复核时 HEAD: `ac6989abb46b22a9b0cf50e8a53b47341d762750`
> 状态: **DECISIONS CAPTURED - NO ALIGNMENT APPLY AUTHORIZED**
> 权威边界: 本文记录如何分类和路由，不替代 main spec、代码、typed contract、ADR 或
> OpenSpec change

返回[审计总览](alignment-audit-00-current-state.md)，执行顺序见
[60 - Progressive Execution Plan](alignment-audit-60-progressive-execution-plan.md)。

## 为什么保留这份记录

本轮讨论形成的价值不只是一个任务顺序，还包括“凭什么可以清理”和“哪些内容绝对
不能借清理之名修改”。如果只保留 checkbox，后续执行者可能知道要改什么，却忘记：

- “旧”必须由当前事实证伪，不能凭文件年龄或措辞感觉判断；
- 仓库事实由执行者调查，产品方向才由产品 owner 决定；
- 删除、迁移 owner、标 `planned`、标 `dormant` 和隔离冲突是不同动作；
- 文档一致不能靠隐瞒代码缺口或替 unresolved spec conflict 选边完成。

因此本文保存判定依据和已确认产品状态；`60` 只负责按这些决定逐关执行。

`50 - Remediation Roadmap` 保留作 cleanup-first 决定之前的初始问题分解，其中
“先解冲突再清词典”不再是实际执行顺序。当前执行顺序与 checkbox 只以 `60` 为准；
本文解释这次顺序变化的依据。若 `55` 与 `60` 的逐项内容、风险或禁碰边界出现差异，
执行者必须停止并先统一两份记录，不能自行选择较方便的一份。

## 判定权与证据顺序

```text
仓库物理结构 / Git metadata ------------> 当前物理事实
代码 / typed contracts / tests ----------> 当前实现事实
approved main specs / accepted design ----> required behavior
用户明确决定 ----------------------------> 产品方向与取舍
本文 ------------------------------------> 分类、路由和禁止越界
```

执行者负责扫描并判断可验证事实，不把可查证问题推给用户。只有“未落地的方向是否还
值得保留”以及冲突合同应选择哪一侧，才需要产品决定。

## 退役门槛

一项内容只有同时满足下列四项，才能进入 `UNAMBIGUOUS-RETIRE`：

1. 已被当前仓库物理事实、现行合同或真实入口明确否定；
2. 不再拥有 current behavior；
3. 删除或改写不会在 A-003、A-004 等 unresolved conflict 中选边；
4. 有明确替代说法，或者能够证明该概念已无合法当前用途。

任一条件证据不足，必须进入 `QUARANTINE`，不能“顺手修正”。

## 固定 Disposition

| Disposition | 含义 | 允许动作 |
| --- | --- | --- |
| `KEEP` | 内容仍准确且 owner 正确 | 不编辑 |
| `UNAMBIGUOUS-RETIRE` | 当前表述已被直接证伪且无合法当前用途 | 删除最小错误语句或用已验证事实替换 |
| `RELOCATE-LINK-OWNER` | 内容可能仍有效，但放错 authority 层或重复 owner | 从错误层移出，链接唯一 owner |
| `RELABEL-PLANNED` | 仍保留为明确未来方向，但没有 current contract/entry | 标 `planned`，不得写成 current |
| `RELABEL-DORMANT` | 历史方向被保留，但当前不作活跃 roadmap 承诺 | 标 `dormant`，保留历史记录 |
| `QUARANTINE` | 证据不足、语义冲突未决或与冲突文本相交 | 原样隔离，等待独立决定 |
| `DEFERRED-CODE-CHANGE` | 文档决定后仍需要实现或 detector 修改 | 本主线不实施，明确登记缺口 |
| `OPTIONAL-HARDENING` | 当前可以诚实表达，但更强机械证明需要代码 | 校准证明措辞，增强工作另案授权 |

## 首轮清理登记表

以下是已经完成事实调查的最小候选，不是对相似字符串的批量替换许可。

| ID | 候选与位置 | 判定证据 | Disposition / 首轮动作 | 禁碰边界 |
| --- | --- | --- | --- | --- |
| C-001 | `openspec/config.yaml:6-9`、`deep_research_harness/AGENTS.md:3-7`、`openspec/agent-charter/charter.md:9-12` 把根 `backend/` / `frontend/` 称为 upstream mirrors | 根没有这两个目录；`deerflow` 的 Git index mode 是 `160000`；根 `AGENTS.md` 定义真实两层边界 | `UNAMBIGUOUS-RETIRE`：改写为真实 `deerflow/` gitlink boundary | 不扫描 `deerflow/` 源码；不声称已有机械 detector |
| C-002 | `openspec/config.yaml:63,82` 的 proposal/closeout 保护对象仍是旧根目录 | authoring/closeout 规则保护了错误对象 | `UNAMBIGUOUS-RETIRE`：原子改成诚实的 gitlink scope/人工 evidence 语言 | A-002 的 detector、manifest 和 tests 仍 deferred；不能把文案写成机械保护已实现 |
| C-003 | `deep_research_harness/README.md:55-56` 要求 `../backend/packages/harness` | `pyproject.toml` 与 lockfile 使用真实 `../deerflow/backend/packages/harness` | `UNAMBIGUOUS-RETIRE`：修正安装路径 | 真实 `deerflow/backend/...` 路径必须保留 |
| C-004 | `deep_research_harness/CONTEXT.md:336-340` 称 Evaluation Run Workspace 包含 Bundle | Runner 在同一 execution root 创建并列 `workspace/` 与 `bundle/` | `UNAMBIGUOUS-RETIRE`：改为 execution-scoped workspace，不承诺从属布局 | 不改变 runtime layout 或 storage contract |
| C-005 | `CONTEXT.md:515-522` 的 “new Suite” / “V1 structural change must...” 及 `:538-540` 对 archived change 名称的当前依赖 | 对应 Suite、目录、Runner、ignore/structure 工作已经存在；current guidance 已由 spec/policy 拥有 | `UNAMBIGUOUS-RETIRE` + `RELOCATE-LINK-OWNER` | archived change 保留且不编辑；不以 archive 内容作 current authority |
| C-006 | `CONTEXT.md:468-541` 的六个设计章节越过 glossary owner | ADR 0022-0026、main specs 与 local-context policy 已拥有其设计/行为 | 安全部分 `RELOCATE-LINK-OWNER`；词典只保留稳定术语 | `:502-508` Rubric/Runner 段属于 A-003，首轮不得改写或删除其语义 |
| C-007 | `openspec/CONTEXT.md:21-24`、`openspec/agent-charter/README.md:18-19` 和相关 route prose 的 “one/only policy” 排他措辞 | config 的 Focus Card、DRC spec 和 checker 均支持 comma-separated 多 policy | `UNAMBIGUOUS-RETIRE`：改为“一个 trigger 路由一个 canonical policy；一个 change 可触发多个” | 保留最小阅读原则和 route table；不改 checker |
| C-008 | `CONTEXT.md:396-401` 把每个 LLM-bearing node 都有 Suite smoke 写成 current | registry 没有覆盖 targeted evidence、readiness、final delivery；CES V1 只要求有限 case | `RELABEL-PLANNED`：降为 roadmap target，并写明 current registry 范围 | 不新增 case、Runner、test 或 spec requirement |
| C-009 | `CONTEXT.md:417-423` 单独要求 `limited` / `inconclusive` 具有 readable report | ReviewSubmission/ReviewRecord 和 protocol 没有独立 readable-report admission owner | `UNAMBIGUOUS-RETIRE`：移除 current required 语气，不自动转 planned | Review Record 已有的结构化字段保持 current；不新增 report contract |
| C-010 | `CONTEXT.md:443-465` 混写 Support Handoff、Report Export、Local-First TUI 的 current/planned 状态 | final `report.md` artifact 已存在；用户侧 export、handoff、dedicated TUI 没有 current public contract/entry | 按下方产品状态表拆分并标时态 | Support Handoff retention 与 External Run Observation 归 A-004，首轮不得改其寿命答案 |
| C-011 | ADR 0002、0003、0006、0008、0010 缺少足以解释当前适用性的状态 | 正文混有 current 原则、planned surface 与 dormant 产品路线 | 保留正文和历史，补一致 status/applicability note | 不通过改旧 ADR 正文伪造当年的决定；与 A-004 相交部分继续隔离 |

## 逐项调整内容、风险与可能副作用

以下分析以一个 C 编号为最小 adjustment unit。执行时不得用一个 cluster-level 风险说明
替代逐项记录；同一 C 编号若拆成多个不同语义编辑，还要为每个编辑分别记录影响。

### C-001 - 真实 upstream topology

1. **调整内容:** 将 current authority 中“根 `backend/` / `frontend/` 是 DeerFlow
   mirrors”改为“根 `deerflow/` 是只 leverage、不修改的 gitlink”；保留 downstream
   product 在 `deep_research_harness/` 的定义。
2. **主要风险:** 字符串级替换会误伤真实 `deerflow/backend/...` 依赖路径、普通 backend
   领域术语和仍有效的 negative drift guard；分散修改又可能制造 authority 中间态。
3. **可能副作用:** contributor 可能把“gitlink 是边界”误解成可以读取其源码，或误以为
   文案已经提供 gitlink 机械保护；未同步的 main spec 可能暂时与 guide 冲突。
4. **控制:** 使用逐 occurrence 人工分类；在一个获授权 change 内原子同步说明性
   authority；明确“不读源码”和“A-002 detector 未实现”。

### C-002 - Proposal/closeout 的真实保护对象

1. **调整内容:** 将 proposal 与 archive/closeout 文案从保持不存在的旧根目录 clean，改为
   声明普通 change 不拥有 `deerflow/` gitlink，并记录当前能够取得的人工 scope/diff
   evidence。
2. **主要风险:** 只删除旧规则而没有诚实替代，会削弱原本想表达的 upstream boundary；
   反过来，写成“验证 gitlink clean”又会虚构尚不存在的 detector。
3. **可能副作用:** closeout 暂时增加人工核查成本；现有 architecture checker 仍可能对
   真实 gitlink 风险假绿，读者也可能高估 prose rule 的执行力。
4. **控制:** A-002 始终标 `DEFERRED-CODE-CHANGE`；不改 checker/manifest/tests；验证记录
   必须区分人工 evidence 与 mechanical enforcement。

### C-003 - Editable harness 安装路径

1. **调整内容:** 将 README 的 `../backend/packages/harness` 改为仓库实际使用的
   `../deerflow/backend/packages/harness`，并保留正确的执行目录前提。
2. **主要风险:** 忽略命令运行目录会让一个字符串正确但实际不可执行的示例继续存在；
   也不能因路径含 `backend` 再次误判为残渣。
3. **可能副作用:** 仍使用旧 V1 外部布局的个人环境将不再符合文档，但它本来就不是本
   V2 checkout 的受支持物理结构。
4. **控制:** 与 `pyproject.toml`、lockfile 和根运行说明交叉核对；不修改 dependency
   metadata，不泛化为其他安装方式。

### C-004 - Evaluation Workspace / Bundle 关系

1. **调整内容:** 将 Workspace 从“包含 Bundle”收紧为 execution-scoped working
   directory，不在 glossary 中承诺二者的物理父子关系。
2. **主要风险:** 过度抽象可能丢失有用的 execution-scope 含义；过度具体则会再次让
   glossary 绑定易漂移的目录布局。
3. **可能副作用:** 依赖旧措辞理解路径的读者需要改从 owning runtime/spec 查找真实
   layout；其他文档可能暴露新的从属关系残留。
4. **控制:** 只改术语事实，不改 storage/runtime contract；复审 sibling/containment
   相关引用并将新发现登记而非顺手扩大 scope。

### C-005 - 已完成任务时态与 archived slug 依赖

1. **调整内容:** 退役 “new Suite”、“V1 structural change must...” 等已完成任务语气，
   移除 current glossary 对 archived change slug 的依赖，改链 current owner。
2. **主要风险:** 整段删除可能同时移除仍有效的 current invariant 或设计理由；错误链接
   owner 会把历史污染换成另一种 authority duplication。
3. **可能副作用:** CONTEXT 变短后，读者需要跳转 spec/ADR/policy；owner link 未来移动
   可能产生 link rot；历史来源不再直接出现在 current glossary。
4. **控制:** 只删除实施时态和 archived dependency，不删除历史 artifact；为仍有效内容
   提供 canonical owner link，并验证相对链接。

### C-006 - CONTEXT 尾部六个设计章节

1. **调整内容:** 将不属于 glossary 的设计/requirement/policy prose 移回或链接其唯一
   owner，CONTEXT 仅保留稳定词义和必要的 Avoid。
2. **主要风险:** 六段并非全部错误；整块删除会丢掉有效概念，尤其可能暗中删除 A-003
   Rubric/Runner 冲突的一侧证据。
3. **可能副作用:** 信息由单页集中阅读变成按需导航；如果 owner link 不清楚，agent 的
   context discovery 成本可能上升；错误清理还可能让语义冲突“看不见但仍存在”。
4. **控制:** 逐段、逐句 disposition；A-003/A-004 相交内容保持 quarantine；局部复审
   必须证明冲突没有被删除或改写掩盖。

### C-007 - Policy cardinality

1. **调整内容:** 将排他的 “choose one/only policy” 改为“每个 trigger 路由一个
   canonical policy；一个 change 可以因多个 trigger 选择多个 policies”。
2. **主要风险:** 只强调“多个”可能诱导 author 每次加载全部 policy，破坏最小上下文
   原则；遗漏某个排他措辞则仍会让 prose 与 checker 冲突。
3. **可能副作用:** proposal 可能选择更多 review policies，增加 planning/review 成本；
   既有示例可能需要澄清，但 checker 行为本身不会变化。
4. **控制:** 同时保留“only triggered policies”和逐 trigger route；不修改 checker；用
   单 policy 与 multi-trigger 示例人工验证没有变成 all-policy default。

### C-008 - 全节点 Suite smoke coverage

1. **调整内容:** 用实际 registry 范围陈述 current coverage，将全 LLM-bearing node
   coverage 降为没有交付承诺的 roadmap target。
2. **主要风险:** 可能把已经存在的其他 calibration evidence 错写成完全无覆盖，或者把
   roadmap target 写成新的 SHALL/期限承诺。
3. **可能副作用:** 读者对当前 evaluation 完整度的判断会降低，这是诚实校准而非功能
   回退；roadmap target 若没有 owner，可能长期保持未完成状态。
4. **控制:** 列出具体 current registered cases，并区分 Suite case 与其他 evidence
   seam；使用 `target` 而非 required/current 语气，不新增 spec 或 task。

### C-009 - Readable review report 要求

1. **调整内容:** 退役 glossary 对 `limited` / `inconclusive` 独立 readable report 的
   current required 语气；保留 Review Record 已拥有的结构化字段事实。
2. **主要风险:** “没有独立 typed owner”不等于人类可读性不重要；删除措辞可能被误解
   为产品不再关心 review usability。
3. **可能副作用:** 后续实现者可能把结构化 record 自动等同于良好的人类呈现；原本隐含
   的 UX 愿望不再作为 planned commitment 存在。
4. **控制:** 明确退役的是无 owner 的 current requirement，不声称 Review Record 已满足
   独立报告体验；未来若重新需要，必须用独立产品 change 定义。

### C-010 - Capability status 拆分

1. **调整内容:** 保留 current Final Report Artifact；将用户 reopen/copy/export 与
   Support Handoff 标 `planned`；将 Dedicated TUI 及相应 Local-First 路线标 `dormant`。
2. **主要风险:** 状态降级可能被误读为删除现有 `report.md`、取消所有未来 UI 意图，或
   借 Support Handoff 的 planned 状态提前决定 A-004 retention。
3. **可能副作用:** README、CONTEXT 与旧 ADR 会同时出现 current/planned/dormant 三种
   时态，导航复杂度增加；外部读者可能把 dormant 理解为永久否决。
4. **控制:** 分成不同术语和 owner；定义 dormant 为保留历史但无活跃承诺；Support
   Handoff 只决定 capability status，其 Bundle-loss 寿命继续 quarantine。

### C-011 - ADR status/applicability

1. **调整内容:** 为 ADR 0002、0003、0006、0008、0010 增加一致的 status 与 current
   applicability note，不重写原始决定正文。
2. **主要风险:** 事后元数据可能被理解为篡改历史决定，或让 ADR status 越权决定当前
   runtime behavior；不同 ADR 使用不一致 schema 也会制造新残渣。
3. **可能副作用:** 文档工具或读者可能不认识新状态；交叉链接需要区分 historical
   rationale 与 current route；某些 ADR 可能同时含 dormant surface 和 current principle。
4. **控制:** 先定义最小统一 schema；保留正文逐字历史；applicability note 明确链接
   current owner，混合内容按子决定说明而不粗暴整篇标废弃。

## 已确认的产品状态

这些状态来自用户对 Q6-Q10 的明确确认，不是执行者从代码擅自推导的 roadmap：

| 概念 | 已确认状态 | 处理方式 |
| --- | --- | --- |
| Dedicated Deep Research TUI | `dormant` | 从 current 词典退出；历史 ADR 保留并注明 dormant/current route |
| Local-First Deployment（以 dedicated TUI 为首个产品 scope） | `dormant` | 不作为活跃 roadmap 承诺；不抹除历史决定 |
| Support Handoff | `planned` | 保留未来能力方向；当前无 producer/schema/public entry 的事实写清 |
| Final Report Artifact / `report.md` | `current` | 保留并链接 final-delivery owner |
| Primary User Report reopen/copy/export | `planned` | 与 current artifact 拆开，不能由文件存在推导用户能力 |
| 全 LLM-bearing node Suite smoke coverage | roadmap target | 写明 current registry 是有限集合；不冒充已覆盖 |
| 独立 readable review report 要求 | retired | 从 current glossary 移除，不自动变成 planned requirement |

## 隔离登记表

| ID | 隔离内容 | 原因 | 解除条件 |
| --- | --- | --- | --- |
| Q-001 | A-003：CES、EVH、`CONTEXT.md:310-334,502-508`、ADR 0025 的 Rubric/Runner 边界 | current specs 对 criterion IDs 是否可进入 execution admission 给出互斥答案 | 独立产品决定与 OpenSpec change 完成；不能由首轮清理选边 |
| Q-002 | A-004：RER/RUS/REJ、External Run Observation、Support Handoff retention、相关 ADR 的 Bundle-loss 后寿命语义 | external retention 与 Bundle-local-only 合同互斥 | 独立产品决定与 OpenSpec change 完成 |
| Q-003 | `project-structure.toml` 和 project-structure spec 中阻止下游进入 legacy root `backend/` / `frontend/` 的负向 guard | 这些 token 可能仍是有效 drift guard，不等于把目录称为 upstream mirror | A-002 单独设计机械保护时决定；首轮不得全局替换 |
| Q-004 | deployment/local-profile 中的 backend environment、compatibility directory、database/persistence backend | 这些是宿主接口或领域术语，不是已证明的 V1 topology residue | 只有 owning contract 提供反证时才能重分类 |
| Q-005 | A-002 gitlink detector 与 A-009 stronger semantic traceability | 都需要 checker/test/机械机制，不是纯历史概念清理 | 单独代码 change 获得明确授权 |

## Q1-Q20 共识记录

| 问题 | 已确认决定 |
| --- | --- |
| Q1 | 事实判断由执行者扫描完成；先建立有证据的候选登记，证据不足就隔离，不要求用户凭记忆判断 |
| Q2 | 采用四项退役门槛；四项不全满足不得称为确定过时 |
| Q3 | 区分删除、迁移 owner、标 planned 和隔离冲突，不用一种动作处理所有旧内容 |
| Q4 | 保留 archived changes 和历史 ADR；清理它们对 current authority 的污染，不抹掉历史 |
| Q5 | alignment-only 冻结代码、测试、治理执行器、可执行 manifest/TOML 与 `deerflow/`；main specs 只能经显式 OpenSpec 决策修改 |
| Q6 | Dedicated TUI 与其 Local-First 产品路线标 `dormant` |
| Q7 | Support Handoff 保留为 `planned`；其 retention 语义仍隔离到 A-004 |
| Q8 | current Final Report Artifact 与 planned Primary User Report Export 拆开 |
| Q9 | 全节点 cognitive smoke 保留为 roadmap target，不再称 current coverage |
| Q10 | 孤立 readable-report 要求退役，不自动转 planned |
| Q11 | 首轮拆为 `retire-v1-topology-residue` 与 `retire-stale-context-concepts` 两个 change |
| Q12 | 每个候选必须记录证据、disposition、动作、禁碰边界和完成证据 |
| Q13 | 每个 change 后局部复审并停止；两次清理后再做完整只读复审 |
| Q14 | 不重写旧 ADR 正文；只增加统一状态和当前适用性说明 |
| Q15 | A-009 排除出首轮；只校准证明措辞，stronger checker 仍 optional |
| Q16 | 复审发现的新问题不得自动扩大 scope；先登记、分类，再获得授权 |
| Q17 | 清理后仍存在的 A-003、A-004 分别用独立 OpenSpec change 决策 |
| Q18 | CONTEXT 分两次收口：先清安全残渣，语义决定后再同步冲突相关术语 |
| Q19 | 最终允许 A-002 保持 deferred、A-009 保持 optional；诚实披露仍可完成 no-code alignment |
| Q20 | 只授权形成计划，不授权创建或 apply OpenSpec change，也不授权修改代码 |

用户随后明确要求保存上述判断上下文，因此 Q12 的物理存放方式调整为：本文保存完整
决策与证据语义，`60` 引用本文并保存执行 checkbox。这个调整不改变任何产品决定或
实施授权。

## 调查限制与透明性

- 未读取或修改 `deerflow/` 源码；只使用 gitlink metadata、仓库自有材料和公开依赖路径。
- archived changes 不作为 current-state 证据，也不得在整改中修改。一次广域文本搜索曾因
  排除模式不精确返回少量 archive 命中行，但没有主动据此解释 archive，也没有用这些
  命中支撑上述判定。
- 没有把字符串出现次数当成错误数量；每个 `backend` / `frontend` / `V1` 命中必须按
  owner 与语境人工分类。
- A-003、A-004 仍是未决产品合同。本文只决定隔离和后续路由，没有决定任何一侧胜出。

## 本记录的变更规则

本文是有日期的共识记录。后续新证据可以追加 correction 或 superseding decision，但
不得静默改写已经作出的决定。若产品方向改变，应记录：旧决定、新决定、证据/原因、
授权人和影响的执行 Stage。
