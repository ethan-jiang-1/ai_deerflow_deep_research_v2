# Alignment Audit 60 - Cleanup-First Progressive OpenSpec Plan

> 类型: 对齐执行计划 / Progressive checkbox ledger
> 计划日期: 2026-08-12
> 原始审计证据快照: `65df2571108cc6b4b81f55d3ba8542786a810b39`
> 计划重排时 HEAD: `ac6989abb46b22a9b0cf50e8a53b47341d762750`
> 执行基线: 尚未锁定；开始每个 Stage 时重新记录 HEAD
> 当前状态: **PLAN ONLY - NOT AUTHORIZED TO CREATE OR APPLY A CHANGE**
> 最近确认的 active OpenSpec change: **none**

本计划执行时必须同时阅读
[55 - Cleanup Decision Record](alignment-audit-55-cleanup-decision-record.md) 和
[逐项 Adjustment Review Index](alignment-audit-60-adjustments/00-review-index.md)。`55`
保存“为什么这样判定”；调整的内容、风险、副作用和控制条件已按一项一个文件拆到
`alignment-audit-60-adjustments/`，本文只保存顺序、checkbox 和停止关卡。

返回[审计总览](alignment-audit-00-current-state.md)。详细证据见
[规格/实现审计](alignment-audit-10-spec-implementation.md)、
[CONTEXT 审计](alignment-audit-20-context.md)、
[OpenSpec 治理审计](alignment-audit-30-openspec-governance.md)和
[验证记录](alignment-audit-40-verification.md)。

## 目标与顺序

本计划采用已经确认的 **cleanup first** 顺序：

```text
锁定退役证据与边界
  |
  +--> Stage 1: 清 V1 topology 残渣 ----> 局部复审并停止
  |
  +--> Stage 2: 清 CONTEXT/术语残渣 ---> 局部复审并停止
                                               |
                                               v
                                    Stage 3: 降噪后只读复审
                                               |
                     +-------------------------+-------------------------+
                     v                                                   v
          Stage 4: 决定 A-003                                Stage 5: 决定 A-004
                     +-------------------------+-------------------------+
                                               v
                              Stage 6: 决策后的术语/状态同步
                                               |
                                               v
                                    Stage 7: 最终诚实复审
```

先删除已被事实证伪的干扰，再重建 mismatch ledger。清理阶段不决定 A-003/A-004，
语义决定阶段也不修改代码来追求绿色。

## Alignment-Only 边界

### 全程冻结

- `deep_research_harness/src/`、`tests/`、`scripts/`、runtime assets、dependency metadata；
- `openspec/governance/`、`openspec/guardrails/` 中的 Python、tests、可执行 registry、
  manifest、TOML 与 generated inventory；
- public API、graph、typed domain contracts、storage、Runner 行为和任何 detector；
- `openspec/changes/archive/` 中的历史 artifacts；
- `deerflow/` gitlink 与 submodule worktree；不得读取其源码来完成本计划。

如果某一项需要修改上述路径，立即标记 `DEFERRED-CODE-CHANGE` 或
`OPTIONAL-HARDENING`，停止该项，不得扩大 scope。

### 只有逐 Stage 授权后才可修改

- 由 OpenSpec CLI 创建并按 instructions 生成的 planning artifacts；
- 明确产品决定后的 delta specs，以及 archive/sync 后对应 main specs；
- `CONTEXT.md`、ADR status/applicability note、README、AGENTS、Charter/policy 等说明性
  authority；
- `openspec/config.yaml` 的 authoring context/rules 文案，但不能暗示未实现的机械保护。

Main specs 不是普通文档。任何 required-behavior 变化都必须由独立 OpenSpec change 和
明确产品决定拥有，不能为减少 diff 直接改写。

## Checkbox 与证据协议

1. 一次最多一个 active OpenSpec change。
2. Planning authorization 与 apply authorization 分开；前者不包含后者。
3. 每个 Stage archive 或明确 deferred 后必须停止，等待下一 Stage 的单独授权。
4. checkbox 只有在证据已经写入本计划或相邻审计记录后才能勾选。
5. 每个完成项至少记录：日期、HEAD/change、涉及路径、命令/人工核查和结论。
6. 新 finding 先登记，不能以“同类问题”为由自动扩大正在执行的 scope。
7. 绿色检查只按其真实证明范围记录，不升级为语义正确或机械保护完整。
8. 每个 adjustment 必须单独说明调整内容、主要风险、可能副作用和控制方式；不得用一段
   change-level 总结替代逐项分析。
