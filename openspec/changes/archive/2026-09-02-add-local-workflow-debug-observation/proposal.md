## Why

The progressive debugger plan (`_backlog/plans/tui-workflow-debugger-progressive-plan.md`,
C0 archived 2026-09-02) leaves observation truth unusable for debugging: journal
bound retention evicts plain node facts, durations are not measured, checkpoint
commits are not aligned with journal outcomes, the initial node-agent invocation
context (rendered runtime MD, initial messages, request, enforced policy, mount
roots) exists only in memory and is unrecoverable after process death, operator
file browsing is duplicated across TUI helpers with ad-hoc path rules, and the
only trace reader is a zero-contract spike (`scripts/experiments/tui_trace.py`)
that opens arbitrary SQLite paths. Without a runtime-owned, versioned, redacted,
live/replay-isomorphic observation surface, C4a driving and C4b presentation
would either guess facts or invent a second authority.

## What Changes

- Add a new `local-workflow-debug-observation` capability owning: the closed,
  versioned `TraceFrame`/`TracePage`/`ActiveVisitProjection` contract with an
  opaque `TraceReadCursor`; the `RunTraceProjector` deep module (verified Bundle
  ref in, paged redacted trace out, live/replay isomorphic, gap/degraded
  disclosure, no graph launch); wrapper-measured `duration_ms` per invocation
  segment; retention priority for finalized node facts inside the existing
  bounded journal; the versioned Bundle-private `NodeContextSnapshot` captured at
  the bridge seam after admission and before `agent.ainvoke`/first provider call,
  with a composition-injected write-only recorder, bounded collection index, and
  typed context inspector views; the local operator-only
  `OperatorWorkspaceReader` bounded read module; and the retirement of the
  read-side spike plus TUI direct path helpers in favor of the typed interfaces.
- This stage does not start, advance, or recover any graph (C4a owns driving) and
  adds no mutation command surface.

## Capabilities

### New Capabilities

- `local-workflow-debug-observation`: LDO-001 trace frame/page contract;
  LDO-002 projector module; LDO-003 explicit invocation duration; LDO-004
  finalized-node retention priority; LDO-005 `NodeContextSnapshot` capture and
  store; LDO-006 context/source inspector; LDO-007 `OperatorWorkspaceReader`;
  LDO-008 typed adapter consumption and spike retirement.

### Modified Capabilities

None. Existing capabilities keep their requirements; `run-event-journal` keeps
its bounded-retention and redaction authority (LDO-004 only adjusts eviction
priority inputs inside the existing bound), `research-demo-tui` keeps its adapter
authority (LDO-008 constrains which interfaces future panes consume; C4b wires
them).

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/` owns projector, snapshot store, recorder protocol, and workspace reader implementation; `domain/` owns the typed contract models; `graph/builder.py` owns segment duration emission; `runtime/node_agent_bridge.py` owns the capture seam call.
- **Seam classification:** wiring plus deterministic-guardrail observation facts; no model-visible behavior change (captured bytes are read-only copies of what the renderer already produced).
- **Question:** how can one runtime-owned observation surface make boundary truth, initial invocation context, and authorized workspace content inspectable — live and replay — without a second lifecycle authority, raw State access, or any graph mutation?
- **Necessary adjacent/external contracts:** `run-event-journal` (journal remains the bounded causal-detail authority; checkpoint remains commit authority), `node-agent-reader-interface` (`workflow.md` stays non-runtime reader projection), `deployment-configuration` (package source stays out of the research sandbox), `research-demo-tui` RED-003 (panes consume, never infer).
- **Evidence seam:** fixture/headless tests through the formal module interfaces — projector over known fixture Bundles (completed/blocked/HITL-suspended), renderer/bridge/provider-spy proof that snapshots commit before the first provider call, filesystem negative tests (path escape, private scope denial), degradation/capacity/privacy sentinels.
- **Not in scope:** DebugRunDriver/control lease/mutation commands (C4a), Textual pane wiring and launcher (C4b), raw provider message history retention, State mutation, cross-run diff, Gateway expansion.
- **Triggered review policies:** authority-and-projections, change-admission, participant-outcomes, local-context, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| What a committed boundary card says | none | checkpoint (commit authority) + journal facts via projector | non-bypassable | started/pre-commit-completed never become frames; uncertain stays uncertain | removes latest-scan and event-only narration guesses | projector fixture tests (replay/live/truth/isolation) |
| What the model actually received at invocation start | none — captured bytes of the already-rendered program | bridge capture seam + Bundle-private snapshot store | non-bypassable | capture failure fails closed before any provider call | ends post-hoc prompt reconstruction and current-source imposture | renderer/bridge/provider-spy tests |
| Which workspace files an operator may list/read | operator chooses paths; policy stays deterministic | composition-injected `OperatorWorkspaceReader` policy | human-decision inputs, deterministic enforcement | host paths, foreign/private scopes, raw checkpoint/State stay denied | retires duplicated TUI path helpers with divergent rules | filesystem negative/positive tests |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Journal evicted/damaged facts | journal + projector quality model | none (bounded retention is by design) | TracePage quality=degraded/unavailable with gap disclosure | inspect what remains; checkpoint boundary identity persists | eviction/degradation fixtures |
| Snapshot capture/store/correlation fails | capture seam fail-closed | none — the invocation must not start | typed pre-provider failure | fix and rerun in a new Bundle | provider-spy zero-call test |
| Capacity exhausted for contexts | snapshot store bound | typed `context_capacity_exhausted` before first provider call | old snapshots retained, new invocation refused | raise bound via config owner; rerun | capacity fixture |
| Path escape / private scope request | workspace reader policy | typed restricted/unavailable denial | no content returned, no host path leaked | navigate allowed roots only | filesystem negative tests |

## Impact

- Apply will add runtime/domain modules and their tests, touch
  `graph/builder.py` (duration emission), `runtime/node_agent_bridge.py`
  (recorder injection point), register LDO-001..LDO-008 in the requirement
  registry, create `openspec/specs/local-workflow-debug-observation/spec.md` at
  sync, and retire `scripts/experiments/tui_trace.py`.
- No graph topology, route, public Gateway surface, or `deerflow/` change; no
  runtime behavior change outside observation (snapshot capture failure fails a
  debug invocation closed before any provider call — a new, explicitly typed
  local-debugger-only admission behavior).
