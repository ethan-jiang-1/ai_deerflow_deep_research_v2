## 1. Admission And Red Evidence

- [x] 1.1 Plan-review: the current apply owner reviews the `control-placement` rows
  against `_demo_core.py`, `tool.py`, and the entry adapters before coding; correct
  the proposal/design if the runtime factory would give presentation a recipe,
  checkpoint, or executor selection authority. Done when the review names the fixed
  composition owner and the focused red test seam.
- [x] 1.2 Add focused red tests in `tests/unit/test_demo_core.py` for fixed
  all-real/fixture-graph runtime selection, concrete executor construction, executor
  injection through `DemoLifecycleTransport`, selected-mode projection from the
  graph-backed Bundle, and rejection of graph-backed dispatch into the full-fake
  fallback.
- [x] 1.3 Add red real CLI and default TUI entry-adapter tests proving both consume
  the shared all-real runtime binding, fail boundedly when it cannot be created, and
  cannot report full-fake completion; retain a before/after regression for the
  full-fake CLI/TUI routes.
- [x] 1.4 Add a red child-process contract for `make demo-fixture-graph`, its
  `--help` wording, and README position. Prove it is graph-composition verification
  while `make demo` and `make demo-scripted` retain their current deterministic
  full-fake command contract.
- [x] 1.5 Add a red deterministic fixture-graph lifecycle test in
  `tests/integration/test_demo_fixture_graph.py`. It must exercise the production
  demo transport and concrete fixture recipe/executor, then require Bundle checkpoint,
  `implementation_mode=fixture`, returned trace including final delivery, and the
  fixture final-delivery gate's completed terminal fact before accepting completion.
  The test SHALL NOT require fixture report publication or widen fixture capabilities.
  Reproject/status the same Bundle to prove the selected mode is durable. Do not
  replace all-real model or web adapters in this test.

## 2. Restore Runtime Composition

- [x] 2.1 Implement the internal `build_demo_runtime(mode, adapter)` boundary in
  `scripts/_demo_core.py` for the two fixed graph-backed modes. It selects the
  existing all-real or fixture recipe, creates its `BundleGraphExecutor`, and exposes
  no caller-controlled recipe/checkpoint/executor selection.
- [x] 2.2 Bind graph-backed `DemoLifecycleTransport` only to the owned executor and
  forward it through the trusted `run_deep_research()` injection seam. Keep the
  generic probe host at its true `infra_probe` use and prevent graph-backed dispatch
  without an executor from reaching the full-fake compatibility path. Persist the
  selected recipe's implementation mode at Bundle creation and project that Bundle
  fact on later lifecycle results; keep legacy/non-graph state at its existing default.
- [x] 2.3 Switch `demo_real.py` and default `demo_tui.py` startup to the shared
  all-real runtime binding after their existing readiness checks. Preserve their
  current typed outcome projection, script/no-stdin behavior, and absence of new
  route-control flags.
- [x] 2.4 Add the dedicated fixture-graph verification entry and
  `make demo-fixture-graph`; enable `src_fake` only in that target's child process.
  Keep the old `make demo`, `make demo-scripted`, and `make demo-tui-fake` behavior
  and command names unchanged.
- [x] 2.5 Update the new entry `--help`, concise README command map, and scripted
  real smoke question so command positioning and bounded comparison/report claims
  match the verified composition.

## 3. Verification And Closeout

- [x] 3.1 Run focused demo-core, real CLI/TUI, full-fake, and fixture-graph process
  tests with the required Harness extras. Update only the relevant requirement
  evidence assets if the changed executable evidence requires it.
- [x] 3.2 Run the fixture-graph lifecycle test and, only after it passes, run a
  bounded credentialed all-real demo canary when local credentials are intentionally
  available. Record a skipped/unavailable canary truthfully; it never substitutes for
  deterministic fixture-graph composition evidence.
- [x] 3.3 Run `openspec validate restore-demo-graph-composition --strict`, applicable
  governance/requirement-evidence checks, `cd deep_research_harness && UV_OFFLINE=1
  make verify`, `git diff HEAD --check`, and record `git status --porcelain=v1
  --untracked-files=all`; confirm `deerflow/`, `backend/`, and `frontend/` remain
  clean.
- [x] 3.4 Archive-closeout-review: the current archive owner rechecks the
  `control-placement` review against the landed runtime boundary and focused evidence.
  Correct any drift before sync/archive. Done when the deterministic executor-handoff,
  full-fake-fallback rejection, and full-fake compatibility evidence are linked from
  the archived change and backlog plan.
- [x] 3.5 Sync accepted delta specs to main specs, archive this change, and update
  `_backlog/plans/cli-tui-entry-integrity-repair_plan.md` with the commands, evidence,
  archive path, and next uncompleted stage.
