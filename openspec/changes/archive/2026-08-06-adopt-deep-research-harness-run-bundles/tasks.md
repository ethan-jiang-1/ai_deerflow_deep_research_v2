## 1. Apply Admission And Current-Head Inventory

- [x] 1.1 **Apply agent, control-placement plan review:** Before any target edit, re-read the proposal's Control Placement Review, Workflow Outcome Review, selected `control-placement` policy, design, ADR-0028, and the historical session/checkpoint counterexample. Add each actionable collision or missing deterministic proof as an unchecked ordinary task. Done when no competing lifecycle authority is unowned.
- [x] 1.2 Record the current-HEAD impact inventory for every `research_id`, `bundle_directory`, external Deep Research checkpoint, session/binding/index, and `deerflow_research/` occurrence. Classify each hit as lifecycle authority, bound-content consumer, projection, structural consumer, historical archive, or unaffected. Verify with `rg -n 'research_id|bundle_directory|deerflow_research/' deerflow_research openspec` and `git status --porcelain=v1 --untracked-files=all` before the structural rename.
- [x] 1.3 Re-read the affected accepted specs and nearest source/test seams for every delta capability, including `node-prompt-catalog`. Reconcile each inventory class with a requirement, task, and deterministic proof; add an unchecked task before coding for any behavior-changing capability not already covered. Done when no target-code hit relies on a deleted/ambiguous contract.
- [x] 1.4 Allocate and register `DRH-*` plus all new/extended requirement IDs before source annotations or evidence claims use them. Update only changed requirement/evidence ownership mappings and add an invalid-fixture detector test for every revised registry/checker rule. Verify before implementation with `cd deerflow_research && UV_OFFLINE=1 make test-req-coverage` and `cd deerflow_research && UV_OFFLINE=1 make test-assets`.
- [x] 1.5 Create a checked-in apply evidence matrix mapping each changed requirement to its direct production seam, red test, green test, and command. Include the `resume` versus `refine` distinction, Bundle loss, and the root move. Done when every delta requirement has one named proof class and no presentation-only proof claims lifecycle authority.
- [x] 1.6 Before implementation, perform an accepted-spec contradiction audit. For every active requirement that names `deerflow_research/`, `research_id`, `bundle_directory`, a session/binding/index control path, or an external Deep Research checkpoint, record the owning delta modification or an intentional unaffected rationale. The audit explicitly includes `DPL-001/004/005/007`, `EVH-005/010`, `NOA-007`, `PRS-001/004/005/006/011/014/015`, `REC-004/005/006`, `RED-002`, `FCO-001`, `RER-001/002/003/006/007/009`, `RUS-001/002/003/004/006`, `RWB-001/002/003/005/006/007`, `RUI-001/002/003/004/006/007/008/009`, `REG-004/005/006/007/009/010/011/012/013/014/016`, `HIN-001/002/004/005`, and `WOU-001/003/004/005/006/009`. Done when an applier cannot encounter a current accepted requirement that contradicts Bundle-local authority or the canonical Harness root.
- [x] 1.7 Reconcile `deerflow_research/CONTEXT.md` and ADR-0028's available-completed-Bundle wording with the approved available-ended-Bundle refinement rule, including the boundary that an unavailable or lost Bundle cannot be reactivated. Preserve their historical/root-migration accuracy when the canonical root moves.

## 2. Red Deterministic Evidence Before Behavior Changes

