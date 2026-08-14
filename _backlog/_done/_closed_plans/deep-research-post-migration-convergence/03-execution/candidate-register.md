# Audited Candidate Register

> 导航: [执行层索引](README.md) | [默认执行入口](99-progressive-execution.md) | [审计结果](../02-audit-findings/)
> 角色: `70-78` 最终审计 Candidate 的唯一导航总账，不复制完整证据
> 应用/spec 取证基线: `5bb41c16a45ff3caae6e5b1e900610c91bf68336`
> 审计综合 revision: `811203726cfa6478ceebdabc378daabce1b6758b`
> 执行编排 revision: `91709e740fdafcb8275c2a182a61554342e2bd08`；8-change program budget
> 状态: Phase I已于2026-08-15关闭；54 个最终 Candidate全有最终disposition，00–07均已 archive 并同步 main spec，07 的 retained-data closeout 为`a8293b6`；0 active OpenSpec changes。最终审计结论见[04 - Final Closeout](../04-final-closeout.md)

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
| [NC-C01](../02-audit-findings/70-node-cognition-findings.md#nc-c01---close-node-capability-migration) | archived 03: deleted legacy binding/default; required ref is the only admission fact | constructor/renderer/bridge negatives and 20-branch join pass | `2026-08-14-converge-node-language-and-product-records` |
| [NC-C02](../02-audit-findings/70-node-cognition-findings.md#nc-c02---converge-node-cognition-language-vertically) | archived 03: vertical terminology convergence | current-surface contract and six synced specs pass | `2026-08-14-converge-node-language-and-product-records` |
| [NC-C03](../02-audit-findings/70-node-cognition-findings.md#nc-c03---restore-context-to-glossary-only-ownership) | archived 03: owner-ledger closure deleted glossary residue | retained definitions and `_Avoid_` contract pass | `2026-08-14-converge-node-language-and-product-records` |

## Run, Bundle, Session, Observation

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [RS-C01](../02-audit-findings/71-run-session-and-observation-findings.md#rs-c01---retire-lifecycle-binding-capability-and-its-positive-registry-claims) | archived 04: retired lifecycle-binding capability and positive registry claims | current DRH/REJ/PRS guards and retired-ID checks pass | `2026-08-14-converge-run-bundle-observation-authority` |
| [RS-C02](../02-audit-findings/71-run-session-and-observation-findings.md#rs-c02---consolidate-research-run-session-into-current-bundlejournal-owners) | archived 04: retired mixed RUS capability after owner/evidence migration | current Bundle/Journal owner coverage and no-resurrection suites pass | `2026-08-14-converge-run-bundle-observation-authority` |
| [RS-C03](../02-audit-findings/71-run-session-and-observation-findings.md#rs-c03---rename-bundle-capabilities-without-changing-semantics) | archived 04: RDO/RSV current capability paths use Run Bundle names | registry/spec source and focused discovery/artifact guards pass | `2026-08-14-converge-run-bundle-observation-authority` |
| [RS-C04](../02-audit-findings/71-run-session-and-observation-findings.md#rs-c04---keep-local-session-workbench-and-move-its-registry-to-the-actual-owner) | archived 04: retained local workbench projects canonical admission state | workbench, lifecycle, pending-response, replay/conflict, and Bundle-loss tests pass | `2026-08-14-converge-run-bundle-observation-authority` |
| [RS-C05](../02-audit-findings/71-run-session-and-observation-findings.md#rs-c05---retain-anti-resurrection-tests-under-current-evidence-owners) | retained guard: evidence owners migrated in archived 04 and rechecked in 07 | DRH/REJ/PRS/RWB evidence remains falsifiable; retained records cannot resurrect a Run | current owners; 04 plus 07 archive `a8293b6` |

## Fixture And Implementation Mode

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [FM-C01](../02-audit-findings/72-fixture-mode-findings.md#fm-c01---resolve-and-retire-the-no-graph-full-fake-lifecycle-path) | archived 05: zero-credential execution is fixed fixture-graph proof; no no-graph full-fake route remains | executor-required start and demo command negatives prove no fallback/completed claim | `2026-08-15-converge-run-input-and-composition-contracts` (`4d91571`) |
| [FM-C02](../02-audit-findings/72-fixture-mode-findings.md#fm-c02---retire-persisted-full_fake-mode-only-after-support-closure) | archived 05: `full_fake` and missing/unknown modes are rejected; uninventoried retained/external data is explicitly unsupported | State decode/no-write negatives prove no default, backfill, or provenance upgrade | `2026-08-15-converge-run-input-and-composition-contracts` (`4d91571`) |
| [FM-C03](../02-audit-findings/72-fixture-mode-findings.md#fm-c03---keep-fixture-source-and-explicit-mixed-composition) | retained guard: explicit fixture/mixed composition and fixture source isolation rechecked in 05 | recipe/topology and demo composition guards remain falsifiable | current owners; 05 archive (`4d91571`) |
| [FM-C04](../02-audit-findings/72-fixture-mode-findings.md#fm-c04---preserve-missing-mode-compatibility-until-retained-states-are-migrated) | archived 05: missing-mode default reader retired; unsupported retained/external states reject before projection | State negative/reload tests prove no write or `all_real` upgrade | `2026-08-15-converge-run-input-and-composition-contracts` (`4d91571`) |

## Entry And Configuration

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [EC-C01](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c01---keep-distinct-current-entry-surfaces) | guard-retained: distinct entries | archived 01; entry guard remains falsifiable | product/operator/evaluation roles remain distinct |
| [EC-C02](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c02---move-dormant-local-first-direction-out-of-current-language) | archived 03: retired dormant glossary term; retained ADR history and current entry routes | glossary owner ledger and entry distinctions pass | `2026-08-14-converge-node-language-and-product-records` |
| [EC-C03](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c03---retain-old-entry-rejection-guards) | guard-retained: old-entry rejection | archived 01; entry guard remains falsifiable | deployment/structure admission |
| [EC-C04](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c04---delete-test-only-demo-compatibility-helpers) | retired after canonical profile/preflight transfer | archived 01; canonical pre-Adapter failure and redaction tests pass | canonical demo profile/preflight APIs |
| [EC-C05](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c05---decide-legacy-checkpointer-support-explicitly) | archived 06: non-null legacy `checkpointer` rejects before provider factory/classification; `database` is sole input | GraphHost/diagnostics parity returns redacted `legacy_checkpointer_unsupported`; no DSN/type leak | `2026-08-15-converge-runtime-input-compatibility` (`69a2dcd`) |
| [EC-C06](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c06---delete-the-researchgraphrecipecreate-constructor-after-export-scope-closure) | archived 05: `ResearchGraphRecipe.create()` removed with no supported facade/alias | tracked consumers use `all_real()` or explicit composition; later support requires a new change | `2026-08-15-converge-run-input-and-composition-contracts` (`4d91571`) |
| [EC-C07](../02-audit-findings/73-entry-and-configuration-findings.md#ec-c07---decide-the-disable_clarification-trusted-context-compatibility-window) | archived 06: `disable_clarification` clean-cutover rejection; canonical `non_interactive` is the sole trusted marker | start/resume/refine negatives return `interactive_required` before Bundle, sandbox, graph, or policy mutation | `2026-08-15-converge-runtime-input-compatibility` (`69a2dcd`) |

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
| [PC-C01](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c01---delete-redundant-profile-compatibility-apis-while-preserving-the-canonical-v1-reader-policy) | archived 05: only the source-controlled current v2 profile content is admitted; old/absent schema is rejected | current writer round-trips and invalid persisted input proves no write | `2026-08-15-converge-run-input-and-composition-contracts` (`4d91571`) |
| [PC-C02](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c02---delete-parse_profile_response-after-test-migration) | archived 05: wrapper deleted; consumers project the canonical parse result | focused domain/evaluation-consumer tests pass with no external support promise | `2026-08-15-converge-run-input-and-composition-contracts` (`4d91571`) |
| [PC-C03](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c03---migrate-graph-checkpoints-before-deleting-repair_counts) | archived 07: `repair_counts` retired; only registered offline migration can produce current checkpoint | current reader rejects old/unregistered records before graph work; reload/replay and no-write negatives pass | `2026-08-15-converge-retained-run-data-compatibility` (`a8293b6`) |
| [PC-C04](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c04---retire-repair_exhausted-only-after-bundle-data-support-closure) | archived 07: `REPAIR_EXHAUSTED` retired without a replacement terminal mapping | current Bundle reader rejects old/unregistered records before control; registered offline migration preserves terminal identity | `2026-08-15-converge-retained-run-data-compatibility` (`a8293b6`) |
| [PC-C05](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c05---keep-current-refinement-facts-and-their-old-state-optional-reader) | retained guard: current refinement facts and optional-reader recovery remain unchanged | lifecycle/refinement guards rechecked in 05 | Bundle refinement recovery; 05 archive (`4d91571`) |
| [PC-C06](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c06---preserve-old-run-observation-readers-until-retained-records-close) | archived 07: runtime Journal reader is v3-only; Summary v2 remains current | registered v2 offline migration, old-reader rejection before append/projection, and restart/replay proof pass | `2026-08-15-converge-retained-run-data-compatibility` (`a8293b6`) |
| [PC-C07](../02-audit-findings/75-persisted-compatibility-findings.md#pc-c07---decide-legacy-checkpointer-precedence-before-any-deletion) | archived 06: database-only local classification; legacy section is explicitly unsupported | provider matrix and no-factory/diagnostic redaction controls pass; recovery is whole-reader hotfix/revert only | `2026-08-15-converge-runtime-input-compatibility` (`69a2dcd`) |

## Evaluation Boundary

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [EV-C01](../02-audit-findings/76-evaluation-boundary-findings.md#ev-c01---keep-the-evaluation-workspacebundlereviewrun-distinctions) | rechecked 03: keep distinctions | glossary contract preserves Workspace, Bundle, Review/Record, Run, and product Run Bundle terms | evaluation domain owners |
| [EV-C02](../02-audit-findings/76-evaluation-boundary-findings.md#ev-c02---retain-missing-layer-compatibility-until-evaluation-bundle-data-closes) | archived: missing/unknown layers reject before Review or quality claim; default reader retired | explicit-layer records remain current; planted records prove no write, default, backfill, or provenance upgrade | `runtime.evaluation` cutover / archive `9b68e4d` |
| [EV-C03](../02-audit-findings/76-evaluation-boundary-findings.md#ev-c03---converge-evaluation-contract-imports-onto-one-supported-route) | archived: facade-only support; re-export module deleted | domain remains fact authority; facade identity and retired-module import failure are covered | domain authority + facade / archive `9b68e4d` |
| [EV-C04](../02-audit-findings/76-evaluation-boundary-findings.md#ev-c04---delete-the-unused-compute_metrics-shim) | archived: zero-caller shim and export deleted | typed metrics and `ValidatedEvaluationOutcome` remain unchanged | typed metrics / archive `9b68e4d` |
| [EV-C05](../02-audit-findings/76-evaluation-boundary-findings.md#ev-c05---retain-live-report-classification-and-fail-closed-archive-admission) | retained guard: rechecked in archived 07 without changing live classification | no credentialed/live claim or reader was introduced by the retained-data cutover | live evidence intake / 07 archive `a8293b6` |
| [EV-C06](../02-audit-findings/76-evaluation-boundary-findings.md#ev-c06---remove-evaluations-dependency-on-the-profile-parser-wrapper) | archived 05: evaluation test consumer uses the canonical parse-result projection; evaluation runtime/review semantics unchanged | focused live-evaluation consumer proof and workflow controls pass | `2026-08-15-converge-run-input-and-composition-contracts` (`4d91571`) |

## OpenSpec And Records

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [OR-C01](../02-audit-findings/77-openspec-and-record-findings.md#or-c01---restore-tracked-ci-workflow-delivery-before-cleanup-implementation) | repaired: tracked CI delivery | archived 01; Git-index guard and clean-clone preflight pass | tracked CI + trackedness guard |
| [OR-C02](../02-audit-findings/77-openspec-and-record-findings.md#or-c02---resolve-and-restore-reproducible-project-openspec-skill-delivery) | repaired: repository-tracked skill delivery | archived 01; no external installer admitted | reproducible skill delivery |
| [OR-C03](../02-audit-findings/77-openspec-and-record-findings.md#or-c03---converge-owner-drifted-capabilities-through-owner-local-changes) | 03 and 04 archived: node and Run Bundle owner-local convergence closed | current-language, current Bundle owner, requirement coverage, and strict OpenSpec checks pass | 05 may only close its independently gated fixture-composition scope; no spec-cleanup mega-change |
| [OR-C04](../02-audit-findings/77-openspec-and-record-findings.md#or-c04---correct-the-structural-registry-in-both-directions) | repaired: delivery inventory and scaffold row | archived 01; structure and trackedness guards pass | completed delivery/test-structure workstreams |
| [OR-C05](../02-audit-findings/77-openspec-and-record-findings.md#or-c05---restore-product-context-to-glossary-only-scope-without-rewriting-adr-history) | archived 03: migrated/deleted glossary residue; ADRs retained | seven-row ledger, glossary contract, and no-ADR-diff scan pass | `2026-08-14-converge-node-language-and-product-records` |
| [OR-C06](../02-audit-findings/77-openspec-and-record-findings.md#or-c06---keep-current-indexes-and-historical-evidence-delete-only-the-grounded-dpt-duplicate) | retired duplicate; retained current and historical routes | archived 01; provenance route contract passes | current docs/evidence owners |
| [OR-C07](../02-audit-findings/77-openspec-and-record-findings.md#or-c07---retain-generated-projections-and-their-freshness-guards) | rechecked 03: retain projections/guards | missing, stale, and extra generated projection output still fails | generators + source authorities |
| [OR-C08](../02-audit-findings/77-openspec-and-record-findings.md#or-c08---preserve-archive-and-completed-backlog-history-as-evidence-only) | rechecked 03: historical keep | archive/completed-backlog records remain evidence-only and unchanged | archive/backlog lifecycle |

## Residual Compatibility Sweep

| Candidate | Grounded disposition | Admission | Target / change |
| --- | --- | --- | --- |
| [RC-C01](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c01---migrate-consumers-and-delete-the-state-only-refinement-wrapper) | archived 04: workbench and integration consumers migrated; state-only wrapper deleted | removed-surface, lifecycle admission, workbench, replay/recovery, and no-resurrection tests pass | `RefinementAdmission` / `2026-08-14-converge-run-bundle-observation-authority` |
| [RC-C02](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c02---delete-the-legacy-short-state-planner-helper) | retired after canonical Bundle-profile transfer | archived 01; profile and negative projection tests pass | canonical profile reader |
| [RC-C03](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c03---resolve-the-joint-profile-and-proposal-input-compatibility-window) | archived 05: approved current profile/proposal/checkpoint matrix is the only reader/writer scope; legacy/external shapes reject | HITL1 no-write, raw semantic input, and reload negatives pass | `2026-08-15-converge-run-input-and-composition-contracts` (`4d91571`) |
| [RC-C04](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c04---decide-supported-appconfig-endpoint-aliases-before-reader-subtraction) | archived 06: only exact selected `base_url` can create a safe endpoint observation; aliases are retired | alias/malformed/userinfo/conflict controls yield no observation and cannot affect model, provider, retry, route, or lifecycle | `2026-08-15-converge-runtime-input-compatibility` (`69a2dcd`) |
| [RC-C05](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c05---retain-composition-and-workspace-alias-drift-guards) | retained guard: composition and workspace drift checks remain current | recipe identity/storage readiness guards rechecked in 05 | current owners; 05 archive (`4d91571`) |
| [RC-C06](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c06---keep-legacy-diagnostic-location-compatibility-until-retained-results-close) | archived 07: current terminal results require explicit diagnostic location | missing location rejects before participant projection; current non-provider result reports factual `unavailable` without a diagnostic reference | `2026-08-15-converge-retained-run-data-compatibility` (`a8293b6`) |
| [RC-C07](../02-audit-findings/78-residual-compatibility-sweep-findings.md#rc-c07---keep-current-normalization-and-bounded-fallback-behavior) | guard-retained: normalization and bounded fallback | archived 01; projection and refinement negatives remain fail closed | existing behavior owners |

## Register Closure

Closed 2026-08-15. All 54 rows have final evidence: 40 are terminally archived, retired, migrated, renamed,
repaired, or rejected by their owning change; 14 are intentional current guards or historical records. There are no
current `ready`, `blocked`, or unknown rows. Audit-era `ready` and `blocked` references above describe the admission
history only. The residual review, retained-guard authority, verification limits, and archive decision are recorded
in [04 - Final Closeout](../04-final-closeout.md).

## 01 Closure

`restore-delivery-and-subtract-dead-assets` archived at
`openspec/changes/archive/2026-08-14-restore-delivery-and-subtract-dead-assets/` and
was committed as `47a3bb5`. Its 16-ID budget is closed by the row-level dispositions
above. Deterministic verification, the bounded clean-clone preflight, and the focused
negative guards passed. Manual-live CI was not run; it remains `workflow_dispatch`
only, makes no live or release claim here, and creates no newly accepted residual risk.
