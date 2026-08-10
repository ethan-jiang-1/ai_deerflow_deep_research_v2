## 0. Control-Placement Review

- [x] 0.1 Owner: current apply agent. Before the first target edit, or before a
  resumed apply edits another target, review this change's Focus Card, Control
  Placement Review, `openspec/policies/control-placement.md`, BUG-024 evidence,
  pending tasks, and the lowest responsible implementation/test seams. Add every
  actionable competing-control, hidden lifecycle input, or redaction finding as an
  ordinary unchecked task; otherwise record bounded no-finding evidence. Done
  condition: the record names the selected evidence and confirms that profile,
  budget, and validation facts remain projections rather than admission, recovery,
  checkpoint, route, or lifecycle authority.

### Plan Review Record

- **Owner:** current apply agent.
- **Reviewed:** this change's Focus Card and Control Placement Review;
  `openspec/policies/control-placement.md`; BUG-024; all pending tasks; the demo
  resolver/composition seam in `scripts/_demo_core.py`; the admitted-Bundle Journal
  seam in `runtime/bundle_graph.py`; and the middleware, bridge, Wave0, and
  topic-planning producer seams.
- **Bounded conclusion:** an explicit selector is a non-bypassable preflight fact;
  the trusted envelope transports only redacted observation evidence after that
  fact has been resolved; `BundleGraphExecutor._journal_envelope()` remains the
  only new Bundle-local writer boundary. Budget and parser facts remain advisory
  Journal projections, while existing node/controller/lifecycle owners retain
  recovery, routing, checkpoint, and terminal authority.
- **Disposition:** no actionable implementation finding before the first target
  edit. New evidence is constrained to existing admission, summary, model-tool,
  and validation event seams; any later competing-control or redaction finding
  will be added as an unchecked ordinary task.

## 1. Explicit Real-Demo Profile Admission

- [x] 1.1 Add red tests in `tests/unit/test_demo_core.py` for a missing, unknown, and deliberately non-unique `DEERFLOW_DEMO_MODEL` selector; prove that each preserves the existing safe prerequisite result and reaches neither graph composition nor Bundle/Journal creation. Verify with `cd deep_research_harness && UV_OFFLINE=1 uv run --locked --no-sync --extra operations python -m pytest tests/unit/test_demo_core.py -q`.
- [x] 1.2 Add red tests in `tests/unit/test_demo_core.py` for an explicit credential-backed selector: it resolves exactly one registered profile, passes that sole config to the all-real composition, and produces the registry-declared safe identity/revision without credentials, endpoint URL, or environment values. Verify with the same focused command.
- [x] 1.3 Implement the typed real-demo profile resolver and safe prerequisite integration in `scripts/_demo_core.py`; add the version-controlled safe revision to each registered profile and bind its one selected config into `DemoAppConfig`/all-real composition before `BundleGraphExecutor` construction, without changing fixture/full-fake composition or the existing launcher-exported selector behavior. Re-run `tests/unit/test_demo_core.py` until tasks 1.1-1.2 are green.
- [x] 1.4 Add an entry-level deterministic test that the real CLI/TUI preflight rejects an unselected profile before a Bundle exists and that a launcher-provided selector remains explicit; keep the existing typed lifecycle failure and legal next action unchanged. Verify with `cd deep_research_harness && UV_OFFLINE=1 uv run --locked --no-sync --extra operations --extra demo-real python -m pytest tests/contract/test_demo_commands.py tests/contract/test_run_experience_contract.py -q`.

## 2. Bundle-Local Profile And Journal Contracts

- [x] 2.1 Add red contract/store tests in `tests/unit/test_run_observation_store.py` for matching profile evidence only on admission/summary, strict redaction, rejection of misplaced or mismatched values, legacy readability without inferred provenance, non-demo absence, and Journal-write failure isolation. Verify with `cd deep_research_harness && UV_OFFLINE=1 uv run --locked --no-sync --extra operations python -m pytest tests/unit/test_run_observation_store.py -q`.
- [x] 2.2 Implement the additive, strictly validated execution-profile Journal representation and reader compatibility in `domain/run_observation.py` and `runtime/run_observation.py`; do not rewrite existing Bundle files or make an inspection result a lifecycle input. Re-run `tests/unit/test_run_observation_store.py` until task 2.1 is green.
- [x] 2.3 Thread only the typed redacted profile evidence through the runtime-owned envelope in `runtime/runtime_adapter.py` and establish it from `BundleGraphExecutor._journal_envelope()` after lifecycle admission; add `tests/unit/test_bundle_graph_journal.py` with a focused proof that a selected Bundle retains it and a rejected start retains nothing. Verify with `cd deep_research_harness && UV_OFFLINE=1 uv run --locked --no-sync --extra operations python -m pytest tests/unit/test_bundle_graph_journal.py tests/contract/test_run_experience_contract.py -q`.

