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

## C-010.a 后续校正（2026-08-12）

本记录最初将 Primary User Report reopen/copy/export 写为 `planned`。在随后只读核查中，
确认当前只有受控 Bundle 内的 `final/report.md` artifact；公开 lifecycle result、CLI、TUI 和
workbench 均没有 report body/ref 或 reopen/copy/export action，且 current artifact-view spec
明确不列出或推断 final report。产品 owner 随后确认：这项表述应从 current authority 退役，
但不将它预先承诺为 `planned`。

因此，以下 C-010 与产品状态表中的旧 `planned` 结论均由本校正取代：未来若要交付报告
读取、复制或导出，必须由独立产品 change 定义公开入口、授权、读取边界与保留语义。本次
alignment 不创建该承诺，也不改动 artifact publisher、Bundle、public lifecycle API 或主规格。

## C-010.b 审阅确认（2026-08-12）

只读核查确认，现有 Bundle-local Event Journal、终端诊断和本地 developer/operator inspection
是受控的诊断观察，不是可交给支持人员的 Support Handoff：当前没有该 handoff 的 producer、
schema 或 Primary User public entry。产品 owner 确认将 Support Handoff 保留为 `planned`
capability。

这只校准 capability status。Support Handoff 是否能够在 Bundle 删除、不可读或 retention loss
后留存，仍属于 A-004 的互斥产品合同；本轮不得借 `planned` 状态选择 external retention，
也不改动 Event Journal、诊断读取、Bundle lifecycle、main specs 或实现。

## C-010.c 审阅确认（2026-08-12）

现有 `make demo-tui` / `make demo-tui-fake` 是 contributor/operator 的 demo visualizer，
不是 Primary User product interface；当前 Primary User route 是 Dedicated Agent 加 reflected
`deep_research` tool。产品 owner 确认："Dedicated Deep Research TUI 作为 Primary User
interface"及以它为首个产品 scope 的 Local-First Deployment，均为 `dormant`，即保留历史
理由和未来重启可能、但没有 active commitment。

此决定不降级 demo TUI、Dedicated Agent route，或 Cognitive Evaluation Suite 的本地
evaluation surface；后三者分别有 current owner。后续只在 ADR status/applicability note 中
校准历史路线，不重写 ADR 正文、main specs、public route 或实现。

## C-011 审阅确认（2026-08-12）

产品 owner 确认，ADR 0002、0003、0006、0008、0010 不能用一个全局 "obsolete" 标签
粗暴处理。后续仅以统一的后记型 status/applicability note 说明每份历史 ADR 在当前的
阅读方式，保留标题与正文逐字不变，并链接对应的现行 owner；该注记不定义或改写运行时
行为、main spec 或 public contract。

