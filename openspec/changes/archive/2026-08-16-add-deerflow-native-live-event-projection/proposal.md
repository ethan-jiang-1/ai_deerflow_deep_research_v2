## Why

The archived runtime-observability change already emits safe standard logs, but the
current Deep Research runtime also needs the same material facts available immediately
through DeerFlow's injected live stream. The installed and already validated DeerFlow
pin exposes a public `ToolRuntime.stream_writer`, so this change must use that current
surface without upgrading DeerFlow or changing package resolution.

## What Changes

- Keep the existing DeerFlow pin
  `66b9e7f21212490cf92fafac137542b9deb06615`, root gitlink, registry lock,
  package metadata, and `uv.lock` unchanged.
- Add a downstream public contract for the current injected
  `ToolRuntime.stream_writer` call shape and the existing
  `get_current_trace_id()` compatibility surface, using imports and signatures only
  and never inspecting DeerFlow source or package paths.
- Capture the callable writer only at trusted runtime adaptation and reduce it
  immediately to an opaque project-owned sink. Only that sink may call the public
  writer; graph/domain owners receive only the existing non-checkpointed observation
  projection.
- Extend the validated safe-observation boundary with one closed live-visible
  operation/outcome predicate. Accepted facts retain their standard log and attempt
  one independent payload with exact discriminator
  `"type": "deep_research.progress.v1"`.
- Keep live projection separate from Bundle Journal, State, checkpoints, lifecycle,
  route, retry, recovery, and root logging configuration. Missing writers and writer
  failures affect only the live attempt.
- Replace the absolute writer/event source ban with a narrow allowlist for public
  writer capture at runtime adaptation and one direct invocation inside
  `runtime/events.py`; retain all other raw-writer, unsafe-payload, private-store,
  and competing-emitter bans.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `runtime-observability`: adds a safe, independently non-controlling live projection
  alongside the existing standard-log contract.
- `runtime-integration`: permits trusted runtime adaptation to reduce the current
  public injected writer to an opaque observation sink without expanding authority.

## Impact

- `deep_research_harness/src/deerflow_deep_research/runtime/events.py`,
  `runtime/runtime_adapter.py`, the trusted non-checkpointed observation projection
  protocols, existing material fact owners, focused tests, and source guards.
- One current-runtime payload contract, `deep_research.progress.v1`, emitted only
  when a callable writer is injected.
- No DeerFlow source browsing or modification, gitlink change, dependency upgrade,
  package metadata change, `uv.lock` change, private Gateway access, Journal event,
  State field, compatibility helper, or logging reconfiguration.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/events.py`; it owns validation of the closed safe observation and its independent standard-log/live projections, while runtime adaptation owns only capture of the current public writer.
- **Seam classification:** deterministic-guardrail because a fixed-pin public contract, one writer capture/invocation path, closed payload schema, and failure-isolation evidence prevent live output from changing execution.
- **Question:** Can the current validated DeerFlow pin project the closed graph/gate/work/validation fact set through its public injected writer while standard logs, Bundle Journal, State, routing, retry, recovery, and lifecycle truth retain their existing owners?
- **Necessary adjacent/external contracts:** `runtime-observability` owns the safe payload and live-visible predicate; `runtime-integration` owns trusted writer capture and outer correlation; `run-event-journal` `REJ-005` forbids Journal-adjacent transport authority; `project-structure` `PRS-018` proves the DeerFlow pin remains unchanged; the public injected `langchain.tools.ToolRuntime.stream_writer` and `deerflow.trace_context.get_current_trace_id` are the only external interfaces.
- **Evidence seam:** current-pin public signature contract; direct safe-observation validator and recording-writer tests; focused owner-duplication, missing-writer, writer-failure, cancellation, no-side-effect, and source guards; full offline application verification.
- **Not in scope:** DeerFlow upgrade/source inspection/modification, package or lockfile changes, private Gateway stores, Bundle Journal schema/persistence, State/checkpoint changes, lifecycle/retry/route changes, root logging configuration, file logging, or presentation rendering.
- **Triggered review policies:** authority-and-projections, workflow-outcome-review, change-admission

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Current runtime supplies no callable writer | Trusted runtime adaptation owns capability capture only | Keep the existing log projection and create no live sink | Originating typed result remains unchanged | Continue the current Run through its existing route | Missing-writer runtime-adapter and projection tests |
| Writer rejects a validated live payload | Event projection owns only the one live attempt | Suppress the writer failure after one bounded log-only `live_event/degraded` observation; no retry or fallback | Existing typed result, Journal, State, route, and lifecycle result remain unchanged | Follow the originating typed result's legal action | Recording/failing-writer and no-side-effect tests |
| Producer supplies unsafe, malformed, duplicate, or caller-forged data | `runtime/events.py` owns payload admission | Reject only the live candidate; do not infer or repair a runtime fact | No new terminal disposition or persisted record | Follow the original fact owner's typed outcome | Allowlist, correlation, redaction, and duplicate-owner tests |
| Logging projection fails while the writer remains available | Standard-log projection owns only its log attempt | Attempt the independent live projection once; add no file or root-handler fallback | Existing typed result and live eligibility remain unchanged | Follow the originating typed result's legal action | Fault-injected logger and recording-writer test |
