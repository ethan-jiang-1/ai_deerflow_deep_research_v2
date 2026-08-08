> req: REG-003, REG-004, REG-005, REG-006, REG-007, REG-009, REG-010, REG-011, REG-012, REG-013, REG-014, REG-016, REG-020, REG-021

## ADDED Requirements

### Requirement: Deep Research graph lifecycle persists only through the selected Run Bundle

Deep Research lifecycle actions and graph transitions SHALL read and write their
durable Research State through the selected available Run Bundle. A graph checkpoint
representation SHALL be contained in that Bundle and SHALL not be selected, recovered,
or recreated from a generic external checkpoint provider. Graph-local transient values
may exist only for an invocation and SHALL not become another lifecycle authority.
(`REG-020`)

#### Scenario: Restart reads Bundle-local lifecycle State
- **WHEN** a later lifecycle action opens an available Bundle after process restart
- **THEN** it derives the action's lifecycle facts from Bundle-local State and not from an external checkpoint namespace

#### Scenario: Missing Bundle prevents graph recovery
- **WHEN** a former external checkpoint exists but its selected Bundle is unavailable
- **THEN** the graph action returns the typed unavailable outcome without compiling a recovery graph or writing replacement State

### Requirement: Graph lifecycle actions use Bundle identity and safe refinement transitions

Start, status, control, cancellation, and refinement transitions SHALL resolve one
validated `bundle_id` through the Harness lifecycle contract. They SHALL preserve the
one-active rule, treat a suspended Bundle-local State as active, and consume an admitted
refinement only at the next durable safe control point. Their projections SHALL not
expose a conversation-derived research identity or checkpoint locator. (`REG-021`)

#### Scenario: Graph consumes an admitted refinement in the same Bundle
- **WHEN** a graph reaches a safe control point after a refinement was admitted for its active Bundle
- **THEN** it records the resulting round transition in that Bundle and does not create another active Run

## RENAMED Requirements

- FROM: `### Requirement: Checkpoints and topology contracts remain durable and deterministic`
- TO: `### Requirement: Bundle-local State and topology contracts remain durable and deterministic`
- FROM: `### Requirement: One typed ResearchState is the canonical checkpointed control authority`
- TO: `### Requirement: One typed ResearchState is the canonical Bundle-local control authority`
- FROM: `### Requirement: Canonical bundle locator is checkpointed physical-root state`
- TO: `### Requirement: Bundle location is resolved privately at the lifecycle boundary`

## MODIFIED Requirements

### Requirement: Graph-owned HITL bridges and resumes from one matching HumanMessage

HITL1 SHALL retain its graph-owned interrupt and its one current correlated
`AcceptedHumanResponse` resume protocol. The selected Bundle-local Research State,
rather than an external LangGraph checkpoint task, SHALL be the durable pending-request,
consumed-response, and continuation authority. The graph may rebuild its
current-invocation interrupt delivery from that State, but a ToolMessage, a cache, a
session record, or an external checkpoint cannot resume, replace, or recover it.
`resume` receives no refinement text; a run-level adjustment uses the distinct `refine`
action. (`REG-003`)

#### Scenario: Only Bundle-local pending State authorizes resume
- **WHEN** a trusted HumanMessage matches a retained external interrupt but the selected
  Bundle is unavailable or its Bundle-local State has no matching pending interaction
- **THEN** the lifecycle returns its bounded unavailable/invalid-transition outcome and
  does not invoke a graph node

### Requirement: Lifecycle actions enforce typed and idempotent transitions

An authorized lifecycle operation SHALL resolve a selected available Run Bundle through
the same trusted-scope validation and typed transition handlers used by an in-conversation
action. It SHALL revalidate Bundle-local State before mutation and fail closed before
graph invocation on Handle/discovery/State validation failure. `resume` SHALL validate a
correlated response against the latest Bundle-local pending interaction and recognize an
identical delivery without invoking a graph node twice. `refine` SHALL be a separate
typed action: it durably admits one bounded refinement at the Bundle lifecycle safe
point, never treats it as an answer, and cannot reactivate an ended Bundle while a
different Bundle is active in the same trusted scope. Without an explicit `bundle_id`,
it resolves only an active Handle/discovered Bundle; an ended Bundle requires an
explicit target.