逐份分类为：0002 保留 shared outcome/recovery principle，dedicated Primary-User TUI 为
`dormant`；0003 保留 Deployment Owner 原则，TUI setup path 为 `dormant`；0006 保留安全
脱敏披露，TUI surface 为 `dormant`、Support Handoff 为 `planned`；0008 的 dedicated-TUI
Local-First 首发路线为 `dormant`，不影响现有 Bundle lifecycle/isolation；0010 保留 current
Bundle report artifact，Primary User inspect/copy/export 不是 current，也不在本轮承诺为
`planned`。Support Handoff 的 Bundle-loss 后 retention 继续保持 A-004 quarantine。

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
| C-004 | `deep_research_harness/CONTEXT.md:336-340` 称 Evaluation Run Workspace 包含 Bundle，且未区分它与 DeerFlow host workspace / Deep Research Run Bundle | 主产品 Run Bundle 位于 host workspace；Runner 在 `evals/runs/<execution-id>/` 创建并列 `workspace/` 与 `bundle/` | `UNAMBIGUOUS-RETIRE`：明确三个 owner；evaluation workspace 是 Runner-owned execution directory，Evaluation Bundle 为 sibling | 不改变 runtime layout、storage contract 或 lifecycle authority |
| C-005 | `CONTEXT.md:515-522` 的 “new Suite” / “V1 structural change must...” 及 `:538-540` 对 archived change 名称的当前依赖 | 对应 Suite、目录、Runner、ignore/structure 工作已经存在；current guidance 已由 spec/policy 拥有 | `UNAMBIGUOUS-RETIRE` + `RELOCATE-LINK-OWNER` | archived change 保留且不编辑；不以 archive 内容作 current authority |
| C-006 | 原先将 `CONTEXT.md:468-541` 的六个设计章节视为应迁移的 glossary 过载 | 它们多数是有用的当前上下文；原提议没有指出一个确定错误，且 `:502-508` 触及 A-003 | `WITHDRAWN-NO-ACTION`：不以“精简 CONTEXT”为理由移动或删除这些章节 | 具体错位仍由独立 adjustment 处理；A-003/A-004 继续隔离 |
| C-007 | `openspec/CONTEXT.md:21-24`、`openspec/agent-charter/README.md:18-19` 和相关 route prose 的 “one/only policy” 排他措辞 | config 的 Focus Card、DRC spec 和 checker 均支持 comma-separated 多 policy | `UNAMBIGUOUS-RETIRE`：改为“一个 trigger 路由一个 canonical policy；一个 change 可触发多个” | 保留最小阅读原则和 route table；不改 checker |
| C-008 | `CONTEXT.md:396-401` 把每个 LLM-bearing node 都有 Suite smoke 写成 current | registry 有 8 个 case，未含 targeted evidence、readiness、final delivery；这些节点仍有其他确定性 evidence；CES V1 只要求有限 case | `UNAMBIGUOUS-RETIRE`：清除错误全覆盖 claim；registry 是 current 范围事实来源，不加 roadmap | 不新增 case、Runner、test 或 spec requirement |
| C-009 | `CONTEXT.md:417-423` 单独要求 `limited` / `inconclusive` 具有 readable report | ReviewSubmission/ReviewRecord 和 protocol 没有独立 readable-report admission owner | `UNAMBIGUOUS-RETIRE`：移除 current required 语气，不自动转 planned | Review Record 已有的结构化字段保持 current；不新增 report contract |
| C-010 | `CONTEXT.md:443-465` 混写 Support Handoff、Report Export、Local-First TUI 的 current/planned 状态 | final `report.md` artifact 已存在；用户侧 export、handoff、dedicated TUI 没有 current public contract/entry；demo TUI 是 operator visualizer，current user route 是 Dedicated Agent + reflected tool | 按下方产品状态表拆分：保留 current artifact；退役 export 的 current claim，且不预先标 `planned`；Support Handoff 标 `planned`；Dedicated TUI / Primary-User Local-First 路线标 `dormant` | Support Handoff retention 与 External Run Observation 归 A-004，首轮不得改其寿命答案 |
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

1. **调整内容:** 明确区分 DeerFlow host workspace、位于其中且由 Deep Research 拥有的
   persistent Run Bundle、以及 Runner 在 `evals/runs/` 创建的 Evaluation Run Workspace。
   后者不是 host workspace，不拥有主产品 lifecycle；同一 evaluation execution root 的
   immutable Evaluation Run Bundle 是 sibling，而不是其 child。
2. **主要风险:** 若只改 glossary，会与 evaluation spec/说明文档脱节；若把目录细节作为
   glossary authority，则会把实现布局误固化为概念契约；改名可能影响既有术语映射。
3. **可能副作用:** 读者仍须依靠前缀区分两个 workspace；过去按旧父子关系理解路径的读者
   需转由 owning runtime/spec 了解布局；复审可能发现更多 owner/containment 残留。
4. **控制:** 只改术语事实，不改 storage/runtime contract；与两个 main spec 交叉核对；
   不扫描 DeerFlow 源码；新发现登记而非顺手扩大 scope，若需 runtime 或 API 改动即停止。

### C-005 - 已完成任务时态与 archived slug 依赖

1. **C-005.a 调整内容（已审，限 planning）:** 退役 “new Suite”、“V1 structural
   change must...” 等已完成任务语气。`evals/control/`、被忽略的 `evals/runs/`、Runner
   source 与 `tests/eval/` 均是当前已落地事实，保留或链接其 canonical owner。
2. **C-005.a 主要风险与控制:** 整段删除可能同时移除仍有效的 control/run-data separation
   invariant。只删除实施时态；若一句同时含当前 invariant 和历史任务，拆句后再审，不能
   整段删除。
3. **C-005.b 调整内容（已审，限 planning）:** 移除 current glossary 中“该纪律来自
   archived plan”的来源宣称；保留 seam-first 规则与现行 `local-context` policy 指针。
   closed plan 只保留历史追溯价值，不再承担 current authority。不得因已审而自动实施。
4. **共同副作用:** CONTEXT 变短后读者需要跳转 spec/ADR/policy；错误链接可能造成新的
   authority duplication 或 link rot。保留历史 artifact，不改写 archive，并验证相对链接。

