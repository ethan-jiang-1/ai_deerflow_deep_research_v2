# Accelerate Deep Research Change Delivery

## Status

Completed and archived on 2026-07-22. OpenSpec
`accelerate-deep-research-change-delivery` now uses one marker catalog, an in-process
architecture contract seam, a representative ledger chain, focused timed targets,
and CI duration policy. Reference benchmark on 2026-07-23 completed 1652 fast-lane
tests in 30.175 seconds (collection 2.212s, setup 1.135s, call 25.668s). This remains
an engineering-throughput improvement, not a reason to weaken deterministic
verification.

## Observed Problem

Changes that cross lifecycle state, graph nodes, retained sessions, CLI/TUI, and
workbench observation take too long to locate, validate, and safely advance. The
deterministic focused tests themselves are fast (the current observation slice is
approximately seconds), but the surrounding work is slowed by broad impact discovery,
large multi-file contract reads, and repeated validation of overlapping suites.

## Measured Test Suite Performance (2026-07-22)

All three deterministic lanes measured with `pytest --durations=30` on a single run
(no warmup, commit f705b72 + checkpoint.py syntax fix).

### Suite Totals

| Suite | Selected | Pass / Fail | Wall Time |
|---|---|---|---|
| `test-fast` | 1636 | 1633 pass / 3 fail | **65.6s** |
| `test-integration` | 133 | 118 pass / 11 fail | **67.6s** |
| `test-workflow` | 15 | 13 pass / 2 fail | **6.6s** |

> The 11 integration failures are a cascading import-chain breakage from a
> `checkpoint.py` `__all__` syntax error (`IndentationError` on line 209) that
> blocks every module importing `runtime/checkpoint.py`. A different agent is
> working on that file; these failures are not a performance concern.

### Top Offenders — 5 Tests Consume ~37s (57% of fast suite)

| Test | Time | Root Cause |
|---|---|---|
| `test_submission_ledger.py::test_exact_record_count_limit_round_trips` | **12.5s** | Loops 4096× constructing hash-chained `SubmissionRecord`, then encode+parse all 4096 |
| `test_test_lane_selection.py::test_deterministic_focused_selections_are_disjoint_exact_partition` | **10.7s** | Calls `_collect()` **5 times**, each triggering a fresh `pytest --collect-only` that scans the entire test tree |
| `test_live_architecture_contract.py::test_live_repository_satisfies_architecture_contract` | **6.4s** | `subprocess.run` launches a separate Python process to run `check_project_architecture.py` |
| `test_regression_descent.py::test_regression_descent_log_classifies...` | **3.4s** | Calls `collect_deterministic_selectors()` — yet another full pytest collection |
| `test_replay_registry.py::test_migrated_replays_bind_to_exact_collected_claims` | **2.9s** | Calls `collect_pytest_selectors()` — same pattern |

### Secondary Offenders — Repeated Collection & Subprocess (1–3s each)

| Test | Time | Root Cause |
|---|---|---|
| `test_test_lane_selection.py::test_live_tests_are_selected_only_by_the_live_lane` | 3.2s | pytest collection |
| `test_test_lane_selection.py::test_release_marker_always_implies_requires_llm` | 3.1s | pytest collection |
| `test_workflow_node_inventory.py::test_every_discovered_owner_has_scripted_real_workflow_claim` | 3.0s | pytest collection |
| `test_live_evaluation.py::test_live_model_config_constructs_with_one_retry_authority` | 1.9s | TBD |
| `test_asset_checker_contract.py::test_subprocess_collector_smoke...` | 1.6s | subprocess spawn |
| `test_work_unit_store_multiprocess.py::test_independent_processes_race_same_candidate...` | 1.2s | multiprocess spawn |

### Root Cause Classification

Two patterns account for essentially all the measurable slowness:

1. **Pytest collection executed repeatedly (≈20–25s wasted).**
   `test_test_lane_selection.py` alone triggers 7 separate `pytest --collect-only`
   invocations across its 6 tests. Each collection scans the full `tests/` tree from
   scratch. Lane-selection governance, replay registry binding, and workflow inventory
   tests all redundantly collect the same selectors.

2. **Subprocess spawn overhead (≈8–10s).**
   `check_project_architecture.py` is invoked via `subprocess.run` instead of being
   imported. Multiprocess store tests pay a spawn cost per test case.
   `test_asset_checker_contract.py` spawns a subprocess for the collector smoke test.

3. **Hash-chain boundary test at full scale (≈12.5s).**
   `test_exact_record_count_limit_round_trips` constructs 4,096 chain-hashed records.
   The invariant under test (record count limit is exactly `MAX_SUBMISSION_LEDGER_RECORDS`,
   encoded size is under `MAX_SUBMISSION_LEDGER_BYTES`) can be proven with 256 records.

