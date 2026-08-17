# Fix Local Demo Tooling (BUG-032 / BUG-033 / BUG-034)

## Why

Three active P1/P2 bugs make the local operator demo surface fragile: sandboxed
`uv` cache access (`EPERM`) blocks every `uv run --locked --no-sync` demo target,
`demo-real`/`demo-tui` hard-fail with a Usage error whenever `PROFILE` is omitted,
and `soft-bundle inspect` always reports mode-002 (scripted-real) bundles as
unavailable even though the run itself passes and the bundle's diagnostics are
healthy. All three are local operator tooling defects; fixing them together in one
change keeps the demo runbooks (001/002) and the soft-bundle CLI trustworthy as the
contract probes they are meant to be.

## What Changes

- **BUG-032 — operator entry commands default `UV_NO_CACHE=1`.** The
  `deep_research_harness/Makefile` `ENTRY_RUN` and `PROFILE_RUN` wrappers (demo,
  sessions, soft-bundle, session-workbench, profile commands) pass `UV_NO_CACHE=1`
  to `uv`, so those local commands bypass the global uv cache by default and the
  `Operation not permitted` failure in restricted/sandboxed environments disappears.
  Test/install/build targets keep normal caching so the offline gate
  (`UV_OFFLINE=1 make verify`) can still resolve build backends from the cache.
  Operators MAY override with `UV_NO_CACHE=0`.
- **BUG-033 — Makefile defaults `PROFILE=demo`.** `deep_research_harness/Makefile`
  sets `PROFILE ?= demo`, so `demo-real` and `demo-tui` launch with the standard
  `demo` profile when the caller omits `PROFILE` (the `PROFILE="${PROFILE:-demo}"`
  pattern the bug card already endorsed). An explicitly empty `PROFILE=` is still
  rejected by the existing guard.
- **BUG-034 — `soft-bundle inspect` becomes mode-aware.** `scripts/soft_bundle.py`
  `cmd_inspect` keeps delegating mode-001 bundles to the existing `demo-sessions`
  inspection route, and for mode-002 bundles resolves the recorded bundle directory
  (same operator-side lookup as `path`/`phases`/`verify`, which already work for
  002) and renders the bundle's contained diagnostics read-only — the same
  "Observed summary" / "Journal health" / event facts — via the shared
  `RunObservationStore` inspection path. **No change to `BundleLifecycle` scope
  containment** (runtime stays untouched): a scope-external Handle remains
  unavailable; the operator record is an observation, never lifecycle authority.
- **BUG-034 (second layer) — the scripted-real workflow now publishes its terminal
  lifecycle observation.** `scripts/debug_scripted_real_workflow.py` drives the
  public tool surface directly and never attached an observation publisher, so its
  journal's `run-summary.json` stayed stuck at the initial establish fact
  (`active@bootstrap`) with no terminal event — making runbook-002's checkpoint
  (`Observed summary: completed@final_delivery generation 0`) unattainable even
  once `inspect` could read the bundle. The workflow now publishes the terminal
  lifecycle fact (mirroring what the demo entry points do through their experience
  wrapper), so the mode-002 journal summary reaches the terminal state exactly like
  fixture-graph runs.
- **Spec deltas.** `soft-bundle-session-cli` (SBC-004) and `demo-pipeline`
  (DPL-005) are amended to state the new behavior (see Capabilities).
- **Bug ledger closeout.** After implementation, BUG-032/033/034 move from
  `_backlog/bugs/` to `_backlog/_done/_fixed_bugs/` following the procedure in
  `_backlog/bugs/README.md`.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `soft-bundle-session-cli`: SBC-004 `inspect` behavior changes from "always
  delegate to the demo-sessions route" to mode-aware: mode-001 bundles delegate to
  the existing demo-sessions inspection route; mode-002 (scripted-real) bundles are
  reported from the recorded bundle's contained diagnostics because they live in an
  independent run scope the fixed demo scope cannot see.
- `demo-pipeline`: DPL-005 Makefile-targets requirement gains the local command
  environment defaults — `UV_NO_CACHE=1` for every local `uv` invocation and
  `PROFILE=demo` default for the profile-bearing real targets — so sandboxed
  environments and runbook-style callers that omit `PROFILE` are not blocked.
- `scripted-real-workflow-debug`: new requirement — the scripted-real workflow
  publishes its terminal lifecycle observation into the run bundle's journal so the
  journal summary reaches the terminal state (the demo entry-point experience
  wrapper does this automatically; the operator workflow drives the tool surface
  directly and must do it itself).

## Impact

- **Code touched:** `deep_research_harness/Makefile` (two defaults),
  `deep_research_harness/scripts/soft_bundle.py` (`cmd_inspect` mode branch), a new
  small shared read-only render helper (`scripts/_inspect_view.py`) so
  `demo_sessions` and `soft_bundle` emit identical diagnosis fact lines, and the
  contract test file. No Harness-core runtime file changes (`bundle_lifecycle.py`,
  `session_workbench.py`, `run_observation.py` stay as-is).
- **Tests:** extend `tests/contract/test_soft_bundle_cli.py` with a mode-002 inspect
  contract test (patched paths, synthetic bundle diagnostics) and keep the
  mode-001 delegation test; add a process-level 002 regression per BUG-034
  (run mode 002, then `inspect` prints summary + journal health). Makefile defaults
  are verified by running a demo target without `UV_NO_CACHE`/`PROFILE` in the
  environment.
- **No dependencies, no API changes:** no new packages; `deerflow/` gitlink is
  neither modified nor source-browsed; no public product surface changes.
- **Bug ledger:** BUG-032/033/034 cards move to `_backlog/_done/_fixed_bugs/`.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/soft_bundle.py`
  (operator-only Soft Bundle CLI — the smallest module owning the `inspect`
  routing decision for scripted-real bundles).
- **Seam classification:** `wiring` — all three fixes are operator command plumbing
  and read-only inspection routing; no model-bearing symptom, no human-decision
  authority, no deterministic-gate change, and no lifecycle-authority change.
- **Question:** How do local demo commands become robust to sandboxed uv-cache
  `EPERM` and omitted `PROFILE`, and how can `soft-bundle inspect` report a healthy
  mode-002 bundle without weakening `BundleLifecycle` scope containment?
- **Necessary adjacent/external contracts:**
  - `deep_research_harness/Makefile` — demo target command surface; question: which
    `UV_NO_CACHE` / `PROFILE` defaults keep local demo runs working without changing
    target semantics or the `demo-real` profile contract.
  - `scripts/demo_sessions.py` + `runtime/run_observation.py`
    (`RunObservationStore`) — shared journal-health/diagnosis fact path; question:
    how to render mode-002 diagnosis facts read-only with no duplicated logic.
  - `deerflow/` gitlink — ordinary downstream work neither modifies nor
    source-browses it; this change stays entirely inside `deep_research_harness/`
    and `_backlog/`.
- **Evidence seam:** `tests/contract/test_soft_bundle_cli.py` (patched-path unit
  tests for inspect routing) plus a process-level mode-002 regression; Makefile
  defaults verified by direct target runs without env overrides.
- **Not in scope:** changing `BundleLifecycle` scope containment or any
  `runtime/`/`domain/`/`graph/` behavior; changing `demo-real`/`demo-tui` target
  semantics; making real runs credential-free; rewriting `_backlog/_local_demo`
  runbooks or creating runbooks 003/004.
- **Triggered review policies:** `deep-research` (local operator surface/operation
  routing only; no workflow-control, node-agent, or deerflow-downstream triggers —
  no state/recovery/outcome/control change, no LLM surface, no public DeerFlow
  interface change).