`start` allocates a fresh opaque Bundle only when no active available Bundle exists in
the trusted scope. Repeating the same admitted start may reproject its prior result but
cannot publish another Bundle; a different start while a Bundle is active returns the
typed continuation/conflict outcome. Status is read-only. Cancel follows the legal
Bundle-local control transition and is idempotent. No action discloses or accepts an
external checkpoint key, session reference, raw path, or conversation-derived Run
identity. (`REG-004`)

#### Scenario: Public start publishes a Bundle and can suspend
- **WHEN** a trusted user/thread starts a new public research lifecycle with ready real prerequisites and no active available Bundle
- **THEN** the handler binds the latest eligible visible HumanMessage, publishes one fresh Bundle-local State, runs to the legal suspension or result, and returns a versioned result without exposing an internal path or checkpoint key

#### Scenario: Repeated start reprojects instead of duplicating
- **WHEN** the same admitted start is retried after Bundle State commits but before its outer ToolMessage is delivered
- **THEN** the same Bundle result is reprojected with the current tool-call id, no node runs twice, and no orphan lifecycle is created

#### Scenario: Different start does not create a multi-active Run
- **WHEN** a different eligible HumanMessage requests start in an outer conversation that already has a non-terminal available Bundle
- **THEN** the action returns the typed continuation/conflict outcome with the existing bounded Bundle fact and does not invoke or reset another graph

#### Scenario: Resume and refine remain distinct
- **WHEN** a Bundle has a pending interaction and the user submits a later run-level refinement
- **THEN** a correlated `resume` may consume only the pending interaction, while `refine` persists its separate input for the next safe point without altering the pending request

#### Scenario: Status and cancel use Bundle-local truth
- **WHEN** status or cancel targets an available suspended or terminal Bundle
- **THEN** status performs no graph mutation and cancel follows only the legal Bundle-local control transition; a repeated cancel returns the same bounded result

#### Scenario: Cross-scope and invalid transitions fail closed
- **WHEN** another outer conversation reuses a valid-looking Bundle id, resume has no matching pending interaction, refine targets an unavailable Bundle, or an ended Bundle is selected while another Bundle is active
- **THEN** the action returns a redacted not-found, invalid-transition, unavailable, or conflict result as applicable and no path mutates or discloses another scope's lifecycle

### Requirement: Bundle-local State and topology contracts remain durable and deterministic

The fake and real Deep Research graphs SHALL persist recoverable lifecycle State only
through the selected Bundle-contained state/checkpoint adapter. `ResearchState` SHALL
contain only bounded control fields, artifact refs, branch summaries, HITL correlation,
consumed-response ids, bounded profile progress, bounded topic-planning data, and a
bounded logical trace; it SHALL NOT contain raw runtime authority or large research
content. File-backed Bundle State SHALL recover an available suspended HITL across
process restart; memory-only adapters SHALL be labelled same-process only. A committed
normalized topology snapshot SHALL reject unexpected node/edge or reachability changes.
Zero-API E2E coverage SHALL include happy completion, repair, rerun, stop, cancel,
stale-response denial, consumed-response delivery reprojection, restart resume, the
real-HITL1 follow-up restart path, and the real-topic-planning blocked path. (`REG-005`)

#### Scenario: Bundle-contained restart resumes the same interrupt
- **WHEN** one process starts a lifecycle to HITL, closes its local adapter, and a fresh process resumes the same trusted scope and available Bundle with a matching HumanMessage
- **THEN** the prior pending interaction and State are read from that Bundle, resume continues from that point, and no outer lead-agent or external checkpoint is read

#### Scenario: Committed suspension survives result-delivery failure
- **WHEN** Bundle-local State commits a suspension and the action fails before the outer ToolMessage is delivered
- **THEN** retrying the same admitted start reprojects the same pending request without rerunning completed nodes

#### Scenario: Unknown State schema fails closed
- **WHEN** status, resume, cancel, or refine reads an available Bundle whose stored `ResearchState.schema_version` is unsupported
- **THEN** it returns `schema_unsupported` before node execution or State mutation

#### Scenario: Topology drift is detected
- **WHEN** a logical node, edge, route label, or reachability property changes beyond declared routes without regenerating the approved semantic snapshot
- **THEN** the topology contract fails with the normalized difference

