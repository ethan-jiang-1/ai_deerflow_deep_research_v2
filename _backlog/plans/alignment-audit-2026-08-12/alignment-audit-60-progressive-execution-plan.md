# Alignment Audit 60 - Alignment-Only Progressive OpenSpec Plan

> 类型: 对齐计划 / Progressive checkbox ledger
> 计划日期: 2026-08-12
> 审计证据快照: `65df2571108cc6b4b81f55d3ba8542786a810b39`
> 执行基线: 尚未锁定；开始每个 Stage 时重新记录 HEAD
> 当前状态: **PLAN ONLY - NOT AUTHORIZED TO APPLY**
> 当前 active OpenSpec change: **none**

返回[审计总览](alignment-audit-00-current-state.md)。详细证据见
[规格/实现审计](alignment-audit-10-spec-implementation.md)、
[CONTEXT 审计](alignment-audit-20-context.md)、
[OpenSpec 治理审计](alignment-audit-30-openspec-governance.md)和
[验证记录](alignment-audit-40-verification.md)。

## 先回答关键问题

**对齐本身默认不改应用代码。** 本计划的目标不是把代码改到某份文档想象的样子，也
不是把文档改到互相看起来一致；目标是让每一层诚实地表达同一组已决定的事实、required
behavior、当前能力和未完成缺口。

本计划冻结：

- `deep_research_harness/src/`、`scripts/`、`tests/`、runtime assets 与 dependency metadata；
- `openspec/governance/*.py`、guardrail Python、checker tests 与任何可执行脚本；
- public API、graph、typed domain contracts、storage、evaluation Runner 行为；
- `deerflow/` gitlink 和 submodule worktree。

在单独授权某个 Stage 后，本计划只允许修改：

- 由 OpenSpec CLI 创建的 proposal/design/delta specs/tasks；
- 经 change 决策批准后的 main spec 同步；
- `CONTEXT.md`、ADR 状态/措辞、README、AGENTS/Charter/policy 等说明性 authority；
- `openspec/config.yaml` 中的 authoring context/rules；
- 只表达结构事实、且不会偷偷改变 checker 行为的声明性 inventory。

如果真正对齐要求修改 Python、测试、runtime contract 或机械 detector，本计划必须标记
`DEFERRED-CODE-CHANGE`，不能勾成 resolved。以后是否另开实施 change，由用户单独决定。

## Honest Alignment 判准

### 三类权威不能混成一种

| 层 | 它能决定什么 | 不能做什么 |
| --- | --- | --- |
| 实现、typed contracts、tests | 当前代码实际上做什么 | 不能仅因存在就自动决定产品应该做什么 |
| approved main specs / accepted design | required behavior 应该是什么 | 不能假称尚未实现的 behavior 已经存在 |
| CONTEXT / ADR / config / guides | 术语、取舍、change 路由、current/planned 状态 | 不能单独创造 runtime behavior 或掩盖 spec/code mismatch |

### 每个 finding 只能落入以下 disposition

| Disposition | 含义 | 对齐 plan 能否直接处理 |
| --- | --- | --- |
| `ALIGNED-AS-IS` | 各层已经一致 | 保持，不编辑 |
| `TERMINOLOGY-FIX` | 事实一致，名称、时态或表述错误/含糊 | 可以，只改语言 owner |
| `AUTHORITY-CLARIFICATION` | 多份文档重复或越权，但不改变 behavior | 可以，收回唯一 owner |
| `SPEC-DECISION` | 两份 current specs 或 spec/code 对 required behavior 无唯一答案 | 可以做决策与 spec 同步；不能伪装成纯措辞 |
| `DEFERRED-CODE-CHANGE` | 选定 required behavior 后，当前实现/门禁仍不满足 | 本计划不实现，只保留明确缺口 |
| `OPTIONAL-HARDENING` | 当前事实可以诚实对齐，但更强机械证明需要代码 | 本计划只校正证明强度，不实现 checker |

### 不允许的“假对齐”

