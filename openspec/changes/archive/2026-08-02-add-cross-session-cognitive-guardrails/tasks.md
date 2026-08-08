## 1. Review And Red Contracts

- [x] 1.1 Owner: current apply agent. Before the first target edit, review this
  change's Focus Card, Control Placement Review, `selected-change-closeout-evidence`
  delta, `openspec/policies/control-placement.md`, pending tasks, and Change 2's
  `missing-boundary` probe. Record any actionable finding as an ordinary unchecked
  task; otherwise record the bounded no-finding evidence. Done condition: the record
  names the selected evidence and does not claim semantic or archive authority.

### Plan Review Record

- **Owner:** current apply agent.
- **Reviewed:** this change's Focus Card and Control Placement Review; the
  `selected-change-closeout-evidence` delta; `openspec/policies/control-placement.md`;
  all fifteen pending implementation tasks; and Change 2's selected-change boundary
  probe in `_backlog/plans/policy-gate-injection-layer/05-operation-guidance-probe-evidence.md`.
- **Bounded conclusion:** OpenSpec's selected `changeName` does not identify a code
  diff, and a shared worktree cannot be claimed as reviewed. The change therefore
  accepts only caller-declared, Git-verified committed ranges and leaves guidance,
  task writing, semantic judgment, and native archive outside guardrail authority.
- **Disposition:** no new actionable implementation finding. The red fixtures in
  tasks 1.2 through 1.4 prove the boundary, record-shape, and no-side-effect claims;
  any later finding will be added as an ordinary unchecked task.
- [x] 1.2 Add red, isolated local-Git fixture coverage for a complete valid
  attestation and the `unknown-change`, `missing-field`, `repository-mismatch`,
  `unknown-commit`, `non-ancestor`, `head-drift`, and `dirty-worktree` rejections.
  (`SCC-001`, `SCC-003`)
- [x] 1.3 Add red focused tests for boundary receipt fields and exact `base..head`
  diff summary, plus review-record dispositions, non-empty limitation and exact
  unchecked-task-label reference requirements, output-path containment, same-invocation
  re-verification before a write, and rejection of semantic-clearance statuses.
  (`SCC-001`, `SCC-002`)
- [x] 1.4 Add red no-side-effect tests proving verification and record operations do
  not modify `tasks.md`, invoke or wrap native archive, or inspect an undeclared
  full worktree. (`SCC-002`, `SCC-003`)

## 2. Bounded Guardrail Implementation

- [x] 2.1 Create `openspec/guardrails/README.md` and the standard-library command
  surface described in `design.md`; document its JSON v1 contract, explicit-call
  posture, output-location restriction, and non-authoritative boundary. (`SCC-001`,
  `SCC-002`)
- [x] 2.2 Implement `verify-boundary` to resolve an active selected change, parse an
  attestation, resolve and compare the declared repository identity, verify commit
  existence and ancestry, require `HEAD == head` and a clean worktree, and emit either
  a bounded `boundary-verified` receipt or a closed-code `missing-boundary` result.
  (`SCC-001`)
- [x] 2.3 Implement `record-review` to re-verify its supplied attestation immediately
  before a write, accept only `review-required` or `inconclusive`, validate unchecked
  ordinary-task references or an evidence limitation, and write a durable record only
  to a caller-requested path below the selected change. (`SCC-002`)
- [x] 2.4 Make all red fixture cases pass and retain a focused command that runs the
  guardrail tests without credentials, providers, model calls, or native archive.
  (`SCC-001`, `SCC-002`, `SCC-003`)

## 3. Charter And Governance Synchronization

- [x] 3.1 Update the concise Charter/config route so a selected `control-placement`
  change can discover the separate committed-range evidence protocol while preserving
  advisory operation guidance and native archive authority. (`DRC-010`)
- [x] 3.2 Confirm the active-delta `SCC` prefix and `SCC-001` through `SCC-003`
  registry entries, synchronize both delta specs into their main specs, and annotate
  the changed route, command, and focused tests with their owning requirements.
  (`SCC-001`, `SCC-002`, `SCC-003`, `DRC-010`)
- [x] 3.3 Register only the new guardrail documentation, command, and focused test
  paths in the existing project-structure and requirement-evidence metadata; update
  their deterministic check fixtures without adding a parallel registry or runtime
  controller. (`SCC-001`, `SCC-002`, `SCC-003`)
- [x] 3.4 Update `_backlog/plans/policy-gate-injection-layer.md` when implementation
  starts and again with exact verification, archive, and commit status; retain the
  five proposal-contract decisions as the authority boundary.

