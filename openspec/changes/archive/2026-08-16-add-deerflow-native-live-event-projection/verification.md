# Apply Verification Evidence

## Change-Specific Evidence

- Current-pin public API, event projection, runtime-adapter, trusted-runtime,
  Bundle-lifecycle, graph-owner, validation, Journal-separation, source-guard,
  architecture, and Gateway-fixture-free focused evidence passes (`357 passed`).
- The deterministic fast lane passes (`2766 passed`, `3 deselected`).
- The workflow lane passes (`35 passed`, `3059 deselected`).
- Project requirement and architecture governance, lock checking, Ruff checking and
  formatting, strict OpenSpec validation, and `git diff HEAD --check` pass.
- DeerFlow nested `HEAD`, root gitlink, and registry lock remain
  `66b9e7f21212490cf92fafac137542b9deb06615`. The submodule is clean, and no
  DeerFlow source, package metadata, or `uv.lock` changed.

## Full Offline Gate

`cd deep_research_harness && UV_OFFLINE=1 make verify` passes every gate before
the integration lane. The fast lane is green; the integration lane reports
`238 passed`, `4 skipped`, `32 deselected`, and the following two failures:

- `tests/integration/test_wave1_work_units.py::test_real_wave1_review_gate_enforces_question_floor_and_review_integrity`
  expects route `repair` but receives `pass`.
- `tests/integration/test_local_entry_environment.py::test_prepared_entries_preserve_dependency_state_and_keep_launcher_credential_bounded`
  expects the empty copied dotenv to stop the real launcher, but the current public
  DeerFlow sandbox import has already loaded the developer credential environment.

Neither failing owner is modified by this change. The Wave1 gate implementation,
demo launcher, and local-entry test remain identical to `HEAD`.

## Baseline Reproduction

Both failures reproduce outside the change in isolated detached worktrees at
baseline `f555abb` with the same interpreter and DeerFlow pin:

- The exact Wave1 test fails with the same expected `repair`, actual `pass` result.
- The exact local-entry test, supplied with the same current `profiles/` input used by
  the working-tree test, reaches the same launcher assertion and fails because the
  real path is considered credential-ready.

The baseline runs did not inspect or modify DeerFlow source and retained no credential
value. Repairing either failure would change Wave1 gate or demo credential-boundary
behavior outside this change's approved runtime-observability/runtime-integration
scope. This evidence records the blockers without weakening, reverting, or expanding
the live projection implementation.
