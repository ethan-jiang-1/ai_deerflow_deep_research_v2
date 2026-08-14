## 1. Admission Review And Red Evidence

- [x] 1.1 Plan-review (current apply agent owner): before changing the admission grammar, re-read the proposal's Control Placement Review, `control-placement` policy, design, and current checker/tests; record every actionable authority, compatibility, recovery, or scope finding as an unchecked task. Done when no unrecorded finding remains and the review still limits the checker to grammar closure.
- [x] 1.2 Add reusable active-program proposal fixtures and planted-invalid cases for mixed forms, missing Program/Workstream fields, invalid or duplicate stable IDs, duplicate owners, unregistered/missing workstreams, duplicate Candidate/obligation IDs, each direction of budget-union mismatch, and a policy review borrowed from the program or sibling workstream; run the focused charter test to establish the red baseline before parser changes.

## 2. Bounded Program Admission

- [x] 2.1 Refactor `check_agent_charter.py` into reusable ordinary/program section, field, list, seam-classification, and selected-policy validation helpers while retaining the existing ordinary `Change Focus` behavior and top-level conditional review records.
- [x] 2.2 Implement the exclusive Program Focus grammar, registered workstream-order closure, unique owners and IDs, exact Candidate/obligation union, and stable `program.*` failures; keep semantic remediation-map scope and diff review outside the checker.
- [x] 2.3 Implement workstream-scoped selected-policy and review-table validation so a program workstream cannot borrow a program-wide review record or another workstream's policy routing.
- [x] 2.4 Make the new positive program fixture and every planted-invalid fixture pass or fail at the intended deterministic boundary, while preserving all ordinary Focus Card and existing policy-review tests.

## 3. Authoring Route And Requirement Alignment

- [x] 3.1 Update `openspec/config.yaml`, `openspec/policies/local-context.md`, `openspec/policies/change-admission.md`, and `deep_research_harness/AGENTS.md` with concise ordinary-versus-program routing, program non-authority, frozen-budget/recovery, and apply/archive semantic-review boundaries; preserve the information-map budgets and do not add runtime behavior.
- [x] 3.2 Confirm the implemented behavior, charter delta, policy routing, and generated structure locator remain aligned without hand-editing generated output or changing DeerFlow.
- [x] 3.3 Add charter-checker anchor coverage for the program route in config, local-context, change-admission, and the application Focus Gate, with planted missing-anchor fixtures that fail without claiming semantic scope review.

## 4. Verification And Closeout

- [x] 4.1 Run the focused charter contract test, `python3 openspec/governance/check_agent_charter.py .`, project requirement/spec/architecture/coverage governance checks, and `cd deep_research_harness && UV_OFFLINE=1 make verify`; repair all failures within this change's declared scope.
- [x] 4.2 Run `openspec validate admit-bounded-program-change-workstreams --strict`, `openspec doctor --json`, `git diff HEAD --check`, and record `git status --porcelain=v1 --untracked-files=all`, gitlink stage/submodule/nested-status evidence, and `git diff --submodule=short` before archive.
- [x] 4.3 Archive-closeout-review (current archive agent owner): compare the actual diff, tasks, valid/invalid fixture evidence, and ordinary compatibility result to the Program Focus contract in the convergence plan. Add every actionable scope-drift or guard-sensitivity correction as an unchecked task. Done when program grammar has no runtime/shared-writer authority, no partial-archive path, and the review leaves no unresolved corrective task.
- [x] 4.4 Closeout correction: align stable-ID validation and its planted-invalid fixture to the approved `[a-z][a-z0-9-]*` grammar rather than applying an unrecorded stricter kebab-case rule. Done when the literal grammar is accepted and a non-matching stable ID still fails deterministically.
