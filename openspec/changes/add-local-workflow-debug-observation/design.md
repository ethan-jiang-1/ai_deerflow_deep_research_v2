## Context

Verified 2026-09-02 on this tree: `openspec list` is empty after C0;
`MAX_EVENT_RECORDS = 256` with outcome-blind eviction priorities;
`scripts/experiments/tui_trace.py` still opens arbitrary paths/SQLite;
`make_node_visit_id` reuses visit ids after HITL resume;
`BudgetMiddleware.model_calls`/`ToolPolicyMiddleware.tool_calls` exist in memory
only; `runtime/node_agent_bridge.py` renders
`render_node_cognitive_control_program` then calls `agent.ainvoke` with no
durable capture between admission and the first provider call.

## Goals / Non-Goals

**Goals:** one runtime-owned observation surface (projector, snapshot store,
inspector, workspace reader) that is versioned, redacted, paged, and
live/replay-isomorphic; required capture for local debugger compositions; spike
and helper retirement. **Non-Goals:** driving/lease (C4a), Textual pane wiring
beyond typed consumption constraints (C4b), raw provider history retention,
cross-run diff, Gateway surface.

## Decisions

### D1. Contract models in domain, I/O in runtime; one new capability spec

`TraceFrame`/`TracePage`/`ActiveVisitProjection`/`TraceReadCursor`,
`NodeContextSnapshot`/`NodeContextPage`/`NodeContextView`/`NodeSourceView`,
`WorkspacePage`/`FilePreview`, and denial types are domain contract models;
`RunTraceProjector`, the snapshot store, context inspector, source reader, and
`OperatorWorkspaceReader` are runtime implementations. Requirement IDs
LDO-001..008 live in the new `local-workflow-debug-observation` capability.
Alternative: spreading requirements across `run-event-journal` and
`research-demo-tui` was rejected — the observation surface is one cross-boundary
contract, and the journal/adapter capabilities must not grow debugger semantics.

### D2. Checkpoint is commit authority; the cursor is opaque and dual

Frames are born only from checkpoint identity (committed/suspended) or a
determined failure event sequence. `TraceReadCursor` internally carries
(checkpoint position/identity, journal high watermark, schema version) and is
opaque to adapters — a single `after_sequence` cannot see "journal write failed
but checkpoint committed". `ActiveVisitProjection(running|committing|uncertain)`
covers started-without-outcome and pre-commit completed facts; the mapping rules
are the projector's hidden implementation.

### D3. Duration is emitted by the wrapper per segment

`_node_wrapper` starts a monotonic timer per invocation attempt and emits
`duration_ms` on the finalized outcome event (completed/suspended/failed),
including the GraphInterrupt path. HITL multi-segment visits accumulate per
segment; pause/human wait is structurally outside the timed region. Retention:
eviction priority for finalized node outcome events raised above plain
start/model-tool success (admission/terminal/validation/failure anchors
unchanged); no bound change.

### D4. Capture seam inside `_run_agent`, recorder injected by composition

The snapshot is taken immediately after
`render_node_cognitive_control_program` and policy/tool/model admission resolve
and before agent construction/`ainvoke`. `RuntimeNodeAgentBridge` receives an
optional `NodeContextRecorderProtocol` (write-only, pre-bound to the exact
Bundle) via composition; bridge supplies typed snapshot candidates plus explicit
parent visit/segment correlation from `NodeAgentContext`. Failure, conflict, or
capacity exhaustion raises a typed local-debug failure before agent construction
(provider spy proves zero calls). Production/Gateway compositions inject no
recorder — behavior identical to today. The store owns containment, layout,
atomic publication, idempotency/conflict, bounds, and the durable
segment→invocations collection index; Journal/TraceFrame carry only opaque refs
and counts.

### D5. Redaction boundary stays closed

Frames and pages expose closed fields only; content access flows through
whitelists or existing authorized refs. The snapshot stores already-rendered
prompt bytes as Bundle-private sensitive content (same retention/deletion as the
Bundle), never credentials, host identity, chain-of-thought, raw State, or
provider histories. `OperatorWorkspaceReader` reuses the existing sandbox mount
projection; host paths never cross the interface.

### D6. Spike and helper retirement is part of the contract

`scripts/experiments/tui_trace.py` is deleted and replaced by formal interface
tests (per LDO-008); TUI direct path helpers are replaced by the reader in
C4b wiring — this change delivers the reader and its tests, and only removes
the spike now (no Textual behavior change in C3).

## Risks / Trade-offs

- **[Risk] Fail-closed capture could block runs if the recorder misbehaves.** ->
  Only local debugger compositions inject a recorder; production compositions
  are unchanged; fixture/embedded prove the happy path plus typed failure.
- **[Risk] Projector complexity leaks into adapters.** -> Adapters see only
  versioned pages/cursors; ordering/merging/quality rules are implementation.
- **[Risk] Retention priority reshuffles eviction under pressure.** -> Anchors
  keep existing protection; capacity fixtures assert the disclosed outcome.

## Migration Plan

1. Red: interface tests for projector/snapshot/reader against a non-existent
   module surface fail deterministically.
2. Land domain contracts, runtime implementations, wrapper duration, capture
   seam, retention priority.
3. Green: focused fixtures (§6.2 matrix), full gate; sync creates the new main
   spec; archive; C4a gate unblocked.