- 不把所有 spec 改成当前代码，仅为了消除 diff。
- 不把代码没有的 Report Export、Support Handoff、Primary User TUI 写成 current。
- 不把 `@impl` 标签覆盖写成逐 scenario 语义证明。
- 不因为 architecture checker green，就说真实 gitlink 已被保护。
- 不删除 conflicting requirement 而不记录谁作了 product decision。
- 不在 CONTEXT 中用新术语绕开 unresolved spec conflict。

## Mismatch Ledger - 到底哪些没对齐

这是本计划的核心账本。每项都列出参与方、当前可证明事实和 alignment-only 能做到的
边界。

### A-001 - V2 topology 语言错位

**没对齐的各方:** 根 `AGENTS.md` 与 Git index 认定 `deerflow/` 是 gitlink；
`openspec/config.yaml`、local AGENTS、Charter/policy、7 份 main specs、structure prose 和
README 仍把根 `backend/` / `frontend/` 当 upstream mirrors。

**当前事实:** 根没有 `backend/` / `frontend/`；editable harness 位于
`../deerflow/backend/packages/harness`。

**Disposition:** `TERMINOLOGY-FIX` + `AUTHORITY-CLARIFICATION`。

**可无代码对齐:** 把 current non-archive authority 与安装文案统一到真实 gitlink；只对
root path 语义做人工分类，不替换 database/persistence backend 普通术语。

**不能顺手声称:** gitlink 已获得机械防修改保护；那属于 A-002。

### A-002 - upstream guardrail 假绿

**没对齐的各方:** architecture checker/manifest 扫描不存在的 `backend` / `frontend`；
真实 upstream boundary 是 `deerflow` gitlink；绿色输出却容易被理解为真实边界受保护。

**当前事实:** checker 的证明对象错误，真实 gitlink shape/diff 没有等价 detector。

**Disposition:** `DEFERRED-CODE-CHANGE`。

**可无代码对齐:** config/spec/guide 必须如实写“ordinary change 不拥有 gitlink”，验证
报告必须写“当前没有机械证明”，不能再宣称 architecture green 覆盖此边界。

**不能无代码完成:** gitlink mode、submodule diff、closeout detector 需要 checker/test
修改。本 plan 保留 A-002 open；若用户以后授权，另开
`harden-upstream-gitlink-guardrail` 实施 change。

### A-003 - Rubric / Runner authority 冲突

**没对齐的各方:** CES 与 CONTEXT 说 Rubric 不是 execution input；较新的 EVH 与当前
admission/typed fixtures 会读取、绑定 criterion IDs。

**当前事实:** Runner 不产生 cognitive verdict，但 execution admission 读取 Rubric
criteria 并让 scenario fixture 携带 review criteria。

**Disposition:** `SPEC-DECISION`，不是普通术语修正。

**可无代码对齐的前提:** 产品决定接受当前边界：criterion IDs 是 case control-integrity
metadata，Rubric content 不面向 model、不决定 output/verdict。随后同步 CES、EVH、ADR
0025 与 CONTEXT，代码保持不变。

**另一种决定:** 如果 required behavior 坚持 review-only Rubric、execution 完全不读取
criteria，则当前实现不满足；标记 `DEFERRED-CODE-CHANGE`，本 plan 不改代码，也不能
将 A-003 勾为 resolved。

### A-004 - Bundle loss 后诊断留存冲突

**没对齐的各方:** RER 与 External Run Observation 词条允许 external diagnostic
outlive Bundle；RUS/REJ 与当前 implementation/tests 坚持 Bundle-local only。

**当前事实:** supported inspection 在 Bundle loss 后返回 unavailable，不读取 external
copy；当前没有 external lifecycle diagnostic owner。

**Disposition:** `SPEC-DECISION`。

**可无代码对齐的前提:** 产品接受当前 Bundle-local-only contract，随后修正 RER 与
CONTEXT/ADR，使 bytes retention、supported reader、participant presentation 三个问题都
得到同一个答案。

**另一种决定:** 如果 required behavior 要保留 external diagnostic，则需要新 typed
owner、retention/redaction、authorization、reader 和 tests；标记
`DEFERRED-CODE-CHANGE`，本 plan 不实现。

### A-005 - 应用 CONTEXT 越过词典边界

**没对齐的各方:** `deep_research_harness/CONTEXT.md` 尾部复制 ADR/spec/policy/archived
change；Workspace 词条又与真实 sibling `workspace/` / `bundle/` 关系不符。

