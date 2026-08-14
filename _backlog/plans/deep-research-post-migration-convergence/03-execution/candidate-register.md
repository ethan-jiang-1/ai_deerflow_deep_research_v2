# Audited Candidate Register

> 导航: [执行层索引](README.md) | [默认执行入口](99-progressive-execution.md) | [审计结果](../02-audit-findings/)
> 角色: `70-78` 最终审计 Candidate 的唯一导航总账，不复制完整证据
> 应用/spec 取证基线: `5bb41c16a45ff3caae6e5b1e900610c91bf68336`
> 审计综合 revision: `811203726cfa6478ceebdabc378daabce1b6758b`
> 执行编排 revision: `91709e740fdafcb8275c2a182a61554342e2bd08`；8-change program budget
> 状态: 本基线审计完成；54 个最终 Candidate；00 governance bootstrap 已 archive（`8661693`）；01 已 archive 并同步 main spec（`47a3bb5`）；其 16 个冻结 Candidate 已记录终态；0 active OpenSpec changes

## 使用规则

- Candidate ID、完整证据、current/target owner、迁移/删除条件和 guard 以对应 findings 尾部为准。
- 所有 `ready` 仍服从 OR-C01/OR-C02 的 P0 repository-delivery gate；P0 archive前不得启动产品 cleanup。
- `ready` 表示证据足以起草 owning OpenSpec change，不表示本 plan 已授权直接改代码。
- `blocked` 必须先关闭表中 decision/data blocker；本地样本不能替代外部 support closure。
- `keep/guard/history` 不创建 keep-only change，但必须作为相关 change 的 non-regression gate。
- umbrella/linked row只做跨报告路由，不重复创建 change。

## Initial hypothesis lineage

原始 plan 的 `PC-001..020` 只是待审假设，不是最终 Candidate ID。它们全部完成取证后按下表收敛；
旧 ID 不再用于实施，避免与本表 `PC-C*`（Persisted Compatibility）混淆：

| Initial hypothesis | Final Candidate | 审计后变化 |
| --- | --- | --- |
| PC-001 `phase agent` identity | NC-C02 | 确认为纵向rename，不与capability contract减法混批 |
| PC-002 legacy capability binding | NC-C01 | 确认为ready deletion，required ref接管 |
| PC-003 `FULL_FAKE` enum/value | FM-C02 | 保持migrate-then-retire，但依赖FM-C01产品选择与data closure |
| PC-004 `bind_full_fake` naming | FM-C01 | 不只是rename；发现no-graph path写入不诚实`all_real` provenance |
| PC-005 `MIXED` mode | FM-C03 | rejected as cleanup；explicit mixed composition是current evidence |
| PC-006 `research-run-session` | RS-C02 | 按requirement逐项迁入Bundle/Journal owners后退役mixed capability |
| PC-007 lifecycle binding | RS-C01 | negative invariants迁移后退役整个空壳capability |
| PC-008 retired import guard | RS-C05 | guard保留，但evidence owner迁到current requirements |
| PC-009 session-named current tests | RS-C02 | 随RUS ownership迁移，不建test-rename-only change |
| PC-010 dormant TUI/local-first | EC-C01, EC-C02 | active operator entries保留；dormant glossary direction迁回history |
| PC-011 demos/workbench overlap | EC-C01 | rejected as merge/delete；各entry有独立用户与责任 |
| PC-012 config/path compatibility | EC-C03, EC-C05, PC-C07, RC-C04 | 拆成old-path rejection guard、checkpointer promise与AppConfig alias support |
| PC-013 CONTEXT tail | NC-C03, OR-C05 | 逐段迁移owner后删除design/status residue，不按篇幅整体搬走 |
| PC-014 superseded/dormant ADRs | OR-C05, OR-C08 | historical keep；只修current glossary/route，不重写ADR事实 |
| PC-015 dated release/baseline docs | TA-C05..C07, OR-C06 | DPT duplicate删除；baseline/attestation历史保留；regression policy current keep |
| PC-016 suspended EVH-024 | TA-C03 | retain suspension boundary，未授权激活或删除 |
| PC-017 empty scaffolding | TA-C01, TA-C02 | 8个冗余marker与唯一空e2e scaffold分别删除 |
| PC-018 evidence registries | TA-C04 | rejected wholesale；只随owning behavior逐行减法 |
| PC-019 old-root strings | EC-C03 | retain rejection/anti-resurrection guards |
| PC-020 `REPAIR_EXHAUSTED` | PC-C04 | 保持migrate-then-retire，需Bundle data与exact target outcome |

