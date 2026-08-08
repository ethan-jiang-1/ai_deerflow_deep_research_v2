> req: HIC-004

## ADDED Requirements

### Requirement: HITL1 deterministic proposal presentation remains action-oriented

For a complete current-proposal interaction, the deterministic presentation context
and node-generated semantic-invalid or semantic-unavailable feedback SHALL retain the
current proposal and its visible control. They SHALL be bounded and state only an
ordinary confirmation/revision/question choice or a legal recovery. They SHALL NOT
teach a hidden action token, expose raw candidate JSON, or require schema or JSON
syntax. Validated model-produced proposal explanation and clarification text remain
bounded candidates governed by `HIC-003`; this requirement does not claim a scripted
fake candidate proves live language quality. Complete-proposal context SHALL NOT
duplicate the trusted action id; the corresponding `HumanInputRequest.action_ids` and
`InteractionProjection.controls` remain the action-binding and visible-control owners.
(`HIC-004`)

#### Scenario: Complete proposal context supports ordinary confirmation
- **WHEN** HITL1 presents a complete current proposal before a person replies
- **THEN** its deterministic context and visible control allow ordinary confirmation,
  revision, or a proposal question without schema/JSON instruction or a duplicated
  action token, while its trusted request action binding and visible control remain
  available

#### Scenario: Closed semantic fallback avoids schema instruction
- **WHEN** semantic intake returns a node-generated invalid or unavailable fallback
- **THEN** the next projection keeps the same proposal/control and gives bounded
  recovery feedback without raw candidate JSON, action-token instruction, or
  schema/JSON teaching

#### Scenario: Revision constraints remain in the proposal rather than feedback
- **WHEN** a person revises the proposal to require first-party sources and citations
- **THEN** the new visible advisory proposal contains those profile constraints and the
  lifecycle presentation keeps the revision pending later confirmation
