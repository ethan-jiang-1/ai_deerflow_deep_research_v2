> req: PRS-018
> structure: openspec/governance/project-structure.toml

## ADDED Requirements

### Requirement: The upstream gitlink boundary is mechanically verified

The exact project-structure registry SHALL declare one `[upstream_gitlink]` table with
only a normalized repository-relative `path` and a full lower-case 40-character Git
`commit` identifier. Full architecture governance SHALL fail closed unless the declared
path is a non-symlink directory whose root Git index contains exactly one stage-zero
gitlink entry (mode `160000`, with no alternate-stage entry) at that path, the entry's
commit identifier equals the declared identifier, the nested worktree's checked-out
`HEAD` equals that identifier, and its porcelain status, including untracked paths, is
empty. A missing, failed, or malformed metadata query SHALL also fail closed.

The checker SHALL inspect only filesystem and Git metadata needed for those facts. It
SHALL NOT read tracked DeerFlow source files, walk the nested worktree, write to either
repository, initialize or update a submodule, or claim runtime compatibility with the
pinned upstream revision. The checker's `--imports-only` mode SHALL validate the static
registry shape but SHALL NOT query the gitlink; it is not full architecture governance.
(`PRS-018`)

#### Scenario: Matching clean gitlink passes architecture governance
- **WHEN** the registry's two-field gitlink lock matches the sole root stage-zero
  gitlink entry, the nested worktree `HEAD`, and an empty nested porcelain status
- **THEN** architecture governance accepts that upstream-boundary fact while retaining
  its existing downstream structure and import checks

#### Scenario: Missing, malformed, or moved boundary fails closed
- **WHEN** the registry entry is malformed, contains an unexpected field, the declared
  path is absent or a symlink, the root index entry is missing/not the sole mode
  `160000` stage-zero entry, or the index or nested `HEAD` commit differs from the
  declared identifier
- **THEN** architecture governance rejects the checkout with a boundary-specific
  diagnostic and does not reset, checkout, stage, or otherwise alter either repository

#### Scenario: Dirty nested worktree fails closed
- **WHEN** the declared gitlink and commit identifiers otherwise match but the nested
  worktree has a modified, deleted, staged, or untracked path
- **THEN** architecture governance rejects the boundary rather than treating the root
  gitlink entry as sufficient evidence of a clean upstream dependency

#### Scenario: Metadata inspection failure fails closed
- **WHEN** the registry lock is structurally valid but any defined Git metadata command
  cannot execute or returns malformed output
- **THEN** full architecture governance rejects the boundary without falling back to a
  guessed commit, stale receipt, source inspection, or a mutating Git command

#### Scenario: Import-only checking does not inspect the gitlink
- **WHEN** the architecture checker is invoked with `--imports-only` against a manifest
  with a valid static gitlink lock
- **THEN** it validates import/registry syntax without issuing a gitlink metadata query
  or treating the result as full architecture-governance validation

#### Scenario: Intentional upstream bump is explicitly declared
- **WHEN** a reviewed owning change updates both the root gitlink index entry and the
  registry's declared commit identifier to the same new full commit identifier, and the
  nested worktree is clean at that commit
- **THEN** architecture governance accepts the new declared boundary without inferring
  that the checker authorized the bump or proved its runtime compatibility
