## Context

See proposal.md for the motivation. Every demo adapter renders phase progress by
iterating the shared returned trace delta and indexing `PHASE_META` in
`scripts/_demo_core.py` with each entry (`scripts/demo_real.py::_trace_lines`,
`scripts/demo_tui.py::_pipeline_tracker`, and the full-fake and fixture-graph
renderers). `PHASE_META` currently maps only the eleven logical phases. The closed
`RunTraceEntry` union (`domain/run_experience.py`) is `LogicalPhaseName | "hitl1_auto_profile"
| "hitl2_auto_proceed"`. The Stage 1 non-interactive policy change added the two
presentation-only trace steps, so any returned trace that includes them raises
`KeyError` during rendering.

## Goals / Non-Goals

**Goals:**

- Let every demo adapter render a returned trace that includes the presentation-only
  `hitl1_auto_profile` / `hitl2_auto_proceed` steps without a `KeyError` crash.
- Keep the real CLI from swallowing the render crash into the misleading
  `本地演示无法启动` message, so the returned lifecycle result is visible.
- Keep `PHASE_META` the single authoritative shared display map and add a
  deterministic gate contract that it covers the complete `RunTraceEntry` set.
- Keep presentation-only trace steps visibly distinct from logical phases in the
  rendered output.

**Non-Goals:**

- Changing graph behavior, non-interactive policy propagation, or the trace content
  the graph writes.
- Adding lifecycle, route, or checkpoint authority to a presentation adapter.
- Changing command grammar, recipe selection, provider prerequisites, or the full-fake
  / fixture-graph contract.

## Decisions

### The shared display map covers the complete RunTraceEntry union

Extend `PHASE_META` in `scripts/_demo_core.py` with the two presentation-only trace
entries, each with a label and a description that names the automatic policy step:

- `"hitl1_auto_profile": ("自动建档", "按自动策略确认研究范围")`
- `"hitl2_auto_proceed": ("自动决策", "按自动策略选择下一步")`

Every renderer (`demo_real._trace_lines`, `demo_tui._pipeline_tracker`, and the
full-fake and fixture-graph trace renderers) reads the same `PHASE_META`, so a single
map extension repairs all adapters without per-renderer fallback logic. Because the
trace-entry union is closed and owned by `domain/run_experience.py`, a unit contract
asserting display-map coverage of every `RunTraceEntry` value keeps the two definitions
synchronized in the deterministic gate.

### Deterministic red evidence first

Before the map extension, add:

1. A unit contract in `tests/unit/test_demo_core.py` that every value of the closed
   `RunTraceEntry` union has a non-empty `PHASE_META` entry. This fails on the current
   code (two missing keys) and passes after the extension.
2. An adapter render contract in `tests/integration/test_demo_run_update_adapters.py`
   that renders a returned `Terminal` whose trace includes `hitl1_auto_profile` (and
   separately `hitl2_auto_proceed`) through both `demo_real.render_run_update` and
   `demo_tui.render_run_update`, asserting no crash and that the presentation-only
   label appears. This fails on the current code with `KeyError` and passes after the
   extension.

### No silent fallback for unknown trace entries

The adapters index `PHASE_META` with a closed `RunTraceEntry`; the fix makes the map
complete for that closed set and adds a gate contract that catches a future trace entry
at test time. The renderers do not silently skip or render a bare step name, because an
uncovered trace entry is a contract violation that should fail the gate, not hide in a
running demo.
