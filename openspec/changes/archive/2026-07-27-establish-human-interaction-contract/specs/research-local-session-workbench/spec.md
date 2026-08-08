> req: RWB-007

## ADDED Requirements

### Requirement: Workbench renders broker-projected visible controls

The local workbench SHALL render only `VisibleControl` values projected from the
authorized current pending input and shall submit a selected control id to the broker.
It SHALL not expose action ids, map text to actions, infer a control from a proposal,
or retain submitted reply text. (`RWB-007`)

#### Scenario: Brokered current-proposal control is selected safely
- **WHEN** the current authorized HITL1 session projection exposes a visible
  current-proposal control
- **THEN** workbench sends only its control id and expected request id to the broker
