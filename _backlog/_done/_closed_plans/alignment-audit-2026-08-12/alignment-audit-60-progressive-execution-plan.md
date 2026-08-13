# Alignment Audit 60 - Cleanup-First Progressive OpenSpec Plan

> 类型: 对齐执行计划 / Progressive checkbox ledger
> 计划日期: 2026-08-12
> 原始审计证据快照: `65df2571108cc6b4b81f55d3ba8542786a810b39`
> 计划重排时 HEAD: `ac6989abb46b22a9b0cf50e8a53b47341d762750`
> 执行基线: 尚未锁定；开始每个 Stage 时重新记录 HEAD
> 当前状态: **STAGE 7 CLOSED - ALIGNMENT AUDIT PLAN COMPLETE**
> 最近归档的 OpenSpec change: `2026-08-13-establish-gitlink-boundary-detector`
> 当前 active OpenSpec change: 无

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
| 1 | `2026-08-13-retire-v1-topology-residue` | A-001；诚实记录 A-002 | 仅 V-001 format-only test exception | `[x] Archived; Stage 2 planning authorized` |
| 2 | `retire-stale-context-concepts` | A-005..A-008 的安全子集 | 否 | `[x] Completed and archived; Stage 3 authorized` |
| 3 | 无，只读 re-audit | 降噪后重建 A-001..A-009 ledger | 否 | `[x] Complete; Stage 4 planning authorized` |
| 4 | `reconcile-evaluation-rubric-authority` | A-003 | 否；实现差异 defer | `[x] Archived; bounded local conformance, no observed deferred gap` |
| 5 | `reconcile-post-loss-diagnostic-authority` | A-004 | 否；实现差异 defer | `[x] Archived; bounded local conformance, A-004-T01 tooling residue remains` |
| 6 | `normalize-post-decision-terminology-status` | A-003/A-004 的 CONTEXT/ADR 收口 | 否 | `[x] Archived; no active change; D-001/D-002 no observed side effects within bounded checks` |
| 7 | 无，最终 re-audit | A-001..A-009 | 否 | `[x] Completed; alignment audit plan closed` |

## Stage 0 - Decision And Scope Lock

### 已完成

- [x] 0.1 建立 A-001..A-009 审计报告集及 deterministic baseline。
- [x] 0.2 完成 Q1-Q20 设计树并取得用户确认。
- [x] 0.3 建立首轮清理登记、产品状态表和隔离登记。
- [x] 0.4 确认 cleanup-first、一次一个 change、每个 change 后停止复审。
- [x] 0.5 确认 no-code alignment 可以在 A-002 deferred、A-009 optional 时诚实完成。
- [x] 0.6 确认当前只授权计划文档，不授权创建或 apply OpenSpec change。

### 执行前未完成

- [x] 0.7 已获得“只创建 Stage 1 planning artifacts”的明确授权（2026-08-12）。
- [x] 0.8 已记录 planning baseline：HEAD `5da7e872e2b264dc74512225a66492f5502313ba`；
  `openspec list --json` 无 active change；Git metadata 显示 `deerflow` gitlink 为
  `66b9e7f21212490cf92fafac137542b9deb06615`。完整 apply-time baseline 必须在 task 1.1 重取。
- [x] 0.9 planning 前确认无 active change，且当时 `git status --porcelain=v1 --untracked-files=all`
  无输出；后续 user edits 或 active changes 仍须在 apply 前重查，不覆盖。
- [x] 0.10 已逐项重验 `55` 中 C-001..C-003；没有外部已解决项：C-001/C-002/C-003 均仍为
  明确目标，证据收录于 Stage 1 change proposal/design。
- [x] 0.11 已书面记录 frozen paths；change tasks 不含 code/test/detector、governance executable、
  manifest/TOML、registry、generated inventory 或 `deerflow/` 工作。

### Gate 0

- [x] 只获得 Stage 1 planning authorization，尚未获得 apply authorization。
- [x] Planning baseline 与当时用户 worktree 状态已经记录；apply 前必须按 task 1.1 重取。
- [x] Stage 1 planning 仅创建 OpenSpec artifacts 与本计划记录；未创建或修改代码、测试、detector
  或 `deerflow/` 内容。

**Gate 0 未通过时停止。**

## Stage 1 - Retire V1 Topology Residue

**Change:** `retire-v1-topology-residue`

**只覆盖:** C-001..C-003 / A-001，以及为恢复既有 full gate 而单独授权的 V-001
formatter-only maintenance。A-002 保持 open。

### 逐项审阅文件

- [x] 1.R1 审阅并确认
  [C-001 real upstream topology](alignment-audit-60-adjustments/alignment-audit-60-01-c001-real-upstream-topology.md)。
- [x] 1.R2 审阅并确认
  [C-002 proposal and closeout boundary](alignment-audit-60-adjustments/alignment-audit-60-02-c002-closeout-boundary.md)。
- [x] 1.R3 审阅并确认
  [C-003 editable harness path](alignment-audit-60-adjustments/alignment-audit-60-03-c003-editable-harness-path.md)。

### Planning checklist

- [x] 1.1 已确认无 active change，并用
  `openspec new change "retire-v1-topology-residue"` 创建 scaffold。
- [x] 1.2 已依次运行 `status` / `instructions`，按 schema 生成实际要求的 artifacts；`skip_specs: true`
  是 CLI 确认的合法 docs-only disposition，未强造空 delta。
