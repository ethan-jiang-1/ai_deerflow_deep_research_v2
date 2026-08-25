# project-structure Delta

> req: PRS-001, PRS-004, PRS-009

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
Deep Research local wrapper/CLI without registering the portable module as a general
project architecture, requirement, specification, coverage, or runtime checker.

The canonical structure SHALL register one OpenSpec root governance aggregate script
beneath `openspec/governance/` as the combined gate over the registered OpenSpec
checkers. The aggregate SHALL be orchestration-only: it SHALL invoke each component
checker, preserve its exit code, and aggregate results without owning any rule
semantics, writing the requirement registry, judging prose, or reimplementing
delta/registry regex or parsing. The aggregate SHALL expose a read-only `plan` phase
that delegates active-change admission checks to the owning components (the Change
Guidance checker for the Focus Card, the selected-change scope of the specification
checker for delta headers and titles, the planning scope of the requirement checker
for reservations and collisions, and native strict change validation for MODIFIED
requirement/scenario preservation) and a `closeout` phase requiring zero exit from
every component checker; closeout SHALL NOT add a separate consistency checker
because the component checkers own registry, header, and evidence consistency. The
aggregate and its focused tests SHALL be registered in the project-structure manifest.
Registering the aggregate SHALL NOT register the portable validation module as a
general project architecture, requirement, specification, coverage, or runtime
checker.

The canonical structure SHALL register `openspec/product/` as the sole product-context
directory and SHALL require its exact current member set to be `README.md`. It SHALL
reject `deep-research.md`, `instance.yaml`, an extra index, a compatibility copy, or
any unregistered member after cutover. It SHALL continue to register
`openspec/governance/selected-change-closeout.py`, its `selected-change-closeout.md`
usage guide, and `openspec/README.md` at their bounded roles.

The exact inventory SHALL remain only in the project-structure manifest, consisting
of the contract file `openspec/governance/project-structure.toml` and the inventory
file `openspec/governance/required-paths.toml`. Product documents, local composition,
checker constants, and authoring entries SHALL link to or validate against that
manifest and SHALL NOT duplicate its source/test/import/gitlink member facts. The
manifest, Change Guidance wrapper, current authoring pointers, and downstream entry
documents SHALL remain synchronized. Repository-root `AGENTS.md` and
`CLAUDE.md`, Deep Research production structure, glossary authority, and the
`deerflow/` gitlink SHALL remain unchanged. (`PRS-009`)

Dependency direction SHALL be `openspec/` to `deep_research_harness/` only. OpenSpec
governance MAY inspect the downstream application, but no Harness guide,
documentation, Makefile, application test, or asset SHALL read, import, execute, or
link OpenSpec content. Harness verification SHALL run independently without the
OpenSpec tree. Application behavior requirements SHALL retain deterministic test
evidence, while OpenSpec-only governance requirements MAY use the implementing
governance script's `@impl` declaration and SHALL NOT require a parallel pytest tree.

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
- **THEN** it links to the project-structure manifest (`project-structure.toml` contract and `required-paths.toml` inventory) and does not recreate an exact inventory or competing machine schema

#### Scenario: Product front door cutover is clean
- **WHEN** current consumers move from `product/deep-research.md` to `product/README.md`
- **THEN** the registry and exact-member guard accept only `README.md`, while archive references remain historical and are not treated as current consumers

#### Scenario: Upstream boundary is preserved
- **WHEN** the Program closes its structural migration
- **THEN** metadata evidence shows the `deerflow` gitlink pointer and nested worktree are unchanged, without source-browsing or modifying the submodule

#### Scenario: Aggregate is orchestration-only and registered
- **WHEN** architecture governance inspects the OpenSpec governance gate
- **THEN** the aggregate is registered beneath `openspec/governance/`, invokes every
  component checker with exit-code preservation and read-only behavior, delegates
  plan-phase semantics to the owning component scopes, adds no duplicate closeout
  consistency checker, and never writes the requirement registry or judges prose

### Requirement: Canonical downstream package ownership

The repository SHALL locate the complete tracked Deep Research module under
`deep_research_harness/`. Its production source SHALL remain
`deep_research_harness/src/deerflow_deep_research/`, its tests SHALL remain under
`deep_research_harness/tests/`, and its production distribution, import namespace,
ownership layers, and public tool name SHALL remain unchanged. The structure registry,
architecture and charter checkers, and checker-rendered module guide SHALL use that
production root as the canonical deployable downstream location. A tracked legacy-root
compatibility directory, symlink, alias, or second production source tree SHALL be
rejected.

The one permitted non-production source root SHALL be
`deep_research_harness/src_fake/deerflow_deep_research_fixtures/`. It SHALL be a
distinct fixture package, may mirror the logical-node organization needed for
deterministic adapters alongside its package-level catalog, scenario, routing, and gate
modules, and SHALL not be included in the production distribution, Gateway editable
installation, or Docker source mount. The structural registry SHALL enumerate both
roots and their one-way dependency rule. No Deep Research source SHALL be added under
`backend/` or `frontend/`.

