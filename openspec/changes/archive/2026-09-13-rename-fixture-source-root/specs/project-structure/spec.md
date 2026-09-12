# project-structure Delta

> req: PRS-001, PRS-017, PRS-019

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
`deep_research_harness/src_fixtures/deerflow_deep_research_fixtures/`. It SHALL be a
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
- **WHEN** the folder contract finds the registered `src_fixtures` fixture package
- **THEN** it accepts its distinct package name and mirrored fixture layout while confirming that production build and deployment paths exclude it

#### Scenario: Unregistered second production source tree is rejected
- **WHEN** a fixture places `deerflow_deep_research` source at repository root, under an upstream tree, or under an unregistered source root
- **THEN** the folder contract fails and identifies the non-canonical owner

### Requirement: Deep Research Harness has one canonical downstream filesystem root

The complete tracked downstream Deep Research project SHALL live under
`deep_research_harness/`. Its production source SHALL remain
`deep_research_harness/src/deerflow_deep_research/`, its fixture source SHALL remain
`deep_research_harness/src_fixtures/deerflow_deep_research_fixtures/`, and its tests SHALL
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

### Requirement: Scripted-real debug command paths have canonical registration

The operator-only scripted-real debug surface SHALL live at the registered canonical
paths: the launcher and its composition at
`deep_research_harness/scripts/debug_scripted_real_workflow.py`, the non-production
scenario data modules beneath
`deep_research_harness/src_fixtures/deerflow_deep_research_fixtures/scripted_real/`, and
its deterministic contract evidence beneath `deep_research_harness/tests/`. The
fixture scenario modules SHALL import only the standard library and the existing
registered production contracts, never the production runtime composition authority;
the launcher SHALL own the scripted-real runtime composition in the presentation
layer. The production package `deep_research_harness/src/deerflow_deep_research/`
SHALL NOT discover or import the scenario scripts. The structure registry SHALL admit
exactly the new registered paths and SHALL continue to reject unregistered placement,
upstream source placement, and generic shared modules. (`PRS-019`)

#### Scenario: New debug surface follows the harness root
- **WHEN** structural governance inspects the scripted-real debug launcher, fixture
  scenario modules, and contract tests
- **THEN** it finds them beneath `deep_research_harness/` at their registered paths and
  rejects a production-package copy, an unregistered path, or upstream placement

#### Scenario: Production package does not discover the scenario scripts
- **WHEN** the production import boundaries are verified
- **THEN** `src/deerflow_deep_research/` has no import of the scripted-real scenario
  modules and the fixture scenario modules stay within the registered fixture
  production-contract allowlist