9. 执行后必须回填实际观察到的副作用；“未观察到”也要写明证据范围，不能留空。

## 单项 Adjustment Record 模板

每个 C 编号、语义决定或新 finding 在进入 apply 前，都必须在本审计子目录的 Stage
evidence 中填写下列记录。一个编号涉及两种不同语义变化时，拆成 `C-xxx.a`、`C-xxx.b`。

```markdown
### Adjustment <ID> - <short name>

- 状态: proposed | authorized | applied | verified | deferred | rolled-back
- Authority owner:
- Affected paths:
- Before（当前到底写了/要求了什么）:
- After（本次到底调整什么，不调整什么）:
- Reason and evidence:
- Main risk:
- Possible side effects:
- Risk controls / stop condition:
- Verification before apply:
- Verification after apply:
- Observed side effects（包括 none observed + evidence bound）:
- Remaining mismatch / follow-up owner:
- Authorization and date:
```

缺少 `Before/After`、risk、possible side effects、control 或 verification 任一项，该
adjustment 不得 apply，也不得勾选对应完成 checkbox。

每项审阅前的内容/风险/副作用分析见
[Adjustment Review Index](alignment-audit-60-adjustments/00-review-index.md)。执行证据必须
写回相同子目录中的新 Stage evidence 文件，不能只在 change artifact 或聊天记录中保留。

## Stage 总表

| Stage | Change | 覆盖 | 是否改代码 | 初始状态 |
| --- | --- | --- | --- | --- |
| 0 | 无 | 决策、退役登记与执行边界 | 否 | `[x] Decision tree closed; execution not authorized` |
| 1 | `retire-v1-topology-residue` | A-001；诚实记录 A-002 | 否 | `[ ] Not started` |
| 2 | `retire-stale-context-concepts` | A-005..A-008 的安全子集 | 否 | `[ ] Blocked by Stage 1` |
| 3 | 无，只读 re-audit | 降噪后重建 A-001..A-009 ledger | 否 | `[ ] Blocked by Stage 2` |
| 4 | `reconcile-evaluation-rubric-authority` | A-003 | 否；实现差异 defer | `[ ] Blocked by Stage 3` |
| 5 | `reconcile-post-loss-diagnostic-authority` | A-004 | 否；实现差异 defer | `[ ] Blocked by Stage 4` |
| 6 | `normalize-post-decision-terminology-status` | A-003/A-004 的 CONTEXT/ADR 收口 | 否 | `[ ] Blocked by Stages 4-5` |
| 7 | 无，最终 re-audit | A-001..A-009 | 否 | `[ ] Blocked by Stage 6` |

## Stage 0 - Decision And Scope Lock

### 已完成

- [x] 0.1 建立 A-001..A-009 审计报告集及 deterministic baseline。
- [x] 0.2 完成 Q1-Q20 设计树并取得用户确认。
- [x] 0.3 建立首轮清理登记、产品状态表和隔离登记。
- [x] 0.4 确认 cleanup-first、一次一个 change、每个 change 后停止复审。
- [x] 0.5 确认 no-code alignment 可以在 A-002 deferred、A-009 optional 时诚实完成。
- [x] 0.6 确认当前只授权计划文档，不授权创建或 apply OpenSpec change。

### 执行前未完成

- [ ] 0.7 获得“只创建 Stage 1 planning artifacts”的明确授权。
- [ ] 0.8 记录当时 HEAD、完整 worktree 状态与 `openspec list --json`。
- [ ] 0.9 若有 active change 或 overlapping user edits，停止并记录 owner，不覆盖。
- [ ] 0.10 逐项重验 `55` 中 C-001..C-003；外部已解决项标 `resolved externally`。
- [ ] 0.11 书面记录全部 frozen paths；确认 change tasks 中没有 code/test/detector 工作。

### Gate 0

- [ ] 只获得 Stage 1 planning authorization，尚未获得 apply authorization。
- [ ] 执行基线与用户已有修改已经记录。
- [ ] 未创建或修改任何代码、测试、detector 或 `deerflow/` 内容。

