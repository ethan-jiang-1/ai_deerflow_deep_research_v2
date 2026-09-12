> req: TEL-001, TEL-002, TEL-003, TEL-004, TEL-005, TEL-006, TEL-007, TEL-008

## MODIFIED Requirements

### Requirement: Mixed-graph integration requires full real chain
Real targeted evidence loop SHALL require full real chain through wave2_synthesis. Fixture targeted_evidence SHALL remain deterministic. Topology SHALL be unchanged.

#### Scenario: Full real chain compiles
- **WHEN** recipe selects targeted_evidence=real with full chain through wave2_synthesis
- **THEN** graph compiles and preserves topology shape
