> req: WON-001, WON-002, WON-003, WON-004, WON-005, WON-006, WON-007, WON-008, WON-009, WON-010, WON-011, WON-012, WON-013

## MODIFIED Requirements

### Requirement: Real Wave1 integrates into mixed graph off full real chain

Real Wave1 SHALL require `bootstrap=real`, `hitl1=real`, `topic_planning=real`,
`wave0=real`, and `targeted_evidence=real`. Selecting `wave1=real` without the full
chain SHALL fail before graph invocation. Topology is unchanged. Fixture Wave1
remains deterministic and does not construct the node-agent bridge.

#### Scenario: Wave1 requires full real chain
- **WHEN** a recipe selects `wave1=real` without `wave0=real` or `targeted_evidence=real`
- **THEN** recipe construction fails with a typed dependency error

#### Scenario: Full-fake Wave1 remains unchanged
- **WHEN** the fixture graph reaches Wave1
- **THEN** it runs the fixture work-unit path without constructing the node-agent bridge