**Gate 0 未通过时停止。**

## Stage 1 - Retire V1 Topology Residue

**Change:** `retire-v1-topology-residue`

**只覆盖:** C-001..C-003 / A-001。A-002 保持 open。

### 逐项审阅文件

- [x] 1.R1 审阅并确认
  [C-001 real upstream topology](alignment-audit-60-adjustments/alignment-audit-60-01-c001-real-upstream-topology.md)。
- [ ] 1.R2 审阅并确认
  [C-002 proposal and closeout boundary](alignment-audit-60-adjustments/alignment-audit-60-02-c002-closeout-boundary.md)。
- [ ] 1.R3 审阅并确认
  [C-003 editable harness path](alignment-audit-60-adjustments/alignment-audit-60-03-c003-editable-harness-path.md)。

### Planning checklist

- [ ] 1.1 确认无 active change 后，用
  `openspec new change "retire-v1-topology-residue"` 创建 scaffold。
- [ ] 1.2 依次运行 `status` / `instructions`，按 schema 生成实际要求的 artifacts；不手工
  猜测或强造空 delta。
- [ ] 1.3 Focus Card 将 owner 限定为 V2 repository topology language，不拥有 detector。
- [ ] 1.4 Proposal 明确 A-001 要关闭、A-002 仍 deferred，并链接 `55` 的精确分类。
- [ ] 1.5 建立逐 occurrence 清单，只纳入“根 `backend/` / `frontend/` 是 upstream
  mirror”及错误 sibling install path。
- [ ] 1.6 为 C-001、C-002、C-003 分别填写完整 Adjustment Record；逐项解释调整内容、
  风险、可能副作用、控制和验证，不使用一个 topology 总风险代替。
- [ ] 1.7 明确排除真实 `deerflow/backend/...`、database/persistence backend、host
  compatibility path、legacy-root negative drift guard 和所有 archive。
- [ ] 1.8 Delta/spec work 只迁移物理边界语言，不承诺 gitlink mode/diff detector 已存在。
- [ ] 1.9 Tasks 只包含 config/spec/guide/README/Charter/policy 文案和只读验证；不包含
  Python、tests、manifest、TOML、registry 或 generated inventory edit。
- [ ] 1.10 `openspec validate retire-v1-topology-residue --strict` 通过并完成人工 plan review。
- [ ] 1.11 单独获得 Stage 1 apply authorization。

### Apply checklist（尚未授权）

- [ ] 1.12 把 config、local AGENTS 和 Charter 中的 upstream mirror 叙述改为真实
  `deerflow/` gitlink boundary。
- [ ] 1.13 把 config proposal/closeout 规则改成诚实的 scope 与人工 evidence 要求；明确
  当前没有 A-002 机械 detector。
- [ ] 1.14 修正 README 的 editable harness 路径；保持 `pyproject.toml`、lockfile 不变。
- [ ] 1.15 仅通过 approved delta 同步真正误称 root upstream 的 main-spec 语言；逐项证明
  没有删除仍有效的 negative drift guard 或 host-interface term。
- [ ] 1.16 搜索 active non-archive authority，逐项分类残余 `backend` / `frontend`；验收
  依据是语义分类完整，不是 token 数归零。
- [ ] 1.17 运行 strict OpenSpec、Markdown/link、whitespace 和现有只读 verification；失败时
  停止，不改 code/test 追绿。
- [ ] 1.18 逐项回填 C-001..C-003 的 observed side effects、remaining mismatch 和 evidence
  bound；空白记录不得进入 archive。
- [ ] 1.19 Archive 后做 A-001/A-002 局部复审并记录 before/after evidence。

### Gate 1

- [ ] Current explanatory authority 对真实 V2 topology 给出同一答案。
- [ ] 所有保留的 `backend` / `frontend` occurrence 都有合法分类理由。
- [ ] A-002 明确保持 `DEFERRED-CODE-CHANGE`，没有 architecture/gitlink 假绿声明。
- [ ] Diff 不含 frozen paths；change 已 archive；无 active change。
- [ ] 已停止并取得进入 Stage 2 的新授权。

## Stage 2 - Retire Stale Context Concepts

**Change:** `retire-stale-context-concepts`

