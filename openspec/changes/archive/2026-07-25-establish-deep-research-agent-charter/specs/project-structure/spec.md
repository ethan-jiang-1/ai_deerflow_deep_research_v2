> req: PRS-004, PRS-009

## ADDED Requirements

### Requirement: The Deep Research charter occupies canonical governance paths

The canonical project structure SHALL register the permanent
`openspec/governance/agent-charter/` tree, including its information-map policy,
its zero-dependency charter checker, and the human-facing `agent/docs/` information
map with its focused runtime-architecture, local-operations, and
testing-and-evaluation documents. `agent/AGENTS.md` SHALL retain the concise
human-authored local-focus gate outside the generated structural block.
`agent/CLAUDE.md` SHALL be the thin Claude Code import entrypoint to that local guide,
while the existing generated block becomes a compact structural locator. The exact
canonical path inventory SHALL remain only in `project-structure.toml`. The
structure registry, generated guide, governance README, OpenSpec configuration
pointer, and focused contract test SHALL remain synchronized. Repository-root
`AGENTS.md` and `CLAUDE.md` are not charter-owned paths and SHALL remain unchanged.
(`PRS-009`)

#### Scenario: Canonical charter paths pass governance
- **WHEN** architecture and charter governance check the repository
- **THEN** the registry, permanent charter tree, module-guide focus gate, docs map,
  OpenSpec authoring pointer, Claude Code compatibility entrypoint, and checker/test
  surfaces are present and mutually discoverable

#### Scenario: Generated guide locates instead of duplicating the inventory
- **WHEN** the architecture checker renders the controlled block in `agent/AGENTS.md`
- **THEN** the block names the registry, source root, test root, ownership-layer
  grammar, and validation command without enumerating every registered path

#### Scenario: Charter navigation drift fails closed
- **WHEN** a required charter policy, its index link, the module-guide focus gate, or
  the proposal-admission rule is removed or malformed
- **THEN** the focused governance check reports the exact missing surface and the
  change cannot pass the deterministic governance target

#### Scenario: Root guide boundary is preserved
- **WHEN** the charter implementation is reviewed for owned paths
- **THEN** it changes only the downstream module guides and project-owned governance
  files, and does not add the charter to root `AGENTS.md` or `CLAUDE.md`

## MODIFIED Requirements

### Requirement: Structural authority survives change archival

The active `project-structure` main spec SHALL own the semantic structure requirements
and SHALL normatively identify `openspec/governance/project-structure.toml` as the
single machine-readable registry for their exact repository-relative roots, current
required paths, ownership layers, forbidden locations, import boundaries, and
top-level node-package grammar. Before the capability's first archive, the one active
owning delta SHALL serve as the pending normative reference; after the main spec
exists, archived deltas SHALL be historical only and SHALL NOT remain authority.
`openspec/governance/architecture-policy.md` SHALL define the authority and
synchronized-change protocol without maintaining a competing path enumeration.
`agent/AGENTS.md` SHALL contain one bounded checker-rendered structural locator plus
human-authored operational guidance. The locator SHALL point to the registry, source
root, test root, ownership-layer grammar, and checker command; it SHALL NOT reproduce
the registry's full required-path inventory. Archived proposals, designs, and tasks
SHALL be historical context only. A deterministic zero-external-dependency governance
checker SHALL reject a missing or invalid registry, a missing lifecycle-appropriate
normative spec reference, controlled-block drift, or a mismatch between the registry
and the repository.

#### Scenario: Active truth is discoverable after archive
- **WHEN** a contributor starts from the active `project-structure` main spec
- **THEN** the spec identifies the permanent policy, exact structure registry,
  compact generated `agent/AGENTS.md` locator, and deterministic checker without
  requiring the archived design

#### Scenario: Synchronized structure passes governance
- **WHEN** the one pending owning delta before first archive or the active main spec
  afterward references the valid registry, the controlled `agent/AGENTS.md` locator
  matches its deterministic rendering, and the required repository paths and
  boundaries conform
- **THEN** the architecture-governance checker passes without semantic inference

#### Scenario: Structural drift fails governance
- **WHEN** the registry and repository disagree, the controlled guide block is not
  the registry's exact rendering, or the lifecycle-appropriate owning spec loses or
  ambiguously declares its normative registry reference
- **THEN** the checker fails with the mechanically mismatched authority surface and no
  archive may complete
