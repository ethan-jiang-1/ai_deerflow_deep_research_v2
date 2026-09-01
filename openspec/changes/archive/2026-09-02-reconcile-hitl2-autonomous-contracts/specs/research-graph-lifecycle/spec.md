> req: REG-001, REG-002, REG-003, REG-004, REG-005, REG-006, REG-007, REG-008, REG-009, REG-010, REG-011, REG-012, REG-013, REG-014, REG-015, REG-016, REG-017, REG-018, REG-019, REG-020, REG-021, REG-022, REG-023

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
