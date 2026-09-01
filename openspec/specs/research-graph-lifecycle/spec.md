# research-graph-lifecycle Specification

> req: REG-001, REG-002, REG-003, REG-004, REG-005, REG-006, REG-007, REG-008, REG-009, REG-010, REG-011, REG-012, REG-013, REG-014, REG-015, REG-016, REG-017, REG-018, REG-019, REG-020, REG-021, REG-022, REG-023

## Purpose
The stable Deep Research graph topology, deterministic implementation selection,
fixture-graph routing and fan-in, graph-owned HITL lifecycle, and durable checkpoint
semantics that later changes replace node by node without redefining control flow.
## Requirements
### Requirement: One explicit topology and implementation map own every phase

The downstream package SHALL declare one normalized top-level Deep Research topology
containing `bootstrap`, `hitl1`, `topic_planning`, `wave0`, `wave1`,
`wave2_synthesis`, `targeted_evidence`, `hitl2`, `rerun`, `readiness`, and
`final_delivery`. The builder SHALL load only explicitly listed production package-root
`NODE_SPEC` values and SHALL resolve every logical node through one complete explicit adapter
selection and its matching gate-definition map. The composition contract SHALL identify the
selected logical nodes that require a gate, and the gate map SHALL contain exactly those names;
it SHALL not silently skip a required gate or attach a gate to a non-gated adapter. Production node specs
supply real adapters only; a fixture adapter can be selected only when a test or demo
composition root supplies the complete fixture catalog. Generic injected recipe construction
SHALL fail closed for an omitted, empty, incomplete, unknown, or unavailable adapter selection,
or a missing, unknown, extraneous, or adapter-mismatched gate definition, before graph
compilation or invocation and SHALL NOT silently select a fixture. The named all-real recipe
factory is the only
production-owned construction path and supplies its fixed real selection itself. Node packages SHALL use one canonical
pure unavailable-real sentinel rather than divergent placeholder behavior.

Real HITL1 SHALL add exactly two HITL1 route labels to the normalized topology:
`needs_followup -> hitl1` and `exhausted -> blocked/END`. Existing HITL1 labels
`accepted -> topic_planning` and `cancel -> cancelled/END` SHALL remain unchanged.
The self-edge is the durable same-phase follow-up path for incomplete profile answers;
the exhausted edge is the typed blocked path for pre-interrupt brief-generation failure.
No new top-level phase is introduced, and no later fixture phase is allowed to observe a
partially completed HITL1 profile as if it were accepted.

Real topic planning SHALL add exactly one topic-planning route label to the normalized
topology: `exhausted -> blocked/END`. The existing `topic_planning --next--> wave0`
label and the inbound `bootstrap/hitl1 -> topic_planning` and `rerun -> topic_planning`
edges SHALL remain unchanged. The exhausted edge is the typed blocked path for a
planner that fails validation or coverage after its bounded repair. topic_planning
remains a non-gated controller node that writes its own route labels and does not
import LangGraph. Real topic planning SHALL chain off the real profile: selecting
real topic planning without real HITL1 (which itself requires real bootstrap) SHALL
fail closed before graph invocation.

Real Wave2 synthesis SHALL add exactly one Wave2 route label to the normalized
topology: `exhausted -> blocked/END`. Existing labels
`evidence_needed -> targeted_evidence` and `pass -> hitl2`, plus the
`targeted_evidence -> wave2_synthesis` return edge, SHALL remain unchanged. The
exhausted edge is the typed blocked path when searchable gaps remain after the
existing Wave2 gate repair budget or fatigue contract is exhausted; no new top-level
phase or alternate bypass around synthesis is introduced.

#### Scenario: Explicit fixture topology resolves only from test or demo assembly
- **WHEN** a test or credential-free demo supplies a complete fixture adapter catalog and
  complete fixture selection
- **THEN** all eleven stable logical nodes resolve deterministically, every top-level node is
  reachable from START and can reach a terminal path, and no filesystem discovery occurs

#### Scenario: Generic empty or incomplete selection fails closed
- **WHEN** a graph builder or generic injected recipe constructor receives no explicit selection,
  an empty selection, a selection missing a logical node, or a gate-definition map that does not
  exactly match the selected adapters' gate membership
- **THEN** construction fails with a bounded implementation-selection error before a
  checkpoint, model, sandbox tool, or node is invoked

#### Scenario: Fixed production factory cannot become a mode selector
- **WHEN** internal code uses the named all-real factory
- **THEN** it supplies the fixed all-real selection, accepts no adapter-selection or mode input,
  and cannot import or select fixture adapters

#### Scenario: Unavailable real selection fails closed
- **WHEN** an implementation selection requests real for a node whose real implementation is
  not available
- **THEN** graph binding fails with the logical node name and `implementation_unavailable`
  before a checkpoint, model, sandbox tool, or node is invoked

#### Scenario: Public callers cannot select a recipe
- **WHEN** a reflected lifecycle caller supplies any recipe, mode, fixture-plan, or adapter
  authority field
- **THEN** strict action validation rejects it and the selected public real recipe remains
  unchanged

