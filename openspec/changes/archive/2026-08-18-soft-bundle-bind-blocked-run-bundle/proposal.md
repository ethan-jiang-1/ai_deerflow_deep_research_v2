# Soft Bundle Binds a Blocked Run's Bundle (BUG-042)

## Why

After two repair-then-blocked mode-003 runs, `soft-bundle run … --mode 003` exited
non-zero (blocked terminal) and left `manifest.json` at `current_bundle_id: null`
with no `bundles/<id>.json` record, so the very diagnostics that the runbook needs
(`inspect`/`status`/`verify`/`phases`) all failed with `current_bundle_id not bound`.
The run did produce a valid bundle (a blocked terminal still writes `state.json`,
`diagnostics/`, `events.jsonl`, checkpoint, and journal); the CLI simply never bound
it because `cmd_run` returned on the non-zero exit before `_record_bundle`.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/soft_bundle.py` — `cmd_run` owns the root→bundle_id→local-path record boundary and the bind-ordering bug.
- **Seam classification:** wiring — binds an existing operator entry surface's resolved bundle id into the operator-side record regardless of run exit code, without changing graph, node, lifecycle, model, or tool authority.
- **Question:** When the underlying operator run exits non-zero but still produced a parseable, resolvable `bundle_id`, why does the CLI fail to bind that bundle into the manifest — and how can it always record the resolved bundle before returning the run's own exit code, so blocked-run diagnostics stay inspectable?
- **Necessary adjacent/external contracts:** none beyond the existing `_parse_bundle_id` / `_find_bundle_dir` / `_record_bundle` unit seam in `tests/contract/test_soft_bundle_cli.py`; the operator `make demo-*` entry surfaces are unchanged.
- **Evidence seam:** `tests/contract/test_soft_bundle_cli.py` — a new fixture where `_run_make` returns a non-zero `CompletedProcess` carrying a valid `Run Bundle: b_xxx` and the bundle dir exists; assert `cmd_run` still records the manifest (`current_bundle_id`, `bundles/<id>.json`) and returns the run's non-zero exit.
- **Not in scope:** no lifecycle authority changes, no path/bundle selection changes, no `deerflow/` changes, no wave2/graph/gate changes, no new CLI commands, no live-model or research quality claims.
- **Triggered review policies:** authority-and-projections, change-admission

## What Changes

- **BUG-042 — `cmd_run` binds a resolved bundle id even when the run exits non-zero.**
  In the **mode 002 and mode 003** branches, the early-return condition currently
  uses an OR-gate (`proc.returncode != 0 or bundle_id is None`, plus a missing
  journal-derived dir in mode 002), so a failed run returns before `_record_bundle`
  even when a valid bundle was produced and resolved. Restructure those two branches
  so the bind decision depends only on "did we resolve a valid bundle id + bundle
  directory", never on the exit code: resolve the bundle, print the raw run output on
  the failure path (so the underlying failure reason stays visible), call
  `_record_bundle(root, manifest, bundle_dir)`, print the bound id/local path, run
  verification (a blocked run reports `RESULT: FAIL`), and return the run's own
  non-zero exit code so the failed/blocked status is preserved. Mode 001 is left
  unchanged: its early return is an AND-gate (`proc.returncode != 0 AND
  bundle_id is None`), so it already flows to binding whenever a bundle is resolved.
  A run that produces no valid `bundle_id`/bundle dir keeps today's "not bound"
  behavior.

This keeps every soft-bundle query command (`inspect`/`status`/`verify`/`phases`)
functional after a blocked run, matching the runbook's "inspect the diagnostics of a
blocked run" flow without ever treating the record as lifecycle authority.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `soft-bundle-session-cli`: `run` records and binds the resolved bundle regardless
  of the operator entry's exit code (blocked terminal included), so post-run
  queries work on failed runs while the failed run's exit status is preserved.

## Impact

- Code: `deep_research_harness/scripts/soft_bundle.py` (`cmd_run` bind ordering for
  modes 002/003; mode 001 untouched).
- Tests: `tests/contract/test_soft_bundle_cli.py` — add non-zero-exit/blocked-run
  bind fixtures for mode 003 and mode 002; deterministic, offline, no network/API
  keys; `make verify` stays offline-green.
- Docs: BUG-042 card moves to `_done/_fixed_bugs/` on completion.
- No changes to `deerflow/` or public DeerFlow interfaces; ordinary downstream work
  neither modifies nor source-browses the `deerflow/` gitlink.