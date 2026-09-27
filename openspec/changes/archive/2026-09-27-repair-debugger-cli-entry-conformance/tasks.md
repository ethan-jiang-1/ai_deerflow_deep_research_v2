# Tasks

## 1. Red-first regression tests

- [x] 1.1 Add a subprocess probe test (in `tests/integration/test_debugger_entry.py`) that spawns a fresh interpreter with `PYTHONPATH` stripped from the environment, drives `DeepResearchDemoTUI(mode="fixture")` via `run_test()`, and asserts the app reaches `Ready` within a bounded wait. Verify: run `cd deep_research_harness && .venv/bin/python -m pytest tests/integration/test_debugger_entry.py -q` and watch the new probe fail red with the user's exact fault ("The local presentation adapter could not continue."). ✓ Red: probe reached Fault with that exact message; launcher-text contract also red
- [x] 1.2 Add an app-construction test asserting the parsed CLI reaches the app: `--fixture --debug` must yield `debug_mode=True` (via the `_build_app(args)` helper), `--fixture` alone must yield `debug_mode=False`. Verify: the test fails red while `_build_app` does not exist / does not wire the flag. ✓ Red: AttributeError on the missing `_build_app`

## 2. Entry-chain repair

- [x] 2.1 In `scripts/demo_tui.py`, extract `main()`'s construction into `_build_app(args) -> DeepResearchDemoTUI` passing `debug_mode=args.debug`, and make `main()` parse + build + run. Verify: task 1.2's test turns green; `--help` output unchanged. ✓ Green; also fixed a latent missing `import sys` surfaced by the self-enable helper
- [x] 2.2 In `scripts/demo_tui.py`, self-enable the harness `src_fixtures` root (guarded, insert-once) when `mode == "fixture"` before the fixture composition load, leaving gateway/embedded modes untouched. Verify: task 1.1's probe turns green; the full deterministic gate stays green (no import-order fallout). ✓ Probe green; differential loop now Ready in both environments
- [x] 2.3 In `run/tui-workflow-debugger.sh`, export `PYTHONPATH` including `$HARNESS_ROOT/src_fixtures` before exec (matching the Makefile demo-target contract) and inject `--debug` when `--fixture` is present (not duplicating a user-supplied `--debug`). Verify: a launcher-text contract test asserts both behaviors; `./run/tui-workflow-debugger.sh --help` still exits 0. ✓ Contract test green; bash -n clean; launcher --fixture --help exit 0

## 3. Honest docs

- [x] 3.1 Update the launcher help text: `--fixture` starts the debugger workbench over the zero-credential fixture graph; `--embedded-smoke` starts the plain all-real TUI (the debug driver is fixture-only today). Verify: the launcher `--help` exit-0 entry tests still pass and assert the updated wording. ✓ Help rewritten; entry tests green
- [x] 3.2 Add a status note to `docs/runbooks/runbook-031-debugger-embedded.md`: the embedded debug workbench is deferred (B1, `_done/_suspended_plans/deferred-stage-b1-embedded-real-run.md`); today `--embedded-smoke` is the plain all-real TUI without step/continue. Verify: doc-layer hygiene passes from the repo root. ✓ Note added; hygiene re-run in task 4.1

## 4. Gates

- [x] 4.1 From the repository root, run `python3 openspec/governance/check_project_gate.py --phase closeout`; from `deep_research_harness/`, independently run `UV_OFFLINE=1 make verify`; then, from the repository root, run `openspec validate repair-debugger-cli-entry-conformance --strict` and `git diff HEAD --check`. Measure every exit code directly (no `| tail` pipelines). Record `git status --porcelain=v1 --untracked-files=all`, `git ls-files --stage deerflow`, `git submodule status -- deerflow`, and `git -C deerflow status --porcelain=v1 --untracked-files=all`, and review `git diff --submodule=short`. Also confirm generation alignment: `openspec --version` equals the `generatedBy` frontmatter in `.agents/skills/*/SKILL.md` (read-only check; `.agents/skills/` is a user-reserved area). Verify: every measured exit code is 0. ✓ All direct exits 0: closeout six checkers, strict validate, diff check, version 1.13.1 aligned, gitlink ceebf97f unchanged, submodule clean; `UV_OFFLINE=1 make verify` exit 0

## Deferred remainder (not a blocking task)

- `--attach <id>` / `--replay <id>` intents are stored on the app but never
  consumed, and RED-014's Attach/Replay entries are not built — filed as
  BUG-069; runbook-030 §6 flows through the launcher remain unavailable until
  that lands. New Run / Start Step / answer / `/context` / `/detach` (the
  runbook-030 core loop) work after this change.