#### Scenario: Real HITL1 follow-up and blocked routes are explicit
- **WHEN** an explicit recipe selects real HITL1
- **THEN** the builder contains conditional edges for `hitl1 --needs_followup--> hitl1` and
  `hitl1 --exhausted--> END`, and topology validation recognizes the exhausted route as
  terminal `blocked`

#### Scenario: Internal component cannot become a phase accidentally
- **WHEN** a Wave dispatch/join component, HITL1 follow-up helper, or an unlisted node
  package is present on disk
- **THEN** the normalized top-level topology and registry omit it and the topology contract
  rejects any edge that exposes it as a logical phase

#### Scenario: Real topic planning blocked route is explicit
- **WHEN** an explicit recipe selects real topic planning
- **THEN** the builder carries a conditional edge `topic_planning -> {next: wave0,
  exhausted: END}`, the `next` and inbound edges are unchanged, and topology validation
  recognizes the topic-planning `exhausted` route as terminal `blocked`

#### Scenario: Real topic planning without the real profile chain fails closed
- **WHEN** a recipe selects real topic planning without real HITL1
- **THEN** recipe construction fails with a typed dependency error before the graph is
  compiled or invoked

#### Scenario: Real Wave2 blocked route is explicit
- **WHEN** the real Wave2 gate exhausts its bounded repair or fatigue contract while
  searchable gaps remain
- **THEN** the builder routes `wave2_synthesis --exhausted--> END`, normalized topology
  classifies the endpoint as `blocked`, and no targeted or HITL2 bypass occurs

### Requirement: Deterministic fakes exercise routing and parallel fan-in

Every fake node implementation SHALL be deterministic and fixture-driven. No fake
SHALL call a model, network API, MCP server, ACP agent, DeerFlow `task` subagent, or
sandbox research tool. Wave0 and Wave1 SHALL each execute a phase-local three-branch
LangGraph `Send` fan-out through the shared work-unit kernel, reduce fixture
`CandidateResult` values without losing or replacing a winner, run deterministic
submit, drain pending/in-flight work, and return one typed phase result. Their fixture
workers MAY write only their controller-assigned `work/<work_id>/<attempt_id>/`
artifacts, and only deterministic submit MAY publish the fixture submission ledger.

Typed routers SHALL support pass, bounded repair, targeted-evidence convergence, all
five HITL2 decisions (`proceed | revise_view | repair | rerun | stop`), typed readiness
repair targets, bounded final-delivery self-repair/evidence-blocked return, real HITL1
follow-up/blocking routes (`needs_followup`, `exhausted`), and completion without
reading free-form model text in fake phases. The validated fixture plan SHALL come from
handler/test construction rather than public tool arguments and SHALL be persisted as
closed data needed for deterministic resume. Bootstrap SHALL expose both
`needs_input -> hitl1` and `profile_complete -> topic_planning`; the default fake path
SHALL still exercise fake HITL1 exactly once and SHALL NOT take the real-HITL1
`needs_followup` or `exhausted` routes unless real HITL1 is selected.

Gate evaluation SHALL remain the routing authority for gated phases. Every gated phase
node SHALL have a registered `GateDefinition` containing a `FixtureSequenceRule` (fake
graph) or real rules (later changes). Wave0 and Wave1 SHALL prepend the shared
deterministic work-completion rule so fixture `pass` cannot override failed or
unaccepted work. After the phase-local component reports structural drain, the node
wrapper SHALL apply a pure reducer preview of the node's work/status/accepted-ref
update to the input state and invoke `evaluate_gate()` against that post-work view, not
the stale pre-node state. The preview SHALL use the same reducers and ownership checks
as checkpoint application for an explicit allowlist of gate-readable work fields. It
SHALL exclude `phase`, `route`, `execution_trace`, fixture visit counters, and every
gate-owned field so fixture sequence indexing and sole-writer authority do not advance
early. The preview SHALL perform no I/O or checkpoint mutation. Gate evaluation then
runs all rules, collects failures, and produces a typed `PhaseVerdict`. The gate's
`route_map` SHALL translate the verdict to the route string written to
`state["route"]`. The existing `_route()` function SHALL read `state["route"]`
unchanged. The graph's conditional edges SHALL continue to match the same route labels
as the normalized topology. HITL1 remains a non-gated controller node and writes its own route labels
directly.

Fixture sequence indexing SHALL remain in `FixtureSequenceRule`, attempt/budget
tracking SHALL remain in the gate kernel, and the frozen `repair_counts` state field
SHALL remain unwritten. The topology snapshot SHALL remain identical in top-level
node/edge structure and every route label SHALL match the normalized topology. Work-unit dispatch,
worker, submit, and drain nodes are internal components and SHALL NOT become top-level
logical phases.

#### Scenario: Three branches join deterministically
- **WHEN** a Wave fake runs with three fixture workers completing in any scheduler order
- **THEN** all three unique candidates are reduced exactly once, normalized into stable order, accepted with at most one winner per logical work across all its attempts, and the parent phase advances only after submit fan-in and drain