### C-006 - CONTEXT 尾部六个设计章节

1. **判定（撤回，无动作）:** 原提议没有识别出确定事实错误，只是认为六段设计说明不应
   位于 CONTEXT。用户与审计者确认，这不足以成为 cleanup 范围。
2. **理由与风险:** 这些文字多数仍是有用上下文；广泛迁移会增加 scope，可能删除有价值的
   人/agent 导航信息，并掩盖 A-003 Rubric/Runner 的未决语义。
3. **结果:** 不移动、不删除、不为本项建立 Stage 2 planning 或 apply task。C-004/C-005
   的具体已审错误仍各自处理；今后发现具体错位时，另建独立 adjustment。
4. **隔离:** A-003/A-004 未因此解决，继续保持 quarantine，不能借“本项撤回”改写或删除
   其相关文字。

### C-007 - Policy cardinality

1. **调整内容（已审，限 planning）:** 将排他的 “choose one/only policy” 改为“每个
   trigger 路由一个 canonical policy；一个 change 可因多个 trigger 选择多个 policy”。
   一个 primary module / causal owner 仍然唯一。
2. **主要风险与控制:** 只强调“多个”会诱导 author 默认加载全库。同步保留“所有且仅所有
   被 trigger 的 policy”和逐 trigger route；不修改 checker，用单 trigger 与 multi-trigger
   示例人工验证。
3. **可能副作用:** proposal 会更诚实地列出已被 checker 支持的多个 review records，
   planning/review 成本更显性；这是既有合同的暴露，不是新增行为。

### C-008 - 全节点 Suite smoke coverage

1. **调整内容（已审，限 planning）:** 清除“每个 LLM-bearing node 都有 Suite smoke”的
   错误 current claim；保留 Smoke Scenario 定义，以 versioned case registry 为 current
   范围事实来源。
2. **主要风险与控制:** 不得将未注册 Suite case 错写为没有任何 evidence；必须区分 Suite
   case 与其他 deterministic/calibration seam。只删除错误 claim，不写 roadmap、期限、
   future case 或新的 SHALL。
3. **可能副作用:** 读者对当前 Suite 完整度的判断更准确；这不是功能回退，不删除已有
   case、Runner、测试或其他 evidence。

### C-009 - Readable review report 要求

1. **调整内容（已审，限 planning）:** 退役 glossary 对 `limited` / `inconclusive` 独立
   readable report 的 current required 语气；保留 Review Record 已拥有的结构化字段事实，
   以及二者不得静默计作 `pass`。
2. **主要风险:** “没有独立 typed owner”不等于人类可读性不重要；删除措辞可能被误解
   为产品不再关心 review usability。
3. **可能副作用:** 后续实现者可能把结构化 record 自动等同于良好的人类呈现；原本隐含
   的 UX 愿望不再作为 planned commitment 存在。
4. **控制:** 明确退役的是无 owner 的 current requirement，不声称 Review Record 已满足
   独立报告体验；未来若重新需要，必须用独立产品 change 定义。

### C-010 - Capability status 拆分

1. **调整内容:** 保留 current Final Report Artifact；退役用户 reopen/copy/export 的 current
   capability claim，但不将其预先标为 `planned`；将没有 current producer/schema/public entry
   的 Support Handoff 标为 `planned`；Dedicated
   TUI 及相应 Local-First 路线标 `dormant`。
2. **主要风险:** 状态降级可能被误读为删除现有 `report.md`、取消所有未来 UI 意图，或
   借 Support Handoff 的 planned 状态提前决定 A-004 retention。
3. **可能副作用:** README、CONTEXT 与旧 ADR 会同时出现 current/planned/dormant 三种
   时态，导航复杂度增加；外部读者可能把 dormant 理解为永久否决。
4. **控制:** 分成不同术语和 owner；明确 report export 目前没有 public entry，也没有
   本次产生的 future commitment；定义 dormant 为保留历史但无活跃承诺；Support Handoff
   只决定 capability status，其 Bundle-loss 寿命继续 quarantine。

### C-011 - ADR status/applicability