**只覆盖:** C-004..C-011 / A-005..A-008 的安全子集。

### 逐项审阅文件

- [ ] 2.R1 [C-004 workspace / bundle](alignment-audit-60-adjustments/alignment-audit-60-04-c004-workspace-bundle-definition.md)
- [ ] 2.R2 [C-005.a completed-work tense](alignment-audit-60-adjustments/alignment-audit-60-05-c005a-completed-work-tense.md)
- [ ] 2.R3 [C-005.b archived change dependency](alignment-audit-60-adjustments/alignment-audit-60-06-c005b-archived-change-dependency.md)
- [ ] 2.R4 [C-006 relocate CONTEXT design material](alignment-audit-60-adjustments/alignment-audit-60-07-c006-relocate-context-design-material.md)
- [ ] 2.R5 [C-007 policy cardinality](alignment-audit-60-adjustments/alignment-audit-60-08-c007-policy-cardinality.md)
- [ ] 2.R6 [C-008 Suite smoke target](alignment-audit-60-adjustments/alignment-audit-60-09-c008-suite-smoke-roadmap-status.md)
- [ ] 2.R7 [C-009 readable-review-report requirement](alignment-audit-60-adjustments/alignment-audit-60-10-c009-readable-review-report-requirement.md)
- [ ] 2.R8 [C-010.a report artifact vs export](alignment-audit-60-adjustments/alignment-audit-60-11-c010a-report-artifact-vs-export.md)
- [ ] 2.R9 [C-010.b Support Handoff status](alignment-audit-60-adjustments/alignment-audit-60-12-c010b-support-handoff-status.md)
- [ ] 2.R10 [C-010.c TUI / Local-First dormant](alignment-audit-60-adjustments/alignment-audit-60-13-c010c-tui-local-first-dormant.md)
- [ ] 2.R11 [C-011 ADR status / applicability](alignment-audit-60-adjustments/alignment-audit-60-14-c011-adr-status-applicability.md)

### Planning checklist

- [ ] 2.1 重新确认 Q-001/A-003 与 Q-002/A-004 的精确禁碰位置。
- [ ] 2.2 用 CLI scaffold；按 `status` / `instructions` 生成需要的 planning artifacts。
- [ ] 2.3 为每个目标词条记录 keep / retire / relocate-owner / planned / dormant / quarantine。
- [ ] 2.4 为 C-004..C-011 分别填写完整 Adjustment Record；同一编号的不同语义动作使用
  子编号，不以“CONTEXT cleanup”总风险代替。
- [ ] 2.5 Proposal 明确不决定 Rubric/Runner，不决定 Bundle-loss 后 external retention。
- [ ] 2.6 ADR 方案只增加 status/applicability note，不重写历史正文。
- [ ] 2.7 Tasks 中无 runtime contract、case、Runner、report schema、handoff schema、UI、
  checker 或 test 实施。
- [ ] 2.8 Strict validate、人工 plan review通过；单独获得 Stage 2 apply authorization。

### Apply checklist（尚未授权）

- [ ] 2.9 修正 Evaluation Run Workspace 定义，不承诺 Bundle 是其子目录。
- [ ] 2.10 移除 “new Suite” / “V1 structural change must...” 等已完成任务语气，以及
  current glossary 对 archived change slug 的依赖。
- [ ] 2.11 从 CONTEXT 移出安全的重复设计章节并链接唯一 owner；A-003/A-004 相交段保持
  quarantine，不借结构清理改写其语义。
- [ ] 2.12 将全节点 Suite smoke 从 current claim 降为 roadmap target，列明有限 registry
  范围，不新增行为要求。
- [ ] 2.13 退役 glossary 单独创造的 readable-report required 语气，不自动标 planned。
- [ ] 2.14 拆分 current Final Report Artifact 与 planned Primary User Report Export。
- [ ] 2.15 将 Support Handoff 标 `planned`，但不回答其 Bundle-loss retention；将 Dedicated
  TUI 与相应 Local-First 路线标 `dormant`，保留 current Dedicated Agent route。
- [ ] 2.16 修正 policy cardinality：一个 trigger 对应一个 canonical policy，一个 change
  可触发多个 policies；不改 checker。