#### Scenario: Complete profile bypass is already part of topology
- **WHEN** the bootstrap fixture returns `profile_complete`
- **THEN** the graph routes directly to topic planning without creating HITL1, while the default fixture still routes through fake HITL1 and the topology snapshot remains deterministic

#### Scenario: Wave0 repair is bounded
- **WHEN** the Wave0 fixture gate definition sequences `repair` then `pass`
- **THEN** gate evaluation returns `REPAIR` on the first attempt (route `"repair"`), the repair path retries only unaccepted failed work and allocates new logical work for already accepted quality repair, gate evaluation returns `PASS` on the second attempt (route `"pass"`), `gate_attempts_by_phase["wave0"]` is 2, and the topology advances to Wave1 only after pass

#### Scenario: Invalid fixture work cannot advance on fixture pass
- **WHEN** a Wave fixture worker omits its result or returns a conflicting candidate while the fixture sequence value is `pass`
- **THEN** the work-completion rule keeps the phase on a typed repair/blocked path, no invalid accepted ref is created, and the graph does not advance to the next phase

#### Scenario: Targeted evidence always returns through synthesis
- **WHEN** Wave2, HITL2 repair, or readiness routes to targeted evidence
- **THEN** the targeted phase returns to Wave2 synthesis before HITL2 or readiness can be reached again, and a fixture cannot bypass synthesis by routing directly to HITL2

#### Scenario: Every later repair edge remains explicit
- **WHEN** fixture gate definitions produce Wave1 repair, HITL2 revise-view/repair, any readiness repair target, final-delivery self-repair, or final evidence-blocked return to readiness
- **THEN** the normalized topology follows the declared bounded edge and eventually reaches the expected next gate or typed terminal without changing unrelated node implementations

#### Scenario: Fake execution has only bounded fixture side effects
- **WHEN** the complete graph runs under spies for model, web, subagent, and sandbox research tools
- **THEN** every spy remains unused, Wave0/Wave1 write only controller-assigned fixture specs/results/outputs plus the validated submissions ledger and its lock/staging files, and no fetched cache, synthesis, review, final report, or non-fixture research output is created

#### Scenario: Gate verdict drives routing through unchanged _route function
- **WHEN** a gated phase node completes its work-unit drain
- **THEN** the gate evaluates the reducer-previewed current-batch submissions, writes `route` via `route_map` (for example `PhaseVerdict.PASS -> "pass"`), `_route()` reads `state["route"]`, and the conditional edge matches that route label

#### Scenario: Gate preview does not advance fixture visit indexing
- **WHEN** a Wave node returns current-batch work fields plus its normal phase and execution-trace update
- **THEN** the gate preview includes only allowlisted work fields, `FixtureSequenceRule` selects its current fixture index, and phase/trace/gate-owned fields are applied only by the final graph transition

#### Scenario: Fixture gate rules preserve lifecycle outcomes
- **WHEN** the fake graph runs with fixture gate definitions encoding the same sequences as the prior `fixture_plan`
- **THEN** every top-level phase transition follows the same path and every E2E lifecycle test (happy completion, repair, rerun, stop, cancel, stale-response denial) passes while Wave0/Wave1 exercise validated work-unit submission

#### Scenario: Fixture-graph HITL1 remains deterministic
- **WHEN** the explicit fixture graph reaches HITL1
- **THEN** fixture HITL1 presents its hardcoded fixture prompt, accepts the matching response once, routes `accepted`, and does not call a model, request-bundle writer, or real-HITL1 follow-up route

#### Scenario: Real HITL1 follow-up does not affect gated phase routing
- **WHEN** real HITL1 routes `needs_followup` or `exhausted`
- **THEN** gate evaluation is not invoked for HITL1, and gated phase route labels come from their gate definitions

### Requirement: Graph-owned HITL bridges and resumes from one matching HumanMessage

HITL1 SHALL retain its graph-owned interrupt and its one current correlated
`AcceptedHumanResponse` resume protocol. The selected Bundle-local Research State,
rather than an external LangGraph checkpoint task, SHALL be the durable pending-request,
consumed-response, and continuation authority. The graph may rebuild its
current-invocation interrupt delivery from that State, but a ToolMessage, a cache, a
session record, or an external checkpoint cannot resume, replace, or recover it.
`resume` receives no refinement text; a run-level adjustment uses the distinct `refine`
action. (`REG-003`)

HITL2 SHALL continue from its validated predecessor without creating a pending human
request, accepting an `AcceptedHumanResponse`, or advertising an internal route label
as a user option. Its internal real or fixture route remains graph-owned and does not
create a second interrupt/resume surface.

#### Scenario: Only Bundle-local pending State authorizes resume
- **WHEN** a trusted HumanMessage matches a retained external interrupt but the selected
  Bundle is unavailable or its Bundle-local State has no matching pending interaction
- **THEN** the lifecycle returns its bounded unavailable/invalid-transition outcome and
  does not invoke a graph node

#### Scenario: HITL2 does not create a second response boundary
- **WHEN** a real or fixture graph reaches HITL2 through a valid predecessor
- **THEN** the graph follows its owned route without creating a pending request,
  accepting a HumanMessage response, or advertising that route as a user choice

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

### Requirement: Large research content stays out of the checkpoint as bounded content refs

