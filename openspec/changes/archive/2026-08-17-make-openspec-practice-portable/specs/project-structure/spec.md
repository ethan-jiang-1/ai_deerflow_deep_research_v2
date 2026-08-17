> req: PRS-009

## MODIFIED Requirements

### Requirement: Deep Research Change Guidance, product context, and closeout evidence occupy canonical OpenSpec paths

The canonical structure SHALL register `openspec/change-guidance/` as the local
design/admission route. Its root SHALL contain exactly one `README.md` router and the
registered `core/`, `profiles/`, and `local/` trees. `core/` SHALL contain only
`change-practice.md`; `profiles/` SHALL contain exactly the independently selectable
`workflow-control/`, `node-agent/`, and `deerflow-downstream/` trees, each with one
complete named profile document; `local/` SHALL contain only `deep-research.md`.
Every current guidance paragraph and policy SHALL have one registered editable owner.
Retired pre-cutover policy paths, a second router, compatibility copy, symlink, or
duplicate policy prose SHALL NOT remain current.

The canonical structure SHALL register the product-neutral validation module under
OpenSpec governance and retain `openspec/governance/check_change_guidance.py` as the
Deep Research local wrapper/CLI. It SHALL register the focused pure-kernel and wrapper
contract tests without registering the portable module as a general project
architecture, requirement, specification, coverage, or runtime checker.

The canonical structure SHALL register `openspec/product/` as the sole product-context
directory and SHALL require its exact current member set to be `README.md`. It SHALL
reject `deep-research.md`, `instance.yaml`, an extra index, a compatibility copy, or
any unregistered member after cutover. It SHALL continue to register
`openspec/governance/selected-change-closeout.py`, its `selected-change-closeout.md`
usage guide, and `openspec/README.md` at their bounded roles.

The exact inventory SHALL remain only in
`openspec/governance/project-structure.toml`. Product documents, local composition,
checker constants, and authoring entries SHALL link to or validate against that
registry and SHALL NOT duplicate its source/test/import/gitlink member facts. The
registry, Change Guidance wrapper, focused tests, current authoring pointers, and
downstream entry documents SHALL remain synchronized. Repository-root `AGENTS.md` and
`CLAUDE.md`, Deep Research production structure, glossary authority, and the
`deerflow/` gitlink SHALL remain unchanged. (`PRS-009`)

Dependency direction SHALL be `openspec/` to `deep_research_harness/` only. OpenSpec
governance MAY inspect the downstream application, but no Harness guide,
documentation, Makefile, application test, or asset SHALL read, import, execute, or
link OpenSpec content. Governance tests SHALL live under `openspec/tests/governance/`,
and Harness verification SHALL run independently without the OpenSpec tree.

#### Scenario: Canonical guidance, product, and closeout paths pass governance
- **WHEN** architecture and Change Guidance governance inspect the target repository
- **THEN** the exact core/profile/local trees, pure validator, local wrapper, product front door, closeout route, and bounded entry documents are registered and mutually discoverable

#### Scenario: An unregistered guidance, product, or policy member fails governance
- **WHEN** a guidance/product tree contains an extra file, old policy location, second router, compatibility copy, or duplicate editable rule
- **THEN** deterministic exact-member checks or the ownership review report the violation rather than accepting required-path presence alone

#### Scenario: A legacy nested tree cannot masquerade as the current route
- **WHEN** current navigation retains a retired pre-cutover policy tree or adds a compatibility copy beside the registered core/profile/local topology
- **THEN** deterministic governance rejects the legacy or duplicate surface rather than accepting it as another route

#### Scenario: Policy prose, product orientation, and executable guardrails remain distinct
- **WHEN** a contributor follows guidance, opens the product front door, or runs a registered governance command
- **THEN** portable/local policy prose, product navigation, and executable validation remain in their registered jurisdictions without claiming each other's authority

#### Scenario: Root guide boundary is preserved
- **WHEN** the target topology is reviewed for owned paths
- **THEN** it changes only project-owned OpenSpec and downstream entry surfaces and does not add Change Guidance to repository-root `AGENTS.md` or `CLAUDE.md`

#### Scenario: Project structure remains the single exact authority
- **WHEN** product or local composition needs to explain a registered path
- **THEN** it links to `project-structure.toml` and does not recreate an exact inventory or competing machine schema

#### Scenario: Product front door cutover is clean
- **WHEN** current consumers move from `product/deep-research.md` to `product/README.md`
- **THEN** the registry and exact-member guard accept only `README.md`, while archive references remain historical and are not treated as current consumers

#### Scenario: Upstream boundary is preserved
- **WHEN** the Program closes its structural migration
- **THEN** metadata evidence shows the `deerflow` gitlink pointer and nested worktree are unchanged, without source-browsing or modifying the submodule
