> req: HIT-001, HIT-002, HIT-003

## MODIFIED Requirements

### Requirement: Mixed-graph integration requires full real chain

Real HITL2 SHALL require `wave2_synthesis=real` (which transitively requires the
full chain through wave0, wave1, and targeted_evidence). Selecting `hitl2=real`
without `wave2_synthesis=real` SHALL fail before graph invocation. Fixture HITL2
SHALL remain deterministic fixture control without an interrupt. Topology SHALL be
unchanged.

#### Scenario: Real HITL2 requires real wave2_synthesis
- **WHEN** a recipe selects `hitl2=real` without `wave2_synthesis=real`
- **THEN** recipe construction fails with a typed dependency error

#### Scenario: Full-fake HITL2 remains fixture-controlled without an interrupt
- **WHEN** the fixture graph reaches HITL2
- **THEN** it consumes its configured fixture route without a pending input, while
  preserving the declared graph edge and fixture-specific terminal attribution
