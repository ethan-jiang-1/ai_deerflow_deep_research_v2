# demo-pipeline Delta

> req: DPL-003

## MODIFIED Requirements

### Requirement: Recipe factory supports fixture and all-real implementation modes

The graph-backed demo runtime SHALL construct one explicit recipe for each of its two
fixed modes. Fixture-graph mode SHALL load the fixture package's complete catalog and
pass an explicit fixture selection; it SHALL not rely on an omitted implementation map
or a production default. Real mode SHALL pass an explicit all-real selection, the
store factory, and the demo-local bridge factory. The runtime factory SHALL not
construct the recipe dataclass manually, and graph-backed dispatch SHALL use the
executor constructed from that selected recipe.

Fixture-graph mode is the sole credential-free deterministic execution route. It is
not a simulator or an alternate lifecycle contract. (`DPL-003`)

The demo real recipe SHALL build the all-real recipe with the demo-local
node-agent bridge. The embedded-smoke real entry SHALL accept an explicit
`--profile-intent {minimal,none}` selection for non-interactive (`--scripted`)
runs whose default is `minimal`: without the flag (or with `--profile-intent
minimal`) the entry declares `profile_intent=minimal` exactly as before,
exercising the real product path under the minimal intent (single-topic
planning, two-round wave2 gate budget, real-output wave2 synthesis headroom,
product fix, see node-agent-runtime). With `--profile-intent none` the entry
SHALL start the automatic run WITHOUT an intent declaration — the default
product path (free 1–8 topic planning, default one-round wave2 gate budget,
degraded auto profile). Demo TUI real non-interactive runs continue to declare
`profile_intent=minimal`; the Gateway default path continues to reject
`--scripted` (the automatic policy is embedded-smoke-only). The fixture recipe
and the production default recipe remain unchanged; runs without the declared
intent keep today's behavior. (`DPL-003`)

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
- **WHEN** a credentialed embedded-smoke demo run starts with the automatic policy
  and no explicit `--profile-intent` selection
- **THEN** the entry declares `profile_intent=minimal`, and the real product path
  (single-topic planning, two-round gate budget) runs with no demo-specific
  budget wiring

#### Scenario: Embedded-smoke explicit none runs the default product path
- **WHEN** a credentialed embedded-smoke demo run starts with `--scripted
  --profile-intent none`
- **THEN** the entry sends no `profile_intent` declaration, the automatic
  non-interactive policy stays at today's absent-intent shape, and the default
  product path (free 1–8 topic planning, default one-round wave2 gate budget)
  runs with no demo-specific budget wiring

#### Scenario: Gateway CLI does not fabricate the scripted policy
- **WHEN** an operator passes `--scripted` without selecting embedded smoke
- **THEN** the CLI explains that the automatic policy is embedded-smoke-only, and
  sends no fixed question, synthetic policy, or automatic run through the
  configured public Gateway path
