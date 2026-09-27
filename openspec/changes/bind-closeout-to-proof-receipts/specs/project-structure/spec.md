# Spec Delta

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
`deerflow/` gitlink SHALL remain unchanged. The canonical structure SHALL also register `openspec/governance/check_proof_receipts.py`
as a component checker of the same aggregate. When a change's touched files intersect a
registered lane's declared surfaces, `closeout` SHALL require, for that lane, a receipt
that a runner produced: exit code zero, recorded on a clean tree, at a revision whose
diff to the delivered revision (the attestation's head commit) is empty for those
surfaces, with a transcript that exists,
whose digest matches the receipt, and whose text carries the lane's registered success
sentinel. A caller-declared or hand-written claim SHALL NOT satisfy this requirement, and
the checker SHALL name the exact rerun command for every missing or stale receipt.
(`PRS-009`)

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

#### Scenario: A stale or missing receipt blocks closeout
- **WHEN** a change touches a file covered by a registered lane and no receipt for that
  lane covers the delivered revision, or the recorded transcript no longer matches
- **THEN** closeout exits non-zero, names the lane and the touched surface, and prints the
  rerun command

#### Scenario: A caller-declared claim never satisfies closeout
- **WHEN** a change states in prose that a lane passed without a runner-produced receipt
- **THEN** the requirement is unmet and closeout exits non-zero
