# project-structure Specification

> req: PRS-001, PRS-002, PRS-003, PRS-004, PRS-005, PRS-006, PRS-007, PRS-009, PRS-010, PRS-011, PRS-012, PRS-013, PRS-014, PRS-015, PRS-016, PRS-017
> structure: openspec/governance/project-structure.toml

## Purpose
The canonical downstream package structure, mechanically enforced import directions and node surface, and archive-durable architecture governance.
## Requirements


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

### Requirement: Import and shared-code boundaries are mechanical

The project SHALL enforce import direction with an AST-based contract. Domain code SHALL
depend only on the standard library and Pydantic; engine code SHALL depend only on domain;
agents SHALL depend only on domain plus public DeerFlow/LangChain APIs; and ordinary
production node modules SHALL depend only on domain/engine, except that graph-owned HITL
node modules MAY import exactly public `langgraph.types.interrupt`. A node package's
optional phase-local `subgraph.py` MAY additionally import public LangGraph APIs required
for its internal `Send` fan-out/fan-in and reusable cross-node subflows under
`graph/components/`. Reusable graph components MAY depend on domain, engine, and public
LangGraph APIs. None of these exceptions MAY import other graph implementation modules,
agents, runtime, sibling nodes, or `deerflow_deep_research_fixtures`.

Fixture source MAY depend on documented production domain contracts, neutral work-unit and
graph-composition contracts, and `runtime.research.ResearchGraphRecipe` solely to invoke its
single test/demo composition entry `from_adapters()`. It SHALL not invoke that class's
`all_real()` or `.create()` factories, or import a production `GraphHost`, action handler, or
control host; production source SHALL not depend on fixture source. Runtime SHALL remain the
only layer allowed to bind graph execution to raw DeerFlow context, request-bundle host I/O,
and the embedded-agent factory.
Production downstream code SHALL not import `app.*`; and generic shared modules named `utils`,
`helpers`, or `common` SHALL be rejected. The existing direct-provider-classifier exception
remains limited to `httpx` and `openai` in `runtime/node_agent_bridge.py`; those packages SHALL
be mechanically rejected from every other production layer.

#### Scenario: Valid one-way fixture dependency passes
- **WHEN** the contract scans a fixture adapter importing documented production contracts and a
  fixture composition root invoking only `ResearchGraphRecipe.from_adapters`
- **THEN** it accepts those fixture-to-production dependencies and finds no production-to-fixture
  dependency

#### Scenario: Reverse fixture dependency fails closed
- **WHEN** production source imports a fixture module, including a helper previously shared
  by real and fixture node paths
- **THEN** the contract fails with the importing and imported module names

#### Scenario: Fixture runtime-controller dependency fails closed
- **WHEN** fixture source imports a production `GraphHost`, research action handler, or control
  host, or invokes `ResearchGraphRecipe.all_real()` or `.create()`
- **THEN** the contract fails with the fixture source and prohibited import or factory call

#### Scenario: Existing production dependency directions remain enforced
- **WHEN** a fixture makes domain code import runtime code, an ordinary non-HITL node module
  import LangGraph or `graph/components/`, a HITL node import LangGraph APIs other than
  `langgraph.types.interrupt`, a node-local `subgraph.py` import graph implementation
  outside `graph/components/`, a node import agents/runtime, or one node import another node
- **THEN** the contract fails with the importing and imported module names

#### Scenario: Direct provider classifier imports stay at the raw binding
- **WHEN** architecture governance scans direct `httpx` or `openai` imports
- **THEN** it accepts them only from `runtime/node_agent_bridge.py` and rejects the same
  imports from every other runtime module or layer

#### Scenario: Real HITL interrupt import passes narrowly
- **WHEN** the contract scans the real HITL1 production node and it imports exactly
  `langgraph.types.interrupt`
- **THEN** the import is accepted as a graph-owned HITL interrupt boundary, while other
  LangGraph imports from ordinary production node modules remain rejected

### Requirement: Top-level nodes expose one stable production surface

Every top-level production workflow node package SHALL expose exactly one valid `NODE_SPEC`
from its package root using the pure contract from `domain/node_spec.py`, its real factory,
and its private contracts. A production node package SHALL not colocate a fixture adapter.
It MAY colocate one optional phase-local `subgraph.py` for internal implementation
components. Reusable cross-node non-top-level subflows SHALL remain under
`graph/components/` and MAY be imported only by node-local `subgraph.py` modules, not by
ordinary node factories. Real factories SHALL accept only pure `NodeBuildDependencies`
containing reduced context/capability contracts. Nodes SHALL NOT import `graph/registry.py`;
the registry/builder SHALL load only an explicitly listed production node package root and
read its public `NODE_SPEC`, never import a private node module path directly.

The fixture catalog SHALL map every fixed logical node to one deterministic fixture adapter
outside the production package. It SHALL use the production node's public contracts and
declared capabilities but SHALL not add a production capability or grant fixture code access
to undeclared runtime resources.

Real HITL1 SHALL retain only the narrow capabilities it consumes: the existing
`NodeExecutionCapabilities.run_agent()` protocol for brief generation and the request-bundle
profile writer for `request/profile.json`. It SHALL not declare or receive bootstrap or
work-unit-controller capability. A fixture HITL1 adapter SHALL receive no request-bundle
capability.

#### Scenario: Production node package is discoverable without fixtures
- **WHEN** a production node package supplies its required production files and a valid
  `NODE_SPEC`
- **THEN** registry discovery returns its stable logical name, real factory, contracts,
  phase, and policy reference without importing a fixture module