**当前事实:** 这是词典所有权和术语事实错误，不需要改变 runtime。

**Disposition:** `TERMINOLOGY-FIX` + `AUTHORITY-CLARIFICATION`。

**可无代码对齐:** 删除重复设计章节、链接唯一 owner、修正 Workspace 定义、给相关 ADR
补 current/planned/superseded 状态。

### A-006 - Cognitive Evaluation 过度承诺

**没对齐的各方:** CONTEXT 说每个 LLM-bearing node 都有 Suite smoke，registry 当前未
覆盖 targeted evidence/readiness/final delivery；CONTEXT 又要求 limited/inconclusive
readable report，而 ReviewSubmission/Record/protocol 没有该字段/门禁。

**当前事实:** Suite case coverage 是有限集合；四态 Review Record 已实现，但没有
typed readable-report contract。

**Disposition:** `TERMINOLOGY-FIX`。

**可无代码对齐:** 写出实际 registry 范围；把全节点 coverage 标成 target；删除
readable report 的 required 语气，除非未来另开 product change 实现它。

### A-007 - current / planned 产品能力混写

**没对齐的各方:** final report artifact 已存在；Primary User Report Export、Support
Handoff 和 dedicated TUI 的正向 public contract/entry 并不存在或明确 planned；CONTEXT
却混用 current 语气。

**当前事实:** current route 是 Dedicated Agent + reflected tool；final `report.md` 是
artifact，不等于用户 export capability。

**Disposition:** `TERMINOLOGY-FIX`。

**可无代码对齐:** 拆分 `Final Report Artifact (current)` 与 `Research Report Export
(planned)`；Support Handoff/Local-First TUI 同样标 planned，保留未来目标但不冒充现状。

### A-008 - policy 基数术语错位

**没对齐的各方:** OpenSpec CONTEXT/Charter 说 choose one policy；config、DRC spec 与
checker 支持 comma-separated 多 policy。

**当前事实:** 一个 trigger 路由到一个 canonical policy；一个 change 可以触发多个
policies。

**Disposition:** `TERMINOLOGY-FIX`。

**可无代码对齐:** 只修正 glossary/route prose，不改变 checker。

### A-009 - `@impl` 证明强度错位

**没对齐的各方:** checker 实际只收集测试 docstring ID set；“requirement coverage
passed”容易被外推为逐 requirement/scenario semantic traceability。

**当前事实:** ID inventory 完整；assertion semantic binding 不是全局机器强制。

**Disposition:** `OPTIONAL-HARDENING`。

**可无代码对齐:** 所有报告、policy/spec 只声称 ID-level traceability，不声称语义完全
等价；保留 audit limitation。

**不能无代码完成:** stronger mapping schema、detector 和 tests。若以后需要，另开
`harden-high-risk-semantic-traceability`；本 plan 不将它作为“文档对齐已完成”的必要
伪装。

## 预计结果

在“不改代码”规则下：

- A-001、A-005、A-006、A-007、A-008 可以完整对齐；
- A-003、A-004 只有在明确接受当前实现所代表的 product contract 后才能完整对齐；
- A-002 不能机械闭环，只能诚实暴露并留作 deferred code change；
- A-009 可以对齐证明措辞，但 stronger enforcement 仍是 optional code hardening。

因此本计划的诚实目标不是强行得到 `9/9 resolved`，而是得到：**所有层不再互相撒谎，
每个仍开放的机械/实现缺口有名称、owner、原因和单独授权边界。**

## Progressive Stages

一次只允许一个 active OpenSpec change。前一 Stage archive 或明确 deferred 后，才能创建
下一 change。

| Stage | Change | 覆盖 | 是否改代码 | 初始状态 |
| --- | --- | --- | --- | --- |
| 0 | 无 | 规则/决策 | 否 | `[ ] Awaiting authorization` |
| 1 | `align-v2-topology-language` | A-001；记录 A-002 | 否 | `[ ] Not started` |
| 2 | `reconcile-evaluation-rubric-authority` | A-003 | 否；否则 defer | `[ ] Not started` |
| 3 | `reconcile-post-loss-diagnostic-authority` | A-004 | 否；否则 defer | `[ ] Not started` |
| 4 | `normalize-context-language-and-status` | A-005..A-008 | 否 | `[ ] Blocked by Stages 2-3` |
| 5 | 无，做只读 re-audit | A-001..A-009 | 否 | `[ ] Blocked by Stages 1-4` |

