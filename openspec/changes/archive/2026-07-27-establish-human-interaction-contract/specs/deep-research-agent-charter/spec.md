> req: DRC-007

## ADDED Requirements

### Requirement: Human-interaction integrity is a routed recurring review policy

The charter SHALL route a focused human-interaction-integrity policy for a change that
adds or revises a human decision, semantic input, visible control, or interaction
recovery surface. The policy SHALL require reviewers to identify the semantic subject,
candidate interpretation authority, graph/action authority, visible legal controls,
adapter binding boundary, failure recovery, and lowest deterministic transcript seam.
It SHALL state that the policy is guidance only and that exact behavior belongs in an
owning capability specification. (`DRC-007`)

#### Scenario: An interaction change has a review route
- **WHEN** a contributor changes a human-input or visible-control surface
- **THEN** the charter index directs that contributor to the focused policy without
  making charter prose a runtime controller