- [x] 1.3 Focus Card 已将 owner 限定为 V2 repository topology language，不拥有 detector。
- [x] 1.4 Proposal 已明确 A-001 要关闭、A-002 仍 deferred，并指向 `55` 的精确分类。
- [x] 1.5 Proposal/design 已建立逐 occurrence allowlist：仅“根 `backend/` / `frontend/` 是
  upstream mirror”及错误 sibling install path 是目标。
- [x] 1.6 C-001、C-002、C-003 分别有审阅记录；tasks 要求 apply 后分别完成完整 Adjustment Record，
  不使用一个 topology 总风险代替。
- [x] 1.7 Proposal/design 已明确排除真实 `deerflow/backend/...`、database/persistence backend、
  host compatibility path、legacy-root negative drift guard 和所有 archive。
- [x] 1.8 CLI 已确认无 delta/spec work；计划不承诺 gitlink mode/diff detector 已存在。
- [x] 1.9 Tasks 只包含 config/guide/README/Charter 文案、审计记录与只读验证；不含 Python、tests、
  manifest、TOML、registry 或 generated inventory edit。
- [x] 1.10 `openspec validate retire-v1-topology-residue --strict` 已通过（2026-08-12）；人工复核
  `proposal.md`、`design.md`、`tasks.md` 后确认 scope 只含四份说明性 authority、保留 valid
  legacy-root guard、A-002 仍 deferred，且无 frozen-path edit task。
- [x] 1.11 单独获得 Stage 1 apply authorization（2026-08-12；仅 C-001..C-003）。

### Apply checklist（已完成）

- [x] 1.12 把 config、local AGENTS 和 Charter 中的 upstream mirror 叙述改为真实
  `deerflow/` gitlink boundary（2026-08-12；full gate 尚被独立格式问题阻塞）。
- [x] 1.13 把 config proposal/closeout 规则改成诚实的 scope 与人工 evidence 要求；明确
  当前没有 A-002 机械 detector（2026-08-12；full gate 尚被独立格式问题阻塞）。
- [x] 1.14 修正 README 的 editable harness 路径；保持 `pyproject.toml`、lockfile 不变
  （2026-08-12；full gate 尚被独立格式问题阻塞）。
- [x] 1.14a 仅运行 configured Ruff 对
  `tests/contract/test_selected_change_closeout.py` 的 V-001 adjacent-literal 格式维护；
  不改变 fixture 字符串、assertion 或测试行为。该例外由用户“继续”于 2026-08-13 单独授权，
  完整风险和副作用记录见 `stage-1-apply` V-001 record；focused Ruff、Ruff check 和
  pytest `15 passed` 已通过。
- [x] 1.15 已复核 main specs：没有真正误称 root upstream 的 current authority；所有命中均为
  negative drift guard、host-interface 或 domain term，故无需也不得创建 delta/spec sync。
- [x] 1.16 搜索 active non-archive authority，逐项分类残余 `backend` / `frontend`；验收
  依据是语义分类完整，不是 token 数归零（分类见 `stage-1-apply` C-001 record）。
- [x] 1.17 运行 strict OpenSpec、Markdown/link、whitespace 和现有只读 verification；失败时
  停止，不改 code/test 追绿。V-001 后 strict/doctor/Charter/diff/link 全通过；完整 gate
  的 targets 亦通过：fast 2495、integration/blocking-I/O 241（4 expected skips）、workflow 35。
- [x] 1.18 逐项回填 C-001..C-003 的 observed side effects、remaining mismatch 和 evidence
  bound；空白记录不得进入 archive（另有 V-001 独立 record）。
- [x] 1.19 Archive 后做 A-001/A-002 局部复审并记录 before/after evidence（见
  `stage-1-apply/alignment-audit-60-s1-archive-local-reaudit.md`）。

### Gate 1

- [x] Current explanatory authority 对真实 V2 topology 给出同一答案。
- [x] 所有保留的 `backend` / `frontend` occurrence 都有合法分类理由。
- [x] A-002 明确保持 `DEFERRED-CODE-CHANGE`，没有 architecture/gitlink 假绿声明。
- [x] Diff 不含 frozen paths（V-001 已授权 exception 除外）；change 已 archive；无 active change。
- [x] 已停止并取得进入 Stage 2 的 planning 授权（2026-08-13）；该授权不包含 apply。

## Stage 2 - Retire Stale Context Concepts

**Change:** `retire-stale-context-concepts`

**只覆盖:** C-004、C-005、C-007..C-011 / A-005..A-008 的安全子集。C-006 已撤回，
不进入 planning 或 apply。

### 逐项审阅文件

- [x] 2.R1 审阅并确认 [C-004 workspace / bundle](alignment-audit-60-adjustments/alignment-audit-60-04-c004-workspace-bundle-definition.md)：
  DeerFlow host workspace、Deep Research Run Bundle 与 Evaluation Run Workspace 是三个不同
  owner 的概念；限 Stage 2 planning，不包含 change/create/apply 授权。
- [x] 2.R2 审阅并确认 [C-005.a completed-work tense](alignment-audit-60-adjustments/alignment-audit-60-05-c005a-completed-work-tense.md)：
  只退役已完成迁移的未来时态；control/run-data separation、Runner 归属和 `tests/eval`
  的当前角色保留或链接 canonical owner；限 Stage 2 planning，不包含 change/create/apply 授权。
- [x] 2.R3 审阅并确认 [C-005.b archived change dependency](alignment-audit-60-adjustments/alignment-audit-60-06-c005b-archived-change-dependency.md)：
  清除 current glossary 对 closed plan 的来源宣称；保留 seam-first 规则及现行 policy 指针，
  archive 仅作历史追溯；限 Stage 2 planning，不包含 change/create/apply 授权。