- [ ] 2.17 给相关 ADR 增加一致 status/applicability note；不静默改写原始决定。
- [ ] 2.18 运行 docs/governance/strict/full read-only verification；记录证明边界。
- [ ] 2.19 逐项回填 C-004..C-011 的 observed side effects、remaining mismatch 和 evidence
  bound；空白记录不得进入 archive。
- [ ] 2.20 Archive 后局部复审 A-005..A-008，并逐项记录哪些已消失、哪些因 quarantine
  仍存在。

### Gate 2

- [ ] 安全残渣已清理，CONTEXT 未替 A-003/A-004 选边。
- [ ] Current/planned/dormant 三类状态不再混用。
- [ ] 历史 ADR/archive 得到保留，current authority 不再依赖 archived slug。
- [ ] C-001..C-011 每个实际 adjustment 均有完整内容、风险、副作用和实测回填记录。
- [ ] Diff 不含 frozen paths；change 已 archive；无 active change。
- [ ] 已停止并取得 Stage 3 只读复审授权。

## Stage 3 - Post-Cleanup Read-Only Re-Audit

本 Stage 不创建 OpenSpec change，不修改 target authority；只允许把证据写回本审计目录。

- [ ] 3.1 锁定新 HEAD、worktree、active changes 和 `deerflow` gitlink metadata。
- [ ] 3.2 对 C-001..C-011 做 before/after 对照，不因文件已编辑自动判 resolved。
- [ ] 3.3 重扫 non-archive current authority，并逐项人工分类残余 topology/术语命中。
- [ ] 3.4 重新取证 A-003、A-004，确认清理没有掩盖或意外扩大冲突。
- [ ] 3.5 重建 A-001..A-009 mismatch ledger，区分：已消失噪声、真实语义冲突、
  deferred code gap、optional hardening。
- [ ] 3.6 对新 finding 先登记证据和 disposition；不自动纳入后续 Stage。
- [ ] 3.7 只有明显同属已授权 scope 的遗漏，才提出 scope amendment；获得新授权前不改。
- [ ] 3.8 记录 strict validation、现有 deterministic verification、skip/warning 及其证明范围。

### Gate 3

- [ ] 有一份以新 HEAD 为基线的 reduced mismatch ledger。
- [ ] A-003/A-004 是否仍存在由新证据回答，不沿用旧结论猜测。
- [ ] 所有新 finding 都已登记但未被顺手处理。
- [ ] 用户已审阅复审结果，并单独授权是否进入 Stage 4。

## Stage 4 - Reconcile Rubric / Runner Authority

**Change:** `reconcile-evaluation-rubric-authority`

### 逐项审阅文件

二选一。两份文件均已列出调整内容、风险、副作用和停止条件：

- [ ] 4.R1 [Option A - Criterion IDs are execution admission metadata](alignment-audit-60-adjustments/alignment-audit-60-15-a003a-criterion-ids-metadata.md)
- [ ] 4.R2 [Option B - Rubric is completely review-only](alignment-audit-60-adjustments/alignment-audit-60-16-a003b-rubric-review-only.md)

### Decision checklist

- [ ] 4.1 重新读取 CES、EVH、ADR 0025、相关 CONTEXT 和当前 admission/Runner 证据。
- [ ] 4.2 分开定义 identity、criterion IDs、Rubric content、model-facing input、quality verdict。
- [ ] 4.3 产品 owner 明确选择唯一 required contract：
  - [ ] criterion IDs 可作为 execution admission 的 control-integrity metadata，但 Rubric
    content 不面向 model、Runner 不产生 quality verdict；或
  - [ ] Rubric 完全 review-only，execution admission 不读取 criteria。
- [ ] 4.4 记录 rejected alternative 与选择理由；不得写“因为代码如此所以 spec 必须如此”。
- [ ] 4.5 为选定方案填写完整 Adjustment Record；apply/archive 后回填实际观察到的
  副作用、未验证范围和 remaining code gap。

### OpenSpec checklist（未授权）

- [ ] 4.6 CLI scaffold，完成被 instructions 要求的 proposal/design/deltas/tasks。
- [ ] 4.7 Deltas 让 CES/EVH 对 required behavior 只有一个答案。
- [ ] 4.8 若所选合同与当前代码不同，明确登记 `DEFERRED-CODE-CHANGE`；本 Stage 不改实现。
- [ ] 4.9 Rubric/Runner 的 CONTEXT 最终措辞继续留到 Stage 6，避免半同步。
- [ ] 4.10 Strict validate、人工 plan review、单独 apply authorization。
- [ ] 4.11 Apply/sync/archive 后运行现有验证，只报告 conformance，不修改测试或实现。

