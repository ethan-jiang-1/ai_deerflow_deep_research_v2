# Design — Fix Local Demo Tooling

## Context

See proposal.md (Why / What Changes). Current state that shapes the approach:

- `deep_research_harness/Makefile` runs every local command through `uv run --locked --no-sync` (`ENTRY_RUN`), which reads the global uv cache and can die with `EPERM` in sandboxed environments (BUG-032). `demo-real`/`demo-tui` hard-require `PROFILE` via `test -n "$(PROFILE)"` (BUG-033). The `_backlog/_local_demo` runbooks already standardize on inline `UV_NO_CACHE=1` and the endorsed `PROFILE="${PROFILE:-demo}"` pattern.
- `scripts/soft_bundle.py` `cmd_inspect` always delegates to `make demo-sessions inspect <bundle_id>`. `scripts/demo_sessions.py` resolves through `DemoAdapter(bundle_root=.deep-research-demo-runs)` whose fixed fixture-graph scope (`demo-user` / `demo-thread-<hash>`) cannot see mode-002 bundles: those are published by `debug-scripted-real-workflow` into an independent run workspace (`workspace/scripted-real/run-<ts>-<hex>/`) under scope `debug-operator` / `thread-<token>` (BUG-034). `BundleLifecycle` scope containment (`runtime/bundle_lifecycle.py`) is intentional and must not change: a scope-external Handle must stay unavailable.
- `soft_bundle` already resolves mode-002 bundles correctly for `path`/`phases`/`verify` via `_find_bundle_dir(bundle_id)` (an operator-side `rglob` under the operator workspace), and the run itself passes with healthy diagnostics (`diagnostics/run-summary.json` has `journal_availability: complete`, 48 events, `final/report.md` exists).
- The shared read path for journal facts is `RunObservationStore(bundle_root=<bundle dir>, bundle_id=...).inspect(...)` — exactly what `BundleWorkbench.diagnosis` uses; `demo_sessions._render` turns that into the human-readable lines (`Observed summary: …@… generation N`, `Journal health: …`, per-event facts).

## Goals / Non-Goals

**Goals:**
- Make every local demo/session/soft-bundle/profile command robust to sandboxed uv-cache `EPERM` by defaulting `UV_NO_CACHE=1` in the Makefile, without a behavior change when explicitly overridden.
- Make `demo-real`/`demo-tui` (and the profile helpers) launch with `PROFILE=demo` when omitted, while an explicitly empty `PROFILE=` keeps failing the preflight guard.
- Make `soft-bundle inspect` report healthy mode-002 bundles (summary + journal health + events) with zero changes to `BundleLifecycle`, `BundleWorkbench`, or any `runtime/`/`domain/`/`graph/` behavior.

**Non-Goals:**
- No change to `BundleLifecycle` scope containment or any lifecycle authority.
- No change to target semantics, recipes, or the `demo-real` profile contract beyond the default value.
- No rewrite of `_backlog/_local_demo` runbooks and no creation of runbooks 003/004.
- No new dependencies.

## Decisions

### D1: Operator entry commands default `UV_NO_CACHE=1`

Set `UV_NO_CACHE ?= 1` in `deep_research_harness/Makefile` and pass
`UV_NO_CACHE=$(UV_NO_CACHE)` through the `ENTRY_RUN` and `PROFILE_RUN` wrappers.
Every demo/session/soft-bundle/session-workbench/profile entry command then bypasses
the global uv cache by default, while `UV_NO_CACHE=0` on the command line or in the
environment still restores caching (`?=` yields to an existing value).

- Why scoped to entry commands, not global: a global `export UV_NO_CACHE=1` also
  hits `uv build` inside the offline gate (`UV_OFFLINE=1 make verify`), where the
  wheel-contract test's `uv build` can then neither read the cache (disabled) nor
  the network (offline) to resolve its `hatchling` build backend — a real gate
  regression in normal environments. Scoping to the entry wrappers covers exactly
  BUG-032's symptom class (`make demo-scripted`, `demo-fixture-graph`,
  `demo-sessions`, `demo-real-embedded-smoke`, soft-bundle, etc.) while test/
  install/build targets keep normal caching.
