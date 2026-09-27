# Design

## Context

The debugger workbench's in-app wiring is complete and Pilot-tested
(`test_debug_pilot_journey.py` constructs `DeepResearchDemoTUI(mode="fixture",
debug_mode=True)` directly). The break is entirely in the entry chain:
`run/tui-workflow-debugger.sh` execs `python scripts/demo_tui.py` without the
`PYTHONPATH=src_fixtures` that every Makefile demo target sets, `main()`
drops the parsed `--debug` flag, and the launcher never injects `--debug`.
A differential repro loop (same child process, only PYTHONPATH varied) shows
Fault-with-the-user's-message without the path and Ready with it. pytest's
own `pythonpath = [".", "src_fixtures"]` config masked the gap for every
in-process test.

## Goals / Non-Goals

**Goals:**

- `./run/tui-workflow-debugger.sh --fixture` starts the debugger workbench
  (Ready state, composer Enter = Start Step) from any cwd, per RED-013.
- The entry chain is regression-locked: env gap, flag drop, and missing
  injection each have a red-capable test.
- Docs stop promising more than the code delivers (embedded debug deferred).

**Non-Goals:**

- No consumption wiring for `--attach`/`--replay` (stored-but-unconsumed
  today) and no RED-014 three-entry screen build — filed as BUG-069.
- No embedded debug (B1 deferred record owns it); no production or lifecycle
  changes; no spec deltas.

## Decisions

1. **Launcher sets `PYTHONPATH` (caller contract) AND fixture mode
   self-enables the path (entry self-sufficiency).** Rationale: the caller
   contract stays aligned with the Makefile targets, but the launch crash
   showed the contract is invisible at the entry seam — a fixture entry that
   dies on a caller-side path variable is a shallow module. The self-enable
   inserts `<harness>/src_fixtures` only when `mode == "fixture"`, so real
   modes never gain fixture-source visibility and `_demo_core`'s local-import
   rule keeps its meaning. Alternative — launcher-only fix — rejected: the
   regression test then cannot actually execute the repaired seam (a
   subprocess cannot drive the TUI through the launcher headlessly), and any
   future direct `python scripts/demo_tui.py --fixture` caller re-digs the
   hole.
2. **`--debug` injection happens in the launcher, keyed on `--fixture`.**
   Rationale: RED-013's scenario names the launcher as the debugger entry;
   the launcher's name, runbook-030, and COMMANDS.md all document it as the
   debugger. Injecting only when `--fixture` is present keeps
   `--embedded-smoke` a plain all-real TUI (the debug driver is fixture-only
   today) and never trips the `--debug applies only with --fixture`
   validation. Alternative — fix runbook-030 to say `--fixture --debug` —
   rejected: it would leave the launcher's own name and three docs lying.
3. **`main()` delegates to a pure `_build_app(args)` helper.** Rationale: the
   flag-drop bug is untestable while construction is inline in `main()`
   (which also calls `app.run()`); a pure builder gives the regression test a
   real seam, and `main()` keeps only parse + run.
4. **Subprocess probe as the symptom-level regression test.** Rationale: the
   user's symptom exists only outside pytest's path-injected environment; an
   in-process test cannot go red on it. The probe spawns a fresh interpreter
   with `PYTHONPATH` stripped, drives `run_test()`, and asserts `Ready` —
   it fails red today (Fault) and green after the self-enable.

## Risks / Trade-offs

- [Path insertion order perturbs imports] → `sys.path.insert(0, ...)` only in
  fixture mode, guarded by a `str(...) not in sys.path` check; real modes are
  untouched, and the full deterministic gate proves no import-order fallout.
- [Launcher injection surprises someone wanting the plain fixture TUI] → the
  plain route keeps its documented entry `make demo-tui-fixture`; the
  launcher's help text now states the debugger semantics explicitly.
- [Entry tests were asserting forwarding syntax, not startup] → this change
  adds the startup probe; the syntax tests stay as cheap tripwires.