### Requirement: One typed ResearchState is the canonical Bundle-local control authority

The downstream package SHALL define one versioned typed `ResearchState` in
`domain/state.py` as the sole durable control authority for one available Run Bundle.
It SHALL organize its fields into `identity`, `request`, `control`, `planning`, `work`,
`quality`, and `delivery` blocks. The identity block SHALL carry `bundle_id`,
refinement-round/generation facts, and `schema_version`; trusted scope is an access
boundary, not a mutable State identity, and neither may be overridden by a node, worker,
or model. The control block SHALL carry phase, phase status, pending interaction,
terminal disposition, gate attempts, repair budget, and admitted refinement facts; at
most one legal current phase/interaction condition SHALL hold at a time. The work block
SHALL carry the existing typed work/status/reference facts. Any future State field SHALL
declare its writer, reader, and reducer. No external checkpoint schema SHALL coexist as
lifecycle authority. (`REG-006`)

Real HITL1 SHALL retain its typed profile fields and bounded follow-up progress, but
they SHALL be persisted in the selected Bundle-local State/content layout and SHALL not
create a duplicate pending-interaction authority, phase cursor, or raw runtime
capability in State.

#### Scenario: Identity cannot be overridden by a node or worker
- **WHEN** a node or worker attempts to write Bundle identity, trusted-scope facts, generation, or schema version
- **THEN** the reducer rejects the write and the lifecycle-selected Bundle identity is preserved

#### Scenario: Only one legal phase and waiting state hold at once
- **WHEN** a reducer receives an update that would set a second active phase or a second pending interaction condition
- **THEN** it rejects the update and the prior single legal control state is preserved

#### Scenario: Every field declares its writer, reader, and reducer
- **WHEN** the `ResearchState` field set is inspected
- **THEN** each field has a declared writer, reader, and reducer in the ownership table, and a contract test fails if any field lacks one

### Requirement: State reducers enforce terminal monotonicity, duplicate-hash idempotency, and sole-writer ownership

`ResearchState` SHALL be updated only through declared Bundle-local reducers. Terminal
work status and terminal refinement disposition SHALL be monotonic; stale values SHALL
not downgrade a terminal value. Replaying the same admitted action/work result with the
same idempotency/content hash SHALL be an idempotent no-op, while a different hash SHALL
return conflict without last-write-wins replacement. Accepted submission references
SHALL remain dedupe-append only. Gate facts remain writable solely by their gate owner;
HITL1 profile facts remain writable solely by controller-authorized graph updates; an
admitted refinement remains writable solely by the lifecycle module. A worker, planner,
repair agent, model output, node-agent result, or runtime capability SHALL not directly
mutate those facts. (`REG-007`)

#### Scenario: Stale terminal state cannot overwrite a newer State
- **WHEN** a stale writer attempts to commit after a newer terminal or admitted-refinement update
- **THEN** the valid Bundle-local State is preserved and the stale writer returns a bounded conflict outcome

#### Scenario: Same-hash replay is idempotent
- **WHEN** the same work/attempt or admitted action is reduced twice with the same correlation and content hash
- **THEN** the second reduction performs no append and does not advance phase, generation, or refinement round

#### Scenario: Non-controller writers cannot mutate guarded authority
- **WHEN** a worker, planner, repair agent, or model-derived update attempts to set gate, profile, pending-interaction, or admitted-refinement facts
- **THEN** reducer ownership rejects the update and the prior Bundle-local authority is preserved

### Requirement: A versioned ResearchState schema fails closed on incompatible versions

The Bundle-local State reader and writer SHALL validate a closed supported
`ResearchState.schema_version` before reading, reducing, or projecting State. An
unsupported, malformed, incomplete, or incompatible State SHALL return a bounded
unavailable/schema outcome and SHALL not be silently reset, auto-migrated, or replaced.
Compatible migration mechanics, when separately approved, SHALL occur wholly inside the
available Bundle and preserve State version/atomicity/containment guarantees. (`REG-011`)

#### Scenario: Incompatible Bundle State is not replaced
- **WHEN** an available Bundle contains an unsupported State version
- **THEN** status, control, and inspection fail closed before graph work and no replacement State is written