## 3. Closed Budget-Stop Attribution

- [x] 3.1 Add red tests in `tests/unit/test_budget_middleware.py` and `tests/unit/test_node_agent_bridge.py` covering every current model/token/tool admission boundary, bridge wall time, an unknown safe fallback, and a non-budget failure. Assert the existing finish reason, failure category, timeout origin, recovery behavior, and raw-detail redaction remain unchanged. Verify with `cd deep_research_harness && UV_OFFLINE=1 uv run --locked --no-sync --extra operations python -m pytest tests/unit/test_budget_middleware.py tests/unit/test_node_agent_bridge.py -q`.
- [x] 3.2 Implement a closed typed budget-stop cause at `BudgetMiddleware`, map it at the bridge deadline/normalization boundary, and carry it only in a private per-invocation bridge recording projection to the existing Journal recorder. Do not put raw stop detail or the new attribution in `NodeProblem`, graph-facing node results, model-visible data, checkpoint state, or a lifecycle projection. Re-run the focused tests from task 3.1 until green.
- [x] 3.3 Extend the Journal store/serialization tests with valid and invalid budget-stop reason combinations, including the rule that unrelated failures cannot carry one. Verify with `cd deep_research_harness && UV_OFFLINE=1 uv run --locked --no-sync --extra operations python -m pytest tests/unit/test_run_observation_store.py tests/unit/test_node_agent_bridge.py -q`.

## 4. Canonical Parser And Materialization Evidence

- [x] 4.1 Add red Wave0 work-unit tests for valid initial parsing, invalid initial plus successful repair, invalid initial plus invalid repair, and a pre-parser invocation failure. Assert initial/repair event ordering, work/attempt correlation, closed codes, no raw draft/source/tool content, and unchanged candidate/controller behavior. Verify with `cd deep_research_harness && UV_OFFLINE=1 uv run --locked --no-sync --extra operations python -m pytest tests/integration/test_wave0_work_units.py tests/graph/test_wave0_worker.py -q`.
- [x] 4.2 Implement the local Wave0 validation-event helper and closed parser-code mapping around the existing parser/one-repair boundary. Keep event persistence best-effort and leave submission validation, ledger admission, repair count, controller, gate, route, and terminal owners unchanged. Re-run the focused Wave0 tests from task 4.1 until green.
- [x] 4.3 Add red topic-planning node tests for valid initial parse/materialization, initial invalid plus repair success, initial invalid plus repair invalid, dynamic coverage/detail redaction, and a provider invocation failure before candidate materialization. Verify with `cd deep_research_harness && UV_OFFLINE=1 uv run --locked --no-sync --extra operations python -m pytest tests/graph/test_topic_planning_node.py tests/graph/test_topic_planning_prompts.py -q`.
- [x] 4.4 Implement topic-planning validation-event publication and closed parser/materializer code mapping. Preserve the existing one-repair and provider-recovery table, planner-owned checkpoint materialization, exhausted route, and terminal behavior. Re-run the focused topic-planning tests from task 4.3 until green.
- [x] 4.5 Add an integration regression that inspects one Bundle Journal across the new Wave0/topic-planning paths and proves the exact event facts are observational only. Verify with `cd deep_research_harness && UV_OFFLINE=1 uv run --locked --no-sync --extra operations python -m pytest tests/integration/test_wave0_work_units.py tests/integration/test_topic_planning_lifecycle.py tests/integration/test_wave1_work_units.py -q`.

## 5. Operator Procedure And Evidence Registration

