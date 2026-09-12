# Tasks: Honest Delivery Degradation and Faithful Real-Run Diagnostics

## 1. Gate kernel: bounded exhaustion-degradation policy (BUG-035 core)

- [x] 1.1 `domain/gate.py`: add `degraded_pass_on_exhaustion: bool = False` to
  `GateDefinition` (no route-label changes; construction validation unchanged).
  Also added `GateResult.exhaustion_degraded` flag (consumed by the state update).
- [x] 1.2 `engine/gate_kernel.py`: exhaustion branch degrades to `PASS` +
  `degraded=True` (no `REPAIR_BUDGET_EXHAUSTED` failure, no terminal fields,
  `remaining_budget` stays 0) when: budget ≤ 0, no hard failure, policy
  declared, marker absent; otherwise today's `BLOCKED` escalation.
- [x] 1.3 `engine/gate_kernel.py`: `gate_result_to_state_update` appends the
  `<phase>:exhaustion_degraded` marker to `degraded_decisions` (full-tuple
  write); exported `exhaustion_degradation_marker()`.
- [x] 1.4 `engine/real_gates.py`: `build_wave2_real_gate_def` declares
  `degraded_pass_on_exhaustion=True`; wave0/wave1/final_delivery unchanged.
- [x] 1.5 `graph/nodes/rerun/planner.py`: `reset_gate_state_for_scope` clears
  `degraded_decisions` in both branches; `domain/state.py` grants GATE writer
  permission for `degraded_decisions` (matching `unresolved_gaps`).
- [x] 1.6 Tests: 6 new kernel cases (first-exhaustion degrade, marker write,
  re-exhaustion block, hard-failure precedence, undeclared gate unchanged,
  resolver-failure never degrades) + rerun-reset case —
  `tests/engine/test_gate_kernel.py` + `tests/unit/test_rerun_planner.py`:
  63 passed.

## 2. Honest gap disclosure in the report (BUG-035 delivery side)

- [x] 2.1 `runtime/work_unit_store.py`: `read_synthesis_gaps()` — bounded
  canonical read of `synthesis/findings.json` (2 MiB cap) returning validated
  `GapRecord` tuples.
- [x] 2.2 `graph/nodes/readiness/materializer.py`: appends one
  `ReportPlanUncertainty` per `unresolved_gaps` id joined against gap records
  (matched body → description; missing body → id-only honest entry; empty
  projection → no additions).
- [x] 2.3 `graph/nodes/readiness/node.py`: reads `unresolved_gaps` from state,
  fetches gap bodies once (failure tolerated → id-only disclosure), passes both
  into the materializer; critic/hard-rules/route untouched.
- [x] 2.4 Tests: 4 materializer/node cases in
  `tests/unit/test_readiness_real.py` (16 passed); composed disclosure-chain
  test (gate degrade → plan → final report text carries the gap description) +
  canonical-artifact round-trip in
  `tests/unit/test_honest_delivery_disclosure.py` (3 passed); real wave2 gate
  degradation cases in `tests/graph/test_gate_integration.py` (16 passed).

## 3. Faithful journal-availability projection (BUG-036)

- [x] 3.1 `runtime/run_experience.py`: `_failure_for_terminal` resolves
  `diagnostic_location`/`journal_record_created` via the observation-verified
  publication check for every blocked incident (renamed helper to
  `_incident_diagnostic_location`); provider incidents still require a
  reference; `RunFailure` journal invariant preserved.
- [x] 3.2 Tests: gate-blocked incident with confirmed reference →
  `bundle_journal`/created; unconfirmed reference → `unavailable`; no
  observation view → `unavailable`; provider-without-reference rejected at the
  domain contract — `tests/unit/test_retained_terminal_result_cutover.py`:
  8 passed.

## 4. Registered checkpoint serialization boundary (BUG-037)

- [x] 4.1 `runtime/checkpoint.py`: registered
  `("deerflow_deep_research.domain.wave1", "Wave1OpenQuestionRef")`; docstring
  now names all three persisted project types.
