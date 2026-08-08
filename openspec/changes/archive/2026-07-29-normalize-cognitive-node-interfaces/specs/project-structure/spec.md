> req: PRS-014

## ADDED Requirements

### Requirement: Reader-interface validation uses canonical downstream governance paths

The non-runtime cognitive-node reader checker, its fixtures, and its focused
contract tests SHALL live under canonical `agent/` paths registered in
`openspec/governance/project-structure.toml`. The architecture checker SHALL verify
that those paths are present without treating `workflow.md` as Python source,
runtime configuration, a prompt resource, or an importable module. No reader
validation implementation or test for this capability SHALL be added under
`backend/` or `frontend/`.

#### Scenario: Registered reader validation passes structure governance
- **WHEN** the project-structure checker inspects the implemented reader interface
- **THEN** it finds the registered downstream checker and focused test paths and no
  corresponding upstream implementation path

#### Scenario: Invalid reader-validation registration is rejected
- **WHEN** a required reader-validation path is absent or its registry entry is
  placed under `backend/` or `frontend/`
- **THEN** the structural contract fails with the missing-path or forbidden-owner
  violation without interpreting a card as a runtime prompt or import surface