- [x] 5.1 Update `README.md`, `docs/local-operations.md`, and `run/README.md` with the bounded calibration procedure: explicit profile selection, fresh scripted real-demo Bundle, read-only inspection, and no model-quality/default-selection claim. Add a documentation/command contract test for the exact procedure and absence of an implicit `make demo-real-scripted` model fallback. Verify with `cd deep_research_harness && UV_OFFLINE=1 uv run --locked --no-sync --extra operations python -m pytest tests/contract/test_demo_commands.py -q`.
- [x] 5.2 Register `DPL-011`, `DPL-012`, `REJ-006`, `REJ-007`, `NOA-015`, `TOP-009`, and `WAN-010` in the smallest applicable test-source and requirement-evidence registries. Use exact collected selectors and lowest responsible seams; add no live claim, because credentialed calibration is supplemental only. Verify with `cd deep_research_harness && UV_OFFLINE=1 make test-assets test-req-coverage`.
- [x] 5.2a Register the seven new requirement IDs in `openspec/governance/req-registry.yaml` and synchronize their implemented active delta requirements into the five owning main specs. This is required because `test-req-coverage` accepts only registered main-spec owners, not a pending delta alone. Preserve all pre-existing main-spec requirements and verify with `python3 openspec/governance/check_project_reqs.py .`, `openspec validate --specs`, and the task 5.2 command.
- [x] 5.3 Run the combined deterministic change suite and correct any implementation/test-asset mismatch: `cd deep_research_harness && UV_OFFLINE=1 uv run --locked --no-sync --extra operations python -m pytest tests/unit/test_demo_core.py tests/unit/test_bundle_graph_journal.py tests/unit/test_run_observation_store.py tests/unit/test_budget_middleware.py tests/unit/test_node_agent_bridge.py tests/graph/test_topic_planning_node.py tests/graph/test_topic_planning_prompts.py tests/graph/test_wave0_worker.py tests/integration/test_wave0_work_units.py tests/integration/test_topic_planning_lifecycle.py tests/contract/test_demo_commands.py tests/contract/test_run_experience_contract.py -q`.

## 6. Completion And Archive Evidence

- [x] 6.1 Before archive, run `cd deep_research_harness && UV_OFFLINE=1 make verify`; record the exact result and any justified external blocker without running paid/real-model tests.
  - Verification (2026-08-10): passed. Governance, lint, format, test-asset, and requirement-coverage gates passed; fast `2457 passed, 3 deselected, 2 warnings`; integration/blocking-I/O `237 passed, 4 skipped, 32 deselected, 16 warnings`; workflow `35 passed, 2747 deselected, 42 warnings`. No paid or real-model test was run. The skips require the unavailable real Gateway app stack; remaining warnings are existing Pydantic serializer/deprecation warnings.
- [x] 6.2 Before archive, run `openspec validate calibrate-real-demo-model-contracts --strict` and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all` and confirm that `deerflow/`, `backend/`, and `frontend/` remain clean.
  - Verification (2026-08-10): strict OpenSpec validation and whitespace check passed. The porcelain status records this active change's implementation, specs, tests, and untracked change artifacts plus the retained BUG-024 research update. `git status --porcelain=v1 --untracked-files=all -- deerflow backend frontend` was empty; `git submodule status --recursive` reports `deerflow` at `66b9e7f21212490cf92fafac137542b9deb06615` with no dirty marker.
- [x] 6.3 Owner: current archive agent. Before requesting archive, review the
  Control Placement Review against the actual selected-change boundary, unresolved
  tasks, and deterministic verification evidence. Add every actionable finding as an
  ordinary unchecked task; otherwise record bounded no-finding evidence without
  treating it as semantic clearance or archive authority. Done condition: the
  closeout record names the exact change boundary and proves that the implemented
  profile, budget, and validation diagnostics cannot control Bundle admission,
  retry, route, checkpoint, terminal, or lifecycle behavior.
  - Closeout review (2026-08-10): reviewed the Focus Card, Control Placement Review,
    BUG-024 evidence, all completed tasks, the real-demo composition boundary,
    Bundle Journal handoff, bridge budget recording, and Wave0/topic-planning validation
    producers against the completed deterministic evidence. The explicit selector is
    the sole non-bypassable pre-admission guard; its post-admission redacted profile
    provenance is an advisory Journal fact. Budget-stop causes remain a private bridge
    recording projection, and validation facts are optional best-effort Journal writes
    after their existing parser/materializer boundaries. None can select a Bundle,
    alter retry, route, checkpoint, terminal, or lifecycle behavior. No actionable
    competing-control, hidden lifecycle-input, or redaction finding was found. This is
    bounded closeout evidence only, not semantic clearance or archive authority.
