## 1. Baseline And Board Contract

- [x] 1.1 Before implementation edits, collect and retain a temporary baseline for
  each canonical fast, integration, workflow, live, and release selector set using
  pytest collection only. Record that this change may add selectors but may not remove,
  rename, move, or relabel an existing selector and must not execute paid lanes.
- [x] 1.2 Add failing focused tests for a test-owned board with exactly the ordered
  eleven `LOGICAL_NODES` rows, the exact twenty prompt-catalog/cohort branch rows, one
  branch-review wrapper per branch, and exact coverage of all forty-one unique cases in
  the four calibration registries. Cover missing, duplicate, grouped, stale, and
  self-consistently empty/mis-scoped denominators. Run
  `cd agent && UV_OFFLINE=1 uv run --extra operations pytest tests/contract/test_cognitive_program_board.py -q`.
- [x] 1.3 Add failing board-row mutation tests for a Charter binary or generic product
  identity, false active-loop claim, missing responsibility/participation/commitment/
  mechanism/authority field, missing cognitive hypothesis, wrong branch owner,
  under-specified branch proof, forbidden active-branch `human-decision` proof, missing
  or cross-branch calibration/claim link, absent live-evaluation applicability, and
  absent known limitation.

## 2. Current Reader And Activation Projections

- [x] 2.1 Add failing reader/dossier contract cases proving readiness and final
  delivery report `current accepted` active zero-tool mechanisms while HITL2 remains
  the sole `conditional/unresolved` activation dossier and requires a fresh separately
  reviewed behavior change rather than an archived successor. Retain the existing test
  selectors. Run
  `cd agent && UV_OFFLINE=1 uv run --extra operations pytest tests/contract/test_node_workflow_reader_interface.py tests/contract/test_deferred_activation_dossiers.py -q`.
- [x] 2.2 Extend the reader checker with a pure immutable identity-field loader used by
  board validation, preserving the existing shape/non-authority checker and adding no
  production import or runtime behavior.
- [x] 2.3 Update readiness and final-delivery `workflow.md` projections to current
  critic/composer facts, reduce the unresolved activation dossier registry to HITL2,
  replace its exact `successor_change` field with the fresh-change admission boundary,
  and update invalid dossier fixtures without deleting a test. Rebind readiness's
  node-conformance success from `readiness-autonomous-continuation` to the already
  collected `readiness-all-clear` current critic-path claim; retain the displaced claim
  and selector, and keep `final-delivery-completed` unchanged.

## 3. Complete Node And Branch Evidence Board

- [x] 3.1 Add `agent/tests/assets/cognitive_program_board.py` with immutable node,
  node-proof-link, branch-review, branch-evaluation-link, and board records. Extend the
  shared proof classification with `human-decision`, permit it only for conditional
  node-board proof, reject it for active-branch proof, and retain
  `obsolete-duplicate` as a non-closing branch annotation.
- [x] 3.2 Populate one product-responsibility-first row for every logical node. Bind
  the eight active model owners to their exact branch IDs and collected workflow/
  conformance evidence, HITL2 to conditional-boundary plus autonomous guardrail
  evidence, and bootstrap/rerun only to deterministic guardrail/wiring evidence. Add
  one review wrapper per branch with exact calibration-case/central-live-claim pairs
  and a known limitation; add each calibration claim's existing case identity to its
  `scenario_case_id` metadata without treating selector collection as live success.
- [x] 3.3 Implement the pure board validator against injected topology, loaded reader
  identities, branch-ledger/cohort, workflow-coverage, node-conformance, four
  calibration registries, central claims, requirement impacts, and collected-selector
  inputs. Reuse `COGNITIVE_PROGRAM_EVIDENCE` as the twenty-row branch body rather than
  copying it. Run each registry's existing validator first, then validate the exact
  forty-one-case union and case/claim/branch joins without reading live reports.
- [x] 3.4 Update the cognitive-program requirement registry/annotations and
  smallest-sufficient impacts for `CPE-001` and new `CPE-004`; update `EVH-017` proof
  classification coverage while keeping branch judgment evidence separate from
  deterministic conformance. Re-run the board test plus
  `tests/graph/test_cognitive_program_evidence.py` and
  `tests/graph/test_node_agent_capability_cohort.py` without deleting or renaming their
  existing selectors.

## 4. Risk-Preserving Consolidation Governance

- [x] 4.1 Add failing requirement-evidence tests for an unknown/uncollected displaced
  or retained claim, self-replacement, missing requirement/risk pair, wrong requirement
  owner, any seam/evidence-class/authenticity difference without rationale, and a
  count/marker/directory/coverage-only basis. Run
  `cd agent && UV_OFFLINE=1 uv run --extra operations pytest tests/contract/test_requirement_evidence_policy.py tests/contract/test_asset_checker_contract.py -q`.
- [x] 4.2 Add immutable consolidation decision/replacement records and a pure validator
  beside `RequirementImpact`. Join displaced and retained claims through collected
  selectors plus exact requirement/risk impacts; require bounded rationale whenever
  seam, evidence class, or authenticity changes, without assigning a universal
  evidence-strength rank.
- [x] 4.3 Export an empty `CONSOLIDATION_DECISIONS` rollout, register `EVH-023` and its
  smallest-sufficient deterministic proof/impact metadata, and prove no board or
  decision object performs or authorizes deletion.

## 5. Integrated Evidence Gate

- [x] 5.1 Add a failing checker-level test showing the existing deterministic
  test-asset gate cannot pass with a missing board row, mis-scoped source denominator,
  missing/cross-branch calibration or central-claim mapping, invalid node proof, or
  incomplete consolidation replacement.
- [x] 5.2 Wire the existing branch-ledger validator, complete board validator, and
  empty-rollout consolidation validator into `agent/scripts/check_test_assets.py` using
  its one collected selector catalog across all focused lanes. Keep the checker offline
  and free of model, network, graph, artifact, live-report, or runtime operations; add
  an integration smoke fixture proving the source is the four real validated registries
  rather than a self-consistent substitute.
- [x] 5.3 Run
  `cd agent && UV_OFFLINE=1 uv run --extra operations pytest tests/contract/test_cognitive_program_board.py tests/contract/test_node_workflow_reader_interface.py tests/contract/test_deferred_activation_dossiers.py tests/contract/test_requirement_evidence_policy.py tests/contract/test_asset_checker_contract.py tests/graph/test_cognitive_program_evidence.py tests/graph/test_node_agent_capability_cohort.py tests/contract/test_workflow_node_inventory.py tests/contract/test_node_conformance_inventory.py -q`,
  then `cd agent && UV_OFFLINE=1 make test-assets`.

## 6. Verification And Closure Readiness

- [x] 6.1 Compare every post-change fast, integration, workflow, live, and release
  selector set with its temporary baseline and prove each is a superset; inspect
  `git diff --name-status HEAD -- agent/tests` and confirm no test file or selector was
  deleted, renamed, moved, or relabeled.
- [x] 6.2 Run `cd agent && UV_OFFLINE=1 make verify` and
  `cd agent && UV_OFFLINE=1 uv run --extra operations python scripts/check_node_workflows.py`.
  Confirm the four project governance checks included by `make verify` pass. Record any
  credentialed live evaluation as supplemental only and do not require or execute it
  for this zero-API governance change.
- [x] 6.3 Run `openspec validate govern-cognitive-program-evidence --strict` and
  `git diff HEAD --check`; record
  `git status --porcelain=v1 --untracked-files=all` and confirm `backend/` and
  `frontend/` remain clean before requesting separate sync/archive authorization.
