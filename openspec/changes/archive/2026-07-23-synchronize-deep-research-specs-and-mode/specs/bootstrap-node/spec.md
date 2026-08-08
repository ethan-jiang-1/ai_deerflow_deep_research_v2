## MODIFIED Requirements

### Requirement: Real bootstrap integrates into the mixed implementation map

The real bootstrap factory SHALL be selectable by the existing per-node fake/real
implementation map (REG-001) in place of the fake while preserving the normalized
topology and the full-fake lifecycle end-to-end path. The full-fake map (all phases
fake) SHALL remain unchanged. The lifecycle handlers SHALL be able to run a mixed
graph, so `ResearchGraphRecipe` SHALL accept an `implementation_modes` override
(default all-fake) without changing the production full-fake recipe. The mixed-graph
end-to-end run SHALL report `implementation_mode=mixed`; it SHALL not claim
full-fake merely because the selected real prefix produces no final research report.

#### Scenario: Mixed map selects the real bootstrap
- **WHEN** the implementation map selects `real` for bootstrap and `fake` for every other phase
- **THEN** the graph compiles, the real bootstrap factory is selected (not the unavailable sentinel), and the normalized node order and all non-bootstrap edges are unchanged

#### Scenario: Lifecycle handlers can run the mixed graph
- **WHEN** `ResearchGraphRecipe` is created with `implementation_modes` setting `bootstrap=real` and every other phase `fake`
- **THEN** the lifecycle handlers compile and run the mixed graph, select the real bootstrap factory, report `implementation_mode=mixed`, and leave the default recipe all-fake

#### Scenario: Full-fake map is unchanged
- **WHEN** the implementation map selects `fake` for every phase
- **THEN** the fake bootstrap is selected, the full-fake lifecycle end-to-end path is unchanged, and results report `implementation_mode=full_fake`

#### Scenario: Mixed end-to-end reports mixed
- **WHEN** the mixed graph runs end-to-end through bootstrap and the remaining fake phases
- **THEN** bootstrap establishes the bundle and routes to `hitl1`, every remaining fake phase completes without a research model call, and the lifecycle result reports `implementation_mode=mixed`
