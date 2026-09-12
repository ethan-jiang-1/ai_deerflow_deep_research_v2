> req: WAN-001, WAN-002, WAN-003, WAN-004, WAN-005, WAN-006, WAN-007, WAN-008, WAN-009, WAN-010, WAN-011, WAN-012

## MODIFIED Requirements

### Requirement: Real Wave0 integrates into the mixed graph off the real topic chain

Real Wave0 SHALL be selectable only in the mixed implementation map and SHALL
require `bootstrap=real`, `hitl1=real`, and `topic_planning=real`, because the
worker consumes the real topic registry. Selecting `wave0=real` without the real
topic chain SHALL fail closed before graph invocation. The Wave0 topology SHALL be
unchanged (`repair`/`pass`/`exhausted`); the real gate writes the route via the
gate kernel. The fixture Wave0 path SHALL remain deterministic and
SHALL NOT construct the node-agent bridge. The lifecycle result SHALL remain
`implementation_mode=mixed` for this recipe composition.

#### Scenario: Real Wave0 requires the real topic chain
- **WHEN** a recipe selects `wave0=real` without `topic_planning=real`
- **THEN** recipe construction fails with a typed dependency error before the graph is compiled or invoked

#### Scenario: Topology is unchanged for real Wave0
- **WHEN** the mixed graph selects real Wave0
- **THEN** Wave0 keeps its `repair`/`pass`/`exhausted` routes, the gate writes the route via the gate kernel, and no top-level edge changes

#### Scenario: Full-fake Wave0 remains the deterministic fixture path
- **WHEN** the fixture graph reaches Wave0
- **THEN** it runs the fixture work-unit path without constructing the node-agent bridge and the topology snapshot is unchanged