- Alternative considered: `UV_CACHE_DIR` pointed at a repo-local writable cache.
  Rejected — it changes the documented `UV_NO_CACHE=1` convention, needs gitignore
  and priming, and does not help fresh offline checkouts either.
- Alternative considered: fix the sandbox/uv-cache directory permissions instead.
  Rejected — environment-specific and out of the repo's control.

### D2: Makefile defaults `PROFILE=demo`

Add `PROFILE ?= demo` next to `DEMO_ARGS ?=`. `?=` sets the value only when `PROFILE` is undefined, so `make demo-real PROFILE=…` and `PROFILE=… make demo-real` keep working, and `make demo-real PROFILE=` (explicitly empty, hence defined) still trips the existing `test -n "$(PROFILE)"` Usage guard. This is exactly the `PROFILE="${PROFILE:-demo}"` semantics the BUG-033 card already endorsed for the (now retired) numbered scripts.

- Why `?=`, not `:=`: preserves caller/environment authority and the explicit-empty rejection.
- Why a Makefile default at all: the bug's failure class is "caller omitted PROFILE"; the default moves that from hard failure to the standard demo profile, which is what every runbook uses. The guard stays as a sanity check for pathological explicit values.

### D3: `soft-bundle inspect` becomes mode-aware; mode 002 renders the recorded bundle read-only

`cmd_inspect` reads the manifest `mode` and branches:

- **mode 001**: unchanged — delegate to `make demo-sessions DEMO_ARGS="inspect <bundle_id>"` and return its exit code.
- **mode 002**: resolve `bundle_dir = _find_bundle_dir(bundle_id)` (same operator-side lookup `path`/`phases`/`verify` already use — proven to find scripted-real bundles). If missing → render the unavailable view and exit 2 (no recreate/recover). Otherwise run `RunObservationStore(bundle_root=bundle_dir, bundle_id=bundle_id).inspect(bundle_id=bundle_id)` — an async method, so the sync `cmd_inspect` runs it via `asyncio.run(...)`, exactly as `demo_sessions.main` does — map the returned `RunObservationInspection` into a `WorkbenchDiagnosisView` (`AVAILABLE` iff `inspectability is AVAILABLE`, `summary`, `events[-8:]`, `incomplete_reasons`), and always render through the shared helper: `Run Bundle: <id>`, `Observed summary: <status>@<phase> generation <n>`, `Journal health: <value>`, diagnostic reference / dropped-event interval when present, last-8 event facts, incomplete reasons, and the read-only note. Exit 0 when the view is `AVAILABLE`, else 2.

The renderer is extracted from `demo_sessions._render` into a small shared script module `scripts/_inspect_view.py` so both routes emit byte-identical fact lines and cannot drift. Both scripts import it as a sibling module (`from _inspect_view import render_diagnosis`), which resolves because the script directory is `sys.path[0]` when run via `uv run python scripts/…`; the contract test must follow `test_demo_sessions.py`'s pattern of inserting `scripts/` onto `sys.path` before importing `soft_bundle`.

- Why direct render instead of extending `demo_sessions`: `demo_sessions`' contract is "resolves the supplied opaque Bundle id through the fixed local lifecycle profile" (its module docstring and REJ-004); giving it an operator-supplied root would silently bypass the very reauthorization that route exists to provide. `soft_bundle` is already the operator-side observation surface (SBC-005: records/paths are observations, never lifecycle authority) and already reads recorded bundle content directly for `phases`/`verify`, so a read-only diagnosis render there is consistent.
- Why `RunObservationStore.inspect` rather than hand-parsing `events.jsonl`: it is the one existing, tested implementation of journal-health/summary/event projection (used by `BundleWorkbench.diagnosis`); reusing it avoids a second, drift-prone journal reader.
- Why no `BundleLifecycle`/`BundleWorkbench` change: scope containment is a deliberate runtime invariant; the bug is that the operator tool delegated to the wrong scope, not that the runtime hides foreign bundles.
- Alternative considered: have `debug-scripted-real-workflow` print the scope/thread token so `demo_sessions` could re-resolve via a matching `BundleLifecycle`. Rejected — requires threading a runtime identity through operator output and still pokes at scope internals; the recorded-path render is simpler and already the pattern for `phases`/`verify`.