Current repository-owned consumers of the production physical root, including active
specs, guides, scripts, CI path filters and working directories, Docker inputs,
profiles, tests, and generated evidence, SHALL use that canonical production root.
Historical archives SHALL retain historical paths unless they actively navigate to,
command, or validate the current checkout. Generic DeerFlow uses of "agent" or
`agents/` SHALL not be rewritten merely because this root changes. All owned runtime
templates and launch tooling SHALL live under `deep_research_harness/`; the registered
fixture source is a non-production implementation tree, not runtime launcher tooling.
The documented production ownership layers SHALL remain `runtime`, `domain`, `engine`,
`agents`, and `graph`.

Real HITL1 SHALL retain the canonical downstream production paths
`deep_research_harness/src/deerflow_deep_research/domain/profile.py`,
`deep_research_harness/src/deerflow_deep_research/graph/nodes/hitl1/prompts.py`, and
`deep_research_harness/src/deerflow_deep_research/runtime/request_bundle.py`. These
paths SHALL remain registered in the project-structure manifest and
reflected in the generated `deep_research_harness/AGENTS.md` block.

Real topic planning SHALL retain
`deep_research_harness/src/deerflow_deep_research/domain/topics.py` and
`deep_research_harness/src/deerflow_deep_research/graph/nodes/topic_planning/prompts.py`.
Real Wave0 SHALL retain
`deep_research_harness/src/deerflow_deep_research/graph/nodes/wave0/prompts.py` and its
existing package-local source-intake result contract. These paths SHALL remain
registered in the project-structure manifest and reflected in the
generated `deep_research_harness/AGENTS.md` block. topic_planning and wave0 remain
non-HITL nodes and their production modules import only `domain`/`engine` under the
existing policy.

Local profile resolution SHALL remain only at
`deep_research_harness/scripts/local_profiles.py`; its deterministic tests SHALL remain
at `deep_research_harness/tests/contract/test_local_profiles.py`. The project-owned
`profiles/` directory SHALL continue to contain only its committed `README.md` and
`.gitignore`, plus ignored materialized profile directories. It remains local
configuration data rather than source or launcher tooling. These paths SHALL remain
registered in the project-structure manifest and reflected in the
generated `deep_research_harness/AGENTS.md` block. No shell hook, source interception,
profile implementation, command adapter, documentation, or ignore rule SHALL modify a
pre-existing root DeerFlow file or directory. The resolver remains pre-process
operations tooling, not graph/runtime source: it SHALL not be placed under
`deep_research_harness/src`, `backend`, `frontend`, or a generic helpers/utils/common
module.

#### Scenario: Production root passes structural governance
- **WHEN** the folder contract inspects the repository
- **THEN** it finds the required production package and tests at their canonical paths, and no production source appears under an upstream module

#### Scenario: Canonical HITL1 paths pass
- **WHEN** the folder contract inspects the repository
- **THEN** the profile, HITL1 prompt, and `runtime/request_bundle.py` paths remain under the canonical production package and no Deep Research source appears under `backend/` or `frontend/`

#### Scenario: Canonical topic planning and Wave0 paths pass
- **WHEN** the folder contract inspects topic planning and Wave0
- **THEN** their registered production paths remain under the canonical package, retain their existing import rules, and no source appears under `backend/` or `frontend/`

#### Scenario: Canonical local profile tooling passes
- **WHEN** architecture governance scans local profile support
- **THEN** the resolver and tests remain under `deep_research_harness/`, profile data is only under `profiles/`, and no upstream-owned root, `backend/`, or `frontend/` path is changed

#### Scenario: Registered fixture root is accepted without becoming production source
- **WHEN** the folder contract finds the registered `src_fake` fixture package
- **THEN** it accepts its distinct package name and mirrored fixture layout while confirming that production build and deployment paths exclude it

#### Scenario: Unregistered second production source tree is rejected
- **WHEN** a fixture places `deerflow_deep_research` source at repository root, under an upstream tree, or under an unregistered source root
- **THEN** the folder contract fails and identifies the non-canonical owner

### Requirement: Structural authority survives change archival

The active `project-structure` main spec and the project-structure manifest — the
contract file `openspec/governance/project-structure.toml` and the inventory file
`openspec/governance/required-paths.toml` — SHALL retain their existing normative
relationship, synchronized-change protocol, and checker guarantees. The one bounded
checker-rendered locator SHALL live at `deep_research_harness/AGENTS.md`, refer to the
canonical Harness root, and be rendered from the registry. An old-root locator or
registry entry SHALL be structural drift, while historical archives may retain factual
old paths when they do not navigate to or validate the current checkout. (`PRS-004`)

#### Scenario: Archive-durable structure names the current root
- **WHEN** the architecture checker validates the active main spec and generated locator
- **THEN** both identify `deep_research_harness/` as the downstream root and no active
  structural authority names `deerflow_research/`
