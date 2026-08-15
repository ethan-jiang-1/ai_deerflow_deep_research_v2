> req: PRS-009

## RENAMED Requirements

- FROM: `### Requirement: The Deep Research Charter and policy library occupy canonical OpenSpec paths`
- TO: `### Requirement: Deep Research Change Guidance and closeout evidence occupy canonical OpenSpec paths`

## MODIFIED Requirements

### Requirement: Deep Research Change Guidance and closeout evidence occupy canonical OpenSpec paths

The canonical project structure SHALL register `openspec/change-guidance/` as the
permanent Deep Research design/admission route. Its root SHALL contain exactly
`README.md`, `principles.md`, `node-edit-map.md`, and one `policies/` directory. The
policy directory SHALL contain exactly the ten canonical trigger-bearing policy
documents and SHALL NOT contain a second routing index. The canonical names, triggers,
Focus Card fields, conditional review schemas, closed postures, and guidance-only
authority of those policies SHALL remain unchanged.

The canonical project structure SHALL register `openspec/governance/closeout-evidence/`
as the home for the selected-change closeout command and its README. It SHALL register
`openspec/README.md` as the bounded navigation entry that distinguishes native
`config.yaml`, `specs/`, and `changes/` workflow surfaces from project Change Guidance
and project governance. The retired `openspec/agent-charter/`, `openspec/policies/`,
and `openspec/guardrails/` roots SHALL NOT remain as canonical, required, symlinked,
redirected, duplicated, or compatibility paths.

The exact inventory SHALL remain only in `openspec/governance/project-structure.toml`.
The structure registry, Change Guidance checker, focused contract test, current
authoring pointers, and downstream entry documents SHALL remain synchronized with that
inventory. Deterministic governance SHALL compare the exact registered Change Guidance
and policy member sets with the checked-out tree and reject missing, extra, duplicate,
or legacy-only members. Repository-root `AGENTS.md` and `CLAUDE.md` SHALL remain
unchanged. (`PRS-009`)

#### Scenario: Canonical Charter and policy-library paths pass governance
- **WHEN** architecture and Change Guidance governance check the target repository
- **THEN** the exact guidance root, complete policy library, closeout-evidence command
  boundary, OpenSpec root navigation, module-guide focus gate, authoring pointer, and
  focused checker/test surfaces are present and mutually discoverable

#### Scenario: An unregistered guidance or policy member fails governance
- **WHEN** the checked-out Change Guidance root or policy library contains an extra
  file, a second policy index, or omits a registered member
- **THEN** deterministic governance reports the exact-member mismatch rather than
  accepting required-path presence as sufficient evidence

#### Scenario: A legacy nested tree cannot masquerade as the current route
- **WHEN** current structure or navigation retains only a retired root or adds a
  compatibility copy beside the canonical Change Guidance or closeout-evidence tree
- **THEN** deterministic governance rejects the retired or duplicate surface instead
  of treating it as a valid route

#### Scenario: Policy prose and executable guardrails remain distinct
- **WHEN** a contributor follows Change Guidance to a selected policy or follows
  governance navigation to the closeout-evidence command
- **THEN** policy prose resolves only under `change-guidance/policies/` and the command
  resolves only under `governance/closeout-evidence/`, without either surface claiming
  runtime or native archive authority

#### Scenario: Root guide boundary is preserved
- **WHEN** the target topology is reviewed for owned paths
- **THEN** it changes only project-owned OpenSpec and downstream entry surfaces and
  does not add Change Guidance to repository-root `AGENTS.md` or `CLAUDE.md`