- [x] 2.R4 [C-006 withdraw broad CONTEXT relocation](alignment-audit-60-adjustments/alignment-audit-60-07-c006-relocate-context-design-material.md)：
  原提议不是确定错位，撤回且无 target edit；具体错误继续由各独立项处理。
- [x] 2.R5 审阅并确认 [C-007 policy cardinality](alignment-audit-60-adjustments/alignment-audit-60-08-c007-policy-cardinality.md)：
  primary owner 唯一；review policy 可多选但仅限实际 trigger；每个 selected policy 保留
  独立 record；限 Stage 2 planning，不包含 change/create/apply 授权。
- [x] 2.R6 审阅并确认 [C-008 remove false all-node smoke claim](alignment-audit-60-adjustments/alignment-audit-60-09-c008-suite-smoke-roadmap-status.md)：
  只清除错误的全节点 current claim；registry 是当前范围事实来源，不新增 roadmap、case 或
  behavior requirement；限 Stage 2 planning，不包含 change/create/apply 授权。
- [x] 2.R7 审阅并确认 [C-009 readable-review-report requirement](alignment-audit-60-adjustments/alignment-audit-60-10-c009-readable-review-report-requirement.md)：
  只退役无 owner 的独立 readable-report 要求；保留结构化 Review Record、四态结果和
  `limited` / `inconclusive` 不得计作 pass；限 Stage 2 planning，不包含 change/create/apply 授权。
- [x] 2.R8 审阅并确认 [C-010.a report artifact vs export](alignment-audit-60-adjustments/alignment-audit-60-11-c010a-report-artifact-vs-export.md)：
  `final/report.md` 是 current Bundle artifact；Primary User report reopen/copy/export 没有
  current public entry，且本轮不把它预先承诺为 `planned`；限 Stage 2 planning，不包含
  change/create/apply 授权。
- [x] 2.R9 审阅并确认 [C-010.b Support Handoff status](alignment-audit-60-adjustments/alignment-audit-60-12-c010b-support-handoff-status.md)：
  当前没有 Support Handoff producer/schema/public entry；标 `planned`，但 Bundle-loss
  后留存问题保持 A-004 quarantine；限 Stage 2 planning，不包含 change/create/apply 授权。
- [x] 2.R10 审阅并确认 [C-010.c TUI / Local-First dormant](alignment-audit-60-adjustments/alignment-audit-60-13-c010c-tui-local-first-dormant.md)：
  dedicated Primary-User TUI 及其首发 Local-First 路线为 `dormant`；不影响 current
  Dedicated Agent route、demo TUI visualizer 或 Cognitive Evaluation 的 local surface；限
  Stage 2 planning，不包含 change/create/apply 授权。
- [x] 2.R11 审阅并确认 [C-011 ADR status / applicability](alignment-audit-60-adjustments/alignment-audit-60-14-c011-adr-status-applicability.md)：
  只加统一后记型 status/applicability note，不改 ADR 标题或正文；0002、0003、0006、0008、
  0010 分别说明 current/dormant/planned/non-current 子决定；A-004 继续 quarantine；限
  Stage 2 planning，不包含 change/create/apply 授权。

### Planning checklist

- [x] 2.1 已重新确认 Q-001/A-003 与 Q-002/A-004 的精确禁碰位置；完整边界见
  `retire-stale-context-concepts/design.md` 与
  [Stage 2 planning baseline](alignment-audit-60-adjustments/stage-2-planning/alignment-audit-60-s2-planning-baseline-and-validation.md)。
- [x] 2.2 已用 CLI scaffold 并依 `status` / `instructions` 生成 planning artifacts：proposal、design、tasks；
  `skip_specs: true` 经 CLI 确认，未创建伪 delta。
- [x] 2.3 已为目标术语建立 keep-current / retire / relocate-owner / planned / dormant /
  quarantine 分类协议、逐 C disposition 和 target allowlist；逐 occurrence 证据表已在 Stage 2
  apply evidence 中完成。
- [x] 2.4 C-004、C-005.a、C-005.b、C-007..C-011 已各自完成 Adjustment Record；同一编号的
  不同语义动作使用子编号，不以“CONTEXT cleanup”总风险代替。Before/After、风险、可能副作用、
  controls、verification 和 observed side effects 均记录在 `stage-2-apply/`。
- [x] 2.5 Proposal/design 明确不决定 Rubric/Runner，也不决定 Bundle-loss 后 external retention。
- [x] 2.6 ADR 方案限定为只增加 status/applicability postscript，不重写历史正文或标题。
- [x] 2.7 Tasks 中无 runtime contract、case、Runner、report schema、handoff schema、UI、
  checker 或 test 实施。
- [x] 2.8a `openspec validate retire-stale-context-concepts --strict`、`openspec doctor --json`、
  Charter checker 和 `git diff --check` 已通过；人工 review 结论见 Stage 2 planning baseline。
- [x] 2.8b 已单独获得 Stage 2 apply authorization（2026-08-13）。

### Apply checklist（已完成）

- [x] 2.9 修正 Evaluation Run Workspace 定义：明确其为 Runner-owned execution directory，
  不等同 DeerFlow host workspace 或 Deep Research Run Bundle；同一 execution root 的
  Evaluation Run Bundle 是 sibling，不承诺为其子目录。
- [x] 2.10 移除 “new Suite” / “V1 structural change must...” 等已完成任务语气，以及
  current glossary 对 archived change slug 的依赖。
- [x] 2.11 清除“每个 LLM-bearing node 都有 Suite smoke”的错误 current claim；保留定义并
  以 registry 作为当前范围事实来源，不添加 roadmap、case 或行为要求。