#### Scenario: Partial production node package is refused
- **WHEN** a production node package omits a required production file, exports internal
  callables directly, uses an unstable logical name, imports a reusable graph component from
  an ordinary node module, or exposes a phase-local worker as a top-level node
- **THEN** registry validation fails before graph compilation

#### Scenario: Fixture catalog covers the fixed topology
- **WHEN** deterministic fixture validation loads the fixture catalog
- **THEN** it finds exactly one adapter for every logical node and no adapter for an unknown
  or internal component

#### Scenario: Production fixture placement is refused
- **WHEN** a production node package exports a fixture callable, contains a fixture adapter
  file, or the production registry attempts to read a fixture package path
- **THEN** structural or registry validation fails before graph compilation

#### Scenario: Node-to-registry cycle is refused
- **WHEN** a node package imports `graph.registry`, another graph implementation module
  outside the narrow `subgraph.py -> graph.components` exception, or a sibling node to
  construct its spec or subgraph
- **THEN** the contract fails and directs the node to the pure domain NodeSpec,
  package-local contract, or registered reusable graph component

#### Scenario: Real HITL1 NodeSpec declares only its capabilities
- **WHEN** the HITL1 package root `NODE_SPEC` is loaded
- **THEN** the real factory is available, its contract routes include `accepted`, `cancel`,
  `needs_followup`, and `exhausted`, it declares the request-bundle capability, and it does
  not declare bootstrap or work-unit-controller capabilities

#### Scenario: Capability injection mismatch fails closed
- **WHEN** the graph wrapper attempts to attach a request-bundle writer to a node that did
  not declare it, or real HITL1 runs without the declared request-bundle writer
- **THEN** graph invocation fails before the node can fabricate a `ContentRef` or write
  profile state

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

### Requirement: Human interaction has a registered domain contract seam

The project structure registry SHALL list the domain-owned human-interaction contract
module and its focused deterministic tests under the existing `domain` ownership layer.
The module SHALL not create a new ownership layer or import runtime, graph, or adapter
code. (`PRS-010`)

#### Scenario: Architecture registry recognizes the contract owner
- **WHEN** architecture governance scans the human-interaction source and test paths
- **THEN** it accepts the registered domain seam and retains existing forbidden-layer
  import checks

### Requirement: Prompt catalog paths have canonical ownership and registration

The registered prompt renderer, graph-owned catalog, prompt-dump script, and focused
tests SHALL use canonical `deep_research_harness/` paths. The ignored optional review
workspace is `deep_research_harness/.node-prompt-review/`; it remains neither a
required structural path nor runtime authority. (`PRS-011`)

#### Scenario: Prompt review workspace follows the canonical root
- **WHEN** architecture governance checks prompt-catalog registration
- **THEN** it rejects a required or optional review path rooted at
  `deerflow_research/` and retains the existing no-generated-authority rule

### Requirement: Node-local capability structure remains mechanically discoverable

The project structure registry SHALL register the canonical domain capability
reference contract and agents-owned resource-validation/composition modules. It SHALL
add `capabilities.py` and the `capabilities/` resource directory to the permitted
node-package grammar, then register the exact declaration/resource locations for the
HITL1, Wave0, and Wave2 migrated packages; no other package gains a required
capability location in this cohort. Node-local declarations SHALL depend only on the
permitted graph/domain direction, capability resources SHALL remain package-local
rather than a global prompt directory, and the agents layer SHALL not import graph
implementation modules to enumerate node cognition. The architecture checker SHALL
reject an unregistered capability source, an escaping resource path, a reverse
graph-to-agents dependency, or a new capability source under `backend/` or
`frontend/`. (`PRS-012`)

#### Scenario: Registered local capability paths pass
- **WHEN** architecture governance inspects the first cohort after implementation
- **THEN** it finds the registered domain and agents modules plus the declared
  `capabilities.py`/`capabilities/` locations only for HITL1, Wave0, and Wave2 under
  the canonical downstream tree

#### Scenario: Global or upstream capability placement fails
- **WHEN** a fixture adds a capability resource under an unregistered global prompt
  directory, an upstream tree, or a graph-to-agents import path
- **THEN** architecture governance fails before the capability can be treated as an
  admitted execution surface

### Requirement: HITL1 profile capability paths are registered locally

The project structure registry SHALL register the HITL1 package declaration and the
two exact local resources `capabilities/hitl1-profile-brief.md` and
`capabilities/hitl1-profile-brief-repair.md`, together with their focused inventory
and real-node evidence paths. The registration SHALL not add a capability location to
another node package or permit a global prompt directory, graph-to-agents import, or
upstream placement. (`PRS-013`)

#### Scenario: Second-cohort local paths pass architecture governance
- **WHEN** architecture governance inspects the HITL1 second cohort
- **THEN** it finds only the registered HITL1 local declaration/resources and rejects
  an escaping, global, reverse, or upstream capability path

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

### Requirement: Research Confirmation has one registered downstream domain surface

The Research Confirmation deterministic admission boundary and its focused domain
tests SHALL occupy registered paths under the existing Deep Research downstream
domain and test roots. The structure registry and generated module locator SHALL
remain synchronized with those paths, preserve the existing ownership-layer import
direction, and introduce no `backend/` or `frontend/` path. (`PRS-016`)

#### Scenario: The confirmation boundary remains a pure registered domain module
- **WHEN** architecture governance validates the registered project structure after
  the Research Confirmation capability is added
- **THEN** it finds the registered downstream module and focused tests, rejects an
  unregistered or upstream placement, and preserves the existing domain-to-graph and
  domain-to-runtime dependency boundary

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