1. **调整内容（已审，限 planning）:** 为 ADR 0002、0003、0006、0008、0010 增加一致的
   后记型 status 与 current applicability note，不重写标题或原始决定正文。0002、0003、
   0006 与 0010 按子决定分别说明 current/dormant/planned/non-current；0008 的 dedicated
   TUI Local-First 路线标 `dormant`，不影响现有 Bundle lifecycle/isolation。
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
| Dedicated Deep Research TUI（Primary User product interface） | `dormant` | 从 current 词典退出；历史 ADR 保留并注明 dormant/current route；不影响 demo TUI visualizer |
| Local-First Deployment（以 dedicated TUI 为首个产品 scope） | `dormant` | 不作为活跃 roadmap 承诺；不抹除历史决定；不影响 Cognitive Evaluation 的 local evaluation surface |
| Support Handoff | `planned` | 保留未来能力方向；当前无 producer/schema/public entry。Bundle-loss 后能否留存仍由 A-004 决定 |
| Final Report Artifact / `report.md` | `current` | 保留并链接 final-delivery owner |
| Primary User Report reopen/copy/export | 不属于 current capability，也不在本轮预先承诺为 `planned` | 与 current artifact 拆开；退役 current claim。将来如需该能力，另开产品 change 定义 public entry、授权与保留语义 |
| 全 LLM-bearing node Suite smoke coverage | roadmap target | 写明 current registry 是有限集合；不冒充已覆盖 |
| 独立 readable review report 要求 | retired | 从 current glossary 移除，不自动变成 planned requirement |

## 隔离登记表

| ID | 隔离内容 | 原因 | 解除条件 |
| --- | --- | --- | --- |
| Q-001 | A-003：CES、EVH、`CONTEXT.md:310-334,502-508`、ADR 0025 的 Rubric/Runner 边界 | 已于 2026-08-12 选择 criterion IDs 仅可作为 admission control-integrity metadata；spec 仍须经独立 change 收口 | 独立 OpenSpec change 完成；不得扩大至 Rubric content、model input 或 quality verdict |
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
| Q8 | 初始决定为将 current Final Report Artifact 与 planned Primary User Report Export 拆开；已由上方 **C-010.a 后续校正（2026-08-12）** 取代：export 不是 current，且本轮不将其承诺为 planned |
| Q9 | 全节点 cognitive smoke 保留为 roadmap target，不再称 current coverage |
| Q10 | 孤立 readable-report 要求退役，不自动转 planned |
| Q11 | 首轮拆为 `retire-v1-topology-residue` 与 `retire-stale-context-concepts` 两个 change |
| Q12 | 每个候选必须记录证据、disposition、动作、禁碰边界和完成证据 |
| Q13 | 每个 change 后局部复审并停止；两次清理后再做完整只读复审 |
| Q14 | 不重写旧 ADR 正文；只增加统一状态和当前适用性说明。C-011 已确认必须逐 ADR、逐子决定说明，不使用全局 obsolete 标签 |
| Q15 | A-009 排除出首轮；只校准证明措辞，stronger checker 仍 optional |
| Q16 | 复审发现的新问题不得自动扩大 scope；先登记、分类，再获得授权 |
| Q17 | 清理后仍存在的 A-003、A-004 分别用独立 OpenSpec change 决策 |
| Q18 | CONTEXT 分两次收口：先清安全残渣，语义决定后再同步冲突相关术语 |
| Q19 | 最终允许 A-002 保持 deferred、A-009 保持 optional；诚实披露仍可完成 no-code alignment |
| Q20 | 只授权形成计划，不授权创建或 apply OpenSpec change，也不授权修改代码 |

## A-003 后续产品决定（2026-08-12）

用户在逐项审阅 15/16 时选择 **A-003 Option A**。唯一允许跨入 execution admission 的
Rubric 信息是 identity 与 criterion IDs，目的仅为 case/fixture 的 control-integrity 校验。
Rubric criteria 正文不得进入 model-facing input；Runner 不得以 Rubric 产生 quality verdict。

Option B（Rubric 完全 review-only、admission 不解析 criteria）已明确排除。该决定来自产品
边界判断，不是由当前代码反向决定规格。仍须在 `reconcile-evaluation-rubric-authority` 的独立
OpenSpec change 中形成 delta/main-spec 一致语言；本记录不授权创建、apply 或实现该 change。

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
- A-003 已于 2026-08-12 选定 Option A，仍待独立 OpenSpec change 将 specs 收口；A-004
  仍是未决产品合同。本文不会代替后续 change 或实现工作。

## 本记录的变更规则

本文是有日期的共识记录。后续新证据可以追加 correction 或 superseding decision，但
不得静默改写已经作出的决定。若产品方向改变，应记录：旧决定、新决定、证据/原因、
授权人和影响的执行 Stage。
