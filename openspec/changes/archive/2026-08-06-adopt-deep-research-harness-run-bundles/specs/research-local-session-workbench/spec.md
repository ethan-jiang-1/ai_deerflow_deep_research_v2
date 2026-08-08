> req: RWB-001, RWB-002, RWB-003, RWB-005, RWB-006, RWB-007, RWB-008

## ADDED Requirements

### Requirement: Local workbench consumes shared Bundle lifecycle results without a broker

The local terminal workbench SHALL use the same trusted scoped Bundle discovery and
typed lifecycle result as other Deep Research entry surfaces. It SHALL display and
submit only legal `bundle_id`-based controls, current State-derived visible input, and
read-only Bundle observations. It SHALL not retain a session broker, session reference,
external checkpoint access, local active-Run cache, or path-derived lifecycle state.
(`RWB-008`)

#### Scenario: Workbench renders Bundle loss truthfully
- **WHEN** the selected Bundle becomes unavailable while the workbench is open
- **THEN** it projects the shared unavailable result and offers no resume/control action for that lost Run

## RENAMED Requirements

- FROM: `### Requirement: Workbench lifecycle controls delegate only to the existing broker`
- TO: `### Requirement: Workbench lifecycle controls delegate only to the Run Bundle lifecycle interface`
- FROM: `### Requirement: Workbench renders broker-projected visible controls`
- TO: `### Requirement: Workbench renders lifecycle-projected visible controls`

## MODIFIED Requirements

### Requirement: Workbench lifecycle controls delegate only to the Run Bundle lifecycle interface

The local workbench SHALL delegate every lifecycle request only to the runtime-owned
Run Bundle lifecycle interface. It SHALL pass no principal, profile, recipe, provider,
thread, host path, session reference, checkpoint, or lifecycle-state authority from its
terminal input. It may select one bounded `bundle_id`, render a trusted shared result,
submit a correlated pending response through `resume`, or submit a separate bounded
refinement through `refine`; it SHALL not construct a graph host, runtime envelope,
sandbox, or parallel state controller. Unavailable, stale, foreign, or denied selections
remain bounded unavailable views and shall not dispatch a lifecycle mutation. (`RWB-001`)

#### Scenario: Workbench selection cannot cross scope
- **WHEN** a terminal user enters a valid-looking Bundle id belonging to another trusted scope
- **THEN** the lifecycle boundary returns a redacted unavailable result before provider, sandbox, graph, or content work

### Requirement: Workbench renders lifecycle-projected visible controls

The workbench SHALL render visible controls only from the shared typed Bundle lifecycle
result and current validated pending-interaction projection. It SHALL bind a displayed
control to the current request id at the lifecycle boundary, never infer a phase/status
from a session trace or report, and never turn a diagnostic into resume/refine authority.
Stale, unknown, or unavailable controls SHALL remain bounded and shall not invoke a
graph node. (`RWB-002`)

#### Scenario: Stale visible control is refused
- **WHEN** the displayed request id no longer matches the Bundle-local pending interaction
- **THEN** the workbench reports bounded unavailability without constructing a graph action or mutating State

### Requirement: Local terminal workbench is bound to one configured durable profile

The standalone local workbench SHALL obtain trusted scope from its fixed local-profile
adapter and discover only through the shared Bundle lifecycle interface. It SHALL render
only bounded `bundle_id` and typed Bundle facts, never a session reference, broker
index, provider, thread, research id, binding path, retained-root path, namespace, or
checkpoint from terminal input. An unavailable profile or Bundle remains a bounded
unavailable operator outcome, not a recovery fallback. (`RWB-001`)

#### Scenario: Fresh workbench process has no legacy discovery fallback
- **WHEN** a fresh local workbench process has trusted profile scope but no Current Bundle Handle
- **THEN** it uses scoped Bundle directories/State through the lifecycle interface and
  does not scan a retained session index or provider checkpoint

### Requirement: Workbench timeline is a bounded read-only observation

For a selected available Bundle, the workbench SHALL render a bounded timeline only
from validated retained observations or Bundle-contained diagnostic facts. It SHALL
first use the shared lifecycle result, then perform no provider open, sandbox initialization,
graph invocation, lifecycle inference, or State mutation. A stale, corrupt, missing, or
post-loss timeline is an unavailable observation and cannot replace Bundle-local status.
(`RWB-003`)

#### Scenario: Timeline cannot authorize a deleted Bundle
- **WHEN** a retained timeline remains after its selected Bundle is deleted
- **THEN** the workbench reports the shared unavailable result and does not call a
  broker, provider, or graph to reconstruct it

### Requirement: Workbench renders authorized retained diagnosis observations

The workbench SHALL render only validated safe diagnosis observations correlated with the
typed Bundle lifecycle result. It retains existing redaction and no-arbitrary-file-
browser guarantees, but diagnosis cannot supply a pending response, select a Run,
recover State, or turn an unavailable Bundle into a live control target. (`RWB-005`)

#### Scenario: Diagnosis does not restore an actionable control
- **WHEN** a retained diagnosis records a prior suspended or terminal fact for an
  unavailable Bundle
- **THEN** the workbench renders it only as history and exposes no answer, resume, or
  refine control for that Run

### Requirement: Workbench renders and submits only projected typed input actions

The workbench SHALL render a control only from the current validated Bundle-local
pending interaction projection and submit it through the shared `resume` path with its
expected request id. A run-level adjustment uses the separate bounded `refine` action;
it is never translated into a pending response. Stale, absent, or unadvertised controls
remain unavailable and the Bundle lifecycle module remains final authority. (`RWB-006`)

#### Scenario: Refinement is not a pending response
- **WHEN** the workbench submits refinement text while a Bundle awaits a response
- **THEN** it calls `refine`, preserves the pending request, and does not encode the text
  as a resume answer