`ResearchState` SHALL NOT store web page bodies, PDFs, full evidence summaries, full
reports, screenshots, large tool output, or full HITL1 profile JSON bodies. Such content
SHALL live only as sandbox artifact files, and `ResearchState` SHALL reference it by at
most a sandbox path, a content hash, a schema version, and a short summary. A hard
checkpoint-size bound SHALL reject any state update whose serialized form exceeds the
bound; semantic content SHALL fail validation rather than be silently truncated. Raw
runtime authority - `TrustedRuntimeEnvelope` fields, AppConfig, model and tool handles,
sandbox handles, file handles, host paths, and credentials - SHALL NOT enter the
checkpoint.

The HITL1 final `ResearchProfile` SHALL be serialized as canonical JSON in
`request/profile.json`; the checkpoint SHALL store only `profile_ref`, short enum/string
fields, bounded `must_answer_questions`, `degraded_profile`, and bounded transient
progress needed to ask follow-ups.

#### Scenario: Oversized content is rejected
- **WHEN** a node returns a state update whose serialized size exceeds the hard checkpoint-size bound
- **THEN** the update is rejected with a typed failure and the checkpoint is not mutated

#### Scenario: Content is referenced, not embedded
- **WHEN** a state update carries large content
- **THEN** the reducer stores only a `ContentRef` (sandbox path, content hash, schema version, short summary) and excludes the raw body from the checkpoint

#### Scenario: Raw runtime authority is rejected
- **WHEN** a state update includes a `TrustedRuntimeEnvelope`, AppConfig, model/tool handle, sandbox handle, or credential field
- **THEN** the reducer rejects the unknown field and the checkpoint is not mutated

#### Scenario: HITL1 profile body is referenced, not embedded
- **WHEN** a complete HITL1 profile includes scope boundaries or custom notes
- **THEN** those full profile values live in `request/profile.json`, while the checkpoint contains only the bounded `ContentRef` and short planning fields

#### Scenario: Runtime authority is rejected from profile state
- **WHEN** a state update tries to carry a request-bundle writer, host path, file handle, AppConfig, model handle, or sandbox handle
- **THEN** checkpoint validation rejects the update and no profile state is mutated

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

### Requirement: A versioned ResearchState schema fails closed on incompatible versions

The Bundle-local State reader and writer SHALL validate a closed supported
`ResearchState.schema_version` before reading, reducing, or projecting State. An
unsupported, malformed, incomplete, or incompatible State SHALL return a bounded
unavailable/schema outcome and SHALL not be silently reset, auto-migrated, or replaced.
Compatible migration mechanics, when separately approved, SHALL occur wholly inside the
available Bundle and preserve State version/atomicity/containment guarantees. (`REG-011`)

The current graph checkpoint schema SHALL omit `repair_counts`. Before graph
construction, node invocation, reducer application, or lifecycle projection, the graph
checkpoint reader SHALL accept only a current schema record or reject the record with
its existing bounded unsupported-schema/checkpoint outcome. It SHALL not silently
upgrade, reset, rewrite, or derive repair facts from an old checkpoint. Only an
explicitly registered old checkpoint may enter the separately invoked offline migration
route. That route SHALL decode and validate the complete old record, prove that removing
`repair_counts` leaves the current gate-owned attempt/budget facts intact, and atomically
write a current-schema record. Its source-controlled migration inventory is an operator
input and evidence record, not a runtime reader, lifecycle authority, or graph entry
selector. An old checkpoint absent from that inventory, malformed, partially migrated,
stale, or replayed across an incompatible identity SHALL be rejected without graph
mutation.

#### Scenario: Incompatible Bundle State is not replaced
- **WHEN** an available Bundle contains an unsupported State version
- **THEN** status, control, and inspection fail closed before graph work and no replacement State is written

#### Scenario: Unregistered legacy checkpoint fails before graph work
- **WHEN** the current graph reader receives a checkpoint with `repair_counts` that is not an approved completed migration output
- **THEN** it returns the bounded checkpoint/schema denial before graph compilation, node invocation, State reduction, or Bundle lifecycle action

#### Scenario: Registered checkpoint migration preserves current control facts
- **WHEN** the offline migration route processes a registered valid checkpoint with `repair_counts`
- **THEN** it validates the whole input, writes one current record without that field, and a reload/replay preserves the existing generation, terminal monotonicity, and gate attempt/budget facts

#### Scenario: Failed migration does not become a graph recovery path
- **WHEN** decoding, validation, identity matching, or atomic output of a registered checkpoint migration fails
- **THEN** no current checkpoint is written, the source record is unchanged, and the next legal runtime action is the same bounded rejection rather than resume or retry

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

### Requirement: Correlated human input supports advertised closed actions

The existing graph-owned human-input protocol SHALL support `response_kind=action` in
addition to text and choice without making action strings implicit text authority. A
pending request SHALL advertise a bounded closed `action_ids` collection separate from
any choice options; an action response SHALL carry exactly one
advertised `action_id`. Direct and brokered resume SHALL preserve request/message
correlation and reject an action that is unadvertised, mismatched, replayed, malformed,
or encoded as text before node execution. HITL1 may advertise only `accept_suggestion`;
other nodes retain their existing response modes and no action may alter lifecycle
identity or routing outside its owning node. (`REG-015`)

