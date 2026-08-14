## 1. Deterministic Failure Proofs

- [x] 1.1 Register `CES-009` as the active delta's pending cognitive-evaluation-suite requirement, then run `python3 openspec/governance/check_project_reqs.py` to establish the governed implementation baseline.
- [x] 1.2 Add focused red tests showing that missing and unknown `evidence_layer` values fail direct Evaluation Bundle manifest and Review Record validation, while both current explicit layers remain valid. (`CES-003`, `CES-005`)
- [x] 1.3 Add focused red review-service and operations tests that plant missing and unknown manifest layers, assert `bundle_manifest_invalid`, no Review Record write, unchanged Bundle bytes, and no quality or live-provenance upgrade. (`CES-003`, `CES-005`)
- [x] 1.4 Add focused facade tests proving the supported runtime facade projects the domain contract identities and that the retired `.contracts` module cannot be imported. (`CES-009`)

## 2. Provenance Admission And Surface Cutover

- [x] 2.1 Remove the evidence-layer defaults from the domain-owned Evaluation Bundle manifest and Review Record models, retain the closed enum validation, and annotate the implementation with the affected requirement IDs. (`CES-003`, `CES-005`)
- [x] 2.2 Preserve `verify_bundle()` as the pre-write manifest admission boundary and the existing bounded `bundle_manifest_invalid` operations diagnostic; make the focused tests pass without adding a default, writer, backfill, retry, or provenance-upgrade route. (`CES-003`, `CES-005`)
- [x] 2.3 Point the supported evaluation facade and internal evaluation implementation modules directly at domain-owned contracts, then remove `runtime/evaluation/contracts.py` with no alias or fallback. (`CES-009`)
- [x] 2.4 Remove the zero-caller `compute_metrics()` shim and its export after confirming the typed metric functions and `ValidatedEvaluationOutcome` remain unchanged.

## 3. Documentation And Governed Inventory

- [x] 3.1 Update evaluation operator documentation so missing or unknown evidence-layer records are explicitly unsupported and fail closed before review; retain the current deterministic and selected-live descriptions. (`CES-003`, `CES-005`)
- [x] 3.2 Update the affected production and focused-test `@impl` annotations for `CES-003`, `CES-005`, and `CES-009`; confirm the existing `PRS-015` architecture-test annotation still proves the changed structural contract. Leave `evaluation-hardening` test-evidence assets unchanged.
- [x] 3.3 Remove the retired contract file from `project-structure.toml`, update structural test fixtures as needed, then use the output of `check_project_architecture.py --render-guide` to update the marked generated block in `deep_research_harness/AGENTS.md` before running the architecture checker. (`PRS-015`)

## 4. Apply Review And Verification

- [x] 4.1 Apply agent performs the control-placement plan review: compare the completed diff, tests, and provenance authority against the Control Placement and Workflow Outcome Review tables; correct any drift before claiming implementation complete. Done when planted missing/unknown records have a deterministic no-write proof and no second import authority remains. (2026-08-14: no control-placement or workflow-outcome drift found; see [verification.md](verification.md).)
- [ ] 4.2 Run the focused evaluation, requirement-evidence, and architecture suites; then run `python3 openspec/governance/check_project_reqs.py`, `python3 openspec/governance/check_project_specs.py`, `python3 openspec/governance/check_project_architecture.py`, `python3 openspec/governance/check_agent_charter.py`, `python3 openspec/governance/check_project_req_coverage.py`, `openspec validate converge-evaluation-boundary-compatibility --strict`, and `git diff HEAD --check`.
- [ ] 4.3 Run `cd deep_research_harness && UV_OFFLINE=1 make verify`; record any intentionally unrun credentialed/live, release, Postgres, external-consumer, or retained-data lane as evidence-limited rather than passed.
- [ ] 4.4 Archive-closeout reviewer checks completed tasks, final diff scope, main-spec sync, strict validation, whitespace, and the bounded gitlink evidence: `git status --porcelain=v1 --untracked-files=all`, `git ls-files --stage deerflow`, `git submodule status -- deerflow`, `git -C deerflow status --porcelain=v1 --untracked-files=all`, and `git diff --submodule=short`. Done when the gitlink remains unchanged and clean, every scope item has deterministic proof, and no external compatibility claim is made.
