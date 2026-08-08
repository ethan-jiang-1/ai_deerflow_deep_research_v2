> req: REG-004, REG-014

## MODIFIED Requirements

### Requirement: Lifecycle actions enforce typed and idempotent transitions

An authorized reopened operation SHALL use the same canonical identity validation and
typed transition handlers as an in-thread action; it SHALL revalidate the authoritative
checkpoint before mutation and fail closed before graph invocation on resolver or binding
failure. Reopened resume SHALL validate the brokered response against the latest pending
interrupt and expected request id while the handler's namespace lock is held, and shall
recognize an identical brokered retry without invoking a graph node twice. The local
broker SHALL enter the shared retained-root dispatch lease before this handler path so a
fresh local process cannot race a normal local lifecycle action. (`REG-004`)

#### Scenario: Start returns an opaque scope and suspends
- **WHEN** a trusted user/thread starts a new fake research lifecycle
- **THEN** the handler binds the latest eligible visible HumanMessage, derives a stable opaque research id, records its message correlation and request digest, runs to HITL1, and returns the versioned suspended result without exposing the internal checkpoint key

#### Scenario: Repeated start reprojects instead of duplicating
- **WHEN** the same start is retried after the nested HITL checkpoint was committed but before its outer ToolMessage was delivered
- **THEN** the same research id and pending request are recovered and reprojected with the current tool-call id, no node runs twice, and no orphan lifecycle is created

#### Scenario: Invalid start message is denied
- **WHEN** no visible genuine HumanMessage remains after synthetic-context filtering, or the newest visible candidate is missing a stable id, empty/oversized, a human-input response, or otherwise ineligible as a new research request
- **THEN** start returns redacted `start_message_invalid` before namespace derivation or checkpoint mutation

#### Scenario: Different start in the same thread does not create a multi-active run
- **WHEN** a different eligible HumanMessage requests start in an outer thread that already owns a suspended or terminal research lifecycle
- **THEN** the action returns `thread_research_exists` with the existing opaque id/status and does not invoke or reset the graph

#### Scenario: Status is read-only
- **WHEN** status is requested for a suspended or terminal lifecycle
- **THEN** it reports the bounded version-1 control result with typed phase, generation, status, pending request metadata if any, and durability class without invoking a node or changing the checkpoint

#### Scenario: Full-fake terminal cannot masquerade as research output
- **WHEN** the fake lifecycle reaches final delivery
- **THEN** the result is marked `implementation_mode=full_fake`, contains only a terminal fixture marker, and contains no finding, evidence, citation, report, or claim that real research completed

#### Scenario: Cancel follows graph routing
- **WHEN** cancel targets a suspended lifecycle
- **THEN** the pending interrupt receives an internal cancel decision, the graph records terminal `cancelled`, and a repeated cancel returns the same terminal state

#### Scenario: Cross-scope and invalid transitions fail closed
- **WHEN** another outer thread reuses the research id, a fresh response resumes with no pending interrupt or targets a terminal lifecycle, or start targets an existing namespace
- **THEN** wrong scope returns `research_not_found`, fresh no-pending or terminal resume returns `invalid_transition`, same-message start reprojects, different-message start returns `thread_research_exists`, and no path mutates or discloses another scope's lifecycle

#### Scenario: Gate-blocked terminal reason replaces fixture exhaustion
- **WHEN** gate fatigue escalation or budget exhaustion produces a `BLOCKED` verdict
- **THEN** `terminal_reason` is `GATE_BLOCKED`, not the change-01 `REPAIR_EXHAUSTED`, and the lifecycle transitions to typed terminal `blocked`

#### Scenario: A foreign opaque id cannot select a namespace
- **WHEN** a caller supplies a research id that differs from the id derived from its
  trusted user/thread envelope
- **THEN** lifecycle rejects it without opening a checkpoint, invoking a graph node,
  or revealing whether that id has a binding

#### Scenario: Reopened cancel cannot select a foreign namespace
- **WHEN** a broker operation resolves a binding for another user or outer thread
- **THEN** it denies before namespace derivation, checkpoint mutation, or node invocation

### Requirement: Run-session records remain derived lifecycle projections

The operation broker SHALL treat manifests, traces, and artifact references as
observations only and SHALL not derive a route, phase, pending request, response, or
evidence decision from them. The only reopened pending-input display and resume
correlation source is the authoritative checkpoint interrupt. (`REG-014`)

#### Scenario: Inspecting a retained bundle cannot advance a graph
- **WHEN** a developer reads a manifest or lifecycle trace for a suspended run
- **THEN** no checkpoint mutation, node invocation, pending-interrupt consumption, or route evaluation occurs

#### Scenario: Session metadata does not impersonate bootstrap output
- **WHEN** full-fake session observation creates an inspectable root after the first
  record-bearing returned lifecycle result
- **THEN** the root contains only session metadata/diagnostics and graph routing does
  not treat it as a bootstrap marker or research content artifact

#### Scenario: Binding lookup cannot advance a graph
- **WHEN** runtime resolves a bound session for a later operation surface
- **THEN** it may reopen and validate the checkpoint but does not consume a pending
  interrupt, invoke a graph node, mutate a route, or accept evidence

#### Scenario: Artifact discovery cannot advance lifecycle state
- **WHEN** an authorized operation includes fixed artifact references
- **THEN** graph control remains solely in the checkpoint and no route or pending input
  is derived from those references