### Long-Term Tracker Record

- **Implementation start:** the tracker recorded the initial apply review, then the
  isolated Git fixture and guardrail implementation progression.
- **Verification:** focused guardrail and Charter/config contracts, governance,
  evidence, strict OpenSpec, and diff checks passed. `UV_OFFLINE=1 make verify`
  retained the three pre-existing LangGraph `Command` integration expectation failures
  recorded in task 4.2; they were not changed here.
- **Archive:** `openspec archive add-cross-session-cognitive-guardrails --yes` moved
  the change to `2026-08-02-add-cross-session-cognitive-guardrails` after its native
  `14/15` warning. The final task was deliberately the post-commit tracker update,
  not a behavioral or archive-authority finding.
- **Implementation/archive commit:** `e487a60`
  (`feat(openspec): add selected change closeout evidence`).

## 4. Verification And Archive Evidence

- [x] 4.1 Run the focused guardrail fixtures, Charter/config contracts, requirement,
  architecture, and evidence checks; resolve only failures inside this change's
  approved governance boundary. (`SCC-001`, `SCC-002`, `SCC-003`, `DRC-010`)
- [x] 4.2 Run `cd deerflow_research && UV_OFFLINE=1 make verify`, then
  `openspec validate add-cross-session-cognitive-guardrails --strict` and
  `git diff HEAD --check`; record exact results and
  `git status --porcelain=v1 --untracked-files=all`, keeping `backend/` and
  `frontend/` clean.

### Verification Record

- **Date:** 2026-08-02.
- **Focused contracts:** `deerflow_research/.venv/bin/python -m pytest
  deerflow_research/tests/contract/test_selected_change_closeout.py
  deerflow_research/tests/contract/test_agent_charter_governance.py -q` — exit 0,
  `102 passed`.
- **Governance and evidence:** `check_agent_charter.py`, `check_project_reqs.py`,
  `check_project_specs.py`, `check_project_architecture.py`,
  `check_project_req_coverage.py`, and `deerflow_research/scripts/check_test_assets.py`
  — all exit 0; the asset check collected `2499` deterministic tests.
- **Project verification:** `cd deerflow_research && UV_OFFLINE=1 make verify` —
  exit `2` only at the existing integration baseline: `test-fast` passed `2289`
  tests, while `test-integration` selected `189` tests and retained three failures
  that expect a mapping but receive a LangGraph `Command`:
  `test_mixed_real_prefixes.py::test_handlers_run_real_prefix_through_wave2_and_keep_later_nodes_fake`,
  `test_wave0_lifecycle.py::test_mixed_wave0_complete_lifecycle`, and
  `test_wave0_lifecycle.py::test_wave0_blocked_when_worker_fails_every_topic`.
  Governance, lock, Ruff, asset, requirement-coverage, and fast-test stages passed.
- **Closeout commands:** `openspec validate
  add-cross-session-cognitive-guardrails --strict` and `git diff HEAD --check` —
  both exit 0.
- **Pre-archive status:** only Change 3's governance, main-spec, tracker, guardrail,
  and focused-test paths were modified or untracked; `backend/` and `frontend/` were
  absent from `git status --porcelain=v1 --untracked-files=all`.
- [x] 4.3 Owner: current archive agent. Before requesting native archive, review the
  selected change's explicit committed boundary, unresolved tasks, guardrail evidence,
  and deterministic results. Record an actionable finding as an ordinary unchecked
  task or record the bounded evidence limitation; never describe a guardrail record
  as native archive authority. Done condition: the review names its exact boundary
  (or `missing-boundary`) and leaves no semantic-clearance claim.

### Archive-Closeout Review Record

- **Owner:** current archive agent.
- **Boundary:** `missing-boundary`. No caller-declared committed `base..head`
  attestation can verify while this implementation remains an uncommitted, dirty
  worktree; this review therefore makes no selected-change coverage or semantic
  clearance claim, and writes no guardrail evidence record.
- **Unresolved task:** 3.4 only. It is an administrative long-term-tracker update
  intentionally deferred until the implementation/archive commit has an exact hash;
  it is not unimplemented behavior, a runtime risk, or an archive blocker.
- **Deterministic evidence:** the 14 focused Git fixtures, Charter/config contract,
  governance, requirement, architecture, test-asset, and strict OpenSpec checks pass.
  The full offline gate's three integration failures are the pre-existing LangGraph
  `Command` expectation baseline recorded above and remain outside this change's
  approved governance boundary.
- **Disposition:** bounded no actionable finding. This record does not grant native
  archive authority; the native archive command remains authoritative.
