# Proposal

## Why

The documented embedded-smoke entry (`./run/tui-workflow-debugger.sh --embedded-smoke`,
runbook-031) fails for every operator whose three variables live in the harness `.env` file
instead of the shell environment: the readiness gate reports 模型配置尚未就绪
(`configuration.model_missing`) before any bundle exists. The root cause is an entry-chain
gap, not a configuration error. The Makefile demo targets and `run/real-research.sh` pass
`--env-file .env` to `uv run`, but the canonical debugger launcher execs
`python scripts/demo_tui.py` directly, and nothing in that chain — launcher, `demo_tui.py`,
or `_demo_core.py` — loads the `.env` file. A differential probe confirms it: the same
readiness check reads not-ready against the bare launcher environment and ready once
`load_dotenv(".env")` runs, and an app-seam subprocess probe reaches `Ready` when the
variables are present in the process environment. `demo_tui` is the only demo entry without
a `.env`-loading wrapper.

## What Changes

- `scripts/_demo_core.py` gains `load_local_environment()`: load the harness-root `.env`
  (or the path named by the `DEMO_ENV_FILE` test seam) with `override=False`, so an
  explicit shell environment always wins and a missing file is a no-op. This matches the
  existing precedent in `scripts/live_preflight.py` and `scripts/controller_live_eval.py`.
- `scripts/demo_tui.py` calls it first in `DeepResearchDemoTUI.__init__`, so every
  construction path (launcher `main()`, headless probes, tests) sees the documented `.env`
  variables before the readiness gate reads the process environment.
- Regression coverage: a subprocess probe in `tests/integration/test_debugger_entry.py`
  starts the embedded-smoke workbench with the three variables present only in a temp
  `.env` (named via `DEMO_ENV_FILE`) and asserts `Ready` instead of
  `configuration.model_missing` — the exact operator symptom, red before the fix. Unit
  tests in `tests/unit/test_demo_core.py` pin the loader contract (`override=False`,
  missing-file no-op, `DEMO_ENV_FILE` honored).
- No spec delta: the docs already promise this behavior (runbook-031's preflight note, the
  README debugger row, the launcher help text). This change repairs implementation
  conformance, like `repair-debugger-cli-entry-conformance` before it.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. No requirement text changes: the `research-demo-tui` `RED-013` launcher entry
  contract is unchanged; the repair makes the documented `.env` preflight behave as the
  runbooks already promise.

## Impact

- Primary implementation: `deep_research_harness/scripts/_demo_core.py`,
  `deep_research_harness/scripts/demo_tui.py`.
- Tests: `deep_research_harness/tests/integration/test_debugger_entry.py`,
  `deep_research_harness/tests/unit/test_demo_core.py`.
- Docs: none — runbook-031, the README debugger row, and the launcher help already
  document the `.env` preflight this change makes true.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/` gitlink;
  this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/demo_tui.py` (the
  entry chain whose readiness gate reads the process environment), with the shared loader
  in `scripts/_demo_core.py`; the launcher stays presentation-only and forwards flags.
- **Seam classification:** wiring — no lifecycle, admission, route, or node-agent behavior
  change; only the environment visibility that connects an operator's `.env` to the
  already-tested readiness gate.
- **Question:** How does the documented embedded-smoke entry see the operator's `.env`
  three variables without widening any authority and without disturbing entries that
  already load the file upstream?
- **Necessary adjacent/external contracts:** the Makefile demo targets and
  `run/real-research.sh` answer `--env-file .env` upstream; `override=False` keeps their
  precedence (explicit environment wins); `python-dotenv` is already in
  `ENTRY_REQUIRED_DISTRIBUTIONS`; the `research-demo-tui` `RED-013` requirement owns the
  launcher entry surface this repair serves; BUG-075 owns the ledger record.
- **Evidence seam:** red-first subprocess probe (embedded-smoke reaches `Ready` from a
  temp `.env` alone), unit tests for the loader contract, then the full deterministic gate
  (`UV_OFFLINE=1 make verify`), the TUI journey (`make tui-journey`), and
  `make debugger-proof`.
- **Not in scope:** `demo_real.py` (both of its documented entry wrappers already load
  `.env`), gateway profiles, live credential validation (real model calls need the
  operator's live window), the B1 embedded-real validation record, any spec delta, and
  anything under `deerflow/`.
- **Triggered review policies:** none: entry-chain conformance repair with no candidate, human judgment, control fact, admission/recovery boundary, node-agent role, or lifecycle output change.
