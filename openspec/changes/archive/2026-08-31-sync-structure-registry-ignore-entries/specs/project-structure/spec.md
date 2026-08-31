> req: PRS-022

## ADDED Requirements

### Requirement: Registered ignore policy mirrors the harness gitignore

The project-structure manifest's registered ignore policy (`[ignored_paths].entries`
in `openspec/governance/project-structure.toml`) SHALL mirror the effective
`deep_research_harness/.gitignore` directory entries exactly — same lines, same
order — and the architecture checker SHALL fail closed (`ignore.entries`) on any
drift between the two. The `.gitignore` remains the fact source for locally ignored
paths; the manifest remains the single registered policy the checker compares
against, and neither surface SHALL be synchronized by editing only one side.
(`PRS-022`)

#### Scenario: Registered ignore policy matches the harness gitignore
- **WHEN** the architecture checker compares `[ignored_paths].entries` with `deep_research_harness/.gitignore`
- **THEN** the comparison passes only on exact ordered equality, and the governance gate exits 0 on a clean working tree

#### Scenario: Ignore policy drift fails closed
- **WHEN** `.gitignore` gains, loses, or reorders an ignored directory without a synchronized manifest entry (as happened when `.uv-cache/` landed in commit `07a7a1c` without a registry sync — BUG-066)
- **THEN** the checker reports `ignore.entries` and exits nonzero instead of accepting a partially synchronized policy
