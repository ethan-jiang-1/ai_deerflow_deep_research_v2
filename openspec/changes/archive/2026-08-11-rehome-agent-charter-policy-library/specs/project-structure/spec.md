> req: PRS-009

## ADDED Requirements

### Requirement: The Deep Research Charter and policy library occupy canonical OpenSpec paths

The canonical project structure SHALL register `openspec/agent-charter/` as the
permanent Deep Research Charter tree containing only `README.md` and `charter.md`.
It SHALL register `openspec/policies/` as the one canonical policy library containing
its index, the nine Charter-routed trigger-bearing policy documents, and
`control-placement.md` as cross-cutting review guidance. It SHALL register
`openspec/guardrails/` as the separate home for executable bounded-evidence command
contracts. The old `openspec/governance/agent-charter/` tree and any nested
`agent-charter/policies/` directory SHALL not remain as canonical, required, or
compatibility paths.

The exact inventory SHALL remain only in `openspec/governance/project-structure.toml`.
The structure registry, Charter checker, focused contract test, current authoring
pointer, and downstream entry documents SHALL remain synchronized with that inventory.
Repository-root `AGENTS.md` and `CLAUDE.md` are not Charter-owned paths and SHALL
remain unchanged. (`PRS-009`)

#### Scenario: Canonical Charter and policy-library paths pass governance
- **WHEN** architecture and Charter governance check the repository
- **THEN** the registry, top-level Charter entry, complete policy library, guardrail
  boundary, module-guide focus gate, OpenSpec authoring pointer, and focused checker/test
  surfaces are present and mutually discoverable

#### Scenario: A legacy nested tree cannot masquerade as the current route
- **WHEN** the registry, checker, or current navigation points only to
  `openspec/governance/agent-charter/` or a nested `agent-charter/policies/` tree
- **THEN** deterministic governance reports the missing canonical path rather than
  accepting the legacy location or a duplicate compatibility copy

#### Scenario: Policy prose and executable guardrails remain distinct
- **WHEN** a contributor follows the Charter route to a selected policy or an
  executable closeout-evidence command
- **THEN** the policy resolves under `openspec/policies/` and the command resolves
  under `openspec/guardrails/` without either directory claiming runtime or native
  archive authority

#### Scenario: Root guide boundary is preserved
- **WHEN** the Charter/policy topology is reviewed for owned paths
- **THEN** it changes only project-owned OpenSpec and downstream entry surfaces and
  does not add the Charter to repository-root `AGENTS.md` or `CLAUDE.md`