#### Scenario: Advertised action passes correlation checks
- **WHEN** a pending HITL1 request advertises `accept_suggestion` and a matching typed action response arrives
- **THEN** the generic extractor accepts that action once and HITL1 decides its profile effect from checkpointed proposal state

#### Scenario: Text cannot spoof a closed action
- **WHEN** a response sends `accept_suggestion` as ordinary text or sends an action not advertised by the pending request
- **THEN** generic validation rejects it before graph-node execution and no response is consumed

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

### Requirement: Known invocation failures remain phase-owned lifecycle facts

When a direct real phase terminally blocks after a known normalized invocation
failure, its checkpoint update SHALL retain a compact `latest_incident` carrying the
same safe category, phase, certainty, safe diagnostic reference, and bounded
recovery facts when observed. When a worker phase fails, its work-unit controller
SHALL retain the corresponding closed attempt/aggregate facts and no node may create
a competing terminal authority. Generic `research.blocked` remains a route outcome,
not a replacement for a known incident.

#### Scenario: Topic planning blocks after exhausted provider recovery
- **WHEN** topic planning exhausts its declared provider-recovery bound
- **THEN** the blocked checkpoint retains a provider terminal incident with the
  topic-planning phase and the route remains the existing terminal blocked route

#### Scenario: Worker exhaustion does not create a second controller
- **WHEN** a Wave worker produces a classified invocation failure and its existing
  controller exhausts permitted work attempts
- **THEN** the controller-derived work outcome supplies the terminal diagnosis and
  the worker does not independently advance, resume, or rewrite graph control state

### Requirement: Visible controls bind only to current advertised graph actions

The graph lifecycle SHALL retain `HumanInputRequest.action_ids` and generic advertised
action verification as the transport authority. A generic control-selection intent
shall be bound by trusted runtime or the authorized broker only when its current visible
control maps to an action advertised by the same current pending request. Adapters and
ordinary text SHALL not map phrases, action ids, or proposal fields into an action.
Stale, forged, or unadvertised controls SHALL fail closed before graph-node execution.
(`REG-017`)

#### Scenario: Current control becomes one typed action
- **WHEN** a current prompt displays its current-proposal control and a caller selects
  it
- **THEN** trusted runtime emits the existing correlated advertised action response
  and HITL1 remains the authority for its effect

#### Scenario: Stale control cannot mutate the graph
- **WHEN** a control id is submitted after the pending request changed or no longer
  advertises its mapped action
- **THEN** lifecycle rejects it before resume and leaves checkpoint state unchanged

### Requirement: Interaction checkpoint facts are bounded and compatible

ResearchState SHALL retain only controller-owned bounded proposal-version and
interaction-feedback facts needed to project the next HITL1 request. It SHALL default
those facts safely for existing schema-v2 checkpoints and SHALL not store raw replies,
semantic prompts, candidates, model output, or provider bodies. Acceptance,
cancellation, and terminal handling SHALL clear transient interaction feedback.
(`REG-018`)

#### Scenario: Existing checkpoint remains readable
- **WHEN** a schema-v2 checkpoint has a proposal but no interaction fields
- **THEN** its next HITL1 projection remains readable and its prior responses are not
  reinterpreted

### Requirement: HITL1 language selection is a correlated bounded option response

The lifecycle wire contract SHALL support a HITL1 `CHOICE` request only for an explicit
supported-language selection whose option identifiers and values are a closed language
set. A matching `OPTION` response SHALL include the current request id and one
advertised option id; trusted lifecycle validation SHALL reject stale, forged, missing,
or non-language options before HITL1 executes. The lifecycle SHALL NOT advertise
internal HITL2 route identifiers as a current `CHOICE` request or accept one as a
language response to HITL1.

The HITL1 language option SHALL not be a generic action id, visible-control alias, or
free-text phrase-to-action mapping. The selected option is an input candidate only;
HITL1 retains validation, profile mutation, and route authority. Existing text HITL1
requests and retained version-1 interrupts SHALL remain readable.

#### Scenario: Current language option is accepted as input rather than an action
- **WHEN** a current HITL1 language-choice request receives its advertised Chinese
  option with the matching request id
- **THEN** lifecycle delivers one correlated option response to HITL1 and does not
  fabricate an action id or graph route

#### Scenario: Stale language option fails before node execution
- **WHEN** a language option from an earlier HITL1 request is submitted after a new
  correlated request is pending
- **THEN** lifecycle rejects the response and leaves the checkpoint unchanged

#### Scenario: Internal HITL2 route is not an HITL1 language answer
- **WHEN** a caller submits an internal HITL2 route identifier such as `proceed`
  against a current HITL1 language-choice request
- **THEN** lifecycle rejects it before HITL1 executes and does not turn it into a
  graph route or a second pending interaction

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
one-active rule, treat a suspended Bundle-local State as active, and keep a correlated
pending human response distinct from an independently admitted refinement. Their
projections SHALL not expose a conversation-derived research identity, host path, or
checkpoint locator.

