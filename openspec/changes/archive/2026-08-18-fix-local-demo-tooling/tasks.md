## 1. Makefile local command defaults (BUG-032, BUG-033)

- [x] 1.1 In `deep_research_harness/Makefile`, add `UV_NO_CACHE ?= 1` with a one-line comment (sandboxed uv-cache `EPERM` workaround for the operator entry commands, overridable with `UV_NO_CACHE=0`) and pass `UV_NO_CACHE=$(UV_NO_CACHE)` through the `ENTRY_RUN` and `PROFILE_RUN` wrappers; test/install/build targets keep normal caching.
- [x] 1.2 In `deep_research_harness/Makefile`, add `PROFILE ?= demo` next to `DEMO_ARGS ?=` so `demo-real`/`demo-tui` (and profile helpers) default to the demo profile when `PROFILE` is unset; the existing `test -n "$(PROFILE)"` guards stay.
- [x] 1.3 Verify defaults by command: `make demo-scripted` (credential-free fixture) succeeds with no `UV_NO_CACHE` in the environment; `make UV_NO_CACHE=0 demo-scripted` uses normal cache behavior (in a sandboxed environment it fails with the cache `Operation not permitted`, proving the override restores cache access); `make demo-real PROFILE=` exits 2 with the Usage message while a `demo-real` run without `PROFILE` passes the preflight guard and reaches the Python entry (real-demo prerequisite checks may still fail later — that is expected and proves the guard no longer blocks).

## 2. Shared read-only inspect renderer

- [x] 2.1 Create `deep_research_harness/scripts/_inspect_view.py` with `render_diagnosis(*, bundle_id: str, diagnosis: WorkbenchDiagnosisView) -> tuple[str, ...]` (moved from `demo_sessions._render`, unchanged output); `demo_sessions` imports and uses it with no output change.
- [x] 2.2 Run the existing `tests/integration/test_demo_sessions.py` to confirm the extraction is behavior-neutral.

## 3. Mode-aware `soft-bundle inspect` (BUG-034)

- [x] 3.1 In `scripts/soft_bundle.py` `cmd_inspect`, read the manifest `mode`: for mode `001` keep the existing `make demo-sessions DEMO_ARGS="inspect <bundle_id>"` delegation; for mode `002` resolve `bundle_dir` via `_find_bundle_dir(bundle_id)`, run `RunObservationStore(bundle_root=bundle_dir, bundle_id=bundle_id).inspect(...)` through `asyncio.run(...)`, map the inspection to a `WorkbenchDiagnosisView`, and render via the shared helper; render the unavailable view and exit 2 when the bundle dir is missing or the view is not `AVAILABLE` (never recreate/reopen).
- [x] 3.2 Extend `tests/contract/test_soft_bundle_cli.py`: insert `scripts/` onto `sys.path` before importing `soft_bundle` (following `test_demo_sessions.py`); add a mode-002 inspect test with a synthetic bundle diagnostics subtree that prints `Observed summary` + `Journal health` and returns 0; a missing recorded bundle returns exit 2 with the unavailable message; mode-001 inspect still delegates (assert `_run_make` invoked with the `demo-sessions` command).
- [x] 3.3 In `scripts/debug_scripted_real_workflow.py` `_observe`, publish the terminal lifecycle observation through `BundleRunObservationPublisher` (scope `world.identity`, lifecycle already resolved) after the in-scope trace checks, so `run-summary.json` reaches the terminal state and the journal gains the terminal event (observation-only; never touches Bundle State or control results).

## 4. Process-level mode-002 regression

- [x] 4.1 Run the runbook-002 sequence once: `soft-bundle create --name 002-demo --mode 002`, `soft-bundle run <root> --mode 002` (expect `RESULT: PASS`), then `soft-bundle inspect <root>` — assert exit 0 and that output contains exactly `Observed summary: completed@final_delivery generation 0` and `Journal health: complete`.

## 5. Bug ledger closeout

- [x] 5.1 `git mv` BUG-032, BUG-033, BUG-034 cards from `_backlog/bugs/` to `_backlog/_done/_fixed_bugs/`; add their rows to `_backlog/_done/_fixed_bugs/README.md` and bump its "Next available bug ID" to BUG-035; remove the three rows from `_backlog/bugs/README.md`; increment the fixed-bug count in `_backlog/_done/README.md`.

## 6. Final verification

- [x] 6.1 Run the focused suites (`tests/contract/test_soft_bundle_cli.py`, `tests/integration/test_demo_sessions.py`) and the repo gate (`UV_OFFLINE=1 make verify` or the documented fast lane); run `openspec validate fix-local-demo-tooling --strict`.
- [x] 6.2 Confirm docs do not contradict the new defaults (grep `deep_research_harness/docs/` and `_backlog/_local_demo/` for stale `Usage: make demo-real PROFILE=demo` failure claims and UV-cache workaround notes that can now be simplified); fix only factual contradictions.
