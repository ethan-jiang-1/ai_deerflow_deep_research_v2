# project-structure Delta

> req: PRS-021

## ADDED Requirements

### Requirement: Architecture checker enforces the generated structure-locator block

The architecture checker SHALL mechanically enforce the generated structure-locator
block in `deep_research_harness/AGENTS.md`. It SHALL require the block's
`begin_marker` and `end_marker`, declared in the `[guide]` registry table, to appear
exactly once each; SHALL require the block content to match the deterministic render
of the current structure registry; and SHALL exit non-zero with the violated rule
named when the block is missing, duplicated, or drifted. The checker SHALL expose a
`--render-guide` mode that prints the deterministic block for regeneration.
(`PRS-021`)

#### Scenario: Locator block matches the registry

- **WHEN** `deep_research_harness/AGENTS.md` contains exactly one generated
  structure-locator block matching the current registry render
- **THEN** architecture governance passes and the block names the current canonical
  roots, ownership layers, node grammar, and validation command

#### Scenario: Missing or duplicated markers are rejected

- **WHEN** the locator markers are absent or appear more than once in
  `deep_research_harness/AGENTS.md`
- **THEN** the architecture checker exits non-zero naming the missing or duplicated
  marker rule

#### Scenario: Registry drift is rejected

- **WHEN** the block content differs from the deterministic render of the current
  structure registry (for example a stale root or layer)
- **THEN** the architecture checker exits non-zero with `guide.drift`, and
  `--render-guide` prints the correct block for regeneration
