> req: REG-017, REG-018

## ADDED Requirements

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
