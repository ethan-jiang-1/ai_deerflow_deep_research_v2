# Design

## Context

The embedded-smoke debugger entry's in-app wiring is complete and journey-proven
(`make debugger-proof` runs the driver matrix, entry contract, workbench tests, the
runbook-030 ladder, and the fifteen operator experiences). The break is entirely in the
entry chain's environment visibility, and it has two layers. First, every other demo
entry wraps the process in a `.env`-loading runner (`uv run --env-file .env` in the
Makefile targets and `run/real-research.sh`) while the launcher execs
`python scripts/demo_tui.py` bare. Second — discovered while building the red test —
the deerflow framework's own module-level `load_dotenv()` (implicit `find_dotenv`) does
fire inside the demo_tui import chain, but its anchor walks up from the framework
package directory in file-mode runs, so it loads the *repo-root* `.env` (which lacks
`DEERFLOW_DEMO_MODEL` on the operator's machine) and never reaches the harness-root
`.env`. That is exactly why the operator's screen reported only
`configuration.model_missing` while the web-tool check passed. A `-c`-mode child
changes `find_dotenv`'s fallback to the working directory and accidentally finds the
harness `.env` — which is why `-c`-based probes lie, and the regression probe below
must spawn a file-mode child. pytest's in-process environment masked the gap for every
existing test.

## Goals / Non-Goals

**Goals:**

- `./run/tui-workflow-debugger.sh --embedded-smoke` reaches `Ready` when the three
  variables (`DEEPSEEK_API_KEY`, `TAVILY_API_KEY`, `DEERFLOW_DEMO_MODEL`) live in the
  harness `.env` file, per runbook-031's preflight promise.
- Explicit environment precedence is preserved: anything already exported in the shell
  still wins (`override=False`).
- The entry chain is regression-locked: the env gap has a red-capable test at the
  app seam, and the loader contract has unit tests.

**Non-Goals:**

- No live credential validation (real model calls need the operator's live window and
  keys; readiness stays a non-network check).
- No `demo_real.py` change — both of its documented entry wrappers already pass
  `--env-file .env`.
- No spec deltas, no launcher logic growth (it stays presentation-only), and no
  changes under `deerflow/`.

## Decisions

1. **Loader lives in `_demo_core.py`, called first in `DeepResearchDemoTUI.__init__`.**
   Rationale: every construction path — launcher `main()`, headless subprocess probes,
   tests — funnels through the app constructor, so one call covers all entries without
   touching `main()` or the launcher. Alternative — launcher-side `set -a; . .env` —
   rejected: it duplicates the owner into bash (quoting hazards), and the regression
   probe cannot execute that seam headlessly (a subprocess cannot drive the TUI through
   the launcher); a future bare `python scripts/demo_tui.py` caller would re-dig the
   hole. Alternative — module-import side effect — rejected: import-order coupling makes
   the seam untestable per-construction.
2. **`load_dotenv(..., override=False)`, matching `scripts/live_preflight.py` and
   `scripts/controller_live_eval.py`.** Rationale: the Makefile and `real-research.sh`
   entries already inject `.env` upstream; `override=False` keeps their precedence
   semantics identical (explicit environment wins), so the repair cannot change behavior
   for entries that already worked.
3. **`DEMO_ENV_FILE` names the file path (test seam).** Rationale: the operator's `.env`
   is a user-reserved file and absent on CI; a deterministic regression test needs a
   temp file with known dummy values. When set, the seam *replaces* the default path so
   tests never depend on a machine's real `.env`. This mirrors the existing
   `DEBUGGER_PYTHON` launcher seam culture. A missing file is a no-op, so fresh clones
   and fixture mode are unaffected.
4. **File-mode subprocess probe as the symptom-level regression test.** Rationale: the
   operator's symptom is "the entry chain never loaded the *harness* file" — only a
   fresh interpreter running a child *file* (like the launcher's
   `python scripts/demo_tui.py`) with the variables stripped and the file supplied via
   the seam can go red on it. The probe drives
   `DeepResearchDemoTUI(mode="embedded_smoke")` via `run_test()` and asserts
   `Ready`; it fails red with `configuration.model_missing` /
   模型配置尚未就绪 and turns green after the `__init__` call. The child script
   lives one directory below the env file and the env file is not named `.env`, so no
   ambient `find_dotenv` walk can rescue it — the loader under test is the only path
   to `Ready`. A `-c` child was rejected after it proved green *before* the fix:
   `find_dotenv`'s cwd fallback found the machine's real harness `.env`, making the
   test lie.

## Risks / Trade-offs

- [Loading `.env` changes behavior for entries that already worked] → `override=False`
  preserves explicit environment precedence, and the full deterministic gate
  (`UV_OFFLINE=1 make verify` plus `make debugger-proof`) proves no entry regressed.
- [The framework's mis-anchored `find_dotenv` still loads a repo-root `.env` first]
  → read-only framework: the loader runs later with `override=False`, so on machines
  where a repo-root `.env` holds values that conflict with the harness `.env`, the
  repo-root values win for overlapping keys (matching today's launcher behavior);
  missing keys — the operator's actual failure — are filled from the harness file.
  The stale-key conflict surface is the operator's own ambient file and is recorded
  in BUG-075 for the live-window handoff.
- [Dummy credentials in tests could reach the network] → the readiness gate is
  non-network by contract and app startup performs no model call; the probe was
  hand-run to `Ready` with dummy values in seconds before being written as a test.
- [`.env` missing on fresh clones] → `load_dotenv` no-ops on a missing file; the
  zero-credential fixture entry tests prove fixture mode is untouched.
- [A wrong `DEERFLOW_DEMO_MODEL` name now surfaces differently] → unsupported names
  still resolve to the same honest `configuration.model_missing` failure; only the
  "configured but unseen" class is repaired.