### Gate 4

- [ ] A-003 已有唯一 product decision 和一致 main specs，或因缺少决定明确停止。
- [ ] 若代码不满足所选 spec，缺口已命名、定界、defer，没有被文案掩盖。
- [ ] No-code diff；无 active change；已停止并取得 Stage 5 新授权。

## Stage 5 - Reconcile Post-Loss Diagnostic Authority

**Change:** `reconcile-post-loss-diagnostic-authority`

### 逐项审阅文件

二选一。两份文件均已列出调整内容、风险、副作用和停止条件：

- [ ] 5.R1 [Option A - Bundle-local-only](alignment-audit-60-adjustments/alignment-audit-60-17-a004a-bundle-local-only.md)
- [ ] 5.R2 [Option B - external diagnostic retention](alignment-audit-60-adjustments/alignment-audit-60-18-a004b-external-diagnostic-retention.md)

### Decision checklist

- [ ] 5.1 重新读取 RER、RUS、REJ、相关 ADR/CONTEXT 与 Bundle deletion 当前证据。
- [ ] 5.2 分别回答 bytes retention、supported reader、participant presentation。
- [ ] 5.3 产品 owner 明确选择唯一 required contract：
  - [ ] Bundle-local-only；Bundle loss 后 inspection unavailable；或
  - [ ] external diagnostic 可留存，并明确它仍无 recovery/selection/authorization 权威。
- [ ] 5.4 若选择 external diagnostic，列出未来 code change 必须拥有的 typed owner、
  retention/redaction、authorization、reader 和 deletion semantics，但不在本 Stage 实施。
- [ ] 5.5 为选定方案填写完整 Adjustment Record；apply/archive 后回填实际观察到的
  副作用、未验证范围和 remaining code gap。

### OpenSpec checklist（未授权）

- [ ] 5.6 CLI scaffold，完成 proposal/design/RER-RUS-REJ deltas/tasks。
- [ ] 5.7 Deltas 对三个问题给出唯一答案，并保留 no-recovery/no-authority invariants。
- [ ] 5.8 若所选合同与实现不同，登记 `DEFERRED-CODE-CHANGE`；不新增 store/schema/tests。
- [ ] 5.9 External Observation/Support Handoff 的 CONTEXT 最终措辞留到 Stage 6。
- [ ] 5.10 Strict validate、人工 plan review、单独 apply authorization。
- [ ] 5.11 Apply/sync/archive 后只读验证并记录真实 conformance gap。

### Gate 5

- [ ] A-004 已有唯一 product decision 和一致 main specs，或因缺少决定明确停止。
- [ ] Support Handoff 的 planned 状态没有被解释成 external retention 已获批准。
- [ ] No-code diff；无 active change；已停止并取得 Stage 6 新授权。

## Stage 6 - Normalize Post-Decision Terminology And Status

**Change:** `normalize-post-decision-terminology-status`

**前置条件:** A-003、A-004 已有明确决定；若决定产生 code gap，gap 已单独 deferred。

### 逐项审阅文件

这两项不是独立产品决定，只能在相应前置决定已完成后进入 planning：

- [ ] 6.R1 [D-001 Rubric / Runner terminology](alignment-audit-60-adjustments/alignment-audit-60-19-d001-rubric-runner-terminology.md)
- [ ] 6.R2 [D-002 post-loss diagnostic terminology](alignment-audit-60-adjustments/alignment-audit-60-20-d002-post-loss-diagnostic-terminology.md)

- [ ] 6.0 为 D-001、D-002 分别填写 Adjustment Record，并在 apply 后回填实际副作用。
- [ ] 6.1 以 Stages 4-5 的 accepted specs 为唯一 required-behavior 来源，重新列出受影响
  CONTEXT/ADR 语句。
