# Design: Soft Bundle Binds a Blocked Run's Bundle

## Context

Observed defect (BUG-042): after two repair-then-blocked mode-003 runs,
`soft-bundle run <root> --mode 003` exited non-zero and left the manifest at
`current_bundle_id: null` with no `bundles/<id>.json` record. The blocking occurred
in `cmd_run` (and mode-003 branch): `_run_make` returned non-zero, and the branch
did `print(output, stderr); return proc.returncode or 1` before ever calling
`_record_bundle(root, manifest, bundle_dir)` — even though `_parse_bundle_id(output)`
had successfully parsed a valid `Run Bundle: b_xxx` id and `_find_bundle_dir` had
resolved the real bundle directory. Because the blocked terminal still writes
`state.json`, `diagnostics/`, `events.jsonl`, checkpoint, and journal, that bundle
is exactly what `inspect`/`status`/`verify`/`phases` need — but they all fail with
`current_bundle_id not bound` until an operator hand-edits the manifest.

Owners today: `scripts/soft_bundle.py` (`cmd_run` branches for modes 001/002/003,
`_record_bundle`, `_parse_bundle_id`, `_find_bundle_dir`), the spec owner
`soft-bundle-session-cli`, and the contract-test seam
`tests/contract/test_soft_bundle_cli.py`.

## Goals / Non-Goals

Goals:

- Whenever a run produces a valid, resolvable `bundle_id`, `cmd_run` records and
  binds it (`current_bundle_id` + `bundles/<id>.json`) regardless of the operator
  entry's exit code, so blocked-run diagnostics stay inspectable.
- The run's truthfulness is preserved: a non-zero run still returns its non-zero
  exit code and is reported as failed; the CLI never claims a blocked run succeeded.

Non-Goals (design-level):

- No lifecycle authority changes: the record remains an operator-side observation,
  never a `start/resume/refine/status/cancel` input or a recovery source.
- No path/bundle selection semantics change; `_parse_bundle_id` / `_find_bundle_dir`
  logic is untouched.
- No change to `verify` semantics itself (a blocked run still `RESULT: FAIL`).
- No `deerflow/` or product `deep_research` tool changes.

## Decisions

### D1 — Bind before returning, keyed on a resolved bundle, not on exit code

Restructure the **mode 002 and mode 003** branches so the bind decision depends only
on "did we resolve a valid bundle id + bundle directory", never on the process exit
code. After parsing and resolving, call `_record_bundle(root, manifest, bundle_dir)`
and print `bound_bundle_id` / `bundle_local_path` unconditionally when a bundle was
resolved. Only the *return code* is derived from the run's exit status: on success
run the existing verification and return `0 if ok else 1`; on a non-zero run still
run verification (a blocked run reports `RESULT: FAIL`) and return the run's original
non-zero code.

Concretely, the mode-003 branch becomes:
- parse `bundle_id` from output; if none → print the raw output to stderr and
  return `proc.returncode or 1` (today's behavior, no bind — no bundle resolved;
  failure detail preserved).
- resolve `bundle_dir`; if none → print the raw output plus a bounded error and
  return 1 (today's behavior, no bind).
- if `proc.returncode != 0` (run failed but produced a resolvable bundle): print the
  raw run output to stderr first, so the underlying failure reason is never lost.
- `_record_bundle(...)`; print `bound_bundle_id`/`bundle_local_path`.
- record `run_exit = proc.returncode` so the shared tail returns the run's own exit
  code below.

The shared tail (reached by all modes after bind) becomes
`return run_exit or (0 if ok else 1)` where `run_exit` is a per-mode captured
non-None/zero exit code. Mode 001 leaves `run_exit = None` so its behavior is
byte-identical to today (`0 if ok else 1`); modes 002/003 set `run_exit =
proc.returncode` so a failed run's actual status (e.g. 1 or 2) is preserved instead
of collapsing to 1. This is the only way to honor "mode 001 not changed" while
threading the failure code through the one shared return line.

The raw-output print on the failure path is intentionally preserved: today's failure
route prints it, and binding on failure must not hide why the run failed. The bounded
case (no resolvable bundle) keeps today's exact output + non-zero return.

Mode 002 gets the same treatment: remove the OR-gate early return so a resolved
journal-derived bundle dir is bound even when the run exited non-zero; still require
a valid `bundle_id` and an existing bundle dir for binding, and keep the raw-output
print on the failure paths.

Mode 001 is deliberately **not changed**: its early return is an AND-gate
(`proc.returncode != 0 and bundle_id is None`), so whenever a bundle id is resolved
it already flows to `_record_bundle` even on non-zero exit. Applying the same
restructure there would be a no-op at best and a behavior change at worst.

Alternative rejected: only special-casing mode 003. The OR-gated early-return pattern
is shared by modes 002 and 003; fixing the shared ordering guards the mode the spec
targets (SBC-002 "bind regardless of exit code") uniformly without touching the
already-correct mode 001 path.

### D2 — Keep `_record_bundle` as the single record writer

`_record_bundle` already writes `bundles/<id>.json` and updates `current_bundle_id`
+ `updated_at`. No new writer is introduced; D1 only calls it in a wider set of
conditions. This keeps the manifest/record format and authority unchanged.

### D3 — Preserve run-status truthfulness via exit code, not via manifest state

The manifest records the *bound bundle*, and the exit code records the *run
outcome*; the two stay separate. `verify` on a blocked run still prints
`RESULT: FAIL` (e.g. `terminal_status=blocked`) — the CLI does not manufacture
success. `status`/`inspect`/`phases` become usable again because the manifest is
bound, which is exactly the runbook-003 diagnostic flow.

## Risks / Trade-offs

- [Binding on failure could mask that the run failed] → no: the exit code and
  `RESULT: FAIL` are preserved; binding only makes diagnostics reachable.
- [Failure detail could be lost when we bind instead of early-returning] → the raw
  run output is still printed to stderr on the failure path before binding, so the
  underlying make failure stays visible; verification problems add the typed reason
  (e.g. `terminal_status='blocked'`).
- [A run that produces an id but a missing/unresolvable bundle directory] → no bind,
  today's bounded error path, unchanged.
- [Mode-001 fallback path (`demo-fixture-graph`) may resolve the latest bundle by
  mtime on a failed run] → unchanged from today (mode 001 is not modified); binding
  already occurs whenever a bundle is resolved, success or failure.
- [Record now references a blocked/incomplete bundle] → the record is an
  observation, not a claim of health; `verify`/`inspect` read real facts from the
  bundle and report FAIL/unavailable appropriately.

## Migration Plan

No data migration: manifest schema is unchanged; a previously-unbound root simply
starts binding on its next `run`. Rollback = restore the early-return ordering;
affected roots return to today's unbound-on-failure behavior with no data damage.

## Open Questions

None.