## 1. Contract And Test Seams

- [x] 1.1 Confirm the two public deterministic test seams with the user: the Bundle-local Run Event Journal recorder/reader contract and the existing typed Bundle lifecycle result. Record the agreed Bundle lifetime, admission boundary, sequence/retention, validation, and coverage decisions in the change artifacts.
- [ ] 1.2 Add a red domain-level contract test for correlated Bundle-local event facts, including generation, validation stage, bounded canonical validation-code collections, monotonic stable sequence identity, and redaction rejection. Verify with `cd deep_research_harness && .venv/bin/python -m pytest tests/unit/test_run_observation_store.py`.
- [ ] 1.3 Implement the versioned Bundle-local Run Event Journal contract and compatibility interpretation required by `REJ-001` through `REJ-005`, without adding lifecycle authority, an external retained fallback, or an unbounded detail field.
- [ ] 1.4 Add a red deterministic persistence test for concurrent producers, protected retention anchors, dropped sequence intervals, corrupted/legacy data, and journal health; then implement serialized retention and truthful `complete`/`incomplete`/`unavailable` reporting. Verify with `cd deep_research_harness && .venv/bin/python -m pytest tests/unit/test_run_observation_store.py tests/integration/test_observation_lifecycle_separation.py`.

## 2. Admitted Execution Journal

- [ ] 2.1 Add a red integration test proving a newly admitted Run retains graph events emitted before its first returned lifecycle projection, that a rejected pre-admission request creates no Journal, and that journal failure leaves the typed lifecycle outcome unchanged. Verify with `cd deep_research_harness && .venv/bin/python -m pytest tests/integration/test_demo_run_update_adapters.py tests/contract/test_run_experience_contract.py`.
- [ ] 2.2 Establish or reopen the Journal in the selected Bundle diagnostics subtree after Bundle admission and before initial, resume, or refinement graph producers execute; retain later lifecycle projections in that same Journal without using it as a Bundle lookup or control source, and remove admitted-Run external terminal fallback persistence.

## 3. Shared Producer Coverage

- [ ] 3.1 Add red graph and bridge tests for node start/end, known provider/model/tool outcomes, safe unknown boundary failures, and absent DeerFlow live subscribers, asserting Journal correlation while existing recovery and terminal authority stay unchanged. Verify with `cd deep_research_harness && .venv/bin/python -m pytest tests/graph/test_research_graph.py tests/graph/test_topic_planning_node.py`.
- [ ] 3.2 Implement Journal capture at the shared graph wrapper and node-agent/provider bridge seams, plus a best-effort DeerFlow `custom` live mirror of already-safe facts, preserving cancellation propagation and never recording raw failure detail.
- [ ] 3.3 Add red work-unit and Wave1 tests for exact initial and repair validation code retention, validation stages and code collections, retries, exhaustion, and distinct concurrent attempt correlations. Verify with `cd deep_research_harness && .venv/bin/python -m pytest tests/integration/test_wave1_work_units.py tests/graph/test_wave1_node.py`.
- [ ] 3.4 Implement the work-unit and narrowly owned validator mappings so each canonical validation outcome reaches the shared Journal without changing candidate admission, repair input, retry bounds, or gate routing.
- [ ] 3.5 Extend the workflow-outcome discovery inventory and requirement-evidence assets so every discovered production `run_agent` owner needs collected journal coverage for its declared non-success outcomes. Verify with `cd deep_research_harness && .venv/bin/python -m pytest tests/contract/test_workflow_failure_outcomes.py tests/assets/test_evidence.py`.

## 4. Read-Only Diagnostic Use

- [ ] 4.1 Add a red inspection test that renders safe Bundle-local Journal health, generation, phase, work/attempt identity, validation stage/codes, dropped intervals, and diagnostic reference without raw details or a journal-derived action. Verify with `cd deep_research_harness && .venv/bin/python -m pytest tests/unit/test_run_observation_store.py tests/integration/test_demo_sessions.py`.
- [ ] 4.2 Implement the bounded contained-inspection projection and operator rendering, including explicit incomplete legacy/capacity/persistence observations and unavailable post-loss inspection with no external fallback or control recovery.

## 5. Evidence And Closeout

- [ ] 5.1 Update only the affected test-evidence claims, requirement impacts, and inventories after the focused tests are collected; add known-violation coverage for the discovery rule.
- [ ] 5.2 Run the focused journal, graph, workflow-outcome, and inspection tests; fix only failures attributable to this change.
- [ ] 5.3 Run `cd deep_research_harness && UV_OFFLINE=1 make verify`, `openspec validate systemic-run-event-journal --strict`, and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all` and confirm `deerflow/`, `backend/`, and `frontend/` remain clean before archive.
