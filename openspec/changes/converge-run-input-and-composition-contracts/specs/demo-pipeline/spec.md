## ADDED Requirements

### Requirement: Credential-free demo execution is explicitly fixture-graph backed

Every supported credential-free demo CLI or TUI route SHALL construct the complete
fixture catalog, its fixed fixture recipe, and its graph executor before lifecycle
dispatch. The selected executor's `fixture` composition SHALL be persisted in the
Bundle-local State and every later lifecycle projection SHALL read that State fact.
No credential-free route SHALL bind or dispatch a lifecycle without a graph executor,
default its composition to `all_real`, use a probe-only host as execution, or claim
completed research without fixture-graph final-delivery evidence. (`DPL-001`,
`DPL-003`, `DPL-010`)

#### Scenario: Credential-free CLI persists fixture composition
- **WHEN** a supported credential-free CLI starts a Run in a prepared checkout with
  fixture source enabled only for its child process
- **THEN** it runs the complete fixture graph, persists `implementation_mode=fixture`,
  and projects lifecycle facts only from that Bundle-local State and graph result

#### Scenario: Missing graph composition fails before a lifecycle claim
- **WHEN** a credential-free demo route lacks its fixed executor or complete fixture
  catalog
- **THEN** it returns a bounded startup failure before a Bundle State write, graph
  dispatch, or completed-research presentation

### Requirement: Full-fake demo compatibility is retired rather than reclassified

The supported demo command map and documentation SHALL identify credential-free
execution as fixture-graph proof and SHALL not retain a full-fake/no-graph lifecycle,
simulator, command alias, or a distinct completed-presentation contract. The fixed
all-real route and explicit fixture/mixed test composition remain separate and no
caller receives recipe, executor, checkpoint, graph-route, or mode selection
authority. (`DPL-003`, `DPL-005`, `DPL-008`)

#### Scenario: A credential-free route is not a no-graph alias
- **WHEN** an operator inspects supported demo help, Make targets, or README command
  guidance
- **THEN** every zero-credential execution route is described as fixture-graph proof
  and no route names or invokes a full-fake/no-graph lifecycle

