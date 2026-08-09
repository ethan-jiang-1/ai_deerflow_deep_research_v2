## Why

Every real CLI/TUI demo run that exercises the graph-owned non-interactive policy now
crashes during result presentation. The Stage 1 policy work extended the shared
`RunTraceEntry` union with presentation-only trace steps `hitl1_auto_profile` and
`hitl2_auto_proceed` (`domain/run_experience.py`). The standalone demo adapters render
phase progress by indexing the shared `PHASE_META` display map with each returned trace
entry; that map still contains only the eleven logical phases, so a returned trace that
includes a presentation-only step raises `KeyError: 'hitl1_auto_profile'`. The broad
`except Exception` in the real CLI turns that render crash into the misleading
`本地演示无法启动` message, so the operator cannot see the actual returned lifecycle
result at all.

The crash is guaranteed for scripted real runs (auto-profile always writes the trace
step), reproducible in the real TUI tracker, and latent in the full-fake and
fixture-graph renderers because they share the same display map.

## What Changes

- Extend the shared `PHASE_META` display map in `scripts/_demo_core.py` so it covers
  every value of the closed `RunTraceEntry` union, including `hitl1_auto_profile` and
  `hitl2_auto_proceed`, with safe display labels and descriptions.
- Add a deterministic unit contract asserting the shared display map covers the
  complete `RunTraceEntry` set, so a future trace entry is caught by the test gate
  rather than by a runtime render crash.
- Add deterministic adapter render evidence that the real CLI and TUI presentation
  adapters render a returned trace containing the presentation-only steps without
  crashing and without inventing a logical phase.
- No change to graph behavior, policy propagation, trace content, command grammar,
  recipe selection, or lifecycle authority.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `demo-pipeline`: Extend the shared-progress-display requirement (`DPL-002`) to
  require adapters to render every entry of the complete shared `RunTraceEntry` set
  from the shared display map, covering presentation-only trace steps, without
  crashing or inventing a phase.

## Impact

- Primary module: `deep_research_harness/scripts/_demo_core.py` shared `PHASE_META`
  display map, consumed by `scripts/demo_real.py`, `scripts/demo_tui.py`,
  `scripts/demo.py`, and `scripts/demo_fixture_graph.py`.
- Adjacent contracts: `deep_research_harness/src/deerflow_deep_research/domain/run_experience.py`
  owns the `RunTraceEntry` closed union that the display map must cover; the shared
  `tests/fixtures/run_updates.py` run-update fixtures drive the adapter render
  evidence.
- Deterministic evidence: unit contract in `tests/unit/test_demo_core.py` asserting
  display-map coverage of the complete trace-entry set, and adapter render tests in
  `tests/integration/test_demo_run_update_adapters.py`.
- No package behavior, graph route, profile, provider, public tool, DeerFlow
  framework, `backend/`, or `frontend/` behavior changes.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/_demo_core.py`
  shared `PHASE_META` display map, which every demo adapter indexes with returned
  trace entries.
- **Question:** How can every demo adapter render the complete shared `RunTraceEntry`
  set, including presentation-only trace steps `hitl1_auto_profile` and
  `hitl2_auto_proceed`, without a `KeyError` crash and without presenting a
  presentation-only step as a logical phase?
- **Necessary adjacent/external contracts:** `domain/run_experience.RunTraceEntry`
  defines the closed trace-entry union; `demo-pipeline` `DPL-002` requires phase
  progress to come only from the shared returned trace delta and shared display
  labels; `tests/fixtures/run_updates.py` supplies the shared `RunUpdate` fixtures.
- **Evidence seam:** deterministic unit and adapter render contracts verify that the
  shared display map covers the complete `RunTraceEntry` set and that the real CLI
  and TUI adapters render a returned trace containing the presentation-only steps
  without crashing.
- **Not in scope:** changing graph behavior, non-interactive policy propagation, the
  trace content written by the graph, command grammar, recipe selection, provider
  prerequisites, or adding lifecycle authority.
- **Triggered review policies:** participant-outcomes
