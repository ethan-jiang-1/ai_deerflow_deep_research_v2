## 1. Admission And Red Evidence

- [x] 1.1 Plan-review: the current apply owner rechecks the `control-placement` rows
  against `demo_sessions.py`, `RunObservationStore.inspect()`, and the renderer before
  editing. Confirm the parser admits only a read-only target and the store remains the
  sole owner of availability; correct the proposal/design if either would gain
  lifecycle authority.
- [x] 1.2 Add focused red parser/read-only tests in `tests/integration/test_demo_sessions.py`
  for required `inspect <bundle-id>` input, rejection of the retired one-argument
  form, zero/nonzero projection of typed available/unavailable observations, and an
  inspect-only store spy that rejects any broader command dispatch. Add a focused
  `tests/contract/test_demo_commands.py` assertion that README and local operations
  publish only the canonical command and no retired spelling.
- [x] 1.3 Add a red Harness-root subprocess contract that publishes one test-owned
  retained observation, invokes the exact renderer command through `make demo-sessions`,
  and proves the current argparse failure before an available observation can render.
  Its `finally` cleanup removes only the published store-derived record, never the
  diagnostic root or a hand-reconstructed storage key. Retarget the existing
  `standalone-inspection-command-execution` evidence claim to this process test;
  retain/add distinct direct-projection and documentation claims plus only their
  matching `requirement_evidence.py` impacts, so every changed selector is collected
  at its matching seam without altering unrelated registry entries.

## 2. Restore One Command Contract

- [x] 2.1 Implement exactly one required `inspect` subcommand in
  `scripts/demo_sessions.py`. Preserve its bounded help and direct
  `RunObservationStore.inspect()` call; reject aliases, arbitrary roots/paths, session
  references, and all lifecycle controls.
- [x] 2.2 Make available inspection return safe facts and zero, while invalid, missing,
  unavailable, and corrupt observations return only their existing safe bounded text
  and nonzero disposition. Expand the Harness-root subprocess contract to prove those
  post-repair dispositions through the canonical command. Keep fixture setup/cleanup
  limited to its unique store-derived retained record.
- [x] 2.3 Align README, `docs/local-operations.md`, and relevant command help with
  `make demo-sessions DEMO_ARGS="inspect <bundle-id>"`; remove the retired spelling
  without changing renderer output or claiming resume/retry.

## 3. Verification And Closeout

- [x] 3.1 Run `UV_OFFLINE=1 uv run --extra operations python -m pytest
  tests/integration/test_demo_sessions.py tests/contract/test_demo_commands.py`, then
  `UV_OFFLINE=1 uv run --extra operations python scripts/check_test_assets.py` from
  `deep_research_harness/`. Confirm the process command begins from the Harness root,
  while focused dispatch evidence proves it has no graph/provider/lifecycle path.
- [x] 3.2 Run `openspec validate repair-rendered-inspection-command --strict`,
  applicable requirement-evidence checks, `cd deep_research_harness && UV_OFFLINE=1
  make verify`, `git diff HEAD --check`, and record `git status --porcelain=v1
  --untracked-files=all`; confirm `deerflow/`, `backend/`, and `frontend/` remain clean.
- [x] 3.3 Archive-closeout-review: the current archive owner rechecks the
  `control-placement` review against the landed parser and subprocess evidence. Correct
  any drift, then archive this `skip_specs` change and update
  `_backlog/plans/cli-tui-entry-integrity-repair_plan.md` with commands, evidence,
  archive path, and Stage 4 as the next uncompleted stage.