- [x] 2.1 Add failing tests for fresh opaque `bundle_id` allocation, no conversation-derived Run identity, staged atomic publication, and valid initial Bundle-local State/content. Prove the tests fail before the core implementation with `cd deerflow_research && uv run --extra operations python -m pytest tests/unit/test_bundle.py tests/unit/test_bootstrap_bundle.py tests/unit/test_request_bundle.py tests/unit/test_state_contracts.py`.
- [x] 2.2 Add failing lifecycle tests for valid Handle continuation, absent-Handle scoped discovery, malformed/foreign/ambiguous candidates, one-active start admission, and fresh starts after ended Bundles. Verify red with `cd deerflow_research && uv run --extra operations python -m pytest tests/integration/test_research_lifecycle_tool.py tests/integration/test_public_entry_replay.py tests/unit/test_session_operation_resolver.py`.
- [x] 2.3 Add failing action-separation tests: `resume` consumes only the current correlated pending response; `refine` requires bounded text, preserves a pending response, and cannot silently choose among ended Bundles. A stale/ended Current Bundle Handle without an explicit `bundle_id` must not reactivate a later round. Verify red with `cd deerflow_research && uv run --extra operations python -m pytest tests/integration/test_research_lifecycle_tool.py tests/integration/test_hitl1_lifecycle.py tests/unit/test_state_reducers.py`.
- [x] 2.4 Add failing State/graph tests for non-terminal-awaiting-input is active, atomic single-writer State, durable refinement admission, safe-point consumption, ended-Bundle reactivation, and rejection when a different Bundle is active. Verify red with `cd deerflow_research && uv run --extra operations python -m pytest tests/unit/test_state_persistence.py tests/unit/test_state_reducers.py tests/integration/test_research_lifecycle_tool.py`.
- [x] 2.5 Add failing loss tests that delete a Bundle before control, during State/content write, and after completion while legacy checkpoint/session/binding observations remain. Assert `unavailable`, no replacement State/directory, no provider reopen, and legal fresh independent start. Verify red with `cd deerflow_research && uv run --extra operations python -m pytest tests/integration/test_research_lifecycle_tool.py tests/integration/test_session_lifecycle_binding.py tests/integration/test_session_operations_lifecycle.py`.
- [x] 2.6 Add failing contained-store/node tests proving Bootstrap, request, work-unit, HITL1, topic planning, Wave1, and Wave2 receive only a runtime-bound Bundle reference and reject legacy identity/path/checkpoint overrides. Verify red with `cd deerflow_research && uv run --extra operations python -m pytest tests/unit/test_bootstrap_bundle.py tests/unit/test_request_bundle.py tests/domain/test_work_unit_bundle.py tests/graph/test_hitl1_node.py tests/graph/test_topic_planning_node.py tests/integration/test_wave1_work_units.py`.
- [x] 2.7 Add failing tool/adapter tests for shared `bundle_id` results, truthful legal-next-action projection, `refine` action validation, and no adapter-local recovery. Verify red with `cd deerflow_research && uv run --extra operations python -m pytest tests/integration/test_public_entry_replay.py tests/contract/test_public_skill.py tests/contract/test_session_workbench_contract.py tests/integration/test_session_workbench.py`.
- [x] 2.8 Add failing structural/evidence tests for the canonical `deep_research_harness/` root, no tracked legacy-root alias, moved Docker/profile/prompt-review paths, generated locator, and Cognitive Evaluation separation. Verify red with `cd deerflow_research && uv run --extra operations python -m pytest tests/contract/test_architecture_governance.py tests/contract/test_docker_compose.py tests/contract/test_local_profiles.py tests/graph/test_prompt_dump.py`.

## 3. Bundle Authority And Lifecycle Core

- [x] 3.1 Implement the typed opaque Bundle identity, private trusted-scope containment bucket, runtime-bound Bundle reference, Bundle-local State schema, and shared typed lifecycle result. Remove public `research_id` and physical locator fields from control contracts. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/unit/test_bundle.py tests/unit/test_state_contracts.py tests/unit/test_state_persistence.py`.
- [x] 3.2 Implement the runtime-owned lifecycle module for scope validation, staged fresh publication, Handle validation, bounded absent-Handle discovery, and non-durable scope coordination. It must not persist an active pointer, registry, binding, or index. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/integration/test_research_lifecycle_tool.py tests/integration/test_public_entry_replay.py tests/unit/test_session_operation_resolver.py`.
- [x] 3.3 Replace Deep Research durable graph/checkpoint persistence with a Bundle-contained adapter. Keep blocking filesystem I/O off the event loop and retain no external-checkpoint fallback. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/unit/test_state_persistence.py tests/blocking_io/test_bootstrap_bundle_runtime.py tests/integration/test_research_lifecycle_tool.py`.
- [x] 3.4 Implement `refine` as a distinct action with bounded text and optional `bundle_id`; retain `resume` exclusively for a correlated `AcceptedHumanResponse`. Persist admitted refinement before its next durable safe point, preserve a pending response, and re-open an available ended Bundle only when no different Bundle is active. Without an explicit target, resolve only an active Bundle; an ended Handle must not reactivate a later round. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/integration/test_research_lifecycle_tool.py tests/integration/test_hitl1_lifecycle.py tests/unit/test_state_reducers.py`.
- [x] 3.5 Make each lifecycle action revalidate Bundle availability before authoritative State/content access and return the bounded unavailable result on loss. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/integration/test_research_lifecycle_tool.py tests/integration/test_session_lifecycle_binding.py tests/unit/test_state_persistence.py`.
- [x] 3.6 Update graph transitions, State reducers, pending-interaction handling, and result projection to use Bundle-local active/ended truth and legal-next-action facts. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/unit/test_state_reducers.py tests/graph/test_hitl1_node.py tests/integration/test_hitl1_lifecycle.py`.

