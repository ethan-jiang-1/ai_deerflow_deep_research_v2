> req: NPC-002

## MODIFIED Requirements

### Requirement: Node prompts have a complete deterministic review catalog

The graph-owned prompt catalog SHALL define a stable, synthetic case for every top-level
node prompt-builder function in `graph/nodes/**/prompts.py` whose body directly
constructs a `NodeExecutionRequest`. A builder with a `repair_error` parameter SHALL
have both initial and repair cases; a dedicated repair builder SHALL have its repair
case. The catalog generator SHALL render only those cases through the shared rendering
interface. When an explicit reviewer runs `make prompt-dump`, it SHALL emit an ignored
local Markdown index and one stable case file below
`deep_research_harness/.node-prompt-review/`. The project SHALL not commit that tree or
register it as a required structural path. Each case file SHALL show the stable case
identity, exact system policy, exact final human message, and clearly labelled requested
tool state, minimum calls, and call limit. It SHALL not contain real-user text, runtime
configuration, provider data, credentials, sandbox identity, timestamps, or a locally
resolved tool inventory. (`NPC-002`)

`make prompt-dump-check` SHALL remain a read-only convenience wrapper over the same
generator check adapter. It SHALL validate an already generated local review tree and
report a missing, stale, unsafe, or unexpected tree without writing. It SHALL not be
selected by `UV_OFFLINE=1 make verify` as a committed-tree freshness baseline. Instead,
the focused fast deterministic selection SHALL retain source-level catalog-inventory,
shared-renderer, and temporary-tree generation checks; it SHALL neither require nor
create the ignored local review workspace.

#### Scenario: A reviewer creates an ignored prompt projection on demand
- **WHEN** a node prompt builder or shared policy changes and a reviewer runs `make prompt-dump`
- **THEN** the generator creates a deterministic projection only below `deep_research_harness/.node-prompt-review/`, Git ignores that workspace, and no runtime path reads it as prompt or execution authority

#### Scenario: Clean deterministic verification has no local-review prerequisite
- **WHEN** a clean checkout without `deep_research_harness/.node-prompt-review/` runs `UV_OFFLINE=1 make verify`
- **THEN** source-level catalog completeness and rendering evidence runs deterministically without creating or requiring the ignored workspace

#### Scenario: Explicit local review detects stale output without writing
- **WHEN** a reviewer has generated the local workspace and a file is stale, omitted, unsafe, or unexpected
- **THEN** `make prompt-dump-check` fails read-only; rerunning `make prompt-dump` is the bounded recovery and does not create a tracked change
