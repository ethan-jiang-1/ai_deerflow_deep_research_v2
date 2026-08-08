## 1. Outcome Contract And Evidence Foundation

- [x] 1.1 Allocate and register the new workflow-outcome requirement IDs; add the domain-owned normalized invocation-outcome contract with direct invalid-fixture tests for known failure preservation, unknown fallback, and cancellation propagation.
- [x] 1.2 Write failing deterministic tests for the six currently discovered `run_agent` owners that assert their declared non-success outcomes at the node or worker seam before changing production adapters.
- [x] 1.3 Extend the syntax-discovered workflow inventory with declared outcome classes and projection selectors; add missing-owner, missing-class, stale-selector, and empty-detector negative tests.
- [x] 1.4 Implement the workflow-outcome seam and migrate shared result/exception normalization without changing graph routes or creating a retry controller.

## 2. Direct Phase Outcomes

- [x] 2.1 Write the BUG-010 regression tests for topic-planning provider timeout: node result, bounded recovery record, terminal incident, lifecycle projection, retained session diagnostics, and standalone CLI rendering.
- [x] 2.2 Split HITL1 and topic-planning execution policies; set topic planning's independent 60-second wall-time bound and test that the bridge still returns a safe classified timeout.
- [x] 2.3 Implement topic planning's phase outcome table: one bounded eligible provider recovery, separate one-shot structured-output repair, safe terminal incident on exhaustion, and no topic-state write after failure.
- [x] 2.4 Write and implement Wave2 synthesis failure handling so known direct invocation failures reach its phase/gate disposition and any terminal block retains a typed incident.
- [x] 2.5 Run the focused direct-phase graph and lifecycle tests, including the real-node scripted workflow selectors, and remove the old success-only/generic-exhaustion expectations.

## 3. Worker Phase Outcomes

- [x] 3.1 Write failing Wave0 worker tests for provider, tool, structured-output, and unknown invocation outcomes through the existing controller record and aggregate seam.
- [x] 3.2 Adapt Wave0 to normalize its worker results while preserving its existing work-unit retry, gate, ledger, and terminal ownership.
- [x] 3.3 Write failing Wave1 and targeted-evidence worker/repair tests that prove known invocation causes are not converted to generic `ValueError` failures.
- [x] 3.4 Adapt Wave1 and targeted evidence to emit the existing closed worker failure outcomes with bounded safe provider observations, preserving their controller-owned retry and routing behavior.
- [x] 3.5 Run focused worker/controller workflow tests and confirm no failed attempt can publish a candidate, accepted evidence artifact, or unauthorized control update.

## 4. Shared UX, Diagnostics, And Governance

- [x] 4.1 Add shared run-experience and run-session tests proving direct incidents and controller-derived worker diagnoses retain category, phase, recovery disposition, diagnostic reference, durability, and exactly one legal next action.
- [x] 4.2 Update the CLI and TUI adapters plus focused rendering tests so known workflow incidents are not reduced to generic blocked text and inspection is never presented as recovery.
- [x] 4.3 Add the `workflow-outcome-review` Agent Charter policy, update the charter route/index and `openspec/config.yaml`, and extend the governance checker with tests for triggered-policy and outcome-review record shape.
- [x] 4.4 Update requirement registry entries, production `@impl` ownership, test evidence claims, and relevant user/developer documentation so the new contract and workflow coverage remain traceable.

## 5. Verification And Rollout Evidence

- [x] 5.1 Run focused domain, graph, runtime, run-session, CLI/TUI, and workflow-conformance tests; record the exact commands and results in the change evidence.
- [x] 5.2 Run `openspec validate harden-deep-research-workflow-outcomes --strict`, `cd agent && UV_OFFLINE=1 make verify`, and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all` and confirm `backend/` and `frontend/` remain untouched.
- [x] 5.3 Execute one bounded real demo only as supplemental evidence, retain its safe bundle/diagnostic reference, and verify the observed terminal or success projection agrees with the typed workflow outcome contract.
