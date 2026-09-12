> req: WSN-001, WSN-002, WSN-003, WSN-004, WSN-005, WSN-006, WSN-007, WSN-008, WSN-009, WSN-010, WSN-011, WSN-012

## MODIFIED Requirements

### Requirement: Mixed-graph integration
Real wave2_synthesis SHALL require full real chain through wave1. Fixture path unchanged.

#### Scenario: Full real chain compiles
- **WHEN** recipe selects wave2_synthesis=real with full chain
- **THEN** graph compiles and preserves topology shape
