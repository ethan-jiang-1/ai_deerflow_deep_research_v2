> req: ALR-001, ALR-002

## ADDED Requirements

### Requirement: Validated graph boundary drives ordinary continuation

The downstream HITL2 continuation policy SHALL accept only a bounded, legal graph
predecessor state established by the existing Wave2 quality gate's pass route. It SHALL
select only the existing ordinary `proceed` route and SHALL not reinterpret quality
gaps, call a model, read sandbox content, parse prompt text, or let a presentation
adapter select a route. The node SHALL apply that route through its existing
graph-owned update path; Wave2 and readiness retain all quality-gate authority.

#### Scenario: Ordinary passing state continues without user input
- **WHEN** HITL2 receives a validated ordinary Wave2-pass state
- **THEN** it routes through the policy without creating a pending interrupt or
  requiring a user response

#### Scenario: Untrusted state cannot select a route
- **WHEN** the candidate policy input is malformed, has an unknown predecessor, or is
  not a validated bounded projection
- **THEN** the node fails closed rather than treating it as an autonomous decision

### Requirement: Current HITL2 does not offer a human-decision fallback

This change SHALL not construct a HITL2 `PendingResearchInterrupt` or present an
ordinary graph route name as a user decision. A future preference or irreversible
authorization feature MUST introduce a typed marker, trusted producer, bounded prompt,
recommendation/default, option effects, and response-binding rules in its own reviewed
change before HITL2 may interrupt again.

#### Scenario: No marker does not create a confirmation prompt
- **WHEN** HITL2 is reached in this change
- **THEN** the runtime does not ask for generic confirmation, a route selection, or a
  substitute human-decision marker
