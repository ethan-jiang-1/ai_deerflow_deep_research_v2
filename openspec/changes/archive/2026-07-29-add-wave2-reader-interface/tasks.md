## 1. Wave2 Reader Interface

- [x] 1.1 Recheck every reader-facing assertion against the current Wave2 source,
  relevant main specs, and named lowest-responsibility tests; retain any uncovered
  repair-feedback fact only as an implemented limitation.
- [x] 1.2 Add the package-local Wave2 `workflow.md` with its non-runtime boundary,
  bounded cognitive job, symptom-to-owner/test map, and only the cross-module facts
  that change a maintenance decision.
- [x] 1.3 Run the fixed reader task against `workflow.md` and record that it reaches
  `build_real`, `build_synthesis_repair_prompt`, the narrow repair test, and the
  feedback-delivery limitation without first changing parser, gate, or graph wiring.
- [x] 1.4 Register the new NRI requirement IDs in the sole requirement registry so
  the active delta participates in governance validation.

## Reader Task Record

- 2026-07-29: Given only `workflow.md` and the repeated
  `synthesis_findings_required` symptom, the review reached
  `node.py::build_real`, `prompts.py::build_synthesis_repair_prompt`, and
  `test_real_synthesis_repairs_gaps_only_output_when_accepted_evidence_exists`.
  It identified missing validation-code delivery as the current limitation and
  rejected parser, gate, and graph wiring as first edits.

## 2. Evidence And Verification

- [x] 2.1 Run the existing Wave2 real-node, gate, topology, capability cohort,
  phase-prompt, runtime-capability, and node-agent bridge tests cited by the
  interface.

## Verification Record

- 2026-07-29: `UV_OFFLINE=1 uv run --extra operations --extra demo-tui pytest`
  over the seven cited focused test modules passed: 175 passed in 3.80s.
- 2026-07-29: `openspec validate add-wave2-reader-interface --strict`,
  `python3 openspec/governance/check_project_architecture.py`, and
  `git diff --check` all passed.
- 2026-07-29: `python3 openspec/governance/check_project_req_coverage.py .`
  passed after linking NRI-001/NRI-002 to the existing Wave2 real-node proof seam;
  the annotation changes traceability only and does not alter test behavior.
- [x] 2.2 Run `openspec validate add-wave2-reader-interface --strict`,
  `python3 openspec/governance/check_project_architecture.py`, and `git diff --check`.
- 2026-07-29: `UV_OFFLINE=1 make verify` passed governance, lock, lint, test assets,
  requirement coverage, and the 1,920-test fast lane. Its integration lane had four
  failures and four expected Gateway-stack skips in
  `tests/integration/test_adversarial_worker_path.py` / `test_gateway_identity.py`.
  The workflow lane, run separately after the integration lane stopped the Make
  target, had the two marked failures in the same adversarial-worker module and 15
  passes. All six failures reproduced unchanged in pre-change worktree `7c4ccc1`;
  they are baseline failures outside this documentation-only change.
- 2026-07-29: `git status --porcelain=v1 --untracked-files=all -- backend frontend`
  was empty. The committed Wave2 change contained no runtime Python, test, checker,
  project-structure, or `agent/AGENTS.md` modification.
- [x] 2.3 Run `cd agent && UV_OFFLINE=1 make verify`; record pre-existing failures or
  skips separately from this documentation-only change, then record a clean
  `git status --porcelain=v1 --untracked-files=all` scope check for `backend/` and
  `frontend/`.

## 3. Change Completion

- [x] 3.1 Review that the completed change added no workflow parser, Markdown schema,
  checker, generated inventory, project-structure registry entry, `agent/AGENTS.md`
  change, or runtime behavior change.
