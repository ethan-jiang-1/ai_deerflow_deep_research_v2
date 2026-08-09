## MODIFIED Requirements

### Requirement: Shared demo core provides infrastructure, lifecycle transport, and prerequisite checks

The agent project SHALL provide
`deep_research_harness/scripts/_demo_core.py` with the existing demo adapter, fixed
recipe factories, idempotent cleanup, shared lifecycle transport adapter, and
non-network preflight primitives. For graph-backed demo modes, the core SHALL own one
trusted runtime composition boundary that selects a fixed all-real or fixture recipe,
the required bridge, and its executor before lifecycle dispatch. That boundary SHALL
not accept a recipe, executor, checkpoint, or graph-route selection from a CLI, TUI,
or reflected public-tool caller.

For a graph-backed Bundle, the selected recipe's `implementation_mode` SHALL be
persisted with the Bundle and every later lifecycle projection for that Bundle SHALL
read its mode from that authoritative state. Fixture-graph execution SHALL therefore
project `fixture`, and real execution SHALL project `all_real`. Retained state and a
separate full-fake compatibility path without a graph executor retain their existing
`all_real` default; neither path gains a caller-selectable mode input.

The generic control probe host SHALL remain usable only for its explicitly named
infrastructure-probe seam and SHALL NOT be treated as a graph-backed lifecycle
composition or completion source. A graph-backed transport binding without the
matching executor SHALL fail closed before dispatch can reach the existing
`BundleControl` full-fake fallback or claim completed research. The older full-fake
commands SHALL remain separately named, zero-credential demonstrations with their
current deterministic behavior; they SHALL NOT be silently reclassified as
fixture-graph verification.

The core SHALL consume only the shared typed Bundle lifecycle result for Deep Research
identity, status, and legal control; it SHALL not derive `research_id`, select a
Bundle path, or make retained demo material a lifecycle recovery source. (`DPL-001`)

#### Scenario: Demo core remains in the canonical root
- **WHEN** any supported demo entry point imports its common transport implementation
- **THEN** it resolves `deep_research_harness/scripts/_demo_core.py` and receives only
  the shared Bundle lifecycle outcome for a Deep Research Run

#### Scenario: Graph-backed demo cannot fall back to full fake
- **WHEN** a real or fixture-graph entry starts without the graph composition required
  for its fixed mode
- **THEN** it produces a bounded startup failure and does not dispatch a probe-only
  host, reach the full-fake fallback, or report a completed research lifecycle

#### Scenario: Fixture graph projects its selected implementation mode durably
- **WHEN** the named fixture-graph route starts a Bundle and its lifecycle is later
  resumed, reprojected, or inspected through the same trusted scope
- **THEN** each graph-backed result identifies `implementation_mode=fixture` from the
  Bundle-local state, without a command or public-tool mode selector

### Requirement: Recipe factory supports fake and real implementation modes

The graph-backed demo runtime SHALL construct one explicit recipe for each of its two
fixed modes. Fixture-graph mode SHALL load the fixture package's complete catalog and
pass an explicit fixture selection; it SHALL not rely on an omitted implementation map
or a production default. Real mode SHALL pass an explicit all-real selection, the
store factory, and the demo-local bridge factory. The runtime factory SHALL not
construct the recipe dataclass manually, and graph-backed dispatch SHALL use the
executor constructed from that selected recipe.

Fixture-graph mode is a named deterministic verification route and is distinct from
the existing full-fake demonstrations. The full-fake commands retain their established
zero-credential behavior and do not become an alternate spelling for fixture-graph
execution. (`DPL-003`)

#### Scenario: Fixture recipe has no node-agent bridge requirement
- **WHEN** the named fixture-graph verification route is selected with the fixture
  source root enabled
- **THEN** it resolves the complete fixture catalog, has no node-agent bridge
  requirement, executes through its selected graph executor, and does not load real
  model, web, or publication prerequisites. Its completion evidence is the
  fixture final-delivery gate's checkpointed terminal fact and trace, not a report
  artifact claim.

#### Scenario: Real recipe requires the demo-local bridge
- **WHEN** a real demo entry selects its fixed mode with a valid store factory
- **THEN** it requires the bridge and bootstrap bundle, resolves policy-filtered local
  tools, and executes through the corresponding all-real graph executor

### Requirement: CLI real demo validates and explains prerequisite readiness

`deep_research_harness/scripts/demo_real.py` SHALL retain the existing shared
preflight, supported-model and `TAVILY_API_KEY` validation, `--question` and
`--scripted` behavior. After successful preflight it SHALL obtain its all-real recipe
and executor only from the shared demo runtime composition boundary, then use the
shared Bundle lifecycle transport. It SHALL not derive a Run/control identity from the
demo process, a checkpoint, or a retained-session record, and it SHALL not accept
recipe, executor, checkpoint, or graph-route selection as a command input.

If the required all-real composition is unavailable, the CLI SHALL present the bounded
startup outcome and SHALL NOT render a full-fake terminal completion as completed
research.
Its scripted real question SHALL contain an explicit comparison pair expressed in a
supported language before bounded report-delivery evidence is asserted. (`DPL-004`)

#### Scenario: Real demo entry follows the canonical root
- **WHEN** an operator starts the real CLI demo from the downstream module
- **THEN** the executable path is `deep_research_harness/scripts/demo_real.py`, its
  all-real executor comes from the shared demo runtime, and its lifecycle result
  remains Bundle-authoritative

#### Scenario: Real demo cannot claim full-fake completion
- **WHEN** a real CLI composition lacks its all-real executor or returns no
  graph-backed final-delivery evidence
- **THEN** the command exits nonzero without reporting completed research

### Requirement: Makefile provides targets for all demo variants

The `deep_research_harness/Makefile` SHALL retain the existing fake and real CLI/TUI
demo targets, `DEMO_ARGS` forwarding, and direct-extra selection. It SHALL add the
explicit `make demo-fixture-graph` verification target, which enables fixture source
only for its child process and selects the fixture-graph composition route. Its
`--help` and README command description SHALL identify that route as deterministic
graph-composition verification, not as a replacement for `make demo`,
`make demo-scripted`, or `make demo-tui-fake`.

Real targets SHALL load `deep_research_harness/.env` when present; full-fake targets
retain their credential-free behavior. No target SHALL use `deerflow_research/` as a
working directory or fallback, and no `backend/` or `frontend/` file is changed.
(`DPL-005`)

#### Scenario: Demo target loads the renamed local environment
- **WHEN** `make demo-real` runs from the canonical downstream module
- **THEN** it loads `deep_research_harness/.env` when present and does not resolve an
  old-root environment file

#### Scenario: Fixture-graph command is not a full-fake alias
- **WHEN** an operator reads the fixture-graph command help or the README entry map
- **THEN** it identifies `make demo-fixture-graph` as graph verification and retains
  the existing full-fake command names for their separate zero-credential contract
