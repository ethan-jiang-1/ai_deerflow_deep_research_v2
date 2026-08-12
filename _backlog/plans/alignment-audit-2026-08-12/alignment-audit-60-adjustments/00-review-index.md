# Alignment Audit 60 - Adjustment Review Index

> 类型: 逐项审阅目录
> 状态: **REVIEW REQUIRED - NONE APPROVED FOR APPLY**
> 总控计划: [60 - Progressive Execution Plan](../alignment-audit-60-progressive-execution-plan.md)
> 判定背景: [55 - Cleanup Decision Record](../alignment-audit-55-cleanup-decision-record.md)

这里的每个文件只解释一个 adjustment 或一个互斥选择。请按编号逐个审阅；勾选
`批准`只代表该项可以进入对应 Stage 的 planning/apply 评审，**不**自动授权创建或
apply OpenSpec change。

## 审阅顺序

| # | 文件 | Stage | 类型 | 当前状态 |
| --- | --- | --- | --- | --- |
| 01 | [C-001 real upstream topology](alignment-audit-60-01-c001-real-upstream-topology.md) | 1 | 确定退役 | 已审，限 planning |
| 02 | [C-002 closeout boundary](alignment-audit-60-02-c002-closeout-boundary.md) | 1 | 确定退役 | 已审，限 planning |
| 03 | [C-003 editable harness path](alignment-audit-60-03-c003-editable-harness-path.md) | 1 | 确定退役 | 已审，限 planning |
| 04 | [C-004 workspace / bundle definition](alignment-audit-60-04-c004-workspace-bundle-definition.md) | 2 | 确定退役 | 已审，限 planning |
| 05 | [C-005.a completed-work tense](alignment-audit-60-05-c005a-completed-work-tense.md) | 2 | 确定退役 | 已审，限 planning |
| 06 | [C-005.b archived change dependency](alignment-audit-60-06-c005b-archived-change-dependency.md) | 2 | 确定退役 | 已审，限 planning |
| 07 | [C-006 withdraw broad CONTEXT relocation](alignment-audit-60-07-c006-relocate-context-design-material.md) | 2 | 撤回，无动作 | 不进入 planning/apply |
| 08 | [C-007 policy cardinality](alignment-audit-60-08-c007-policy-cardinality.md) | 2 | 确定退役 | 已审，限 planning |
| 09 | [C-008 remove false all-node smoke claim](alignment-audit-60-09-c008-suite-smoke-roadmap-status.md) | 2 | 确定退役 | 已审，限 planning |
| 10 | [C-009 readable-review-report requirement](alignment-audit-60-10-c009-readable-review-report-requirement.md) | 2 | 确定退役 | 已审，限 planning |
| 11 | [C-010.a report artifact vs export](alignment-audit-60-11-c010a-report-artifact-vs-export.md) | 2 | current claim 退役 | 已审，限 planning |
| 12 | [C-010.b Support Handoff status](alignment-audit-60-12-c010b-support-handoff-status.md) | 2 | 状态校准 | 已审，限 planning |
| 13 | [C-010.c TUI / Local-First dormant](alignment-audit-60-13-c010c-tui-local-first-dormant.md) | 2 | 状态校准 | 已审，限 planning |
| 14 | [C-011 ADR status / applicability](alignment-audit-60-14-c011-adr-status-applicability.md) | 2 | 历史状态 | 已审，限 planning |
| 15 | [A-003 option A: criterion IDs metadata](alignment-audit-60-15-a003a-criterion-ids-metadata.md) | 4 | 互斥产品决定 | 已确认，限后续 planning |
| 16 | [A-003 option B: Rubric review-only](alignment-audit-60-16-a003b-rubric-review-only.md) | 4 | 互斥产品决定 | 已审，明确排除 |
| 17 | [A-004 option A: Bundle-local-only](alignment-audit-60-17-a004a-bundle-local-only.md) | 5 | 互斥产品决定 | 待定 |
| 18 | [A-004 option B: external diagnostic retention](alignment-audit-60-18-a004b-external-diagnostic-retention.md) | 5 | 互斥产品决定 | 待定 |
| 19 | [D-001 Rubric / Runner terminology](alignment-audit-60-19-d001-rubric-runner-terminology.md) | 6 | 条件同步 | 等待 A-003 |
| 20 | [D-002 post-loss terminology](alignment-audit-60-20-d002-post-loss-diagnostic-terminology.md) | 6 | 条件同步 | 等待 A-004 |

## 使用规则

- Stage 1、2 的每个 `C-*` 文件都必须先审阅，才能进入对应 change 的 planning。
- 15/16 和 17/18 各自只能选择一个；未选择前不触碰 A-003/A-004 相关 authority。
- 19/20 不是独立产品决定，只能忠实投影已选择的 A-003/A-004 合同。
- 每个文件的“审阅结论”由审阅者填写。执行者还必须按 `60` 的 Adjustment Record 模板
  回填实施后的实际副作用和证据范围。
- 本目录中的文件与 `55` 判断记录不一致时，立即停止。先更新判定和本文件，再继续。