- [x] 4.2 `runtime/bundle_lifecycle.py`: `open_graph_checkpoint` assigns the
  app serde onto the opened `AsyncSqliteSaver` before yielding (mirrors
  graph_host).
- [x] 4.3 Tests: three-type round-trip, strict-mode subprocess case extended
  to `Wave1OpenQuestionRef`, and a wiring test that the bundle graph saver
  opens with the registered serde — `tests/unit/test_checkpoint_msgpack.py`:
  3 passed.
- [x] 4.4 `Makefile` `test-strict-checkpoint` lane gains
  `tests/unit/test_bundle_graph_journal.py` (full graph through the bundle
  graph store under `LANGGRAPH_STRICT_MSGPACK=true`); lane equivalent run:
  87 passed, zero unregistered-type warnings.

## 5. Documentation and closeout

- [x] 5.1 `_backlog/_local_demo/runbook-003-medium-real-auto.md`: acceptance
  section documents honest-gap degraded delivery (completed run + real report +
  disclosed gap uncertainties; only repeated exhaustion blocks).
- [x] 5.2 `_backlog/bugs/`: BUG-035/036/037 marked fixed with evidence pointers
  and archived via `git mv` to `_backlog/_done/_fixed_bugs/`;
  `_fixed_bugs/README.md`, `_backlog/bugs/README.md` (empty active list), and
  `_backlog/_done/README.md` updated. The two pre-existing red-gate defects left
  by the archived `low-scale-real-auto` commit were also filed and archived as
  BUG-038 (eval digest drift) and BUG-039 (stale workflow test after spec sync);
  ledger now 39 fixed, Next ID BUG-040. Lessons — both systemic and this
  apply's own planning mistakes — recorded in
  `_backlog/_done/_closed_plans/2026-08-18-honest-delivery-apply.md`.
- [x] 5.3 Full offline gate via the venv, all deterministic, nothing new behind
  `requires_llm`: lint (ruff check + format on all changed files) clean;
  `check_test_assets.py` pass; fast lane 2555 passed / 3 deselected (1
  pre-existing environmental failure — `test_production_wheel_excludes_fixture_package`
  shells out to `uv build`, which the session sandbox blocks on
  `~/.cache/uv`; proven identical on stashed baseline); integration +
  blocking_io 252 passed / 4 skipped; workflow lane 35 passed; strict-msgpack
  lane 87 passed. Two pre-existing `make verify` breaks left by the archived
  `low-scale-real-auto` commit were repaired to make the gate honest (both
  proven failing on the stashed baseline): (a) eval control digests for
  `domain/synthesis.py` and `tool.py` refreshed in
  `evals/control/cases/*.json` per the established bump convention; (b)
  `test_wave2_malformed_output_consumes_repair_and_leaves_no_partial_authority`
  updated to the spec'd bounded terminal (route `exhausted`, typed
  `output.structured_invalid` incident, no artifact) instead of expecting the
  pre-13249bb uncaught `ValueError`.

## 6. Operator confirmation (not a CI gate)

- [x] 6.1 Post-fix runbook-003 executed by the agent with real credentials
  (`soft-bundle run … --mode 003`, bundle `b_T0PuZxnG4jibqyHqAaVEP8kjB-uq-zDwnY_TXDaZiWc`,
  real DeepSeek + Tavily, 2026-08-18). Checkpoint-decoded gate timeline:
  `repair(budget 1) → repair(budget 0) → degraded PASS (marker written,
  trace continued through hitl2/readiness, gap disclosed in
  `review/report-plan.json` as "Unresolved research gap gap:g1") → second
  exhaustion after the one degradation → compliant `blocked/exhausted` —
  the gap genuinely failed to converge in both rounds, so the blocked
  terminal is the designed honest outcome, not a defect. BUG-036: terminal
  prints `诊断引用: diag_68670e0507bcfa723e4e401f` and `inspect` shows
  `Journal health: complete` — no more "journal unavailable" misreport.
  BUG-037: zero "unregistered type" warnings; post-run decoding of
  `graph.sqlite` writes through the app serde succeeds. Evidence recorded
  in the BUG-035/036/037 entries ("修复后真机验证" sections).