- [x] 2.12 退役 glossary 单独创造的 readable-report required 语气，不自动标 planned。
- [x] 2.13 拆分 current Final Report Artifact 与不存在的 Primary User Report Export public
  capability：保留前者；退役后者的 current claim，不将其写成 `planned` 或本轮 roadmap 承诺。
- [x] 2.14 将 Support Handoff 标 `planned`，但不回答其 Bundle-loss retention；将 Dedicated
  TUI 与相应 Local-First 路线标 `dormant`，保留 current Dedicated Agent route。
- [x] 2.15 修正 policy cardinality：一个 trigger 对应一个 canonical policy，一个 change
  可触发多个 policies；不改 checker。
- [x] 2.16 给相关 ADR 增加一致 status/applicability note；不静默改写原始决定。
- [x] 2.17 已运行 docs/governance/strict/full read-only verification；记录证明边界。
- [x] 2.18 已逐项回填 C-004、C-005、C-007..C-011 的 observed side effects、remaining mismatch 和 evidence
  bound；空白记录不得进入 archive。
- [x] 2.19 已完成局部 re-audit，逐项记录 A-005..A-008 的已消失残渣及继续 quarantine 的
  A-003/A-004；archive 后结构、active-change 和 gitlink 复核也已通过。

### Gate 2

- [x] 安全残渣已清理，CONTEXT 未替 A-003/A-004 选边。
- [x] Current/planned/dormant 三类状态不再混用。
- [x] 历史 ADR/archive 得到保留，current authority 不再依赖 archived slug。
- [x] C-001..C-011 每个实际 adjustment 均有完整内容、风险、副作用和实测回填记录。
- [x] Diff 不含 frozen paths；change 已 archive；无 active change。
- [x] 已停止并取得 Stage 3 只读复审授权（2026-08-13）；该授权不包含 Stage 4 planning 或 apply。

## Stage 3 - Post-Cleanup Read-Only Re-Audit

本 Stage 不创建 OpenSpec change，不修改 target authority；只允许把证据写回本审计目录。

- [x] 3.1 已锁定新 HEAD、worktree、active changes 和 `deerflow` gitlink metadata；完整基线见
  [Stage 3 baseline](alignment-audit-60-adjustments/stage-3-reaudit/00-stage-3-baseline-and-boundary.md)。
- [x] 3.2 已对 C-001..C-011 做 before/after 对照；C-006 继续标 withdrawn，C-007 的 main-spec/
  policy README residual 被诚实列为 partial，而非因文件改过即判 resolved。
- [x] 3.3 已重扫 non-archive current authority，并按拓扑、术语、历史 ADR、spec 和 policy role
  分类残余命中；不以 token 数归零为目标。
- [x] 3.4 已重新取证 A-003、A-004，确认 Stage 2 清理没有掩盖或扩大其互斥合同。
- [x] 3.5 已重建 A-001..A-009 reduced mismatch ledger，区分 resolved、真实语义冲突、
  `DEFERRED-CODE-CHANGE` 与 `OPTIONAL-HARDENING`。
- [x] 3.6 已登记 N-001、N-002 的证据和 disposition；没有顺手处理。
- [x] 3.7 已判定 N-001 不构成 scope amendment；N-002 需要独立授权的 policy-routing change，
  不自动塞入 Stage 4。
- [x] 3.8 已记录 strict validation、现有 deterministic verification 及其 live/semantic 证明边界。

### Gate 3

- [x] 有一份以新 HEAD 为基线的 reduced mismatch ledger。
- [x] A-003/A-004 是否仍存在由新证据回答，不沿用旧结论猜测。
- [x] 所有新 finding 都已登记但未被顺手处理。
- [x] 用户已审阅复审结果，并单独授权进入 Stage 4 的 planning（2026-08-13）；该授权不包含 apply、sync、archive 或 commit。

## Stage 4 - Reconcile Rubric / Runner Authority

**Change:** `reconcile-evaluation-rubric-authority`

### 逐项审阅文件

二选一。两份文件均已列出调整内容、风险、副作用和停止条件：

- [x] 4.R1 [Option A - Criterion IDs are execution admission metadata](alignment-audit-60-adjustments/alignment-audit-60-15-a003a-criterion-ids-metadata.md)：2026-08-12 已确认，限后续 planning。
- [x] 4.R2 [Option B - Rubric is completely review-only](alignment-audit-60-adjustments/alignment-audit-60-16-a003b-rubric-review-only.md)：2026-08-12 已审并明确排除。

### Decision checklist

- [x] 4.1 已重新读取 CES、EVH、ADR 0025、相关 CONTEXT 和当前 admission/Runner 证据。
- [x] 4.2 已分开定义 identity、criterion IDs、Rubric content、model-facing input、quality verdict。
- [x] 4.3 产品 owner 已明确选择唯一 required contract：
  - [x] criterion IDs 可作为 execution admission 的 control-integrity metadata，但 Rubric
    content 不面向 model、Runner 不产生 quality verdict。
  - [x] Rubric 完全 review-only，execution admission 不读取 criteria：已排除。
- [x] 4.4 已记录 rejected alternative 与选择理由；选择不是“因为代码如此所以 spec 必须如此”。
- [x] 4.5 已填写 planning Adjustment Record（含 Before/After、风险、可能副作用、控制、
  验证和当前 observed-effect boundary），见
  [Stage 4 planning record](alignment-audit-60-adjustments/stage-4-planning/00-stage-4-planning-baseline-and-decision.md)。
  apply/archive 后仍必须回填实际观察到的副作用、未验证范围和 remaining code gap。