The graph lifecycle SHALL define the refinement round boundary as a Bundle-contained
graph execution boundary at which the preceding graph write is durably committed, no
graph writer is in flight, and no current human subject is being replaced. At that
boundary, a shared Bundle-local coordination facility usable by independent runtime
instances SHALL provide a short transition exclusion for every published Bundle State
read/validate/reducer/write sequence, including the authoritative State revision check,
RequestBundleStore/HITL1's permitted profile materialization and resulting State
projection, response/cancellation/terminal mutations, graph-progress projection,
checkpoint preparation, Bundle-State commit, and continuation authorization. HITL1 SHALL
re-reduce only its permitted profile/interaction fields from current State after a lawful
concurrent direction write; the facility SHALL NOT grant that node lifecycle authority.
It SHALL be the cross-instance/process serializer; the State revision check remains a
stale-write fence, not the sole mutex. The facility also provides a separate execution
exclusion held across every selected-Bundle graph `ainvoke` and an immediate
terminal-boundary continuation owned by that same invocation. The execution exclusion SHALL serialize competing
continuations but SHALL NOT prevent an active Bundle from admitting one pending
refinement through the transition exclusion. Neither exclusion stores a lifecycle fact.
The facility SHALL remain contained in the validated selected Bundle and SHALL not
recover or recreate an unavailable Bundle. For an ended Bundle's terminal-to-active
commit only, the lifecycle SHALL first use the transient trusted-scope exclusion that
serializes it with fresh start; that exclusion stores no scope fact and is released
before graph execution.

Only a synchronized `COMPLETED` terminal graph snapshot is eligible for automatic
pending-refinement preparation/consumption. `STOPPED`, `CANCELLED`, and `BLOCKED`
snapshots preserve any pending direction but SHALL NOT prepare a checkpoint, commit a
new current round, or continue graph work. A later user-requested explicit selected
textless `refine` continuation remains the only path that may reactivate that available
ended Bundle with its existing pending direction.

Coordinator acquisition and release SHALL remain off the event loop, permit a cancelled
waiter to leave no State/checkpoint write, and revalidate the selected Bundle's
no-follow path and live directory identity after acquisition and before each durable
write or graph invocation. Loss or replacement of that Bundle SHALL be unavailable;
the lifecycle SHALL not write through a detached descriptor or recreate the root. The
lifecycle SHALL atomically move at most one pending refinement to the new current round
only as its Bundle-State transition, after preparing the separate Bundle-contained
checkpoint; it SHALL not imply a cross-file filesystem transaction. Preparation SHALL
submit only the typed output of the pure full-rerun compiler shared with the rerun node
to the compiled production graph's `aupdate_state(..., as_node="rerun")` writer/edge;
it SHALL not accept a hand-built alternative update. Checkpoint preparation SHALL not
invoke a graph node, model, tool, or provider or publish graph/topic/artifact facts
before that Bundle-State commit. The existing full-rerun transition then re-enters
`topic_planning` in the same Bundle and generation lineage. A stale graph writer or
replayed boundary SHALL not consume the refinement, advance the generation, or publish
the round twice.

An admitted refinement SHALL remain pending across a suspension until its correlated
human subject has been resolved and a legal round boundary is reached. An explicit
direction form for an available ended Bundle, or an explicit textless continuation form
for its existing pending direction, SHALL create only the graph work required to start
that Bundle's next round; an active graph invocation SHALL use its already bound
Bundle-contained graph store. The textless form is legal only for an explicit available
terminal target with one pending direction; it consumes that record and never admits or
reconstructs text. After its CAS commits, an explicit selected textless retry may only
continue the current record's exact queued `topic_planning` task when Bundle State has no
pending human or later direction and the Bundle-contained checkpoint proves the same
token; it remains no admission or new direction. When a checkpoint is prepared before the Bundle-State commit, a later
selected text-bearing `refine` SHALL first reconcile the pending operation's matching
token: the same trusted operation receives `refinement_applied`, while a different
operation receives `refinement_conflict` for its submitted action and the first round's
post-reconciliation `applied` Bundle projection. That recovery SHALL terminate the
different operation's admission attempt; it SHALL NOT fall through to ordinary admission
now that the pending slot has cleared. A qualified textless continuation MAY reconcile
only the selected pending record's matching token and returns `refinement_applied` only
when that exact record commits or is observed committed during its locked attempt; it
SHALL NOT enter ordinary direction admission. Before that commit, the preceding terminal
Bundle State remains authoritative with its pending direction and an explicit selected
`refine` next action only while capacity permits it; otherwise its legal next action is
`start` while the pending fact remains inspectable. `status` remains read-only. No
lifecycle action SHALL use an external checkpoint, session record, diagnostic, or prior conversation text to recover
or authorize the transition.

#### Scenario: Graph consumes an admitted refinement in the same Bundle
- **WHEN** a graph reaches the declared round boundary after a refinement was admitted for its active Bundle
- **THEN** it records one pending-to-applied round transition in that Bundle, enters the existing full-rerun path toward `topic_planning`, and does not create another active Run

