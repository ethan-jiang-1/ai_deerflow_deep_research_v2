## Context

See [proposal.md](proposal.md) for the motivation. Current code has a typed retained
event model and shared producers, but it publishes the observation outside the Run
Bundle and only after graph dispatch returns. Graph, work-unit, and node-agent events
produced during that dispatch therefore have no durable journal to receive them. The
current event shape also cannot distinguish refinement generations, collapses some
validation facts, and can silently lose event history at its bounded limit.

The existing Bundle lifecycle remains the sole owner of Run existence, legal actions,
and terminal State. Terminal incidents own terminal classifications; validators and
phase/work controllers own their classified facts and recovery bounds. The Journal is a
Bundle-local observation and must never substitute for any of those owners.

## Goals / Non-Goals

**Goals:**

- Give every admitted Run one dependable observation route before its first producer
  executes, inside that Run's Bundle.
- Make material execution facts correlated, redacted, bounded, and explainable across
  all shared execution paths.
- Make loss of observability visible without allowing observability to change research
  execution.
- Provide one small producer interface and one read-only inspection surface rather than
  each node inventing log payloads or storage behavior.
- Use DeerFlow's public runtime context and `custom` stream writer as ingress and live
  projection boundaries without treating either as retained evidence.

**Non-Goals:**

- This is not a raw application-log, distributed-tracing, or telemetry platform.
- It does not make an event stream a checkpoint, an audit controller, a retry queue, or
  a provider diagnostic substitute.
- It does not add new lifecycle actions, change recovery limits, expose event detail to
  the Primary User by default, or require a DeerFlow source change.
- It does not retain a Journal for a rejected pre-admission request, recreate a lost
  Bundle to save diagnostics, or keep a persistent external Support Handoff.

## Decisions

### 1. Use four separate meanings, not one overloaded "diagnostic log"

| Meaning | Owner | What it can contain | What it cannot do |
| --- | --- | --- | --- |
| Lifecycle fact | Bundle-local typed State and result | legal status, phase, and next action | infer its truth from a Journal |
| Run Event Journal | Bundle-local `diagnostics/` record | redacted observed process fact and correlation | route, retry, alter State, or outlive its Bundle |
| Diagnostic finding / Support Handoff | terminal or inspection projection from owning typed facts and events | bounded explanation and opaque reference while the Bundle is available | create a terminal incident, control action, or external retained record |
| Live Progress Projection | optional DeerFlow `custom` stream subscriber | current safe display update | serve as durable evidence or control authority |

This avoids two existing failure modes: treating a terminal summary as the whole story,
and treating a transient progress sink as durable evidence.

### 2. Make the Event Journal a deep module with one producer seam

Producers will call a small asynchronous recorder interface with a typed event fact.
The journal implementation supplies Run identity, allocates the stable sequence, checks
redaction and bounds, and records journal health. Producers do not receive a retained
path, file handle, lifecycle object, or generic string-detail field.

The typed event distinguishes: admitted execution, lifecycle observation, node start/end
or safe boundary failure, work-attempt allocation/result, model/tool invocation result,
validation result, recovery/retry decision, exhaustion, and terminal observation. A
validation event records its `initial` or `repair` stage and a bounded canonical code
collection, including an empty collection for success, rather than an arbitrary error
string. Existing safe failure classifications remain their current owners; the Journal
copies rather than reclassifies them.

The public test seam is the recorder/reader contract, not a JSONL implementation or a
private graph callback. Before implementation, confirm this seam and the existing
typed Bundle lifecycle result as the two supported test surfaces with the user.

### 3. Establish a contained Journal after admission and before producer execution

The lifecycle adapter creates or opens the Journal only after it has a validated,
preselected `RunBundleRef`, using the Bundle's protected `diagnostics/` subtree. It does
so before handing graph execution a context that can produce events. Later lifecycle
projection updates the same Journal with authoritative outcome facts; it does not create
the Journal retroactively.

This keeps the lifecycle in charge of identity and permissions while giving initial,
resume, and refinement graph paths the same observation facility. A Journal lookup is
never used to find a Bundle or decide whether it can run. A rejected pre-admission
request is not given a ghost Bundle or persistent Journal; an unavailable/deleted Bundle
has no readable Journal and cannot be recreated to record one.

### 4. Capture at shared execution seams, with narrowly owned validation mappings

