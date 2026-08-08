> req: DPL-003, DPL-005, DPL-008

## MODIFIED Requirements

### Requirement: Recipe factory supports fake and real implementation modes

`build_demo_recipe(*, mode, work_unit_store_factory)` SHALL construct one explicit recipe.
Fixture mode SHALL load the fixture package's complete catalog and pass an explicit fixture
selection; it SHALL not rely on an omitted implementation map or a production default.
Real mode SHALL pass an explicit all-real selection, the store factory, and the demo-local
bridge factory. The demo factory SHALL not construct the recipe dataclass manually.

#### Scenario: Fixture recipe has no node-agent bridge requirement
- **WHEN** fixture mode is selected with the fixture source root enabled
- **THEN** it resolves the complete fixture catalog, has `requires_node_agent_bridge=False`,
  and does not load real model or web prerequisites

#### Scenario: Real recipe requires the demo-local bridge
- **WHEN** real mode is selected with a valid store factory
- **THEN** it requires the bridge and bootstrap bundle and resolves policy-filtered local tools

## ADDED Requirements

### Requirement: Fixture-backed demo and local-session commands activate fixture source only for their child process

The fake CLI and TUI demo targets, `demo-sessions` operation path, and fixed-profile
`session-workbench` target SHALL add the registered fixture source root only to their selected
child process when they compose a fixture recipe. Real demo targets, ordinary production
packaging, and reflected runtime launch paths SHALL not add that root. `demo-sessions` and
`session-workbench` remain local demo/operator surfaces and SHALL not turn fixture composition
into reflected public authority. Every target SHALL retain `DEMO_ARGS` forwarding and the
existing credential-free or credentialed prerequisite behavior.

#### Scenario: Fixture demo is self-contained
- **WHEN** `make demo` or `make demo-tui-fake` runs without model or web credentials
- **THEN** its child process can import the fixture package, completes the deterministic
  fixture path, and no production package import resolves to fixture source

#### Scenario: Real demo does not activate fixture source
- **WHEN** `make demo-real` or `make demo-tui` runs with real prerequisites
- **THEN** it constructs the all-real recipe without adding the fixture source root to its
  import path

#### Scenario: Fixture-backed local session tools remain explicitly isolated
- **WHEN** `make demo-sessions` performs a profile-mediated operation or `make session-workbench`
  constructs its fixed local demo profile
- **THEN** only that child process can import the fixture package, the selected recipe remains
  fixture/test-demo-only, and no public reflected runtime path gains fixture source
