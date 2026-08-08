## MODIFIED Requirements

### Requirement: Lifecycle actions enforce typed and idempotent transitions

An authorized reopened operation SHALL use the same canonical identity validation and
typed transition handlers as an in-thread action; it SHALL revalidate the
authoritative checkpoint before mutation and fail closed before graph invocation on
resolver or binding failure. Reopened resume SHALL validate the brokered response
against the latest pending interrupt and expected request id while the handler's
namespace lock is held, and shall recognize an identical brokered retry without
invoking a graph node twice. The local broker SHALL enter the shared retained-root
dispatch lease before this handler path so a fresh local process cannot race a normal
local lifecycle action. (`REG-004`)

Every `DeepResearchControlResult` SHALL carry a closed
`implementation_mode` derived solely from its handler's resolved
`ResearchGraphRecipe`: `full_fake` when every logical node is fake, `all_real`
when every logical node is real, and `mixed` otherwise. The mode SHALL be supplied
to normal, status, resumed, terminal, and handler-generated denial projections; it
SHALL NOT be selected by caller input, checkpoint state, manifests, session bindings,
or model output. It describes implementation composition only and SHALL NOT assert
provider success, accepted evidence, report quality, or public-entry availability.

#### Scenario: Start returns an opaque scope and suspends
- **WHEN** a trusted user/thread starts a new all-fake research lifecycle
- **THEN** the handler binds the latest eligible visible HumanMessage, derives a stable opaque research id, records its message correlation and request digest, runs to HITL1, and returns the versioned suspended result with `implementation_mode=full_fake` without exposing the internal checkpoint key

#### Scenario: Recipe mode is stable across projections
- **WHEN** start, status, resume, cancel, a duplicate delivery, or a handler denial is projected through one all-real or mixed recipe
- **THEN** every returned control result carries that same recipe-derived mode without reading or changing checkpoint control state

#### Scenario: Repeated start reprojects instead of duplicating
- **WHEN** the same start is retried after the nested HITL checkpoint was committed but before its outer ToolMessage was delivered
- **THEN** the same research id and pending request are recovered and reprojected with the current tool-call id, no node runs twice, and no orphan lifecycle is created

#### Scenario: Invalid start message is denied
- **WHEN** no visible genuine HumanMessage remains after synthetic-context filtering, or the newest visible candidate is missing a stable id, empty/oversized, a human-input response, or otherwise ineligible as a new research request
- **THEN** start returns redacted `start_message_invalid` before namespace derivation or checkpoint mutation and retains the handler recipe's implementation mode

#### Scenario: Different start in the same thread does not create a multi-active run
- **WHEN** a different eligible HumanMessage requests start in an outer thread that already owns a suspended or terminal research lifecycle
- **THEN** the action returns `thread_research_exists` with the existing opaque id/status, preserves the handler recipe mode, and does not invoke or reset the graph

#### Scenario: Status is read-only
- **WHEN** status is requested for a suspended or terminal lifecycle
- **THEN** it reports the bounded version-1 control result with typed phase, generation, status, pending request metadata if any, durability class, and recipe-derived mode without invoking a node or changing the checkpoint

#### Scenario: Full-fake terminal cannot masquerade as research output
- **WHEN** an all-fake lifecycle reaches final delivery
- **THEN** the result is marked `implementation_mode=full_fake`, contains only a terminal fixture marker, and contains no finding, evidence, citation, report, or claim that real research completed

#### Scenario: Cancel follows graph routing
- **WHEN** cancel targets a suspended lifecycle
- **THEN** the pending interrupt receives an internal cancel decision, the graph records terminal `cancelled`, and a repeated cancel returns the same terminal state with the recipe-derived mode

#### Scenario: All-real demo is not mislabeled full-fake
- **WHEN** a standalone demo dispatches a handler built from the all-real recipe
- **THEN** its suspended, terminal, or denial result reports `implementation_mode=all_real` and does not inherit the public tool's full-fake label

#### Scenario: Cross-scope and invalid transitions fail closed
- **WHEN** another outer thread reuses the research id, a fresh response resumes with no pending interrupt or targets a terminal lifecycle, or start targets an existing namespace
- **THEN** wrong scope returns `research_not_found`, fresh no-pending or terminal resume returns `invalid_transition`, no path mutates or discloses another scope's lifecycle, and the returned mode remains handler-derived

#### Scenario: Gate-blocked terminal reason remains typed
- **WHEN** gate fatigue escalation or budget exhaustion produces a `BLOCKED` verdict
- **THEN** `terminal_reason` is `GATE_BLOCKED`, not `REPAIR_EXHAUSTED`, and the lifecycle transitions to typed terminal `blocked` with the recipe-derived mode

#### Scenario: A foreign opaque id cannot select a namespace
- **WHEN** a caller supplies a research id that differs from the id derived from its trusted user/thread envelope
- **THEN** lifecycle rejects it without opening a checkpoint, invoking a graph node, or revealing whether that id has a binding

#### Scenario: Reopened cancel cannot select a foreign namespace
- **WHEN** a broker operation resolves a binding for another user or outer thread
- **THEN** it denies before namespace derivation, checkpoint mutation, or node invocation