### Requirement: Run-session records remain derived lifecycle projections

Any retained run-session trace, manifest, diagnostic, or inspection record SHALL be a
bounded observation of an available Bundle lifecycle result. It SHALL not select a Run,
authorize a transition, supply a pending interaction, recover State, block a fresh Run,
or contradict a Bundle-unavailable outcome. It SHALL preserve only the approved
redaction, correlation, and projection guarantees of the typed lifecycle result.
(`REG-014`)

#### Scenario: A retained projection cannot recover lost State
- **WHEN** a retained session trace refers to a deleted Bundle
- **THEN** it remains an observation only and a later lifecycle request returns unavailable without graph recovery

### Requirement: Bundle location is resolved privately at the lifecycle boundary

The Run Bundle's physical location SHALL be resolved only inside the runtime-owned
Bundle lifecycle/store boundary from its validated opaque `bundle_id` and trusted scope.
Nodes, workers, callers, lifecycle results, State, retained sessions, and checkpoints
SHALL not receive a physical locator or derive a path from a legacy research identity.
Contained content helpers MAY use the bound Bundle reference internally and SHALL reject
symlink/path escape, cross-Bundle content, and malformed identity input. (`REG-016`)

#### Scenario: Caller cannot select a Bundle location
- **WHEN** caller context supplies a timestamp, path, locator-like value, or legacy identity
- **THEN** lifecycle validation rejects it before Bundle resolution or content access

### Requirement: Control, evidence, and content authorities remain distinct

Within one available Run Bundle, Bundle-local Research State SHALL own lifecycle and
control truth, the validated contained evidence ledger SHALL own accepted evidence, and
contained content artifacts SHALL own their bytes. These are distinct direct owners
inside the same Bundle boundary; a projection, session record, external checkpoint,
cache, or artifact path SHALL not substitute for any of them. (`REG-009`)

#### Scenario: In-Bundle evidence cannot restore lost lifecycle State
- **WHEN** a retained evidence artifact remains observable after Bundle-local State is
  unavailable or the Bundle is lost
- **THEN** it does not authorize lifecycle control, infer status, or create replacement State

### Requirement: A minimal research bundle layout and path-containment contract scope sandbox writes

Every Deep Research durable State, evidence, and content write SHALL resolve from the
runtime-selected Bundle reference and remain beneath that Bundle's private contained
root. The Bundle's opaque `bundle_id`, not a conversation-derived `research_id`, is its
Run/directory/control identity. Nodes and helpers MAY use declared relative child paths
only through the bound reference; they SHALL not accept a root, construct a path from a
legacy id, select an external checkpoint, or write a replacement Bundle. The exact
internal child layout remains encapsulated by the lifecycle/store boundary. (`REG-010`)

#### Scenario: Contained writer cannot select a replacement root
- **WHEN** a node or helper is given a path-like value or retired research identity beside
  a selected Bundle reference
- **THEN** it rejects the override before I/O and writes only inside the selected Bundle

### Requirement: Pending interrupt projection never creates a second control authority

The graph-owned interrupt remains the current-invocation delivery mechanism, but its
durable request correlation and pending-interaction facts SHALL be read from and written
to Bundle-local Research State. A projection may describe that State to a consumer but
cannot replace it, recover it from an external checkpoint, or consume a response after
Bundle loss. (`REG-012`)

#### Scenario: Pending projection follows Bundle-local State
- **WHEN** a process restarts while an available Bundle awaits a response
- **THEN** the lifecycle module rebuilds the legal pending projection only from that
  Bundle's State and no external checkpoint or presentation cache is consulted

### Requirement: Terminal incidents remain compact, safe, and status-visible

Terminal incident facts SHALL remain compact, redacted, and status-visible through the
shared typed Bundle lifecycle result. They are contained in available Bundle-local State
or a bounded observation derived from it; they do not turn an external checkpoint,
session, diagnostic, or report into a way to reopen a lost Run. Bundle loss remains an
unavailable outcome rather than a synthetic terminal State. (`REG-013`)

#### Scenario: Terminal observation does not replace Bundle availability
- **WHEN** a retained terminal incident remains after its ended Bundle is deleted
- **THEN** status and control report unavailable rather than treating that observation as
  an ended Bundle that can be refined or resumed