#### Scenario: Suspended graph keeps its current human subject
- **WHEN** a refinement is admitted while the graph is suspended on a correlated human subject
- **THEN** the graph leaves that subject and its response correlation unchanged, reports the refinement as waiting, and applies it only after a later legal round boundary

#### Scenario: User terminal intent does not auto-reactivate a Bundle
- **WHEN** an active graph with a pending direction projects `STOPPED` or `CANCELLED`, or projects `BLOCKED`
- **THEN** the projection preserves that pending direction but performs no rerun preparation or continuation; only a later user-requested explicit selected textless `refine` continuation with legal remaining capacity may reactivate the available ended Bundle

#### Scenario: Boundary replay is exactly once
- **WHEN** process restart or checkpoint replay revisits a graph boundary whose refinement round was already committed
- **THEN** the graph observes the committed generation and applied refinement and neither consumes nor starts that round again

#### Scenario: Prepared checkpoint reconciles the first pending operation before a later request
- **WHEN** a process stops after preparing the matching rerun checkpoint but before the pending-to-current Bundle-State commit, and a selected `refine` later arrives
- **THEN** the lifecycle commits only the prepared first operation's matching token without another generation update; the same text-bearing operation returns `refinement_applied` with `applied`, while a different text-bearing operation returns `refinement_conflict` with the same `applied` Bundle projection and cannot enter ordinary admission or replace the first direction in that call; a qualified textless continuation may reconcile only the selected pending record and returns `refinement_applied` only for that record's committed token

#### Scenario: Pre-commit preparation never makes status a hidden recovery path
- **WHEN** the matching rerun checkpoint is prepared but its Bundle-State commit has not occurred
- **THEN** `status` reports the preceding terminal State and pending direction without reconciliation, while the typed legal next action remains explicit selected `refine` and the textless continuation predicate stays at the lifecycle boundary

#### Scenario: Stale graph writer loses to committed refinement state
- **WHEN** a graph writer based on an older Bundle revision attempts to commit after a refinement boundary was committed
- **THEN** the stale write is rejected and cannot restore the pending refinement, erase the applied direction, or overwrite the new generation

#### Scenario: Stale graph projection cannot overwrite the committed round
- **WHEN** a graph snapshot carries a Bundle identity, generation, or round token that does not match the committed current refinement round
- **THEN** graph-progress synchronization makes no Bundle-State write and cannot replace the committed applied direction, generation, or pending refinement

#### Scenario: Terminal State defeats a late graph projection
- **WHEN** cancellation or another lawful terminal State transition commits while a graph invocation still holds an older snapshot
- **THEN** its later graph-progress projection makes no Bundle-State write and cannot restore an active status, pending subject, or refinement fact

#### Scenario: Competing continuation does not execute a graph task twice
- **WHEN** two independently constructed runtime instances attempt to continue the same prepared refinement round
- **THEN** only the holder of the selected Bundle's execution exclusion may invoke its pending graph task, and the other re-reads the checkpoint after acquiring that exclusion without creating a second node/model/tool/artifact effect or refinement round

#### Scenario: Refinement admission races eligible terminal projection safely
- **WHEN** a valid refinement is admitted immediately before or after the current graph invocation projects its `COMPLETED` terminal snapshot
- **THEN** one transition path preserves the pending direction, prepares and commits one matching refinement token, and the Bundle starts no more than one next-round continuation; when the terminal projector already owns execution, it continues that queued task without re-acquiring the execution exclusion

#### Scenario: Ended refinement starts Bundle-contained graph work
- **WHEN** an explicit direction form legally reactivates an available ended Bundle, or a qualified textless continuation legally consumes its pending direction
- **THEN** graph execution opens that Bundle's contained graph store, commits the full-rerun transition, and makes observable progress in the new round without consulting an external lifecycle checkpoint

#### Scenario: Textless continuation cannot become an implicit recovery route
- **WHEN** `refine` omits text for an explicit target that is active, suspended, unavailable, terminal without a pending direction, or otherwise cannot legally start another round
- **THEN** lifecycle returns its bounded denial without preparing a checkpoint, admitting a direction, changing a profile, or invoking graph work, except for an active post-CAS current record whose exact token has its one queued `topic_planning` task; that exception only invokes the already-authorized task under execution exclusion. An omitted-text call without a `bundle_id` is rejected by the public schema before lifecycle dispatch

#### Scenario: Post-CAS continuation recovers one exact queued task
- **WHEN** an explicit selected textless continuation finds a current refinement after its CAS but before graph continuation, and the selected Bundle checkpoint has exactly that token's queued `topic_planning` task
- **THEN** it invokes that task once under the execution exclusion, retains the committed generation/refinement, and rejects every mismatch or completed task without an admission or second round

#### Scenario: Missing Bundle prevents refinement recovery
- **WHEN** a former graph checkpoint or conversation record exists but the selected Bundle becomes unavailable before the refinement boundary
- **THEN** the graph returns the typed unavailable outcome without consuming the pending direction, recreating State, or starting replacement graph work

