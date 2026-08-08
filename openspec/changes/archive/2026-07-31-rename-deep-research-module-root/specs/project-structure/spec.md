> req: PRS-001

## MODIFIED Requirements

### Requirement: Canonical downstream package ownership

The repository SHALL locate the complete tracked Deep Research module under
`deerflow_research/`. Its source SHALL remain
`deerflow_research/src/deerflow_deep_research/`, its tests SHALL remain under
`deerflow_research/tests/`, and its distribution, import namespace, ownership layers,
and public tool name SHALL remain unchanged. The structure registry, architecture and
charter checkers, and checker-rendered module guide SHALL use that root as the single
canonical downstream location. A tracked `agent/` compatibility directory, symlink,
alias, or second source tree SHALL be rejected.

Current repository-owned consumers of the old physical root, including active specs,
guides, scripts, CI path filters and working directories, Docker inputs, profiles,
tests, and generated evidence, SHALL be migrated to the canonical root. Historical
archives SHALL retain their historical paths unless they actively navigate to, command,
or validate the current checkout. Generic DeerFlow uses of "agent" or `agents/` SHALL
not be rewritten merely because this root changes. (`PRS-001`)

#### Scenario: Canonical root passes structural governance
- **WHEN** the architecture checker inspects the renamed checkout
- **THEN** it finds every registry-required downstream path under
  `deerflow_research/`, renders that root in the controlled guide block, and finds no
  tracked compatibility root at `agent/`

#### Scenario: A stale active path consumer is rejected
- **WHEN** a registry entry, checker fixture, current guide, or active contract still
  identifies `agent/` as the physical Deep Research module root
- **THEN** its focused contract test or governance validation fails with the stale
  repository-relative consumer