## Node Cognition

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [NC-C01](../02-audit-findings/70-node-cognition-findings.md#nc-c01---close-node-capability-migration) | delete legacy capability cohort/default | ready | required capability ref / `converge-node-language-and-product-records` |
| [NC-C02](../02-audit-findings/70-node-cognition-findings.md#nc-c02---converge-node-cognition-language-vertically) | vertical rename | ready after NC-C01 | canonical product/program/runtime terms / `converge-node-language-and-product-records` |
| [NC-C03](../02-audit-findings/70-node-cognition-findings.md#nc-c03---restore-context-to-glossary-only-ownership) | migrate design facts, delete glossary tail | after NC-C02 term table | ADR/spec own design / `converge-node-language-and-product-records` |

## Run, Bundle, Session, Observation

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [RS-C01](../02-audit-findings/71-run-session-and-observation-findings.md#rs-c01---retire-lifecycle-binding-capability-and-its-positive-registry-claims) | migrate invariants then retire capability | ready | DRH/REJ/PRS owners / `converge-run-bundle-observation-authority` |
| [RS-C02](../02-audit-findings/71-run-session-and-observation-findings.md#rs-c02---consolidate-research-run-session-into-current-bundlejournal-owners) | migrate then delete mixed old capability | after RS-C01 | Bundle/Journal owners / `converge-run-bundle-observation-authority` |
| [RS-C03](../02-audit-findings/71-run-session-and-observation-findings.md#rs-c03---rename-bundle-capabilities-without-changing-semantics) | rename capability paths | with RS-C02 | Run Bundle capability names / `converge-run-bundle-observation-authority` |
| [RS-C04](../02-audit-findings/71-run-session-and-observation-findings.md#rs-c04---keep-local-session-workbench-and-move-its-registry-to-the-actual-owner) | keep surface; repair stale registry prose | with RS-C02 | Bundle lifecycle + workbench adapter / `converge-run-bundle-observation-authority` |
| [RS-C05](../02-audit-findings/71-run-session-and-observation-findings.md#rs-c05---retain-anti-resurrection-tests-under-current-evidence-owners) | retain guards; migrate evidence owner | non-regression | DRH/REJ/PRS/RWB requirements / attached to `converge-run-bundle-observation-authority` |

## Fixture And Implementation Mode

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [FM-C01](../02-audit-findings/72-fixture-mode-findings.md#fm-c01---resolve-and-retire-the-no-graph-full-fake-lifecycle-path) | product decision; recommend migrate then delete | blocked: zero-credential UX decision | explicit fixture graph or honest simulator / `converge-run-input-and-composition-contracts` |
| [FM-C02](../02-audit-findings/72-fixture-mode-findings.md#fm-c02---retire-persisted-full_fake-mode-only-after-support-closure) | migrate then delete old enum | blocked: FM-C01 + retained data | honest current modes / `converge-run-input-and-composition-contracts` |
| [FM-C03](../02-audit-findings/72-fixture-mode-findings.md#fm-c03---keep-fixture-source-and-explicit-mixed-composition) | keep | non-regression | fixture/mixed guard / attached to `converge-run-input-and-composition-contracts` |
| [FM-C04](../02-audit-findings/72-fixture-mode-findings.md#fm-c04---preserve-missing-mode-compatibility-until-retained-states-are-migrated) | migrate then delete default reader | blocked: retained states | explicit mode / `converge-run-input-and-composition-contracts` |

## Entry And Configuration

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [EC-C01](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c01---keep-distinct-current-entry-surfaces) | guard-retained: distinct entries | archived 01; entry guard remains falsifiable | product/operator/evaluation roles remain distinct |
| [EC-C02](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c02---move-dormant-local-first-direction-out-of-current-language) | migrate history, delete dormant glossary term | ready | ADR history + current entry terms / `converge-node-language-and-product-records` |
| [EC-C03](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c03---retain-old-entry-rejection-guards) | guard-retained: old-entry rejection | archived 01; entry guard remains falsifiable | deployment/structure admission |
| [EC-C04](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c04---delete-test-only-demo-compatibility-helpers) | retired after canonical profile/preflight transfer | archived 01; canonical pre-Adapter failure and redaction tests pass | canonical demo profile/preflight APIs |
| [EC-C05](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c05---decide-legacy-checkpointer-support-explicitly) | deployment decision | linked to PC-C07 | database-only or bounded legacy reader / `converge-runtime-input-compatibility` |
| [EC-C06](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c06---delete-the-researchgraphrecipecreate-constructor-after-export-scope-closure) | delete alias after support closure | blocked: Python export support | `all_real()` / `converge-run-input-and-composition-contracts` |
| [EC-C07](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c07---decide-the-disable_clarification-trusted-context-compatibility-window) | runtime/product decision | blocked: host producer inventory | `non_interactive` / `converge-runtime-input-compatibility` |

## Tests And Evidence Assets

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [TA-C01](../02-audit-findings/74-test-and-evidence-asset-findings.md#ta-c01---delete-eight-redundant-gitkeep-markers) | retired: eight redundant markers | archived 01; retained roots and asset guard pass | real tracked files |
| [TA-C02](../02-audit-findings/74-test-and-evidence-asset-findings.md#ta-c02---retire-the-empty-testse2e-scaffold-and-registry-entry) | retired: empty scaffold and exact registry row | archived 01; lane and structure guards pass | actual test directories |
| [TA-C03](../02-audit-findings/74-test-and-evidence-asset-findings.md#ta-c03---retain-the-evh-024-suspension-boundary) | guard-retained: EVH-024 suspension | archived 01; selector remains suspended and uncollected | evaluation-hardening owner |
| [TA-C04](../02-audit-findings/74-test-and-evidence-asset-findings.md#ta-c04---keep-executable-evidence-registries-and-subtract-rows-only-with-their-owner) | guard-retained: executable joins | archived 01; owner-local row subtraction only | existing executable joins |
| [TA-C05](../02-audit-findings/74-test-and-evidence-asset-findings.md#ta-c05---delete-the-superseded-dpt-report-and-its-shape-only-test-after-evidence-comparison) | retired after provenance comparison | archived 01; retained provenance route contract passes | baseline + attestation + regression policy |
| [TA-C06](../02-audit-findings/74-test-and-evidence-asset-findings.md#ta-c06---preserve-dated-baseline-and-attestation-as-explicitly-historical-evidence) | historical-retained | archived 01; dated epochs remain distinct | frozen evidence epochs |
| [TA-C07](../02-audit-findings/74-test-and-evidence-asset-findings.md#ta-c07---keep-regression-descent-as-current-evidence-policy) | guard-retained: regression descent | archived 01; current policy route retained | test/evaluation governance |

## Persisted Compatibility

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [PC-C01](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c01---delete-redundant-profile-compatibility-apis-while-preserving-the-canonical-v1-reader-policy) | delete duplicate helper; decide v1 window | helper ready, reader blocked | canonical runtime reader / `converge-run-input-and-composition-contracts` |
| [PC-C02](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c02---delete-parse_profile_response-after-test-migration) | delete wrapper after test/export migration | blocked: Python export support | `parse_profile_input()` / `converge-run-input-and-composition-contracts` |
| [PC-C03](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c03---migrate-graph-checkpoints-before-deleting-repair_counts) | migrate then delete schema field | blocked: checkpoint inventory/cutover | gate kernel / `converge-retained-run-data-compatibility` |
| [PC-C04](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c04---retire-repair_exhausted-only-after-bundle-data-support-closure) | migrate then delete enum | blocked: Bundle data + target reason | current terminal outcomes / `converge-retained-run-data-compatibility` |
| [PC-C05](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c05---keep-current-refinement-facts-and-their-old-state-optional-reader) | keep | non-regression | Bundle refinement recovery |
| [PC-C06](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c06---preserve-old-run-observation-readers-until-retained-records-close) | migrate/expire old readers; keep summary v2 | blocked: Journal retention | v3 manifest/event / `converge-retained-run-data-compatibility` |
| [PC-C07](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c07---decide-legacy-checkpointer-precedence-before-any-deletion) | deployment decision | blocked: supported config inventory | database-only or bounded reader / `converge-runtime-input-compatibility` |

## Evaluation Boundary

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [EV-C01](../02-audit-findings/76-evaluation-boundary-findings.md#ev-c01---keep-the-evaluation-workspacebundlereviewrun-distinctions) | keep distinctions | non-regression | evaluation domain owners |
| [EV-C02](../02-audit-findings/76-evaluation-boundary-findings.md#ev-c02---retain-missing-layer-compatibility-until-evaluation-bundle-data-closes) | migrate then retire default reader | blocked: evaluation archive inventory | explicit layer / `converge-evaluation-boundary-compatibility` |
| [EV-C03](../02-audit-findings/76-evaluation-boundary-findings.md#ev-c03---converge-evaluation-contract-imports-onto-one-supported-route) | migrate then delete re-export module | blocked: Python import support | domain authority + chosen facade / `converge-evaluation-boundary-compatibility` |
| [EV-C04](../02-audit-findings/76-evaluation-boundary-findings.md#ev-c04---delete-the-unused-compute_metrics-shim) | delete | ready | typed metrics / `converge-evaluation-boundary-compatibility` |
| [EV-C05](../02-audit-findings/76-evaluation-boundary-findings.md#ev-c05---retain-live-report-classification-and-fail-closed-archive-admission) | retain guard | non-regression | live evidence intake |
| [EV-C06](../02-audit-findings/76-evaluation-boundary-findings.md#ev-c06---remove-evaluations-dependency-on-the-profile-parser-wrapper) | delete dependency | with PC-C02 | canonical profile parser / `converge-run-input-and-composition-contracts` |

## OpenSpec And Records

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [OR-C01](../02-audit-findings/77-openspec-and-record-findings.md#or-c01---restore-tracked-ci-workflow-delivery-before-cleanup-implementation) | repaired: tracked CI delivery | archived 01; Git-index guard and clean-clone preflight pass | tracked CI + trackedness guard |
| [OR-C02](../02-audit-findings/77-openspec-and-record-findings.md#or-c02---resolve-and-restore-reproducible-project-openspec-skill-delivery) | repaired: repository-tracked skill delivery | archived 01; no external installer admitted | reproducible skill delivery |
| [OR-C03](../02-audit-findings/77-openspec-and-record-findings.md#or-c03---converge-owner-drifted-capabilities-through-owner-local-changes) | owner-local migrate/rename/retire | umbrella | attached to changes 03-05; no spec-cleanup mega-change |
| [OR-C04](../02-audit-findings/77-openspec-and-record-findings.md#or-c04---correct-the-structural-registry-in-both-directions) | repaired: delivery inventory and scaffold row | archived 01; structure and trackedness guards pass | completed delivery/test-structure workstreams |
| [OR-C05](../02-audit-findings/77-openspec-and-record-findings.md#or-c05---restore-product-context-to-glossary-only-scope-without-rewriting-adr-history) | migrate/delete current glossary residue; keep ADRs | ready | glossary/ADR/spec roles / `converge-node-language-and-product-records` |
| [OR-C06](../02-audit-findings/77-openspec-and-record-findings.md#or-c06---keep-current-indexes-and-historical-evidence-delete-only-the-grounded-dpt-duplicate) | retired duplicate; retained current and historical routes | archived 01; provenance route contract passes | current docs/evidence owners |
| [OR-C07](../02-audit-findings/77-openspec-and-record-findings.md#or-c07---retain-generated-projections-and-their-freshness-guards) | retain projections/guards | non-regression | generators + source authorities |
| [OR-C08](../02-audit-findings/77-openspec-and-record-findings.md#or-c08---preserve-archive-and-completed-backlog-history-as-evidence-only) | historical keep | non-regression | archive/backlog lifecycle |

## Residual Compatibility Sweep

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [RC-C01](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c01---migrate-consumers-and-delete-the-state-only-refinement-wrapper) | migrate consumers then delete wrapper | after RS-C02 + export scope | `RefinementAdmission` / `converge-run-bundle-observation-authority` |
| [RC-C02](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c02---delete-the-legacy-short-state-planner-helper) | retired after canonical Bundle-profile transfer | archived 01; profile and negative projection tests pass | canonical profile reader |
| [RC-C03](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c03---resolve-the-joint-profile-and-proposal-input-compatibility-window) | product/data decision; then migrate/retain | blocked: profile/checkpoint/producer matrix | versioned profile/proposal inputs / `converge-run-input-and-composition-contracts` |
| [RC-C04](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c04---decide-supported-appconfig-endpoint-aliases-before-reader-subtraction) | product/support decision | blocked: supported AppConfig versions | approved endpoint field set / `converge-runtime-input-compatibility` |
| [RC-C05](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c05---retain-composition-and-workspace-alias-drift-guards) | retain guards | non-regression | recipe identity + storage readiness |
| [RC-C06](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c06---keep-legacy-diagnostic-location-compatibility-until-retained-results-close) | migrate/expire reader or bounded retain | blocked: retained Run results | exact diagnostic publication / `converge-retained-run-data-compatibility` |
| [RC-C07](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c07---keep-current-normalization-and-bounded-fallback-behavior) | guard-retained: normalization and bounded fallback | archived 01; projection and refinement negatives remain fail closed | existing behavior owners |

## Register Closure

The register closes only when every `ready` row is archived with evidence, every `blocked` row has an authorized
decision and data/consumer closure or an explicit retained-support disposition, and every non-regression row has been
rechecked against the final residual scan. Implementation order and blockers live in
[80 - Remediation Change Map](80-remediation-change-map.md); stepwise gates live in
[99 - Progressive Execution](99-progressive-execution.md).

## 01 Closure

`restore-delivery-and-subtract-dead-assets` archived at
`openspec/changes/archive/2026-08-14-restore-delivery-and-subtract-dead-assets/` and
was committed as `47a3bb5`. Its 16-ID budget is closed by the row-level dispositions
above. Deterministic verification, the bounded clean-clone preflight, and the focused
negative guards passed. Manual-live CI was not run; it remains `workflow_dispatch`
only, makes no live or release claim here, and creates no newly accepted residual risk.