### D4: Exit codes and error text stay consistent with today

Available → 0, unavailable → 2, bounded `error:` messages on stderr. Mode-002 inspect reuses the same "unavailable" wording as the current delegation failure so runbooks and scripts see a stable contract.

### D5: The scripted-real workflow publishes its terminal observation

While implementing D3's process regression, the mode-002 journal's `run-summary.json`
was found stuck at the initial establish fact (`active@bootstrap`, no terminal event):
`debug_scripted_real_workflow.py` drives the public tool surface (`run_deep_research`)
directly, so unlike `demo.py`/`demo_real.py`/`demo_tui.py` it never attaches an
observation publisher, and the runtime only publishes lifecycle facts when one is set.
Runbook-002's checkpoint (`Observed summary: completed@final_delivery generation 0`)
was therefore unattainable regardless of the inspect fix.

Fix: in `_observe`, after resolving the completed bundle and validating the in-scope
trace, publish the terminal lifecycle fact via the existing
`BundleRunObservationPublisher` (same class the demo adapter exposes), using the
already-resolved lifecycle, `world.identity` scope, and the terminal state read from
Bundle State. `publish` appends a `terminal` event and rewrites `run-summary.json` to
the terminal state (verified in `_bundle_publish_sync`). This is observation-only: it
never changes Bundle State or control results.

- Why publish in `_observe` rather than refactoring `_drive` onto
  `ResearchRunExperience`: the workflow's drive loop intentionally exercises the
  public tool surface (`run_deep_research` with a scripted runtime), which is the
  point of SCR-001; one terminal publish at observation time reaches the same journal
  end-state with minimal change and no graph/control refactor.
- Why the `publish` class and not a hand-written journal write: it is the single
  tested implementation of lifecycle-fact projection and keeps the journal
  consistent (manifest, summary, events, dropped-event accounting).
- Alternative considered: relax runbook-002's checkpoint to accept any summary. Rejected — it would paper over a real journal-accuracy defect; mode 001 runs reach terminal summaries, so 002 should match.

## Risks / Trade-offs

- [Global `UV_NO_CACHE=1` slows non-sandboxed dev (no cache reuse)] → Default is overridable (`UV_NO_CACHE=0`); the repo's local commands are `--no-sync` anyway, so the cost is small; CI's environment-regression lane already runs `UV_OFFLINE=1`.
- [`UV_NO_CACHE=1` also affects `make install`/`lock-check`/test targets] → Intended for uniform local robustness; no correctness impact (uv still resolves from lockfile/network); escape hatch documented in design/tasks and the Makefile comment.
- [`PROFILE=demo` default masks a genuinely forgotten profile] → The default equals the profile every runbook uses; explicitly empty `PROFILE=` still fails; real deployments use `demo-real` only as a local surface.
- [Direct render for mode 002 skips lifecycle reauthorization] → Bounded: the operator record is observation-only (SBC-005), the render reads only the recorded bundle's contained diagnostics, and a missing/deleted bundle yields `unavailable` — never a recreate or reopen. Same posture `verify`/`phases` already have.
- [Renderer drift between `demo_sessions` and `soft_bundle`] → Single shared render helper (D3).
- [`_find_bundle_dir` rglob cost] → Operator workspace is small; already used by three commands; no new scaling surface introduced.

## Migration Plan

No data migration or external deployment: this is a local operator-tooling change. Rollback = revert the commit; behavior reverts to the pre-change defaults. After implementation, move BUG-032/033/034 cards to `_backlog/_done/_fixed_bugs/` per `_backlog/bugs/README.md` and update the two ledger READMEs.

## Open Questions

None that change specs, approach, or tasks. Implementation details deferred to tasks: exact shared-render module name/placement and exact reworded unavailable message for mode 002.
