## 1. Admission And Red Evidence

- [x] 1.1 Confirm the closed `RunTraceEntry` union in
  `deep_research_harness/src/deerflow_deep_research/domain/run_experience.py` is the
  sole authority for the trace-entry set the demo adapters render, and that every
  renderer indexes the shared `PHASE_META` map from `scripts/_demo_core.py` rather
  than owning per-phase display data. Done when the focused review names `PHASE_META`
  as the single display-map owner and confirms no renderer has a second phase table.
  Review conclusion: `PHASE_META` in `scripts/_demo_core.py` is the only phase display
  map; `demo_real._trace_lines`, `demo_tui._pipeline_tracker`, `demo.py`, and
  `demo_fixture_graph.py` all index it with returned trace entries, and the closed
  `RunTraceEntry` union (`LogicalPhaseName | "hitl1_auto_profile" |
  "hitl2_auto_proceed"`) is the single authority for the trace-entry set.
- [x] 1.2 Add red deterministic evidence before changing `PHASE_META`:
  - a unit contract in `tests/unit/test_demo_core.py` asserting every `RunTraceEntry`
    value has a non-empty `PHASE_META` label/description;
  - adapter render cases in `tests/integration/test_demo_run_update_adapters.py`
    rendering a returned `Terminal` whose trace delta includes `hitl1_auto_profile`
    (and separately `hitl2_auto_proceed`) through both `demo_real.render_run_update`
    and `demo_tui._pipeline_tracker`, asserting no crash and an automatic-policy label.
  Run the focused selection and record the expected failures before changing
  `_demo_core.py`.
  Red baseline: 3 expected failures before the fix --
  `test_phase_meta_covers_all_run_trace_entries` (PHASE_META lacks the two entries),
  `test_standalone_adapters_render_shared_run_updates_without_lifecycle_wire[terminal-auto-profile]`
  (`KeyError: 'hitl1_auto_profile'`), and
  `test_tui_pipeline_tracker_renders_presentation_only_trace_steps`
  (`KeyError: 'hitl1_auto_profile'`).

## 2. Implement The Shared Display Map Extension

- [x] 2.1 Extend `PHASE_META` in `scripts/_demo_core.py` with
  `hitl1_auto_profile` and `hitl2_auto_proceed`, each mapping to a non-empty label and
  description that names the automatic-policy step, without changing any logical-phase
  entry.
- [x] 2.2 Run the focused unit and adapter render tests; the previously failing cases
  pass and no existing render contract changes. Evidence: `tests/unit/test_demo_core.py`
  + `tests/integration/test_demo_run_update_adapters.py` = 54 passed; demo command /
  real / tui / sessions suites = 50 passed.

## 3. Verification And Closeout

- [x] 3.1 Run the focused command/render suites and the deterministic project gate
  (`UV_OFFLINE=1 make verify`), `openspec validate repair-cli-tui-trace-rendering
  --strict`, `openspec validate --specs`, and `git diff HEAD --check`.
  Evidence: `UV_OFFLINE=1 make verify` passed (governance/lock/lint/assets/reqs all
  green; fast=2395, integration=234 + 4 expected skips, workflow=35),
  `openspec validate repair-cli-tui-trace-rendering --strict` passed,
  `openspec validate --specs` = 48/48 passed, `git diff HEAD --check` clean.
  `Triggered review policies: participant-outcomes` recorded on the Focus Card and
  charter governance passes.
- [x] 3.2 Sync the `demo-pipeline` main spec, archive the change to
  `openspec/changes/archive/`, and record evidence here.
  Evidence: `openspec archive repair-cli-tui-trace-rendering -y` applied the
  `demo-pipeline` delta (1 modified requirement) and archived the change as
  `2026-08-09-repair-cli-tui-trace-rendering`. Main spec `demo-pipeline` now requires
  the shared display map to cover the complete closed `RunTraceEntry` set, including
  presentation-only trace steps, with a rendering scenario.