## Stage 0 - Authorization And Disposition Lock

### 已完成的准备

- [x] 0.1 建立 A-001..A-009 审计证据与统一报告集。
- [x] 0.2 在审计快照完成 deterministic baseline：fast 2494、integration 237 passed /
  4 skipped、workflow 35、OpenSpec strict 49/49。
- [x] 0.3 写明 alignment-only 不改代码规则与每项 mismatch ledger。

### 未授权事项

- [ ] 0.4 用户明确授权“只创建 Stage 1 的 OpenSpec planning artifacts”。
- [ ] 0.5 记录当时 HEAD、worktree 与 `openspec list --json`；若有其他 active change 或
  overlapping user edits，停止，不覆盖。
- [ ] 0.6 重验 A-001/A-002 当前事实；外部提交已经解决的内容标 `resolved externally`。
- [ ] 0.7 书面确认 Stage 1 frozen paths 包含全部 Python、tests 与 `deerflow/`。

### Gate 0

- [ ] 只获得 planning 授权，尚未获得 apply 授权。
- [ ] 当前基线和无关用户修改均已记录。
- [ ] 未创建或修改任何代码/测试。

**Gate 0 未通过时停止。**

## Stage 1 - Align V2 Topology Language

**Change:** `align-v2-topology-language`

### Planning checklist

- [ ] 1.1 用 `openspec new change "align-v2-topology-language"` 创建 scaffold，不手工建
  change directory。
- [ ] 1.2 按 `status` / `instructions` 创建 proposal、design、delta specs、tasks。
- [ ] 1.3 Focus Card owner 是 V2 repository topology language，不是 architecture checker。
- [ ] 1.4 Proposal 明确：A-001 要关闭；A-002 保持 open/deferred，不声称添加 detector。
- [ ] 1.5 列出所有 root-path 旧引用，并排除 database/persistence backend 普通术语、
  archives 与 `deerflow/` 源码。
- [ ] 1.6 Delta requirements 只描述真实 physical boundary 与 change scope，不承诺当前
  checker 尚未实施的 gitlink/diff enforcement。
- [ ] 1.7 Tasks 只包含 spec/config/CONTEXT/guide/README/声明性 inventory 的语言同步与
  只读验证；没有 Python/test task。
- [ ] 1.8 `openspec validate align-v2-topology-language --strict` 通过并完成人工 plan review。
- [ ] 1.9 单独获得 Stage 1 apply 授权。

### Alignment checklist（未授权）

- [ ] 1.10 同步 config、local guide、Charter/policy 与相关 specs 的 upstream topology。
- [ ] 1.11 修正 README harness path；保持 `pyproject.toml` 不变。
- [ ] 1.12 对 structure inventory 的每个候选改动证明不会触发 checker 扫描 DeerFlow；
  无法证明则不改，并记录 deferred inconsistency。
- [ ] 1.13 搜索 active non-archive authority，人工分类所有残余 root-path phrase。
- [ ] 1.14 运行现有只读 governance/strict/full verify；不为使其通过改代码或 tests。
- [ ] 1.15 Archive 后重新审计 A-001/A-002：A-001 可 resolved，A-002 必须仍明确 open。

### Gate 1

- [ ] 所有说明性 authority 对真实 V2 topology 给出同一个答案。
- [ ] 没有声称 architecture green 已保护 gitlink。
- [ ] No-code scoped diff 已复核；change 已 archive；无 active change。

## Stage 2 - Reconcile Rubric Authority Without Code

**Change:** `reconcile-evaluation-rubric-authority`

### Decision checklist

- [ ] 2.1 重新取证 CES、EVH、ADR 0025、CONTEXT 与当前 admission/Runner。
- [ ] 2.2 分开定义 identity、criterion IDs、Rubric content、model input、quality verdict。
- [ ] 2.3 产品 owner 选择：
  - [ ] 接受当前 behavior，并把 criterion IDs 定义为 execution admission 的 control
    integrity metadata；或
  - [ ] 坚持完全 review-only，A-003 标 `DEFERRED-CODE-CHANGE`，停止本 Stage 的
    spec sync。
