## ADDED Requirements

### Requirement: Credential-free TUI uses the fixed fixture graph

The credential-free standalone TUI SHALL use the same fixture catalog, fixed fixture
recipe, graph executor, shared Bundle lifecycle result, and truthful `fixture`
composition fact as the credential-free CLI. It SHALL remain a non-product
visualization, require no model, Gateway, network, or real-demo configuration, and
shall not construct a no-graph lifecycle or infer completed research from local UI
state. (`RED-001`, `RED-002`, `RED-008`)

#### Scenario: Credential-free TUI starts a fixture-backed Run
- **WHEN** an operator starts the named credential-free TUI route in a prepared
  checkout with fixture source available to that child process
- **THEN** its shared updates originate from the fixture graph and Bundle-local State
  identifies `implementation_mode=fixture`

#### Scenario: Credential-free TUI lacks its fixture executor
- **WHEN** the TUI cannot construct its fixed fixture executor
- **THEN** it presents the bounded startup fault and does not create a State record or
  render completed research