### OpenSpec Planning Checklist（已完成）

- [x] 4.6 在 planning 完成时，CLI scaffold 已生成 instructions 要求的
  proposal/design/CES-EVH-HITL1 deltas/tasks；当时完整 apply checklist 尚未开始。其后的
  已授权 apply/sync/verification 由 4.11 和 `stage-4-apply/` 记录，不回写这段 planning 历史。
- [x] 4.7 Deltas 已将 CES/EVH/HITL1 收敛到一个 required contract：identity/version 与 unique
  criterion IDs 只作 deterministic admission control-integrity metadata；content 和 verdict
  不跨进 execution。
- [x] 4.8 计划已规定：若 apply-time 真实 handoff 与所选合同不同，明确登记
  `DEFERRED-CODE-CHANGE` 并停止；本 Stage 不改实现。
- [x] 4.9 Rubric/Runner 的 CONTEXT 最终措辞继续留到 Stage 6，避免半同步。
- [x] 4.10 Strict validate、doctor、Charter checker、whitespace 和人工 plan review 已完成
  （2026-08-13）；结果、证明边界和 HITL1 owner 补全记录见
  [Stage 4 planning validation](alignment-audit-60-adjustments/stage-4-planning/01-stage-4-planning-validation.md)。
  随后已获得独立 apply authorization；apply/sync 证据、证明边界和无代码边界见
  [Stage 4 apply record](alignment-audit-60-adjustments/stage-4-apply/00-a003-apply-baseline-and-control-placement-review.md)。
- [x] 4.11 在独立 apply authorization 后完成真实 handoff inspection、CES/EVH/HITL1
  main-spec sync、strict/governance/whitespace 和现有 verification；只报告 bounded
  conformance，不修改测试或实现。CES、EVH 与 HITL1 现给出同一 required contract；在已检查
  本地路径未发现 `DEFERRED-CODE-CHANGE`，但 invalid-Rubric registry fixture、HITL1/Wave0/
  Wave1 real-node prompt 和 live evidence 仍是明确未证明范围。详见
  [Stage 4 apply evidence](alignment-audit-60-adjustments/stage-4-apply/)。

### Gate 4

- [x] A-003 已有唯一 product decision 和一致 main specs：identity/version 与 unique criterion
  IDs 只作 admission control-integrity metadata；content/judgment 不跨进 execution。
- [x] 在已检查本地路径未发现所选 spec 的实现缺口；没有把该 bounded 结论写成全路径或未来
  自动保护。若未来发现 crossing，必须命名、定界并 `DEFERRED-CODE-CHANGE`，不能被文案掩盖。
- [x] No-code diff；无 active change；已停止。Stage 4 已归档；post-archive baseline、gitlink
  metadata 与实际 A-003 disposition 见
  [Stage 4 post-archive record](alignment-audit-60-adjustments/stage-4-apply/09-a003-post-archive-baseline.md)。
  随后已获得独立 Stage 5 planning authorization；A-004 planning 仍不等同于 apply/sync/archive。

## Stage 5 - Reconcile Post-Loss Diagnostic Authority

**Change:** `reconcile-post-loss-diagnostic-authority`

### 逐项审阅文件

二选一。两份文件均已列出调整内容、风险、副作用和停止条件：

- [x] 5.R1 [Option A - Bundle-local-only](alignment-audit-60-adjustments/alignment-audit-60-17-a004a-bundle-local-only.md)：2026-08-12 已确认，限后续 planning。
- [x] 5.R2 [Option B - external diagnostic retention](alignment-audit-60-adjustments/alignment-audit-60-18-a004b-external-diagnostic-retention.md)：2026-08-12 已审并明确排除。

### Decision checklist

- [x] 5.1 已重新读取 RER、RUS、REJ、相关 ADR/CONTEXT 与 Bundle deletion 当前证据。
- [x] 5.2 已分别回答 bytes retention、supported reader、participant presentation：不对物理残留
  bytes 作绝对断言；没有 supported external reader；没有 Bundle-loss 后 participant presentation。
- [x] 5.3 产品 owner 已明确选择唯一 required contract（2026-08-12）：
  - [x] Bundle-local-only；Bundle loss 后 inspection unavailable。
  - [x] external diagnostic 可留存，并明确它仍无 recovery/selection/authorization 权威：已排除。
- [x] 5.4 external-diagnostic 的 typed owner、
  retention/redaction、authorization、reader 和 deletion semantics，但不在本 Stage 实施。
  不适用：Option B 已排除；其未来实现义务保留在被拒绝替代方案记录中。
- [x] 5.5 已填写完整 planning Adjustment Record；apply/archive 后仍必须回填实际观察到的
  副作用、未验证范围和 remaining code gap，见
  [Stage 5 planning record](alignment-audit-60-adjustments/stage-5-planning/00-stage-5-planning-baseline-and-decision.md)。

### OpenSpec checklist（planning、apply/sync 与 archive 已完成）

- [x] 5.6 CLI scaffold，完成 proposal/design/RER-RUS-REJ deltas/tasks。
- [x] 5.7 Deltas 对 bytes retention、supported reader、participant presentation 给出唯一答案，
  并保留 no-recovery/no-authority invariants。
- [x] 5.8 已在 tasks/design 中规定：若所选合同与实现不同，登记 `DEFERRED-CODE-CHANGE` 并停止；
  不新增 store/schema/tests。实际 current/required inspection 尚未获 apply 授权。
- [x] 5.9 External Observation/Support Handoff 的 CONTEXT 最终措辞留到 Stage 6；本 Stage 未编辑
  `CONTEXT.md` 或 ADR。