## 4. Contained Content And Node Consumers

- [x] 4.1 Refactor Bundle, bootstrap, request, work-unit, and storage interfaces so the only durable root input is the runtime-bound Bundle reference. Preserve containment, locks, atomic publication, and per-Run isolation; delete legacy identity/path overloads. Green: `cd deep_research_harness && uv run --extra operations python -m pytest tests/unit/test_bundle.py tests/unit/test_bootstrap_bundle.py tests/unit/test_request_bundle.py tests/domain/test_work_unit_bundle.py tests/unit/test_work_unit_store.py`.
- [x] 4.2 Bind Bootstrap to lifecycle publication and Bundle-local validation; it must not select a checkpoint root or publish a second marker/root. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/unit/test_bootstrap_bundle.py tests/blocking_io/test_bootstrap_bundle_runtime.py`.
- [x] 4.3 Move HITL1 request ids, pending correlation, profile progress, and profile artifacts to Bundle-local State/content while preserving the existing typed response and visible-control integrity. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/graph/test_hitl1_node.py tests/integration/test_hitl1_lifecycle.py tests/unit/test_request_bundle.py`.
- [x] 4.4 Bind the node-agent bridge to ephemeral selected-Bundle context only. Retain current tool/capability/model boundaries and prevent agent code from selecting a Bundle, root, checkpoint, or State writer. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/unit/test_node_agent_bridge.py tests/domain/test_node_agent_capability.py tests/graph/test_node_agent_capability_cohort.py`.
- [x] 4.5 Migrate topic planning, Wave1, Wave2, evidence materialization, and work-unit replay to selected Bundle interfaces; preserve ledger/evidence invariants and fail on Bundle loss before publication. Green: `cd deep_research_harness && uv run --extra operations python -m pytest tests/graph/test_topic_planning_node.py tests/integration/test_topic_planning_lifecycle.py tests/integration/test_wave1_work_units.py tests/graph/test_wave2_synthesis_real.py tests/integration/test_work_unit_submit_boundary.py`.

## 5. Retire Competing Session And Checkpoint Authorities

- [x] 5.1 Rebuild retained session manifests, lifecycle bindings, and indexes as bounded observation-only records, or remove them where no observation is needed. They must not authorize discovery, control, resume, cancel, refinement, State recovery, or Bundle recreation. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/unit/test_run_session_store.py tests/unit/test_session_lifecycle_binding.py tests/integration/test_session_lifecycle_binding.py`.
- [x] 5.2 Replace session/broker discovery with trusted-scope Bundle directory plus Bundle-local State discovery. Foreign, malformed, stale, deleted, and ambiguous candidates must fail before provider/sandbox/graph/content work. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/unit/test_session_operation_resolver.py tests/contract/test_session_operations_contract.py tests/integration/test_session_operations_lifecycle.py`.
- [x] 5.3 Rebind artifact inspection and the local workbench to shared typed Bundle results. Historical observations cannot become lifecycle actions and unavailable Bundles reveal no forbidden details. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/contract/test_session_workbench_contract.py tests/contract/test_session_workbench_runtime.py tests/integration/test_session_workbench.py`.
- [x] 5.4 Remove Deep Research use of external checkpoint namespaces and provider reopen as lifecycle recovery while keeping generic infrastructure-probe behavior unchanged. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/integration/test_research_lifecycle_tool.py tests/integration/test_public_entry_replay.py tests/unit/test_state_persistence.py`.

## 6. Public Controls And Shared Projections

- [x] 6.1 Update `deep_research` schema, `LifecycleAction`, trusted runtime dispatch, and reflected tool docs to expose `start|resume|status|cancel|refine`. Require `refine` text, reject legacy identities, and project transient Handles only through trusted context. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/integration/test_research_lifecycle_tool.py tests/integration/test_public_entry_replay.py`.
- [x] 6.2 Update run experience, CLI, demo TUI, demo pipeline, fake CLI, and workbench to project one typed lifecycle result. Remove adapter-local identity derivation and lifecycle inference. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/contract/test_session_workbench_contract.py tests/integration/test_session_workbench.py tests/contract/test_public_skill.py`.
- [x] 6.3 Update the public skill, dedicated Agent SOUL, README/operations text, and transcripts to distinguish Harness, Run Bundle, `resume`, `refine`, ended, and unavailable states with `bundle_id`. Keep documents observational and preserve public tool/distribution/import names. Green: `cd deerflow_research && uv run --extra operations python -m pytest tests/contract/test_public_skill.py tests/contract/test_architecture_governance.py`.

## 7. Canonical Harness Root And Domain Separation

- [x] 7.1 Update `project-structure.toml` first, render the generated module-guide locator, and update every active OpenSpec delta/main-spec path reference governed by the contradiction audit, including `node-prompt-catalog`, release/evidence paths, demo/CLI/TUI documentation, and Cognitive Evaluation's separate root. Do this before the tracked directory rename. Green: `python3 openspec/governance/check_project_architecture.py` and `cd deerflow_research && uv run --extra operations python -m pytest tests/contract/test_architecture_governance.py tests/graph/test_prompt_dump.py`.
- [x] 7.2 Perform the one tracked repository rename from `deerflow_research/` to `deep_research_harness/`; preserve `src/deerflow_deep_research`, `src_fake/deerflow_deep_research_fixtures`, package metadata, and public tool names. Do not leave a symlink, alias, or second root. Green after the move: `cd deep_research_harness && uv run --extra operations python -m pytest tests/contract/test_architecture_governance.py`.
- [x] 7.3 Update all active root consumers: repository/module AGENTS/CLAUDE guides, Makefiles, Docker Compose/mount/PYTHONPATH configuration, profiles, scripts, build metadata, fixture roots, contract fixtures, configuration materialization, path protections, active docs, and the ignored prompt-review workspace. Do not rewrite historical archives unless an active command/contract needs a corrected link. Green: `cd deep_research_harness && uv run --extra operations python -m pytest tests/contract/test_docker_compose.py tests/contract/test_local_profiles.py tests/contract/test_architecture_governance.py tests/graph/test_prompt_dump.py`.
- [x] 7.4 Update OpenSpec authoring routes, test commands, and generated locators to use `deep_research_harness/` while preserving the small information-map boundary and the `backend/`/`frontend/` exclusion. Green: `cd deep_research_harness && UV_OFFLINE=1 make governance`.
- [x] 7.5 Audit Cognitive Evaluation paths, registries, and run-store discovery after the move. Keep Evaluation Workspaces/Bundles outside Deep Research discovery/control and add the cross-domain negative evidence case. Green: `cd deep_research_harness && uv run --extra operations python -m pytest tests/unit/test_bundle.py tests/integration/test_research_lifecycle_tool.py`.

## 8. Evidence, Synchronization, And Closeout

### Execution Record (2026-08-06)

- Overall progress is **48/49 tasks complete**. Tasks 1--7 and every deterministic
  closeout gate have passed; only the archive-closeout review remains.
- `UV_OFFLINE=1 make test-assets` currently passes: **364 central claims, 2460
  deterministic tests**. `make test-req-coverage` remains pending until the stale test
  contracts below are fully retired.
- The full `UV_OFFLINE=1 make test-fast` lane was run after the root and authority
  migration. It selected 2262 tests and exposed **113 stale-contract failures**. The
  remaining fixtures primarily use old `r_...` identities, old
  `workspace/deep-research/<id>/...` paths, or the deleted
  `WorkUnitStore(bundle_id=...)` constructor. They are being migrated to
  `RunBundleRef`, `run_bundle_root()` / `bundle_host_relative_root()`, and explicit
  Bundle publication where real content storage is exercised.
- Completed during this closeout pass: migrated the zero-tool conformance seam;
  renamed the obsolete `ResearchCheckpoint` contract to `ResearchGraphState` and
  updated its direct test users; fixed and covered initial empty-`final/` root
  publication so staged final content is atomically published.
- Batch 1 complete: migrated `tests/domain/test_work_units.py` and
  `tests/graph/test_work_unit_component.py` to a real `RunBundleRef`-derived
  identity/root, updated their canonical hash fixtures, and verified **44 passed**.
  The subsequent complete fast lane reduced the stale-contract failure count from
  **113 to 84**.
- Batch 2 complete: migrated the work-unit kernel, targeted-evidence, Wave0 worker,
  and Wave0 result seams. Their focused gate passed **67 tests**. A complete persisted
  fast lane then reduced the remaining failure count from **84 to 56**
  (`2206 passed`, `2 deselected`).
- Batch 3 complete: migrated the runtime storage verifier, work-unit projection, and
  capability resolver to explicit runtime-bound Bundles. Their focused gate passed
  **32 tests**, including explicit Bundle publication before real storage probes.
- Batch 4 complete: migrated final delivery, the fixture graph, and the checkpoint
  serializer to Bundle-local State/content paths. Their focused gate passed
  **19 tests**, including the retained initial `state.json` assertion for published
  Bundles. The subsequent complete fast lane reduced the remaining failure count from
  **56 to 24** (`2238 passed`, `2 deselected`).
- Batch 5 complete: aligned public opaque-`bundle_id` projections, unavailable action
  preconditions, retained observation assertions, and deterministic diagnostic hashes.
  The focused gate passed **110 tests**. The live canary runner now binds both
  `SelectedBundleContext` and matching node-agent attribution before creating Wave1,
  Wave2, or targeted-evidence nodes. The subsequent complete fast lane reduced the
  remaining failure count from **24 to 10** (`2252 passed`, `2 deselected`).
- Closeout checkpoint: the multiprocess contained-store migration now passes
  **3 tests**. Rechecking the remaining fast-lane seams narrowed the outstanding work
  to **5 deterministic failures**, all stale closeout evidence rather than an open
  lifecycle-design question:
  - `test_model_timeout_cancellation_propagates_through_real_runtime_bridge` reaches
    the bridge but exhausts its old 2,000-token test budget on the current Wave2 prompt
    before the blocking fake model is invoked; raise only that test budget so it tests
    cancellation as intended.
  - Two Cognitive Evaluation node tests still construct deleted `r_...` identities,
    a fake request store, or `WorkUnitStore(bundle_id=...)`; migrate them to a
    published `RunBundleRef`, selected-Bundle context, and contained store.
  - The EVH-024 impact contract still expects retired attestation/release selectors;
    the active registry correctly names the public release report plus the two
    Bundle-authorization/loss selectors.
  - `docs/regression-descent.md` still names a non-collected HITL selector; replace it
    with the current Bundle-local pending-HITL restart selector.
  Tasks 8.1, 8.1a, and 8.1b remain unchecked until their declared asset and
  requirement-coverage gates pass.
- Follow-up batch: the Wave2 cancellation seam and the regression-descent selector
  now pass. The remaining two focused failures are both test-fixture corrections:
  Cognitive Evaluation must use its existing deterministic storage-verifier seam when
  constructing the real Bundle-bound request store, and the EVH-024 contract must read
  expected lanes from its local expectation map rather than a nonexistent field on the
  requirement-impact value. Re-run the four focused seams after those corrections,
  then run the complete fast lane before changing any task checkbox.
- Focused closeout batch complete: **42 passed** across the Wave2 cancellation,
  Cognitive Evaluation, EVH-024 asset-contract, and regression-descent seams. The
  Cognitive Evaluation cases now publish and consume a real selected Run Bundle; the
  release impact contract now tracks the three active Bundle-authoritative selectors.
  The next gate is the complete `test-fast` lane.
- Complete fast lane passed after the closeout migration: **2262 passed, 2 deselected**
  in `146.643s` pytest time. Its duration profile identified six selectors above the
  existing 5-second policy; the evidence and a scoped follow-up recommendation are
  recorded in `_backlog/_done/_suspended_plans/2026-08-06-fast-lane-duration-profile.md` without
  widening this authority/root migration change.
- Evidence synchronization gate passed: `make test-assets` reports **364 central
  claims / 2456 deterministic tests**, and `make test-req-coverage` passed. Task 8.1
  is complete; the legacy-control scan and release-lane evidence remain separate
  closeout gates.
- Legacy-control scan passed for collected test seams. No test imports the deleted
  Deep Research session/binding/operations control contracts; retained `research_id`
  and `bundle_directory` mentions are negative-rejection assertions or bounded
  observation checks. `GraphHost` remains only the explicitly separate generic
  infrastructure-probe contract and has no registered Deep Research lifecycle action.
  With the passing asset gate, task 8.1a is complete.
- Final deterministic closeout passed: `make verify` completed fast (**2266 passed,
  2 deselected**), integration (**174 passed, 4 environment skips**), and workflow
  (**16 passed**) lanes. Strict OpenSpec validation, architecture governance, and
  `git diff HEAD --check` also passed. The recorded porcelain status contains only
  Harness/OpenSpec changes; `backend/` and `frontend/` are clean.
- Selected credentialed release evidence remains incomplete: two explicitly selected
  runs stopped at `first_resume:blocked` before report and citation assertions; the
  later run took **510.70s**. The terminal blocked-incident projection is now covered
  deterministically, but no third credentialed attempt was started during closeout.
- The provider-dependent successful release acceptance is now explicitly deferred to
  `_backlog/plans/evh-024-release-acceptance-diagnosis.md`. It is not represented as
  a passing run and no longer blocks this structural/lifecycle change.
- Archive-closeout control-placement review (2026-08-06): re-read the proposal's
  Control Placement and Workflow Outcome reviews, the selected control-placement,
  authority-and-projections, and control-and-recovery policies, the impact and
  accepted-contract audits, and the deterministic evidence matrix. The actual action
  boundary remains `tool.py -> BundleControl -> BundleLifecycle`; Bundle-local State
  is the sole lifecycle authority. `GraphHost` remains confined to the independent
  `infra_probe`, retained observations/workbench projections cannot control or
  recover a Bundle, and the EVH-024 runner reauthorizes only its public `bundle_id`
  before reading contained artifacts. No competing authority, recovery fallback, or
  misleading projection finding remains. The provider-dependent successful release
  selector remains an honest, separately owned issue in
  `_backlog/plans/evh-024-release-acceptance-diagnosis.md`.

- [x] 8.1 Update delta-linked deterministic evidence claims, scenario/fault assets, requirement registry mappings, and source-ownership annotations for every changed requirement. Add detector-smoke cases for scans that could otherwise pass empty. Green: `cd deep_research_harness && UV_OFFLINE=1 make test-assets && UV_OFFLINE=1 make test-req-coverage`.
- [x] 8.1a Retire or replace every collected test module that imports a deleted Deep Research session, checkpoint, or `research_id` control contract; retain each still-required behavior through a Bundle-authoritative deterministic seam. Green: `cd deep_research_harness && UV_OFFLINE=1 make test-assets`.
- [x] 8.1b Replace the EVH-024 release runner's `research_id`, external GraphHost/checkpoint, and workspace-derived result path with one Bundle-bound public execution adapter. Preserve its fixed Chinese request, model-led HITL1 proposal, natural confirmation, canonical source-set admission, remaining lifecycle, Chinese report, and citation assertions. Deterministically prove the runner observes Bundle-local State/contained artifacts and fails on Bundle loss without fallback. The separately authorized credentialed successful execution is deferred to `_backlog/plans/evh-024-release-acceptance-diagnosis.md`; do not skip, fake, or weaken that future manual selector. Green: `cd deep_research_harness && UV_OFFLINE=1 make test-assets` and `UV_OFFLINE=1 uv run --extra operations python -m pytest tests/unit/test_release_control_plane.py`.
- [x] 8.1c Ensure every terminal `BLOCKED` gate projects a bounded Bundle-local terminal incident: retain a specific controller-owned worker diagnosis when available, otherwise persist only `research.blocked` plus the known phase. Prove the direct gate -> Bundle State -> public lifecycle-result chain without adding a release, session, checkpoint, or workspace fallback. Green: `cd deep_research_harness && UV_OFFLINE=1 uv run --extra operations python -m pytest tests/engine/test_gate_kernel.py tests/unit/test_state_persistence.py tests/unit/test_release_control_plane.py`.
- [x] 8.1d Migrate every remaining collected integration/blocking test fixture from retired `r_` identities, `WorkUnitStore(bundle_id=...)`, and `GraphHost(research_recipe=...)` setup to an explicitly published runtime-bound Run Bundle and the direct lifecycle executor. Preserve each test's original adversarial, durability, demo, or non-blocking-I/O assertion. Green: `cd deep_research_harness && UV_OFFLINE=1 make test-integration`.
- [x] 8.2 Re-run the impact and accepted-spec contradiction inventories after the root move. Prove active production/control/configuration and current OpenSpec contract paths contain no retired `research_id` lifecycle identity, `bundle_directory` authority, external Deep Research checkpoint recovery, session/binding/index authority, or canonical old-root reference; record only intentional historical/archive exceptions. Green: `rg -n 'research_id|bundle_directory|deerflow_research/' deep_research_harness openspec` plus the focused contract tests named in tasks 5.1, 5.2, and 7.3.
- [x] 8.2a Replace the current live-evaluation report projection's stale `research_id_present` field with `bundle_id_present`. Migrate every report fixture and schema rejection test; preserve its bounded identity-presence-only diagnostic and do not introduce a lifecycle selector or retained identity authority. Green: `cd deep_research_harness && UV_OFFLINE=1 uv run --extra operations python -m pytest tests/unit/test_live_evaluation.py`.
- [x] 8.3 Run the complete deterministic gate and structural/OpenSpec validation: `cd deep_research_harness && UV_OFFLINE=1 make verify`; `openspec validate adopt-deep-research-harness-run-bundles --strict`; `python3 openspec/governance/check_project_architecture.py`; and `git diff HEAD --check`. Record `git status --porcelain=v1 --untracked-files=all` and verify `backend/` and `frontend/` remain clean.
- [x] 8.3a Register the valid project-local `.venv/` ignore entry in the exact canonical structure policy so the canonical Harness `.gitignore`, profile contract, and architecture checker have one shared list. Green: `python3 openspec/governance/check_project_architecture.py` and `cd deep_research_harness && UV_OFFLINE=1 uv run --extra operations python -m pytest tests/contract/test_local_profiles.py tests/contract/test_architecture_governance.py`.
- [x] 8.3b Resolve the complete deterministic verification lane's Ruff findings inside the Harness without weakening lint or widening into upstream DeerFlow. Preserve behavior while applying only mechanical import/unused-name corrections and readable line wrapping. Green: `cd deep_research_harness && UV_OFFLINE=1 uv run --extra operations ruff check . && UV_OFFLINE=1 make verify`.
- [x] 8.4 **Archive-closeout agent, control-placement review:** Before archive, re-read the selected Control Placement Review/policy, actual change boundary, unresolved tasks, impact matrix, and deterministic evidence. Add every competing-authority, recovery, or projection finding as an unchecked ordinary task. Done when Bundle-local State remains sole lifecycle authority, no unchecked actionable finding remains, and bounded closeout evidence is recorded before `openspec-archive-change`.
