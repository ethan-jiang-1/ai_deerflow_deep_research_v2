> req: PRS-009

## MODIFIED Requirements

### Requirement: Deep Research Change Guidance, product context, and closeout evidence occupy canonical OpenSpec paths

The canonical project structure SHALL register `openspec/change-guidance/` as the
permanent Deep Research design/admission route. Its root SHALL contain exactly
`README.md`, `principles.md`, `node-edit-map.md`, and one `policies/` directory. The
policy directory SHALL contain exactly the ten canonical trigger-bearing policy
documents and SHALL NOT contain a second routing index. The canonical names, triggers,
Focus Card fields, conditional review schemas, closed postures, and guidance-only
authority of those policies SHALL remain unchanged.

The canonical project structure SHALL register `openspec/product/` as the sole
product-context directory. Its root SHALL contain exactly `deep-research.md`, the
canonical product-context entry. The product directory SHALL not contain a
`platform/` abstraction, a second product index, a compatibility copy, or a document
that claims runtime or specification authority.

The canonical project structure SHALL register `openspec/governance/closeout-evidence/`
as the home for the selected-change closeout command and its README. It SHALL register
`openspec/README.md` as the bounded navigation entry that distinguishes native
`config.yaml`, `specs/`, and `changes/` workflow surfaces from the Deep Research
product context, project Change Guidance, and project governance. The retired
`openspec/agent-charter/`, `openspec/policies/`, and `openspec/guardrails/` roots
SHALL NOT remain as canonical, required, symlinked, redirected, duplicated, or
compatibility paths.

The exact inventory SHALL remain only in `openspec/governance/project-structure.toml`.
The structure registry, Change Guidance checker, focused contract test, current
authoring pointers, and downstream entry documents SHALL remain synchronized with that
inventory. Deterministic governance SHALL compare the exact registered Change Guidance,
product, and policy member sets with the checked-out tree and reject missing, extra,
duplicate, or legacy-only members. Repository-root `AGENTS.md` and `CLAUDE.md` SHALL
remain unchanged. (`PRS-009`)

#### Scenario: Canonical guidance, product, and closeout paths pass governance
- **WHEN** architecture and Change Guidance governance check the target repository
- **THEN** the exact guidance root, product-context entry, complete policy library,
  closeout-evidence command boundary, OpenSpec root navigation, module-guide focus
  gate, authoring pointer, and focused checker/test surfaces are present and mutually
  discoverable

#### Scenario: An unregistered guidance, product, or policy member fails governance
- **WHEN** the checked-out Change Guidance root, product directory, or policy library
  contains an extra file, a second index, or omits a registered member
- **THEN** deterministic governance reports the exact-member mismatch rather than
  accepting required-path presence as sufficient evidence

#### Scenario: A legacy nested tree cannot masquerade as the current route
- **WHEN** current structure or navigation retains only a retired root or adds a
  compatibility copy beside the canonical Change Guidance, product, or
  closeout-evidence tree
- **THEN** deterministic governance rejects the retired or duplicate surface instead
  of treating it as a valid route

#### Scenario: Policy prose, product orientation, and executable guardrails remain distinct
- **WHEN** a contributor follows Change Guidance to a selected policy, opens the
  product-context route, or follows governance navigation to the closeout-evidence
  command
- **THEN** policy prose resolves only under `change-guidance/policies/`, product
  orientation resolves only through `product/deep-research.md`, and the command
  resolves only under `governance/closeout-evidence/`, without any surface claiming
  runtime or native archive authority

#### Scenario: Root guide boundary is preserved
- **WHEN** the target topology is reviewed for owned paths
- **THEN** it changes only project-owned OpenSpec and downstream entry surfaces and
  does not add Change Guidance to repository-root `AGENTS.md` or `CLAUDE.md`
