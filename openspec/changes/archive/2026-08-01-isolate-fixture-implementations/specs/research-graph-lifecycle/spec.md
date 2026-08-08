> req: REG-001, REG-003, REG-004, REG-016, REG-019

## MODIFIED Requirements

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
production-owned construction path and supplies its fixed real selection itself; its internal
compatibility alias accepts no selection or mode argument. Node packages SHALL use one canonical
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
- **WHEN** internal code uses the named all-real factory or its compatibility alias
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

### Requirement: Graph-owned HITL bridges and resumes from one matching HumanMessage

HITL1 SHALL use a public LangGraph interrupt and checkpoint its pending request before
returning. Suspension SHALL project one stable outer `ToolMessage` with
`name=deep_research`, the active tool-call id, and a version-1
`artifact.human_input` request whose source and request id identify the pending research
interrupt. A reflected public suspension SHALL visibly identify
`implementation_mode=all_real`; a fixture demo MAY identify its separately selected
fixture composition. Its bounded text fallback SHALL contain the same version-1
control-result envelope, including opaque research and request ids, that non-suspended
actions return. Resume tool arguments SHALL contain no answer. Resume SHALL select only the
latest eligible post-suspension `HumanMessage` from trusted runtime state, correlate a
structured response to the pending source/request id when present, and supply the accepted
request id, HumanMessage id, exact value, response kind, and optional option id as one typed
`Command(resume=...)` payload. The resumed HITL1 node SHALL let LangGraph consume the pending
interrupt and SHALL record consumed request/message ids in the same graph transition; runtime
code SHALL NOT patch interrupt tasks or checkpoint fields outside the graph. Pre-suspension,
mismatched, empty, synthetic-summary, ToolMessage, AIMessage, model-provided argument, and
already consumed responses SHALL NOT advance the graph. After checkpoint inspection, an exact
match to the checkpointed consumed request/message pair SHALL be classified before fresh-answer
correlation and MAY only reproject the current durable pending or terminal result without
requiring the old interrupt to remain pending or invoking another node.

The LangGraph checkpoint interrupt task SHALL be the only pending-request authority;
ResearchState SHALL NOT duplicate a mutable pending descriptor. Request ids SHALL include a
deterministic HITL ordinal derived from prior checkpointed logical HITL1 visits, so retrying
the same interrupt is stable. A suspended lifecycle and every fresh resume SHALL require
exactly one pending interrupt descriptor. Multiple descriptors SHALL always fail closed; zero
SHALL be valid only for a typed terminal lifecycle or the locked action before suspension, and
an exact consumed-response delivery retry MAY only reproject that current durable outcome.

For real HITL1, an incomplete answer MAY route `needs_followup` and create a later HITL1
interrupt with a new ordinal; the consumed response ids for the incomplete answer SHALL still
be recorded before the follow-up route is published. Durable HITL1 profile-progress fields are
allowed only as bounded profile data, not as a second pending request copy. HITL2 SHALL
continue autonomously and SHALL NOT create a pending interrupt, advertise ordinary route names
as choices, or require a user response.

#### Scenario: Reflected real suspension produces the UI contract
- **WHEN** the all-real graph reaches HITL1 through the reflected async tool with ready
  runtime prerequisites
- **THEN** the nested checkpoint contains the pending interrupt before the tool returns a
  `Command` that adds one stable human-input `ToolMessage`, visibly labels the card
  `all_real`, and ends the current lead-agent turn

#### Scenario: Matching card response resumes once
- **WHEN** the newest eligible HumanMessage carries a non-empty `human_input_response` with
  source `deep_research` and the pending request id
- **THEN** one typed response envelope resumes that interrupt exactly once, LangGraph consumes
  the pending interrupt, the HITL node records the response request/message ids and completed
  logical visit in the same transition, and later replay cannot advance another interrupt

#### Scenario: Plain-client response can resume
- **WHEN** a client without structured-card metadata supplies one newer visible non-empty
  HumanMessage after the suspension cursor
- **THEN** its normalized text is accepted for the one pending request and no earlier message
  is substituted

#### Scenario: Forged or stale response is denied
- **WHEN** an answer appears only in tool arguments, an AI/ToolMessage, a hidden summary, a
  pre-suspension HumanMessage, a mismatched request id, or a different outer thread
- **THEN** resume returns `response_mismatch` for an in-scope correlation failure or
  indistinguishable `research_not_found` for another thread, and leaves the checkpoint and
  pending interrupt unchanged

#### Scenario: Consumed response reprojects durable outcome
- **WHEN** resume is retried with a HumanMessage already recorded as consumed after the graph
  reached its next interrupt or terminal checkpoint
- **THEN** the handler reprojects that current suspended or terminal result without invoking a
  node or accepting the message as another answer

#### Scenario: Autonomous HITL2 never requests a response
- **WHEN** a real or explicitly composed fixture graph reaches HITL2 after its valid
  predecessor
- **THEN** it follows its deterministic route without creating a pending interrupt, publishing
  a human-input request, or accepting a user route choice

#### Scenario: Incomplete real-HITL1 answer creates a fresh pending request
- **WHEN** real HITL1 consumes a matching incomplete response and routes `needs_followup`
- **THEN** the next suspended checkpoint contains exactly one new HITL1 interrupt with an
  incremented ordinal, and the consumed response cannot be replayed as the follow-up answer

