## MODIFIED Requirements

### Requirement: Recipe factory supports fixture and all-real implementation modes

The demo real recipe SHALL build the all-real recipe with the demo-local
node-agent bridge. Credentialed demo non-interactive runs (embedded smoke real
with `--scripted`, demo TUI real) SHALL declare `profile_intent=minimal` at the
entry, exercising the real product path: the minimal profile drives single-topic
planning, the wave2 gate budget resolver yields two evidence rounds, and the
wave2 synthesis budget carries real-output headroom (product fix, see
node-agent-runtime). The fixture recipe and the production default recipe remain
unchanged; runs without the declared intent keep today's behavior. (`DPL-003`)

#### Scenario: Fixture recipe has no node-agent bridge requirement
- **WHEN** the named fixture-graph verification route is selected with the fixture
  source root enabled
- **THEN** it resolves the complete fixture catalog, has no node-agent bridge
  requirement, executes through its selected graph executor, and does not load real
  model, web, or publication prerequisites. Its completion evidence is the
  fixture final-delivery gate's checkpointed terminal fact and trace, not a report
  artifact claim.

#### Scenario: Real recipe requires the demo-local bridge
- **WHEN** real mode is selected with a valid store factory
- **THEN** it requires the bridge and bootstrap bundle, resolves policy-filtered local
  tools, and executes through the corresponding all-real graph executor

#### Scenario: Non-interactive demo runs declare the minimal intent
- **WHEN** a credentialed demo run starts with the automatic policy
- **THEN** the entry declares `profile_intent=minimal`, and the real product path
  (single-topic planning, two-round gate budget) runs with no demo-specific
  budget wiring
