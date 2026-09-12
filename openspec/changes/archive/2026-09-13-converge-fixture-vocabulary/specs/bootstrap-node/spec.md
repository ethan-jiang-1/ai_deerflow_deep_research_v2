> req: BON-001, BON-002, BON-003, BON-004, BON-005, BON-006, BON-007

## MODIFIED Requirements

### Requirement: Real bootstrap integrates into the mixed implementation map

The real bootstrap factory SHALL be selectable by the existing per-node fake/real implementation
map (REG-001) while preserving the normalized topology and all-fake recipe. The lifecycle
handlers SHALL be able to run a mixed graph, so `ResearchGraphRecipe` SHALL accept an
`implementation_modes` override (default all-fake). The mixed-graph end-to-end run SHALL report
`implementation_mode=mixed`; it SHALL not use `full_fake` merely because the selected prefix
produces no final research report.

#### Scenario: Mixed map selects the real bootstrap
- **WHEN** the implementation map selects `real` for bootstrap and `fake` for every other phase
- **THEN** the graph compiles, the real bootstrap factory is selected (not the unavailable sentinel), and the normalized node order and all non-bootstrap edges are unchanged

#### Scenario: Lifecycle handlers can run the mixed graph
- **WHEN** `ResearchGraphRecipe` is created with `implementation_modes` setting `bootstrap=real` and every other phase `fake`
- **THEN** the lifecycle handlers compile and run the mixed graph, select the real bootstrap factory, report `implementation_mode=mixed`, and leave the default recipe all-fake

#### Scenario: Full-fake map is unchanged
- **WHEN** the implementation map selects `fake` for every phase
- **THEN** the fake bootstrap is selected and the fixture lifecycle end-to-end path is unchanged

#### Scenario: Mixed end-to-end reports mixed
- **WHEN** the mixed graph runs end-to-end through bootstrap and the remaining fake phases
- **THEN** bootstrap establishes the bundle and routes to `hitl1`, every remaining fake phase completes without a research model call, and the lifecycle result reports `implementation_mode=mixed`