### Requirement: Lifecycle actions enforce typed and idempotent transitions

An authorized reopened operation SHALL use the same canonical identity validation and typed
transition handlers as an in-thread action; it SHALL revalidate the authoritative checkpoint
before mutation and fail closed before graph invocation on resolver or binding failure.
Reopened resume SHALL validate the brokered response against the latest pending interrupt and
expected request id while the handler's namespace lock is held, and SHALL recognize an
identical brokered retry without invoking a graph node twice. The local broker SHALL enter the
shared retained-root dispatch lease before this handler path so a fresh local process cannot
race a normal local lifecycle action.

#### Scenario: Public start returns an opaque scope and suspends in real mode
- **WHEN** a trusted user/thread starts a new public research lifecycle with ready real
  prerequisites
- **THEN** the handler binds the latest eligible visible HumanMessage, derives a stable opaque
  research id, records its message correlation and request digest, runs to real HITL1, and
  returns the versioned suspended result without exposing the internal checkpoint key

#### Scenario: Repeated start reprojects instead of duplicating
- **WHEN** the same start is retried after the nested HITL checkpoint was committed but before
  its outer ToolMessage was delivered
- **THEN** the same research id and pending request are recovered and reprojected with the
  current tool-call id, no node runs twice, and no orphan lifecycle is created

#### Scenario: Invalid start message is denied
- **WHEN** no visible genuine HumanMessage remains after synthetic-context filtering, or the
  newest visible candidate is missing a stable id, empty/oversized, a human-input response, or
  otherwise ineligible as a new research request
- **THEN** start returns redacted `start_message_invalid` before namespace derivation or
  checkpoint mutation

#### Scenario: Different start in the same thread does not create a multi-active run
- **WHEN** a different eligible HumanMessage requests start in an outer thread that already
  owns a suspended or terminal research lifecycle for the current recipe revision
- **THEN** the action returns `thread_research_exists` with the existing opaque id/status and
  does not invoke or reset the graph

#### Scenario: Status is read-only
- **WHEN** status is requested for a suspended or terminal lifecycle
- **THEN** it reports the bounded version-1 control result with typed phase, generation,
  status, pending request metadata if any, and durability class without invoking a node or
  changing the checkpoint

#### Scenario: Fixture terminal remains demo/test-only
- **WHEN** an explicitly composed fixture lifecycle reaches final delivery
- **THEN** its result is marked as fixture composition, contains only the deterministic fixture
  marker, and is not returned through the reflected public research lifecycle

#### Scenario: Cancel follows graph routing
- **WHEN** cancel targets a suspended lifecycle
- **THEN** the pending interrupt receives an internal cancel decision, the graph records
  terminal `cancelled`, and a repeated cancel returns the same terminal state

#### Scenario: Cross-scope and invalid transitions fail closed
- **WHEN** another outer thread reuses the research id, a fresh response resumes with no
  pending interrupt or targets a terminal lifecycle, or start targets an existing namespace
- **THEN** wrong scope returns `research_not_found`, fresh no-pending or terminal resume
  returns `invalid_transition`, same-message start reprojects, different-message start returns
  `thread_research_exists`, and no path mutates or discloses another scope's lifecycle

#### Scenario: Gate-blocked terminal reason replaces fixture exhaustion
- **WHEN** gate fatigue escalation or budget exhaustion produces a `BLOCKED` verdict
- **THEN** `terminal_reason` is `GATE_BLOCKED` and the lifecycle transitions to typed terminal
  `blocked`

#### Scenario: A foreign opaque id cannot select a namespace
- **WHEN** a caller supplies a research id that differs from the id derived from its trusted
  user/thread envelope
- **THEN** lifecycle rejects it without opening a checkpoint, invoking a graph node, or
  revealing whether that id has a binding

#### Scenario: Reopened cancel cannot select a foreign namespace
- **WHEN** a broker operation resolves a binding for another user or outer thread
- **THEN** it denies before namespace derivation, checkpoint mutation, or node invocation

### Requirement: Canonical bundle locator is checkpointed physical-root state

`ResearchState` SHALL carry a bounded optional controller-owned `bundle_directory` that
selects the canonical physical root for graph content artifacts and retained session metadata.
Every new public real lifecycle start SHALL set the trusted timestamp-prefixed locator before
graph invocation; it is not derived from user input, mutable by nodes/workers, or a
replacement for `research_id`. An explicitly composed fixture locator SHALL remain
session-metadata-only and SHALL not imply graph artifact materialization. Compatible existing
checkpoints without the field SHALL deterministically use legacy `r_<research-id>` roots
without migration.

#### Scenario: Locator does not replace lifecycle identity
- **WHEN** a new timestamp-prefixed locator is checkpointed
- **THEN** research scope, namespace derivation, binding, marker identity, and CLI inspect
  argument remain the opaque `research_id`

#### Scenario: Fixture demo has a stable metadata-only locator
- **WHEN** an explicit fixture lifecycle starts through a demo/test composition root
- **THEN** its checkpoint and retained session use the same trusted timestamp-prefixed locator,
  while inspection identifies the content layout as session metadata only unless a real
  bootstrap marker exists
