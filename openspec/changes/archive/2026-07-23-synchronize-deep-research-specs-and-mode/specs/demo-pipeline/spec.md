## MODIFIED Requirements

### Requirement: Recipe factory supports fake and real implementation modes

`build_demo_recipe(*, mode, work_unit_store_factory)` SHALL call
`ResearchGraphRecipe.create()`. Fake mode supplies neither implementation modes nor
a node-agent bridge factory; real mode supplies `ALL_REAL_MODES`, the store factory,
and the demo-local bridge factory. It SHALL not construct the recipe dataclass
manually. Every lifecycle result returned through the selected recipe SHALL expose
the recipe-derived implementation mode: fake mode is `full_fake` and the all-real
demo mode is `all_real`. The mode identifies selected implementation composition,
not provider success, evidence acceptance, or report quality. (`DPL-003`)

#### Scenario: Fake recipe has no node-agent bridge requirement
- **WHEN** fake mode is selected
- **THEN** the recipe has `requires_node_agent_bridge=False` and returned lifecycle
  results report `implementation_mode=full_fake`

#### Scenario: Real recipe requires the demo-local bridge
- **WHEN** real mode is selected with a valid store factory
- **THEN** it requires the bridge and bootstrap bundle, resolves policy-filtered
  local tools, and returned lifecycle results report `implementation_mode=all_real`

#### Scenario: Recipe mode cannot be supplied by a demo caller
- **WHEN** a demo receives a lifecycle result or a pre-graph denial
- **THEN** it uses the host handler's constructed recipe mode and cannot alter the
  mode through question text, a command-line answer, or retained session data