- [x] 5.10 Strict validate 与人工 plan review 已完成；其后已获得单独 apply authorization 并完成
  RER/RUS/REJ sync。OpenSpec full-replacement correction、A-004-T01 工具链遗留及证明边界见
  [Stage 5 planning validation](alignment-audit-60-adjustments/stage-5-planning/01-stage-5-planning-validation.md)
  和 [Stage 5 apply evidence](alignment-audit-60-adjustments/stage-5-apply/)。
- [x] 5.11 已在 apply/sync 后完成只读验证并记录真实 conformance disposition：已检查本地路径没有
  `DEFERRED-CODE-CHANGE`，但结论仅为 bounded local conformance；4 个 Gateway skip、Pydantic
  warnings、live/physical/uninspected-path 限制与 A-004-T01 均已记录。随后在单独 archive
  authorization 下完成 closeout、preflight 与正常归档。

### Gate 5

- [x] A-004 已有唯一 product decision；RER/RUS/REJ main specs 已通过已授权 apply 正常 sync，三者
  对 physical-residue scope、supported reader、participant presentation、terminal location 和
  planned Support Handoff 给出同一 required answer。当前实现结论仅为 bounded local conformance；
  完整 evidence 见 [Stage 5 apply evidence](alignment-audit-60-adjustments/stage-5-apply/)。
- [x] Support Handoff 的 planned 状态没有被解释成 external retention 已获批准；deltas 仅允许它在
  Bundle 可用期间作为未来独立 capability 工作。
- [x] 没有应用代码或 DeerFlow gitlink diff；已无 active change，且已停止。A-004 archive、post-archive
  baseline 和实际 disposition 见
  [Stage 5 post-archive record](alignment-audit-60-adjustments/stage-5-apply/09-a004-post-archive-baseline.md)。
  Stage 6 新授权尚未发生；`DEFERRED-TOOLING-CHANGE A-004-T01` 仍须由独立 OpenSpec tooling
  change 拥有。

## Stage 6 - Normalize Post-Decision Terminology And Status

**Change:** `normalize-post-decision-terminology-status`

**前置条件:** A-003、A-004 已有明确决定；若决定产生 code gap，gap 已单独 deferred。

### 逐项审阅文件

这两项不是独立产品决定，只能在相应前置决定已完成后进入 planning：

- [x] 6.R1 [D-001 Rubric / Runner terminology](alignment-audit-60-adjustments/alignment-audit-60-19-d001-rubric-runner-terminology.md)
- [x] 6.R2 [D-002 post-loss diagnostic terminology](alignment-audit-60-adjustments/alignment-audit-60-20-d002-post-loss-diagnostic-terminology.md)

- [x] 6.0 已为 D-001、D-002 分别填写 apply-time Adjustment Record，并回填实际副作用和
  evidence bound，见 [Stage 6 apply evidence](alignment-audit-60-adjustments/stage-6-apply/)。
- [x] 6.1 以 Stages 4-5 的 accepted specs 为唯一 required-behavior 来源，重新列出受影响
  CONTEXT/ADR 语句；完整 before/after、allowlist 与 evidence boundary 见
  [Stage 6 planning record](alignment-audit-60-adjustments/stage-6-planning/00-stage-6-planning-baseline-and-adjustment-records.md)。
- [x] 6.2 CLI scaffold docs-only change；Focus Card 不拥有 runtime behavior；proposal、design、
  tasks 已完成，`skip_specs: true` 已由 strict validation 接受。
- [x] 6.3 已同步 Rubric/Runner 的 glossary 和 ADR 0025 applicability；只允许
  identity/version + unique criterion IDs 的 deterministic metadata，不扩大已决定合同。
- [x] 6.4 已同步 External Run Observation、Support Handoff 与 Bundle-loss 术语；分别说明
  physical-residue non-claim、supported Bundle-local readability 和 participant presentation。
- [x] 6.5 没有新的 observed deferred code gap；保留 Stages 4-5 的 bounded current/required
  evidence 与 A-004-T01 tooling owner，不用 glossary 掩盖其证明边界。
- [x] 6.6 已复核 Stage 2 的 `planned` Support Handoff 与 `dormant` Dedicated-TUI 状态仍成立，
  没有重新激活路线。
- [x] 6.7a Strict validate、doctor、Charter checker、whitespace 和人工 planning review 已通过；
  这些只证明 planning/doc governance，不证明 apply 或 current behavior。
- [x] 6.7b 已获得单独 docs-only apply authorization；planning completion、validation 或此前
  Stage 的授权均不构成 apply authorization。
- [x] 6.8a Apply 后 docs/governance/full deterministic verification 已通过；结果与限制见
  [Stage 6 scope and verification](alignment-audit-60-adjustments/stage-6-apply/03-stage-6-scope-and-verification.md)。
- [x] 6.8b 已完成 archive 后验证和 post-archive baseline；没有 active OpenSpec change，详见
  [Stage 6 post-archive baseline](alignment-audit-60-adjustments/stage-6-apply/06-stage-6-post-archive-baseline.md)。

### Gate 6

- [x] CONTEXT 只定义语言，不复制 requirement、ADR 论证或 change task。
- [x] Specs、ADR applicability 和 glossary 不再对 A-003/A-004 给出互斥答案。
- [x] 所有已知实现/证明差异均以 bounded evidence 或 deferred gap 明示。
- [x] No-code diff；无 active change；已停止、完成 Stage 7 并关闭 audit plan。

### Stage 6 Planning Evidence

