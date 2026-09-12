> req: REN-001, REN-002, REN-003, REN-004, REN-005, REN-006, REN-007, REN-008

## MODIFIED Requirements

### Requirement: Mixed-graph integration with unchanged topology

Real rerun SHALL require `hitl2=real` (which transitively requires the full chain through wave0, wave1, wave2_synthesis, and targeted_evidence). Selecting `rerun=real` without `hitl2=real` SHALL fail before graph invocation. The fixture rerun SHALL remain unchanged, preserving the existing `generation <= MAX_RERUN_GENERATIONS` ceiling check and the `{"next": "topic_planning", "exhausted": END}` edge set. Topology SHALL be unchanged — only the allowed route values expand to include `wave0` and `wave1`.

#### Scenario: Real rerun requires real hitl2
- **WHEN** a recipe selects `rerun=real` without `hitl2=real`
- **THEN** recipe construction fails with a typed dependency error

#### Scenario: Full-fake rerun remains unchanged
- **WHEN** the fixture graph reaches the rerun node at generation 1
- **THEN** it bumps generation to 2 and routes `next` → `topic_planning` with no scope, no invalidation, and no WorkSpec creation

#### Scenario: Real rerun back edges coexist with fake-compat edge keys
- **WHEN** the real rerun node routes to `"topic_planning"`, `"wave0"`, or `"wave1"`
- **THEN** the graph topology accepts the route — the conditional edge map includes the new semantic keys alongside the existing `"next"` key (fake backward compat) and `"exhausted"` key, both of which route to the same targets as before
