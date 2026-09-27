# Proposal

## Why

The documented debugger entry (`./run/tui-workflow-debugger.sh --fixture`) has
never started the debugger workbench from a shell. The C4b change
(`2026-09-02-connect-tui-workflow-debugger`) was applied partially: the in-app
debug wiring (start/advance/context/detach) landed and its Pilot tests pass by
constructing the app with `debug_mode=True` directly, while the CLI chain is
broken in three places — the launcher does not enable `src_fixtures` for its
child (fixture-graph import fails and the TUI swallows the error into a
generic presentation fault), `main()` parses and validates `--debug` but never
passes it to the app, and the launcher never injects `--debug`. An operator
following runbook-030 today hits "The local presentation adapter could not
continue." with a swallowed cause.

## What Changes

- The launcher enables `src_fixtures` for its child process (same contract the
  Makefile demo targets already honor) and injects `--debug` when `--fixture`
  is present, so the launcher's fixture entry starts the debugger workbench as
  RED-013's scenario requires.
- `demo_tui.py` `main()` passes `debug_mode=args.debug` to the app (completing
  the C4b CLI wiring); argument-to-app construction is extracted into a
  testable `_build_app(args)` helper.
- `demo_tui.py` fixture mode self-enables the harness `src_fixtures` root
  before loading the fixture composition, so the entry cannot fail on a
  caller-side path contract again; real modes (gateway/embedded) never insert
  the path, preserving the "real paths do not discover fixture source" intent.
- Regression coverage: a subprocess probe asserts the fixture workbench
  reaches Ready in a PYTHONPATH-stripped environment (the exact user
  symptom), an app-construction test asserts `--debug` reaches
  `debug_mode=True`, and launcher-text contracts pin the env export and the
  `--debug` injection.
- Honest docs: the launcher help distinguishes the debugger workbench entry
  from the plain TUI compositions, and runbook-031 gains a status note that
  the embedded debug workbench is deferred (B1), since the debug driver is
  fixture-only today.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. This change repairs implementation conformance with the existing
  `research-demo-tui` `RED-013` requirement ("Explicit intents reach the
  validated workbench") and its launcher contract; no requirement text
  changes.

## Impact

- Primary implementation: `deep_research_harness/run/tui-workflow-debugger.sh`,
  `deep_research_harness/scripts/demo_tui.py`.
- Tests: `deep_research_harness/tests/integration/test_debugger_entry.py`,
  `deep_research_harness/tests/integration/test_demo_tui.py`.
- Docs: launcher help text, `docs/runbooks/runbook-031-debugger-embedded.md`.
- Ordinary downstream work neither modifies nor source-browses the
  `deerflow/` gitlink; this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/demo_tui.py`,
  which owns the CLI-to-app wiring (`main()`/`_build_app`) and the fixture
  composition load; the launcher is the presentation-only forwarder whose env
  and flag forwarding RED-013 owns.
- **Seam classification:** wiring — the debug driver, adapter, lifecycle, and
  workbench behaviors are unchanged; only the entry chain (env enablement,
  flag plumbing) that connects an operator's shell command to the already
  tested workbench is repaired.
- **Question:** How can `./run/tui-workflow-debugger.sh --fixture` start the
  already-tested debugger workbench exactly as RED-013's scenario promises,
  without widening any lifecycle, admission, or tool authority?
- **Necessary adjacent/external contracts:** the Makefile demo targets answer
  the existing `PYTHONPATH=src_fixtures` caller contract; `_demo_core.build_fixture_demo_recipe`
  answers the local-import rule that keeps fixture source undiscovered by real
  paths; `research-demo-tui` `RED-013` owns the launcher entry scenario this
  change restores; the deferred B1 record (`_suspended_plans/deferred-stage-b1-embedded-real-run.md`)
  answers why embedded debug is not part of this repair.
- **Evidence seam:** a subprocess probe drives the real entry chain in a
  PYTHONPATH-stripped environment and asserts the workbench reaches `Ready`;
  app-construction tests assert `--debug` reaches `debug_mode`; launcher-text
  contracts pin env export and `--debug` injection; all existing Pilot
  journeys and the full deterministic gate stay green.
- **Not in scope:** attach/replay intent consumption and the RED-014 three-entry
  screen remainder (filed separately as BUG-069), embedded debug (deferred B1),
  production budgets, spec deltas, `LIVE_CANARIES`, and anything under
  `deerflow/`.
- **Triggered review policies:** none: entry-chain conformance repair with no candidate, human judgment, control fact, admission/recovery boundary, node-agent role, or lifecycle output change.