- [x] 2026-08-13：OpenSpec planning artifacts 完成且
  `openspec validate normalize-post-decision-terminology-status --strict`、
  `openspec doctor --json`、`python3 openspec/governance/check_agent_charter.py` 和
  `git diff HEAD --check` 通过。唯一 future-apply allowlist 是 `CONTEXT.md` 的精确
  glossary occurrences、ADR 0006 的既有 postscript 与 ADR 0025 的新增 postscript；用户的
  concept-map worktree hunk 受保护。详见
  [Stage 6 planning record](alignment-audit-60-adjustments/stage-6-planning/00-stage-6-planning-baseline-and-adjustment-records.md)
  与 [Stage 6 planning validation](alignment-audit-60-adjustments/stage-6-planning/01-stage-6-planning-validation.md)。
- [x] 2026-08-13：target 文档 edit 前已重新 capture protected worktree baseline，获得明确
  `APPLY` 授权，并为 D-001/D-002 建立 apply-time Adjustment Record；archive/commit 仍通过
  后续单独 gate 获得授权。

- [x] 2026-08-13：已在 docs-only `APPLY` authorization 下完成并验证 D-001/D-002。HEAD
  `b54eaea` 的 concept-map commit 使 apply baseline clean；Stage 6 contribution 只包含
  allowlisted glossary/ADR occurrences、active change task status 及 Stage 6 evidence。
  验证后出现的 `openspec/CONTEXT.md` Authority Ladder user edit 不重叠且未被吸收。
  strict/doctor/Charter/whitespace、ADR link 与 `UV_OFFLINE=1 make verify` 都通过；实际
  副作用为 `none observed`，但不扩张到 physical/live/future/uninspected proof。详细记录见
  [Stage 6 apply evidence](alignment-audit-60-adjustments/stage-6-apply/)。
- [x] 2026-08-13：已取得独立 archive/commit authorization；正常 OpenSpec workflow 以
  `--skip-specs` 归档至 `2026-08-13-normalize-post-decision-terminology-status`，无 delta/main
  spec sync。归档后检查、最终 disposition 和当时仍未获授权的 Stage 7 见
  [Stage 6 post-archive baseline](alignment-audit-60-adjustments/stage-6-apply/06-stage-6-post-archive-baseline.md)。

## Stage 7 - Final Honest Re-Audit

本 Stage 不创建 change，只读复审 target authority并更新本审计目录。

- [x] 7.1 已锁定 HEAD `198cf290146b4308e7a8da432d28abd46aca51d1`；无 active change，
  `deerflow/` gitlink/worktree 未修改，详见
  [Stage 7 baseline](alignment-audit-60-adjustments/stage-7-reaudit/00-stage-7-baseline-and-verification.md)。
- [x] 7.2 OpenSpec doctor/strict、Charter/coverage、Markdown/whitespace 和
  `UV_OFFLINE=1 make verify` 均已运行；4 个 real-Gateway integration skip、未运行 live/release
  与其证明边界已如实记录。
- [x] 7.3 已对 A-001..A-009 按 current non-archive authority 逐项重新取证；没有因 archive
  自动关闭任何 finding，见
  [Stage 7 final matrix](alignment-audit-60-adjustments/stage-7-reaudit/02-current-authority-final-matrix.md)。
- [x] 7.4 Stage 7 closeout 当时 A-002 仍是 `DEFERRED-CODE-CHANGE`，没有自动 gitlink detector；
  因而登记了独立 owner。该后续工作随后已完成，见“关闭后交接状态”的 A-002 closeout 与
  [DONE-002](../../../_done/_done_todos/todo-a002-gitlink-boundary-detector.md)。
- [x] 7.5 A-009 仍只声称 ID-level traceability；semantic mapping 仍为 `OPTIONAL-HARDENING`，
  并已登记 [A-009 backlog candidate](../../../todos/todo-a009-risk-based-semantic-traceability.md)。
- [x] 7.6 A-003/A-004 的 required behavior、bounded current inspection 与 deferred work 均有明确
  owner；A-004-T01 被独立登记，未被当作 runtime gap。
- [x] 7.7 已更新 `alignment-audit-00-current-state.md` 的 Stage 7 final matrix，同时保留
  2026-08-12 原始审计快照。
- [x] 7.8 已为仍需代码/工具或可选 hardening 的事项建立独立 backlog candidates；本 Stage 未实施它们。
- [x] 7.9 N-002 已通过独立 change `2026-08-13-reconcile-policy-routing-cardinality` 修正并归档；
  policy-library index、authoring route、Harness Focus Gate 与 DRC-001 现在均要求选择所有
  route-table trigger 实际适用的 canonical policy，同时保持一个 primary causal owner 与
  guidance-only boundary。归档后 strict/doctor/Charter/coverage/whitespace 均通过，详见
  [Stage 7 N-002 closeout](alignment-audit-60-adjustments/stage-7-reaudit/03-n002-post-archive-closeout.md)。

### Definition Of Done

- [x] 已被事实证伪的历史概念不再污染 current authority。
- [x] 文档之间不再互相矛盾；N-002 的 policy-cardinality current-authority 矛盾已由独立 change
  修正并归档。
- [x] Main spec 的每次语义变化都有产品决定和 OpenSpec change，不是静默追随实现。
- [x] 每个 adjustment 的内容、风险、可能副作用、控制与实际观察均可逐项追溯。
- [x] 未实现能力全部标 `planned`、`dormant` 或 `deferred`，不冒充 current。
- [x] A-002 已由独立 metadata-only detector change 关闭；A-009 保持开放，但没有假绿或过度证明声明。
- [x] alignment 主线未修改 Python、tests、runtime contracts、governance executables 或
  `deerflow/`。