#### Scenario: Coordinator cancellation and root loss release without a write
- **WHEN** a contender is cancelled while waiting for the selected Bundle coordinator, or the selected Bundle is removed or replaced after coordination is acquired
- **THEN** it releases its transient exclusion, performs no State/checkpoint/graph invocation write, and returns cancellation or the typed unavailable outcome without recreating the Bundle

### Requirement: Persisted composition truth is explicit and closed

Every accepted Bundle-local Research State SHALL carry an explicit composition mode
derived from its selected graph recipe and executor. The supported closed set is
`fixture`, `mixed`, and `all_real`. A missing, `full_fake`, unknown, incompatible, or
otherwise unregistered mode/schema input SHALL fail before lifecycle projection, graph
invocation, State mutation, or a quality/completion claim; it SHALL not default,
backfill, auto-migrate, or strengthen provenance. The fixed production factory remains
all-real and generic test/demo composition remains explicit; no compatibility factory,
no-graph execution path, or caller-selected production mode is retained. (`REG-004`,
`REG-005`, `REG-006`, `REG-011`, `REG-019`)

#### Scenario: Missing mode is rejected without a State write
- **WHEN** a lifecycle reader receives a Bundle State mapping with no explicit
  composition mode
- **THEN** it returns the existing bounded invalid/unsupported State outcome before a
  graph node, State reducer, or lifecycle projection runs and leaves the payload
  unchanged

#### Scenario: Removed full-fake provenance cannot be upgraded
- **WHEN** a State mapping names `full_fake` or an unknown composition mode
- **THEN** the reader rejects it without interpreting it as `all_real`, producing a
  completion claim, or rewriting the mapping

#### Scenario: Trusted executor supplies the initial mode
- **WHEN** a supported graph-backed start publishes a new Bundle
- **THEN** its State receives exactly the selected recipe's explicit mode and no caller
  may replace that fact through a lifecycle action

### Requirement: Bundle graph checkpoints cross one explicit registered serialization boundary

Every code path that opens the Bundle-contained graph store — including the
recoverable graph checkpoint opened for graph execution and resume — SHALL use the
application's explicit msgpack serialization boundary (the same registered-type
serializer the generic host uses), never the serialization library's silent
default. That boundary SHALL register exactly the project value types research
checkpoints persist — `deerflow_deep_research.domain.state.ContentRef`,
`deerflow_deep_research.domain.work_units.AttemptStatus`, and
`deerflow_deep_research.domain.wave1.Wave1OpenQuestionRef` — and strict msgpack
mode SHALL keep failing closed for every other project type. Reading or resuming a
research checkpoint SHALL produce no unregistered-project-type deserialization
warnings, and the set of registered types SHALL stay equal to the set of project
types actually persisted in research checkpoints. (`REG-022`)

#### Scenario: The bundle graph store opens with the registered serializer
- **WHEN** a run opens its Bundle-contained graph checkpoint store
- **THEN** the store's serializer is the application's explicit registered-type
  boundary, and a checkpoint written and read through it round-trips
  `ContentRef`, `AttemptStatus`, and `Wave1OpenQuestionRef` values faithfully

#### Scenario: Wave1 open-question projections round-trip under strict mode
- **WHEN** a checkpoint containing `wave1_open_questions` entries is deserialized
  with strict msgpack mode enabled
- **THEN** the projection entries decode as the registered project type without a
  blocked or warned unregistered-type deserialization

#### Scenario: Strict mode still blocks unlisted project types
- **WHEN** strict msgpack mode deserializes a payload carrying a project type
  outside the registered boundary
- **THEN** the deserialization is blocked and the registered types remain usable

### Requirement: A suspended bundle without pending input is legally recoverable

When a Run Bundle's lifecycle projects an active suspended state whose pending
request id is absent — a process death that interrupted graph execution after a
human request was already consumed — the lifecycle SHALL project
`legal_next_action = RESUME` for that bundle, and the resume path SHALL
continue the run from its durable graph checkpoint without requiring or
fabricating any human response. Such a resume SHALL hold the existing execution
exclusion lease, SHALL re-enter the existing compiled graph at its persisted
checkpoint, and SHALL NOT write terminal state, mutate terminal invariance for
other bundles, or bypass any gate. A bundle whose suspended state carries a
pending human request SHALL keep the existing answer-resume path unchanged, and
terminal bundles SHALL keep REFINE/START unchanged. (`REG-023`)

#### Scenario: Orphaned mid-flight bundle projects RESUME
- **WHEN** the lifecycle projects a suspended bundle whose pending request id
  is absent and no live execution lease is held
- **THEN** the projected legal next action is RESUME rather than REFINE or
  STATUS

#### Scenario: Orphan resume continues from the durable checkpoint without a fabricated answer
- **WHEN** the resume path executes for such a bundle
- **THEN** the graph re-enters at its persisted checkpoint under the execution
  exclusion lease, no human response is constructed or required, and the run
  proceeds through its normal phase machinery to a natural terminal

#### Scenario: Pending-input and terminal contracts are unchanged
- **WHEN** a suspended bundle carries a pending human request, or a bundle is
  terminal
- **THEN** the projected legal next action matches the pre-change contract
  exactly (RESUME via answer for pending input; REFINE/START for terminals)
