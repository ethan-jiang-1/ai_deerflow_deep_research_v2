> req: TOP-001, TOP-002, TOP-003, TOP-004, TOP-005, TOP-006, TOP-007, TOP-008, TOP-009, TOP-010

## MODIFIED Requirements

### Requirement: Real topic planning integrates into the mixed graph off real HITL1

Real topic planning SHALL be selectable only in the mixed implementation map and
SHALL require `bootstrap=real` and `hitl1=real`, because the planner consumes the
real HITL1 profile constraints. Selecting `topic_planning=real` without real HITL1
SHALL fail closed before graph invocation. The normalized topology SHALL add exactly
`topic_planning --exhausted--> blocked/END` and keep the existing
`topic_planning --next--> wave0` and inbound edges unchanged. topic_planning SHALL
remain a non-gated controller node that writes its own route labels and SHALL NOT
import LangGraph or interrupt. The fixture topic planning path and every other
fake phase SHALL remain unchanged, and the lifecycle result SHALL report
`implementation_mode=mixed` for a mixed recipe.

#### Scenario: Real topic planning requires the real profile chain
- **WHEN** a recipe selects `topic_planning=real` without `hitl1=real` (and thus without `bootstrap=real`)
- **THEN** recipe construction fails with a typed dependency error before the graph is compiled or invoked

#### Scenario: The exhausted route is explicit and minimal
- **WHEN** the mixed graph selects real topic planning
- **THEN** the builder carries a conditional edge `topic_planning -> {next: wave0, exhausted: END}`, topology validation recognizes `exhausted` as terminal `blocked`, and no other topic_planning edge changes

#### Scenario: Full-fake topic planning remains unchanged
- **WHEN** the fixture graph reaches topic planning
- **THEN** fake topic planning routes `next` without calling a model, writing topic state, or taking the real `exhausted` route, and the topology snapshot is unchanged

#### Scenario: The mixed graph completes through real topic planning
- **WHEN** the mixed graph runs real bootstrap, real HITL1, and real topic planning followed by fake Wave0 onward
- **THEN** a valid plan routes `next` into fake Wave0, the lifecycle reports `implementation_mode=mixed`, and no fake terminal marker is presented as findings or a report