- [x] 全量验证结果及其不能证明的部分均已记录。

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

本 alignment audit plan 已完成并关闭。A-001、A-003、A-004、A-005、A-006、A-007 和 A-008/N-002
均已在其明确证据边界内关闭；N-002 的 archived change 是
[`2026-08-13-reconcile-policy-routing-cardinality`](../../../../openspec/changes/archive/2026-08-13-reconcile-policy-routing-cardinality/)。
完整的归档后结论、验证范围和不应过度声称的边界见
[Stage 7 N-002 closeout](alignment-audit-60-adjustments/stage-7-reaudit/03-n002-post-archive-closeout.md)。

后续不再属于本计划：A-004-T01 的 owner 调查已完成，确认它是外部 OpenSpec CLI 的
scenario-identity/rename 能力缺口，而不是本仓或 DeerFlow 的实施项。除非获得对
`Fission-AI/OpenSpec` 外部协作或已支持版本升级的单独授权，它没有本仓可安全执行的下一步；A-009
仅在高风险 requirement change 需要更强保证时才启动。它们的顺序、风险和重启条件见
[active todo index](../../../todos/README.md)。

## 关闭后交接状态

本节只记录已关闭 audit 的后继工作，不重新打开 Stage 0..7，也不把独立实现授权倒灌为
alignment audit 的 scope。

- [x] 2026-08-13：已从三个独立 backlog 中选定 A-002 为下一项工作；原因是它是唯一高优先级的
  repository-governance 保护缺口，而非 current-authority 文案矛盾。
- [x] 2026-08-13：已完成 `establish-gitlink-boundary-detector` 的 OpenSpec **planning only**；
  [proposal](../../../../openspec/changes/archive/2026-08-13-establish-gitlink-boundary-detector/proposal.md)、
  [delta spec](../../../../openspec/changes/archive/2026-08-13-establish-gitlink-boundary-detector/specs/project-structure/spec.md)、
  [design](../../../../openspec/changes/archive/2026-08-13-establish-gitlink-boundary-detector/design.md) 和
  [tasks](../../../../openspec/changes/archive/2026-08-13-establish-gitlink-boundary-detector/tasks.md) 已齐全。方案指定
  `project-structure` registry/architecture checker 为唯一 metadata-only owner：锁定 `deerflow`
  路径与 full SHA，要求 root index gitlink、nested `HEAD` 和 nested porcelain 同时一致；intentional
  bump 只在同一受审 change 同步指针与 lock 时通过。规划没有读取/修改 `deerflow/` 源码，也没有实施
  Python、测试、registry、gate 或 main-spec sync。`openspec validate ... --strict`、Charter checker、
  doctor 与 whitespace 检查均通过。
- [x] A-002：用户于 2026-08-13 明确发出 `APPLY`，独立 change
  `establish-gitlink-boundary-detector` 已进入实施。准入 baseline、风险/副作用和停止条件记录在
  [A-002 apply admission](alignment-audit-60-adjustments/a002-gitlink-detector-apply/00-a002-apply-admission-baseline-and-control-review.md)；
  本授权不包含 archive 或 commit，也不允许读取或修改 `deerflow/` 源码。
- [x] 2026-08-13：A-002 已完成 archive closeout 并归档为
  [`2026-08-13-establish-gitlink-boundary-detector`](../../../../openspec/changes/archive/2026-08-13-establish-gitlink-boundary-detector/)。
  `PRS-018` 现在使完整 architecture governance 对 `deerflow` 的 declared lock、root index、nested
  `HEAD` 与 porcelain 清洁度 fail closed；它只使用三条固定的只读 Git metadata 查询和 `lstat`，不读取
  或修改上游源码，不批准 future bump，也不证明 compatibility。归档前 strict/doctor、全部 project
  governance gates、`UV_OFFLINE=1 make verify` 和 `git diff --check` 均通过；归档后无 active
  change，真实 gitlink pointer/nested `HEAD` 仍为 `66b9e7f21212490cf92fafac137542b9deb06615`，nested
  porcelain 与 gitlink diff 均为空。完整的风险、副作用和证明边界见
  [A-002 archive closeout](alignment-audit-60-adjustments/a002-gitlink-detector-apply/02-a002-archive-closeout-review.md)。
  A-002 todo 已移至 [DONE-002](../../../_done/_done_todos/todo-a002-gitlink-boundary-detector.md)；没有
  自动启动 A-004-T01 或 A-009。
- [x] 2026-08-13：已完成 A-004-T01 的只读 owner 调查。安装的
  `@fission-ai/openspec@1.8.0` 用 scenario 标题字符串判断 `MODIFIED` requirement 是否会丢失既有
  scenario；同一函数同时供 strict validate 与 archive 使用，且只实现 requirement 级 rename，未实现
  scenario-level mapping 或 stable ID。因此两处 legacy RER 标题不能由本仓 governance checker、Harness
  或 DeerFlow 安全地修复。最小 no-write 复现仅替换两条标题时仍报告旧标题缺失；正文的 Bundle-local
  contract 未改变。完整的 owner、风险、证据与重启条件见
  [A-004-T01 owner research](alignment-audit-60-adjustments/a004t01-scenario-rename-owner-research/a004t01-scenario-rename-owner-research.md)。
  当前 disposition 是 `DEFERRED-EXTERNAL-TOOLING`: 保留标题作为 validation-compatible identifiers，
  等待用户单独授权上游 Fission-AI/OpenSpec issue/proposal/PR 或明确支持该能力的版本升级调查；没有
  自动启动 A-009，也没有外部写入、CLI patch、RER spec 或 `deerflow/` 改动。