### Quick Wins (No Architectural Change Needed)

| Change | Estimated Saving | Effort |
|---|---|---|
| Share one pytest collection result across all lane-selection tests in the module | 15–20s | Low — module-scoped fixture or session-scoped cached helper |
| Import `check_project_architecture` instead of `subprocess.run` | 5–6s | Trivial — one-line change |
| Reduce submission ledger loop from 4096 → 256 (or parameterize: one smoke at 4096, invariants at 256) | 10–11s | Trivial — change the loop bound or split into two tests |
| **Projected fast suite after changes** | **~30s** | |

### What NOT to Remove

None of these slow tests should be deleted. Each guards a real invariant:

- `test_test_lane_selection.py` — ensures deterministic/live/release lanes are an exact
  partition (governance requirement EVH-004).
- `test_live_architecture_contract.py` — verifies the live repo matches the canonical
  project-structure TOML (PRS-005).
- `test_regression_descent.py` — validates every regression-descent entry classifies
  its discovery and names a collected test or live rationale (EVH-006, EVH-010).
- `test_exact_record_count_limit_round_trips` — proves the work-unit ledger boundary
  is exact and the encoding stays under the byte limit (WUK-003).

### Integration Suite Notes

The demo/TUI subprocess tests (`test_demo_tui.py`, `test_demo_cli.py`,
`test_demo_sessions.py`) run at 1.5–2.2s each because they import Textual and
construct full TUI app instances. These are reasonable for integration-level
tests and don't dominate the wall clock. No action needed unless the integration
suite grows beyond ~90s.

## Goal

Make the next cross-cutting Deep Research change faster to execute without weakening
red-green discipline, capability boundaries, or release verification.

## Proposed Work

1. For every requirement, select exactly three evidence layers at most:
   - one pure contract/unit test for validation, redaction, or reducer logic;
   - one runtime integration test for persistence/correlation/authorization wiring;
   - one user-path fixture only when the user-visible outcome cannot be proven below.
   A second test must name a distinct risk; "another layer" is not a justification.
2. Add a maintained change-impact map from each requirement to the owning contract,
   runtime seam, presentation adapter, and its smallest selector. Start each task from
   that map instead of re-reading unrelated graph and UI modules.
3. Provide named focused Make targets for intake, retained-observation, work-unit, and
   strict-checkpoint slices. Each target prints its elapsed time and a single purpose;
   complete verification remains the final gate, not the edit-loop command.
4. Keep a short active-change progress checkpoint in `tasks.md`: current group, exact
   completed evidence, next smallest selector, elapsed time, and a concrete blocker if
   one exists. Do not use prose status as a substitute for checkboxes.
5. **Measure test collection/setup/body separately.** The measured data (see above)
   confirms the original hypothesis: focused observation tests complete in seconds, and
   the first optimization target is **redundant pytest collection** and **unnecessary
   subprocess spawning**, not parallelizing the test runner.
6. Identify modules that repeatedly require simultaneous edits across graph/runtime/
   presentation and propose one narrow projection or injected capability boundary for
   each. Do not introduce generic helpers merely to reduce file count.

### Concrete Performance Actions (from measured data)

7. **Cache pytest collection** across lane-selection, replay-registry, regression-descent,
   and workflow-inventory tests. One collection per session, shared via a module- or
   session-scoped fixture.
8. **Inline `check_project_architecture.py`** — import and call its `main()` or
   equivalent entry point rather than spawning a subprocess.
9. **Shrink the submission ledger boundary test** — 256 records prove the same
   invariants as 4,096. Keep a separate smoke test at full scale if needed, gated behind
   a `--run-slow` marker.
10. **Add a `--durations=20` gate to CI** — fail or warn if any single deterministic
    test exceeds 5 seconds without a documented reason. This prevents silent regression.

## Non-Goals

- Do not skip tests, turn off strict validation, or replace deterministic coverage with
  manual inspection.
- Do not modify `backend/` or `frontend/` for the downstream Deep Research roadmap.
- Do not optimize provider/network latency under this plan; that needs separately
  measured live-run evidence.

## Acceptance Evidence

- A future cross-cutting change states its minimum selector before code edits and no
  requirement has more than the three evidence layers above without a recorded risk.
- Focused selector timing and complete verification timing are both recorded; the
  focused selector is the normal edit-loop command.
- The active `tasks.md` can be read alone to determine current work and next evidence.
- No architecture or redaction regression is introduced by the acceleration work.
- `make test-fast` runs in ≤35s (from 65s baseline), with the improvement attributable
  to the three quick wins above.

## OpenSpec Link

Archived change:
`openspec/changes/archive/2026-07-22-accelerate-deep-research-change-delivery/`.
Its completed `tasks.md` is the implementation progress authority; this plan remains
the measured motivation and decision record.
