> req: REG-003, REG-015

## MODIFIED Requirements

### Requirement: Graph-owned HITL bridges and resumes from one matching HumanMessage

HITL1 SHALL use a public LangGraph interrupt and checkpoint its pending request before
returning. Suspension SHALL project one stable outer `ToolMessage` with
`name=deep_research`, the active tool-call id, and a version-1
`artifact.human_input` request whose source and request id identify the pending
research interrupt. Its title/context SHALL visibly identify `implementation_mode=full_fake`.
Its bounded text fallback SHALL contain the same version-1 control-result envelope,
including opaque research and request ids, that non-suspended actions return. Resume
tool arguments SHALL contain no answer. Resume SHALL select only the latest eligible
post-suspension `HumanMessage` from trusted runtime state, correlate a structured
response to the pending source/request id when present, and supply the accepted
request id, HumanMessage id, exact value, response kind, and optional option id as one
typed `Command(resume=...)` payload. The resumed HITL1 node SHALL let LangGraph
consume the pending interrupt and SHALL record consumed request/message ids in the
same graph transition; runtime code SHALL NOT patch interrupt tasks or checkpoint
fields outside the graph. Pre-suspension, mismatched, empty, synthetic-summary,
ToolMessage, AIMessage, model-provided argument, and already consumed responses SHALL
NOT advance the graph. After checkpoint inspection, an exact match to the checkpointed
consumed request/message pair SHALL be classified before fresh-answer correlation and
MAY only reproject the current durable pending or terminal result without requiring
the old interrupt to remain pending or invoking another node.

The LangGraph checkpoint interrupt task SHALL be the only pending-request authority;
ResearchState SHALL NOT duplicate a mutable pending descriptor. Request ids SHALL
include a deterministic HITL ordinal derived from prior checkpointed logical HITL1
visits, so retrying the same interrupt is stable. A suspended lifecycle and every
fresh resume SHALL require exactly one pending interrupt descriptor. Multiple
descriptors SHALL always fail closed; zero SHALL be valid only for a typed terminal
lifecycle or the locked action before suspension, and an exact consumed-response
delivery retry MAY only reproject that current durable outcome.

Real HITL1 MAY route an incomplete answer to `needs_followup` and create a later HITL1
interrupt with a new ordinal; the consumed response ids for the incomplete answer
SHALL still be recorded before the follow-up route is published. Durable HITL1
profile-progress fields are allowed only as bounded profile data, not as a second
pending request copy. HITL2 SHALL continue autonomously and SHALL NOT create a
pending interrupt, advertise ordinary route names as choices, or require a user
response.

#### Scenario: Reflected suspension produces the existing UI contract
- **WHEN** the fake graph reaches HITL1 through the reflected async tool
- **THEN** the nested checkpoint contains the pending interrupt before the tool
  returns a `Command` that adds one stable human-input `ToolMessage`, visibly labels
  the card `full_fake`, and ends the current lead-agent turn

#### Scenario: Matching card response resumes once
- **WHEN** the newest eligible HumanMessage carries a non-empty
  `human_input_response` with source `deep_research` and the pending request id
- **THEN** one typed response envelope resumes that interrupt exactly once, LangGraph
  consumes the pending interrupt, the HITL1 node records the response request/message
  ids and completed logical visit in the same transition, and later replay cannot
  advance another interrupt

#### Scenario: Plain-client response can resume
- **WHEN** a client without structured-card metadata supplies one newer visible
  non-empty HumanMessage after the suspension cursor
- **THEN** its normalized text is accepted for the one pending request and no earlier
  message is substituted

#### Scenario: Forged or stale response is denied
- **WHEN** an answer appears only in tool arguments, an AI/ToolMessage, a hidden
  summary, a pre-suspension HumanMessage, a mismatched request id, or a different
  outer thread
- **THEN** resume returns `response_mismatch` for an in-scope correlation failure or
  indistinguishable `research_not_found` for another thread, and leaves the checkpoint
  and pending interrupt unchanged

#### Scenario: Consumed response reprojects durable outcome
- **WHEN** resume is retried with a HumanMessage already recorded as consumed after
  the graph reached its next interrupt or terminal checkpoint
- **THEN** the handler reprojects that current suspended or terminal result without
  invoking a node or accepting the message as another answer

#### Scenario: Autonomous HITL2 never requests a response
- **WHEN** a real or fake graph reaches HITL2 after its valid predecessor
- **THEN** it follows its deterministic route without creating a pending interrupt,
  publishing a human-input request, or accepting a user route choice

#### Scenario: Incomplete real-HITL1 answer creates a fresh pending request
- **WHEN** real HITL1 consumes a matching incomplete response and routes
  `needs_followup`
- **THEN** the next suspended checkpoint contains exactly one new HITL1 interrupt
  with an incremented ordinal, and the consumed response cannot be replayed as the
  follow-up answer

### Requirement: Correlated human input supports advertised closed actions

The existing graph-owned human-input protocol SHALL support `response_kind=action` in
addition to text and choice without making action strings implicit text authority. A
pending request SHALL advertise a bounded closed `action_ids` collection separate from
any choice options; an action response SHALL carry exactly one advertised `action_id`.
Direct and brokered resume SHALL preserve request/message correlation and reject an
action that is unadvertised, mismatched, replayed, malformed, or encoded as text
before node execution. HITL1 MAY advertise only `accept_suggestion`; other nodes
retain their existing response modes and no action may alter lifecycle identity or
routing outside its owning node. (`REG-015`)

#### Scenario: Advertised action passes correlation checks
- **WHEN** a pending HITL1 request advertises `accept_suggestion` and a matching
  typed action response arrives
- **THEN** the generic extractor accepts that action once and HITL1 decides its
  profile effect from checkpointed proposal state

#### Scenario: Text cannot spoof a closed action
- **WHEN** a response sends `accept_suggestion` as ordinary text or sends an action
  not advertised by the pending request
- **THEN** generic validation rejects it before graph-node execution and no response
  is consumed