- [ ] 2.4 记录 rejected alternative 与为什么这不是“为了配合代码而改 spec”。

### OpenSpec checklist（未授权）

- [ ] 2.5 无 active change后使用 CLI scaffold，完成 proposal/design/deltas/tasks。
- [ ] 2.6 Deltas 让 CES/EVH 只有一个答案，并明确 Runner 不产生 quality verdict、Rubric
  content 不进入 model-facing input。
- [ ] 2.7 Tasks 只同步 specs/ADR/CONTEXT；不改 typed contracts、Runner、subjects 或 tests。
- [ ] 2.8 Strict validate、人工 plan review、单独 apply 授权。
- [ ] 2.9 Apply 后运行现有 focused/full verification；若现有代码不满足选定 spec，停止并
  标 deferred，不能改代码补绿。
- [ ] 2.10 Archive 并复审 A-003。

### Gate 2

- [ ] A-003 resolved，或诚实标记 deferred code change；不得处于含糊中间态。
- [ ] Specs、ADR、CONTEXT 不再给出互斥答案。
- [ ] No-code scoped diff；无 active change。

## Stage 3 - Reconcile Post-Loss Diagnostic Authority Without Code

**Change:** `reconcile-post-loss-diagnostic-authority`

### Decision checklist

- [ ] 3.1 重新取证 RER、RUS、REJ、CONTEXT/ADR 与当前 Bundle deletion behavior。
- [ ] 3.2 分别回答 bytes retention、supported reader、participant presentation。
- [ ] 3.3 产品 owner 选择：
  - [ ] 接受当前 Bundle-local-only contract；或
  - [ ] 要求 external diagnostic，A-004 标 `DEFERRED-CODE-CHANGE`，停止 spec sync。
- [ ] 3.4 无论选择哪侧，都保留 unavailable/no-recovery/no-authority invariants。

### OpenSpec checklist（未授权）

- [ ] 3.5 CLI scaffold，完成 proposal/design/RER-RUS-REJ deltas/tasks。
- [ ] 3.6 Tasks 只同步 specs/CONTEXT/ADR，不添加 store/schema/reader/tests。
- [ ] 3.7 Strict validate、人工 plan review、单独 apply 授权。
- [ ] 3.8 Apply 后运行现有 deletion/inspection/full verification；不改代码修结果。
- [ ] 3.9 Archive 并复审 A-004 与 Support Handoff status。

### Gate 3

- [ ] A-004 resolved，或诚实标记 deferred code change。
- [ ] RER/RUS/REJ 对三层 retention/readability/presentation 没有互斥答案。
- [ ] No-code scoped diff；无 active change。

## Stage 4 - Normalize Terms, Ownership, And Status

**Change:** `normalize-context-language-and-status`

**前置条件:** Stages 2-3 已作出决定或明确 deferred；CONTEXT 不替 unresolved spec 选边。

### Planning checklist

- [ ] 4.1 为每个词条建立 disposition：keep / tighten / mark planned / move to owner /
  remove duplicate。
- [ ] 4.2 Current capability 必须有 owning spec + real entry；否则标 planned/target。
- [ ] 4.3 readable Review report 若仍是未来要求，移出 current glossary；不在此 Stage
  创建 runtime contract。
- [ ] 4.4 定义 ADR status schema，至少复核 0002、0003、0006、0008、0010。
- [ ] 4.5 CLI scaffold，完成 docs-only proposal/design/deltas/tasks、strict validation、
  人工 review与单独 apply 授权。

### Alignment checklist（未授权）

- [ ] 4.6 删除应用 CONTEXT 尾部 6 个非词典章节，保留其 owning ADR/spec/policy。
- [ ] 4.7 修正 Workspace sibling relationship。
- [ ] 4.8 按 registry 实际范围描述 Suite smoke；全节点 coverage 标 target。
- [ ] 4.9 删除 limited/inconclusive readable report 的 current required 语气。
- [ ] 4.10 拆分 current Final Report Artifact 与 planned Report Export；Support Handoff、
  Local-First TUI 同样显式标状态。
