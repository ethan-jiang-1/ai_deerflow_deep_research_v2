## MODIFIED Requirements

### Requirement: Real Wave0 integrates into the mixed graph off the real topic chain

Real Wave0 SHALL be selectable in a mixed implementation map and SHALL require
`bootstrap=real`, `hitl1=real`, and `topic_planning=real`, because the worker
consumes the real topic registry. Selecting `wave0=real` without the real topic
chain SHALL fail closed before graph invocation. The Wave0 topology SHALL remain
`repair`/`pass`/`exhausted`; the real gate writes the route through the gate kernel.
The full-fake Wave0 fixture path SHALL remain deterministic and SHALL NOT construct
the node-agent bridge. A recipe with real Wave0 and later fake nodes SHALL report
`implementation_mode=mixed`, not `full_fake`; all-fake remains `full_fake`.

#### Scenario: Real Wave0 requires the real topic chain
- **WHEN** a recipe selects `wave0=real` without `topic_planning=real`
- **THEN** recipe construction fails with a typed dependency error before the graph is compiled or invoked

#### Scenario: Topology is unchanged for real Wave0
- **WHEN** the mixed graph selects real Wave0
- **THEN** Wave0 keeps its `repair`/`pass`/`exhausted` routes, the gate writes the route via the gate kernel, and no top-level edge changes

#### Scenario: Mixed Wave0 reports its selected composition
- **WHEN** the real bootstrap, HITL1, topic-planning, and Wave0 chain completes and later phases are fake
- **THEN** the lifecycle reports `implementation_mode=mixed` while accepted evidence and any fake terminal marker retain their separate authorities

#### Scenario: Full-fake Wave0 remains the deterministic fixture path
- **WHEN** the full-fake graph reaches Wave0
- **THEN** it runs the fixture work-unit path without constructing the node-agent bridge, results report `implementation_mode=full_fake`, and the topology snapshot is unchanged
