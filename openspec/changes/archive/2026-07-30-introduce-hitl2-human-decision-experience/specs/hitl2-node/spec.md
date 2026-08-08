> req: HIT-001, HIT-002, HIT-003

## RENAMED Requirements

- FROM: `### Requirement: Interrupt presents brief and parses closed-set user decision`
- TO: `### Requirement: HITL2 retains autonomous continuation without a human interrupt`

## MODIFIED Requirements

### Requirement: HITL2 retains autonomous continuation without a human interrupt

HITL2 SHALL not use the interrupt/resume pipeline. The fake factory SHALL consume its
configured fixture route as test control without a `PendingResearchInterrupt`; the
real factory SHALL apply the validated autonomous `proceed` route. Ordinary route
names SHALL NOT be shown as user decisions. A future human-decision feature MUST
define a separate typed authority marker, trusted producer, bounded prompt,
response-binding rules, and options contract in its own reviewed change before it may
restore an HITL2 interrupt.

#### Scenario: Fixture routing remains graph-testable without an interrupt
- **WHEN** a deterministic fake fixture selects any existing HITL2 route
- **THEN** the graph takes that route without a pending input or a user-attributed
  terminal reason

### Requirement: Mixed-graph integration requires full real chain

Real HITL2 SHALL require `wave2_synthesis=real` (which transitively requires the
full chain through wave0, wave1, and targeted_evidence). Selecting `hitl2=real`
without `wave2_synthesis=real` SHALL fail before graph invocation. Full-fake HITL2
SHALL remain deterministic fixture control without an interrupt. Topology SHALL be
unchanged.

#### Scenario: Real HITL2 requires real wave2_synthesis
- **WHEN** a recipe selects `hitl2=real` without `wave2_synthesis=real`
- **THEN** recipe construction fails with a typed dependency error

#### Scenario: Full-fake HITL2 remains fixture-controlled without an interrupt
- **WHEN** the full-fake graph reaches HITL2
- **THEN** it consumes its configured fixture route without a pending input, while
  preserving the declared graph edge and fixture-specific terminal attribution

#### Scenario: Fixture gate rules preserve lifecycle outcomes
- **WHEN** the fake graph runs with fixture gate definitions encoding the same
  sequences as the prior `fixture_plan`
- **THEN** every top-level phase transition follows the same path and every E2E
  lifecycle test for happy completion, repair, rerun, stop, cancel, and stale-response
  denial passes while Wave0/Wave1 exercise validated work-unit submission

#### Scenario: Full-fake HITL1 remains unchanged
- **WHEN** the full-fake graph reaches HITL1
- **THEN** fake HITL1 presents its hardcoded fixture prompt, accepts the matching
  response once, routes `accepted`, and does not call a model, request-bundle writer,
  or real-HITL1 follow-up route

#### Scenario: Real HITL1 follow-up does not affect gated phase routing
- **WHEN** real HITL1 routes `needs_followup` or `exhausted`
- **THEN** gate evaluation is not invoked for HITL1, and gated phase route labels
  come from their gate definitions