- [ ] 4.11 修正 policy cardinality 术语，不改 checker。
- [ ] 4.12 给相关 ADR 加一致状态，不改行为决定内容。
- [ ] 4.13 运行现有 docs/governance/full verify；不新增 lint/checker 代码。
- [ ] 4.14 Archive 并复审 A-005..A-008。

### Gate 4

- [ ] CONTEXT 只定义语言，不复制 spec/ADR/task，不创造 runtime behavior。
- [ ] Current/planned 状态有 owner；A-005..A-008 resolved。
- [ ] No-code scoped diff；无 active change。

## Stage 5 - Final Honest Re-Audit

本阶段默认不创建 change，只读复审。

- [ ] 5.1 锁定最终 HEAD，确认无 active change、`deerflow/` 未修改。
- [ ] 5.2 运行 OpenSpec doctor/strict 与 `UV_OFFLINE=1 make verify`；记录 skips/warnings。
- [ ] 5.3 对 A-001..A-009 逐项重新取证，不因 change archived 自动勾 resolved。
- [ ] 5.4 确认 A-002 仍被清楚标为 mechanical guardrail gap，除非另一个获授权 code
  change 已真实实现 detector。
- [ ] 5.5 确认 A-009 只声称 ID traceability；stronger mapping 未实现时仍标 optional。
- [ ] 5.6 确认 A-003/A-004 的 disposition 与实际 product decision / code 状态一致。
- [ ] 5.7 更新 `alignment-audit-00-current-state.md` 的最终矩阵，但保留原审计快照历史。
- [ ] 5.8 若仍有 spec/code required-behavior gap，建立明确 deferred backlog，不修改代码。
- [ ] 5.9 只有所有 no-code alignment 项完成且开放 gap 均被诚实记录，才关闭本 plan。

### Definition Of Done

- [ ] 文档之间不再互相矛盾，也不再与已验证的 current behavior 相矛盾。
- [ ] Main spec 的每次变化都有明确 product decision，不是静默追随代码。
- [ ] 未实现能力全部标 planned/deferred，不冒充 current。
- [ ] 未实现 detector/traceability 全部标 open/optional，不冒充 mechanical proof。
- [ ] 整个 alignment 主线没有修改 Python、tests、runtime contracts 或 DeerFlow。
- [ ] 全量验证结果被如实记录；绿色范围没有被夸大。

## 每个 OpenSpec Change 的固定 No-Code Gate

- [ ] 开始前 `openspec list --json` 无另一个 active change。
- [ ] 必须用 `openspec new change <slug>` scaffold。
- [ ] Proposal Focus Card 写清唯一 owner、question、adjacent contracts、evidence、non-goals
  与 triggered policies。
- [ ] Design 分开 current fact、accepted decision、unresolved/deferred。
- [ ] Delta requirements 不承诺本 change 不会实现的 checker/runtime behavior。
- [ ] Tasks 中不得出现 Python、tests、runtime assets、dependency 或 DeerFlow edit。
- [ ] Planning artifacts strict-valid并经人工批准后，才可 apply。
- [ ] Apply diff 只含授权的 specs/context/config/guides/ADR/README/inventory prose。
- [ ] 现有 focused/full tests 只运行不修改；失败时停止并重新分类。
- [ ] Archive 后重新 strict validate，并确认无 active change再进入下一 Stage。

## 停止条件

出现任一条件立即停止：

- 需要修改应用/治理 Python或 tests 才能使选定 spec 成立；
- 需要读取或修改 DeerFlow 源码；
- 只能通过删除失败 requirement 或弱化事实措辞来“变绿”；
- product owner 尚未选择 A-003/A-004 的 required behavior；
- 另一个 active change 或用户修改与当前 authority cluster 重叠；
- baseline failure owner 不明；
- 计划开始实现 Report Export、Support Handoff、Primary User TUI、gitlink detector 或
  stronger traceability checker。

## 下一动作

当前唯一允许的下一动作是评审本计划。得到明确授权前，不创建 OpenSpec change，不修改
spec、CONTEXT、config、ADR、guide，更不会修改代码或 tests。