- [ ] 6.2 CLI scaffold docs-only change；Focus Card 不拥有 runtime behavior。
- [ ] 6.3 同步 Rubric/Runner 的 glossary 和 ADR applicability，不扩大已决定合同。
- [ ] 6.4 同步 External Run Observation、Support Handoff 与 Bundle-loss 术语；分别说明
  retention、supported readability 和 participant presentation。
- [ ] 6.5 若存在 deferred code gap，current behavior 与 required behavior 分开陈述，不能
  用统一术语掩盖不一致。
- [ ] 6.6 复核 Stage 2 的 current/planned/dormant 状态仍成立；不重新激活 dormant 路线。
- [ ] 6.7 Strict validate、人工 review、单独 apply authorization。
- [ ] 6.8 Apply/archive 后运行 docs/governance/full read-only verification。

### Gate 6

- [ ] CONTEXT 只定义语言，不复制 requirement、ADR 论证或 change task。
- [ ] Specs、ADR applicability 和 glossary 不再对 A-003/A-004 给出互斥答案。
- [ ] 所有实现差异均以 deferred gap 明示。
- [ ] No-code diff；无 active change；已停止并取得 Stage 7 授权。

## Stage 7 - Final Honest Re-Audit

本 Stage 不创建 change，只读复审 target authority并更新本审计目录。

- [ ] 7.1 锁定最终 HEAD，确认无 active change、`deerflow/` gitlink/worktree 未被修改。
- [ ] 7.2 运行 OpenSpec doctor/strict、Markdown/link/whitespace checks 与
  `UV_OFFLINE=1 make verify`；如实记录 skip、warning 和未运行 live evidence。
- [ ] 7.3 对 A-001..A-009 逐项重新取证；不因 change archived 自动勾 resolved。
- [ ] 7.4 确认 A-002 仍标 `DEFERRED-CODE-CHANGE`，除非另一个获授权 code change 已真实
  实现 gitlink detector。
- [ ] 7.5 确认 A-009 只声称 ID-level traceability；stronger semantic mapping 仍
  `OPTIONAL-HARDENING`，除非另案已经实现。
- [ ] 7.6 确认 A-003/A-004 的 required behavior、current implementation 和 deferred
  gap 分别有明确 owner。
- [ ] 7.7 更新 `alignment-audit-00-current-state.md` 最终矩阵，同时保留原审计快照历史。
- [ ] 7.8 为仍需代码的事项建立独立 backlog/候选 change，不在本计划中实施。
- [ ] 7.9 只有 no-code alignment 项全部完成、开放缺口均被准确披露，才关闭本计划。

### Definition Of Done

- [ ] 已被事实证伪的历史概念不再污染 current authority。
- [ ] 文档之间不再互相矛盾；与代码不同之处明确标为 required/current gap。
- [ ] Main spec 的每次语义变化都有产品决定和 OpenSpec change，不是静默追随实现。
- [ ] 每个 adjustment 的内容、风险、可能副作用、控制与实际观察均可逐项追溯。
- [ ] 未实现能力全部标 `planned`、`dormant` 或 `deferred`，不冒充 current。
- [ ] A-002 与 A-009 可以保持开放，但没有假绿或过度证明声明。
- [ ] alignment 主线未修改 Python、tests、runtime contracts、governance executables 或
  `deerflow/`。
- [ ] 全量验证结果及其不能证明的部分均被记录。

## 固定停止条件

出现任一条件立即停止当前 Stage：

- 需要修改应用/治理 Python、tests、runtime contract、manifest/TOML/registry 才能继续；
- 需要读取或修改 `deerflow/` 源码；
- 需要修改 archived change 才能让 current authority 看起来一致；
- 只能通过删除失败 requirement、弱化事实或隐藏 conformance gap 来“变绿”；
- 清理动作会触碰 A-003/A-004 的未决语义；
- 发现新 finding 但尚未登记、分类和获得 scope authorization；
- 另一个 active change 或用户修改与当前 authority cluster 重叠；
- baseline failure owner 不明；
- 计划开始实现 Report Export、Support Handoff、Primary User TUI、gitlink detector 或
  stronger traceability checker。

## 当前下一动作

本计划与决策记录已经形成，但没有实施授权。下一动作只能是用户单独授权
“创建 Stage 1 的 OpenSpec planning artifacts”。在那之前，不创建 active change，不修改
spec、CONTEXT、config、ADR、guide、README、代码或 tests。
