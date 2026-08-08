> req: PRS-001, PRS-004, PRS-005, PRS-006, PRS-011, PRS-014, PRS-015, PRS-017

## ADDED Requirements

### Requirement: Deep Research Harness has one canonical downstream filesystem root

The complete tracked downstream Deep Research project SHALL live under
`deep_research_harness/`. Its production source SHALL remain
`deep_research_harness/src/deerflow_deep_research/`, its fixture source SHALL remain
`deep_research_harness/src_fake/deerflow_deep_research_fixtures/`, and its tests SHALL
remain under `deep_research_harness/tests/`. The distribution
`deerflow-deep-research`, Python import `deerflow_deep_research`, ownership layers,
and public `deep_research` tool SHALL remain unchanged. The structure registry,
architecture checker, generated module-guide locator, scripts, configuration, mounts,
fixtures, tests, active documents, and automation SHALL use this one root. No tracked
`deerflow_research/` compatibility root, symlink, alias, or second production source
tree SHALL remain. Deep Research source SHALL not move into `backend/` or `frontend/`.
(`PRS-017`)

#### Scenario: Canonical Harness root passes structural governance
- **WHEN** architecture governance inspects the checkout after the migration
- **THEN** it finds the production, fixture, and test roots beneath `deep_research_harness/`, preserves the established package/tool identities, and rejects a tracked old-root alias or upstream source copy

#### Scenario: Generated locator follows the registry
- **WHEN** the structural registry changes its canonical root entries
- **THEN** the architecture renderer regenerates the `deep_research_harness/AGENTS.md` locator from that registry and validation finds no hand-maintained conflicting path inventory

## MODIFIED Requirements

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
paths SHALL remain registered in `openspec/governance/project-structure.toml` and
reflected in the generated `deep_research_harness/AGENTS.md` block.

Real topic planning SHALL retain
`deep_research_harness/src/deerflow_deep_research/domain/topics.py` and
`deep_research_harness/src/deerflow_deep_research/graph/nodes/topic_planning/prompts.py`.
Real Wave0 SHALL retain
`deep_research_harness/src/deerflow_deep_research/graph/nodes/wave0/prompts.py` and its
existing package-local source-intake result contract. These paths SHALL remain
registered in `openspec/governance/project-structure.toml` and reflected in the
generated `deep_research_harness/AGENTS.md` block. topic_planning and wave0 remain
non-HITL nodes and their production modules import only `domain`/`engine` under the
existing policy.

Local profile resolution SHALL remain only at
`deep_research_harness/scripts/local_profiles.py`; its deterministic tests SHALL remain
at `deep_research_harness/tests/contract/test_local_profiles.py`. The project-owned
`profiles/` directory SHALL continue to contain only its committed `README.md` and
`.gitignore`, plus ignored materialized profile directories. It remains local
configuration data rather than source or launcher tooling. These paths SHALL remain
registered in `openspec/governance/project-structure.toml` and reflected in the
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

### Requirement: Reader-interface validation uses canonical downstream governance paths

The non-runtime cognitive-node reader checker, its fixtures, and its focused contract
tests SHALL live under registered canonical `deep_research_harness/` paths. The
architecture checker SHALL retain its existing missing-path and upstream-placement
rejection rules; a stale `deerflow_research/` registry entry SHALL fail rather than
silently omit the moved surface. (`PRS-014`)

#### Scenario: Reader validation cannot pass from the former root
- **WHEN** a reader-validation registry entry retains `deerflow_research/` after the move
- **THEN** the structural checker rejects the entry before treating its fixture or test
  as governed evidence

### Requirement: Structural authority survives change archival

The active `project-structure` main spec and
`openspec/governance/project-structure.toml` SHALL retain their existing normative
relationship, synchronized-change protocol, and checker guarantees. The one bounded
checker-rendered locator SHALL live at `deep_research_harness/AGENTS.md`, refer to the
canonical Harness root, and be rendered from the registry. An old-root locator or
registry entry SHALL be structural drift, while historical archives may retain factual
old paths when they do not navigate to or validate the current checkout. (`PRS-004`)

#### Scenario: Archive-durable structure names the current root
- **WHEN** the architecture checker validates the active main spec and generated locator
- **THEN** both identify `deep_research_harness/` as the downstream root and no active
  structural authority names `deerflow_research/`

### Requirement: Run-experience contracts use the canonical domain and runtime ownership layers

The existing run-experience domain and runtime contracts SHALL remain under
`deep_research_harness/src/deerflow_deep_research/` at their registered canonical
paths. Their existing dependency-direction, runtime-binding, and presentation-adapter
boundaries remain unchanged; `deep_research_harness/scripts/` remains only a permitted
presentation-adapter location, not a lifecycle authority. (`PRS-005`)

#### Scenario: Run-experience paths follow the Harness root
- **WHEN** structural governance inspects the registered run-experience modules
- **THEN** it finds their domain/runtime paths beneath `deep_research_harness/` and
  rejects an old-root duplicate or upstream placement

### Requirement: Run-session ownership is canonical and runtime-bound

Any retained session, timeline, diagnostic, operation, or local-workbench source that
survives this migration SHALL live beneath `deep_research_harness/` at registered
domain/runtime/adapter paths. Such retained material is observation-only under the
Bundle lifecycle contract; removed legacy broker/index components SHALL be removed from
the registry rather than left as a second root or authority. The downstream-owned
`.gitignore` and permitted ignored local-output paths SHALL likewise move under
`deep_research_harness/`. (`PRS-006`)

#### Scenario: Retained observations do not preserve a second structural root
- **WHEN** a retained-session or workbench component remains after the migration
- **THEN** its registered path is beneath `deep_research_harness/`, and it cannot
  create an old-root alias or a lifecycle controller

### Requirement: Prompt catalog paths have canonical ownership and registration

The registered prompt renderer, graph-owned catalog, prompt-dump script, and focused
tests SHALL use canonical `deep_research_harness/` paths. The ignored optional review
workspace is `deep_research_harness/.node-prompt-review/`; it remains neither a
required structural path nor runtime authority. (`PRS-011`)

#### Scenario: Prompt review workspace follows the canonical root
- **WHEN** architecture governance checks prompt-catalog registration
- **THEN** it rejects a required or optional review path rooted at
  `deerflow_research/` and retains the existing no-generated-authority rule

### Requirement: Cognitive evaluation paths have separate ownership

The Cognitive Evaluation contracts, Runner source, control surface, and ignored run
store SHALL retain their existing separate-domain semantics beneath
`deep_research_harness/`. Evaluation control and run paths SHALL not be accepted as
Deep Research Bundle discovery/control paths, and a root move SHALL not merge their
registries or storage areas. (`PRS-015`)

#### Scenario: Evaluation paths move without joining Deep Research discovery
- **WHEN** structural governance validates evaluation source and `evals/` paths after the move
- **THEN** they resolve beneath `deep_research_harness/` and remain outside Deep Research
  Run Bundle discovery