| Capture seam | Required facts | Deliberately not owned there |
| --- | --- | --- |
| Lifecycle dispatch | admission, dispatch lifecycle observation, journal health | lifecycle transition or retry policy |
| Graph node wrapper | node start/end and safe uncaught boundary failure | node-specific validation semantics |
| Work-unit kernel | work/attempt allocation, submission, validation, retry, exhaustion | semantic interpretation of a candidate |
| Node-agent/provider bridge | invocation start/end and safe classified provider/model/tool result | terminal disposition or recovery decision |
| Deterministic validator | canonical validation code or codes, including initial and repair results | raw validator text or new control authority |

This is the coverage closure. Phase-specific code supplies only the canonical semantic
code that a generic boundary cannot know. The existing discovery-based workflow outcome
inventory becomes the guardrail that prevents a newly added `run_agent` owner from
escaping the shared route.

### 5. Preserve a bounded Journal with stable sequence and diagnostic anchors

The durable adapter may use an atomically published bounded snapshot or a physical
append format; the contract does not require a storage technology. It serializes
concurrent producers and allocates a monotonically increasing Bundle-local sequence
that is never renumbered. Sequence records persistence order only; causal meaning comes
from `generation`, `phase`, `work_id`, and `attempt_id`.

Capacity pressure preserves the admission anchor and terminal, health, validation
failure, provider/boundary failure, retry, and exhaustion facts before ordinary start or
success events. Retained tails keep their original sequence values; an explicit dropped
count or interval and `incomplete` health make a missing middle visible. Corruption or
write failure causes `incomplete` or `unavailable`, never a silent suffix that is called
a complete Journal.

This deliberately trades an impossible "every event survives every storage failure"
promise for an honest, testable guarantee: when the system cannot preserve an event
history, it will not claim that it did. The graph does not await a successful Journal
write as a condition of lifecycle success, but the recorder must retain its own failure
state whenever durable observation remains possible.

### 6. Keep readers and DeerFlow progress as projections

Read-only inspection uses a selected available Bundle lifecycle result to authorize
contained observation, then renders only safe correlation, event, health, and
diagnostic-reference fields. It does not infer State from ordering, open a provider, or
offer a Journal-derived action. Bundle Loss returns no historical Journal from an
external store.

DeerFlow's public `custom` stream writer is an optional best-effort subscriber to the
same already-safe typed event facts. Trusted `ToolRuntime` context supplies ingress
correlation only: an outer DeerFlow run id never becomes a Bundle or Journal identity.
The live projection may fail, be absent, or be filtered without changing the durable
Journal. An admitted Run has no external terminal-support fallback after Bundle loss.

## Risks / Trade-offs

- [Concurrent worker records can race or reorder] -> The durable adapter owns one
  serialized sequence allocator; tests exercise multiple worker attempts.
- [Event volume can exceed bounded local storage] -> Preserve diagnostic anchors and a
  tail with original sequence values, expose dropped intervals, and surface incomplete
  history explicitly.
- [A new phase can bypass instrumentation] -> Extend syntax discovery and collected
  outcome evidence to require journal coverage for every production model owner.
- [Safe codes drift into raw details] -> Validate strict typed fields at the recorder
  seam and test hostile values at the reader and writer boundaries.
- [Legacy data lacks the new correlation fields or remains outside a Bundle] -> Do not
  import it into a Bundle or treat it as the Journal; a readable contained legacy record
  is explicitly incomplete and missing/lost Bundles remain unavailable.
- [Journal failure adds latency] -> Keep I/O off the event loop and bound persistence;
  failure remains observational rather than a graph-control dependency.

## Migration Plan

1. Introduce the versioned contained Event Journal contract, including canonical
   validation stages/codes, monotonic sequences, and retention health. Do not import
   existing external observations.
2. Establish the Journal at the admitted execution boundary and pass the producer seam
   through initial, resume, and refinement composition without changing lifecycle
   authority.
3. Move shared graph, work-unit, bridge, and validation observations onto the contract;
   add the canonical validation mappings and optional DeerFlow live mirror that shared
   code cannot infer.
4. Update contained read-only inspection and the workflow evidence inventory, then run
   focused deterministic tests followed by the complete verification gate.

Rollback preserves Bundle State, routing, provider behavior, and lifecycle actions;
the new Journal can be absent or marked unavailable without falling back to an external
record.
