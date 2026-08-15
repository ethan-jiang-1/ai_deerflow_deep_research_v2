# Closed Plans Index — 已完成 plan 归档

> 最后更新: 2026-08-15 | `_backlog/_done/_closed_plans/` — 已完成 plan 的归档目录。
> 接收来自 [`../../plans/`](../../plans/) 的 plan。`_` 前缀 = coding agent 默认忽略。
>
> **plan 完成后文件名不变，位置即状态。** 移入时分配 `CLS-NNN` 序号（Closed），按完成时间递增。

## 接收一个完成的 plan

plan 完成后从 `_backlog/plans/` 通过 `git mv` 移入本目录：
1. 在本文件表格加一行（CLS-NNN + 日期 + 文件名 + 简述），编号 = 当前最大 + 1
2. 更新最后的 "Next available plan ID" 行
3. 更新 `../../plans/README.md`（移除该 plan 的行）
4. 更新 `../README.md`（计数 +1）

---

## 已完成列表

| ID | Date | File | Summary |
|----|------|------|---------|
| CLS-001 | 2026-07-13 | [deep-research-tui-hitl-terminal-workbench.md](deep-research-tui-hitl-terminal-workbench.md) | HITL in Terminal Workbench — demo TUI split to `add-deep-research-lifecycle-demo-tui`; formal integration deferred to backlog |
| CLS-002 | 2026-07-15 | [deep-research-05-bootstrap-node.md](deep-research-05-bootstrap-node.md) | Real bootstrap node — atomic bundle establishment + schema/version marker, non-gated binding-validation replacing the fake fixture pass (OpenSpec `implement-deep-research-bootstrap-node`, archived 2026-07-15) |
| CLS-003 | 2026-07-17 | [test-assets-postmortem-real-mode-integration.md](test-assets-postmortem-real-mode-integration.md) | Real-mode integration incident timeline and root-cause evidence absorbed by executable incident coverage and regression descent |
| CLS-004 | 2026-07-17 | [test-assets-bug-to-test-mapping.md](test-assets-bug-to-test-mapping.md) | Historical bug-to-test recommendations reconciled against collected deterministic selectors |
| CLS-005 | 2026-07-17 | [test-assets-demo-design-coverage.md](test-assets-demo-design-coverage.md) | Demo/public-entry design risks absorbed into deterministic and release acceptance assets |
| CLS-006 | 2026-07-17 | [test-assets-layered-strategy.md](test-assets-layered-strategy.md) | Early layered strategy superseded by the four asset classes, authenticity ladder, and three execution lanes |
| CLS-007 | 2026-07-17 | [deep-research-test-assets-master-strategy.md](deep-research-test-assets-master-strategy.md) | Three-batch testing strategy completed through deterministic PR, credentialed live, and full-real release gates |
| CLS-008 | 2026-07-19 | [deep-research-demo-full-pipeline.md](deep-research-demo-full-pipeline.md) | Demo CLI fake + real + TUI full pipeline design; implemented via `add-deep-research-demo-full-pipeline` (archived 2026-07-17) |
| CLS-009 | 2026-07-19 | [deerflow-native-deep-research-graph.md](deerflow-native-deep-research-graph.md) | Master architecture: DPT isomorphic mapping, 00–18 roadmap — all 18 changes implemented and archived |
| CLS-010 | 2026-07-19 | [deep-research-spec-gates-and-coverage.md](deep-research-spec-gates-and-coverage.md) | Earlier spec-gate proposal largely absorbed by evaluation-hardening; remaining work distilled into [deep-research-unified-verification-gates.md](deep-research-unified-verification-gates.md) |
| CLS-011 | 2026-07-19 | [deep-research-unified-verification-gates.md](deep-research-unified-verification-gates.md) | Unified verification gates implemented and archived via OpenSpec `consolidate-deep-research-verification-gates` |
| CLS-012 | 2026-07-19 | [deep-research-tui-onboarding-and-visibility.md](deep-research-tui-onboarding-and-visibility.md) | TUI onboarding and stage visibility design implemented through OpenSpec `improve-deep-research-tui-onboarding` |
| CLS-013 | 2026-07-22 | [deep-research-run-bundle-session-and-workbench.md](deep-research-run-bundle-session-and-workbench.md) | Run bundle as the durable local session, including binding, brokered discovery/operations, and metadata-only local terminal workbench; implemented through four archived OpenSpec changes, with Gateway/Web deferred |
| CLS-014 | 2026-07-22 | [deep-research-structured-output-linting.md](deep-research-structured-output-linting.md) | Architecture audit: LangGraph/Python retains control authority; existing node-local JSON/Pydantic boundaries and future reopen triggers replace the obsolete global Markdown/YAML/JSON linter proposal |
| CLS-015 | 2026-07-23 | [deep-research-real-run-intake-and-observability.md](deep-research-real-run-intake-and-observability.md) | Real CLI intake, lifecycle visibility, retained summary/event journal, inspection, and strict-msgpack hardening completed through two archived OpenSpec changes; external provider/tool root cause remains an evidence-led follow-up |
| CLS-016 | 2026-07-22 | [accelerate-deep-research-change-delivery.md](accelerate-deep-research-change-delivery.md) | Deterministic change-delivery acceleration completed through one cached marker catalog, focused timed verification targets, duration policy, requirement-impact metadata, and a 30.175-second reference benchmark |
| CLS-017 | 2026-07-28 | [node-agent-capability-remediation-plan.md](node-agent-capability-remediation-plan.md) | Node-agent capability remediation completed across all 16 direct model branches through four archived cohorts; future readiness/final-delivery admission remains separately deferred |
| CLS-018 | 2026-07-28 | [human-interaction-remediation-plan.md](human-interaction-remediation-plan.md) | Human-interaction contract remediation completed through the typed semantic-intake contract and hardened HITL1 lifecycle; supporting HITL UX research is retained alongside the closed plan |
| CLS-019 | 2026-07-28 | [agentic-workflow-governance-plan.md](agentic-workflow-governance-plan.md) | Agentic workflow governance, capability foundation, and behavior calibration completed through six archived OpenSpec changes; future deferred-node admission remains independently guarded |
| CLS-020 | 2026-07-29 | [node-agent-control-flow-readability-progressive-plan.md](node-agent-control-flow-readability-progressive-plan.md) | Two-change reader-interface rollout completed; its deliberately non-uniform projection decision is superseded by the cognitive-node-first governance plan. |
| CLS-021 | 2026-07-29 | [node-agent-control-flow-readability.md](node-agent-control-flow-readability.md) | Node-agent control-flow readability audit and v1 reader-interface direction absorbed by the completed reader-interface rollout; supporting worksheets and examples are retained in the sibling directory. |
| CLS-022 | 2026-07-30 | [node-agent-cognitive-loop-governance-progressive-plan.md](node-agent-cognitive-loop-governance-progressive-plan.md) | Cognitive-node-first governance completed through all 12 planned changes, including verification, main-spec synchronization, and archive. |
| CLS-023 | 2026-07-31 | [agent-directory-name-and-module-seam.md](agent-directory-name-and-module-seam.md) | Deep Research module-root naming decision and impact audit completed; the `agent/` → `deerflow_research/` migration subsequently landed in commits `12b94a7` and `b8204ac`. |
| CLS-024 | 2026-08-01 | [bootstrap-fake-placement-and-default-mode.md](bootstrap-fake-placement-and-default-mode.md) | Historical package-local fixture and full-fake-default baseline superseded by OpenSpec `isolate-fixture-implementations`, which isolates fixture source and makes the reflected public lifecycle all-real. |
| CLS-025 | 2026-08-01 | [node-prompt-review-output-isolation.md](node-prompt-review-output-isolation.md) | Hidden, ignored, on-demand node-prompt review output implemented by OpenSpec `isolate-fixture-implementations`; the committed catalog is removed and clean-checkout behavior is verified. |
| CLS-026 | 2026-08-02 | [real-demo-stabilization-bugfix-program.md](real-demo-stabilization-bugfix-program.md) | BUG-017 至 BUG-021 completed through two archived repair changes and deterministic acceptance; the retained credentialed Budget exhaustion is supplemental, non-blocking evidence and does not open a third change. |
| CLS-027 | 2026-08-02 | [policy-gate-injection-layer.md](policy-gate-injection-layer.md) | 三项连续 OpenSpec policy/guardrail change 均已实现、验证、归档并提交；配套架构审查与 operation-guidance probe 证据一并归档。 |
| CLS-028 | 2026-08-03 | [real-research-reliability.md](real-research-reliability.md) | 真实 CLI 的外部读取重试和 HITL1 prompt/parser 兼容性已通过 OpenSpec `harden-real-research-external-io` 实现、验证、同步主规范并归档；后续历史红绿差分回放关闭 BUG-022/023。 |
| CLS-029 | 2026-08-04 | [cognitive-evaluation-suite.md](cognitive-evaluation-suite.md) | V1 认知评估 Runner、隔离 Bundle、人工发起 Review 和 HITL1/Wave0 smoke 已通过 OpenSpec `add-cognitive-evaluation-suite` 实现、同步主规格、归档并提交；V2 Flow lane 与脱敏仍需独立 change。 |
| CLS-030 | 2026-08-08 | [deep-research-harness-agent-native-progressive-plan.md](deep-research-harness-agent-native/deep-research-harness-agent-native-progressive-plan.md) | Agent-native ownership 计划完成 Direction-loop、HITL1、Wave0、Wave1、Wave2 与 shared deterministic gate repair，全部同步/归档后明确收拢，不建立 successor change。 |
| CLS-031 | 2026-08-08 | [deep-research-harness-agent-native-workflow-research.md](deep-research-harness-agent-native/deep-research-harness-agent-native-workflow-research.md) | DeerFlow/LangGraph workflow、`note` 语义与 refinement gap 的一手资料研究，已由 Direction-loop 和后续 ownership changes 吸收。 |
| CLS-032 | 2026-08-08 | [deep-research-harness-test-asset-audit.md](deep-research-harness-agent-native/deep-research-harness-test-asset-audit.md) | 测试资产基线、证据真实性分层与缺口审计，已作为 Direction-loop 与认知 ownership deterministic evidence 的历史输入保留。 |
| CLS-033 | 2026-08-09 | [cli-tui-entry-integrity-repair_plan.md](cli-tui-entry-integrity-repair_plan.md) | CLI/TUI entry-integrity repair 的五个 OpenSpec changes 已验证、同步主规格并归档；README 已提供受限的 Entry Surfaces 选择地图，配套[研究记录](cli-tui-entry-integrity-repair-research.md)随同保留。 |
| CLS-034 | 2026-08-10 | [diagnostics-event-journal.md](diagnostics-event-journal.md) | Bundle-local Run Event Journal 的系统性诊断设计已通过 `systemic-run-event-journal` 实现、同步主规格、归档并提交；配套[研究记录](diagnostics-event-journal/research.md)随同保留。 |
| CLS-035 | 2026-08-11 | [openspec-agent-charter-topology-flattening.md](openspec-agent-charter-topology-flattening.md) | Charter/policy 一级拓扑迁移经 `rehome-agent-charter-policy-library` 落地并归档；charter 边界行被 @impl 清理误删后已恢复，governance 全绿后关闭。 |
| CLS-036 | 2026-08-12 | [openspec-extension-readme-restructure.md](openspec-extension-readme-restructure.md) | OpenSpec 治理分层收口：SCC closeout 契约经 `selected-change-closeout-evidence` 修复并归档，governance README 改为纯导航索引，ID 约定迁至 req-registry；两项完成后关闭。 |
| CLS-037 | 2026-08-13 | [alignment-audit-2026-08-12/](alignment-audit-2026-08-12/alignment-audit-00-current-state.md) | 七阶段 Harness/OpenSpec/CONTEXT 对齐审计完成；A-002 gitlink detector 随后完成，A-004-T01 外部 OpenSpec 工具限制已暂停，A-009 保持条件触发的可选 hardening。 |
| CLS-038 | 2026-08-15 | [deep-research-post-migration-convergence/](deep-research-post-migration-convergence/) | 迁移后收敛审计的54个Candidate经00--07八个OpenSpec changes全部关闭；最终复审记录authority/surface/recovery/guard、residual allowlist、验证基线和未运行外部证据。 |
| CLS-039 | 2026-08-15 | [openspec-support-topology-simplification.md](openspec-support-topology-simplification.md) | OpenSpec 支持拓扑收敛已通过 `simplify-openspec-support-topology` 实现、同步主规格、归档并提交为 `188bba5`；治理与 focused gate 通过，full verify 的三项基线 metadata selector 失败不归因于该 change。 |

**Next available plan ID: CLS-040**
