> req: PRS-001, PRS-002, PRS-003, PRS-006, PRS-011

## MODIFIED Requirements

### Requirement: Canonical downstream package ownership

The repository SHALL locate the complete tracked Deep Research module under
`deerflow_research/`. Its production source SHALL remain
`deerflow_research/src/deerflow_deep_research/`, its tests SHALL remain under
`deerflow_research/tests/`, and its production distribution, import namespace, ownership
layers, and public tool name SHALL remain unchanged. The structure registry, architecture
and charter checkers, and checker-rendered module guide SHALL use that production root as
the canonical deployable downstream location. A tracked `agent/` compatibility directory,
symlink, alias, or second production source tree SHALL be rejected.

The one permitted non-production source root SHALL be
`deerflow_research/src_fake/deerflow_deep_research_fixtures/`. It SHALL be a distinct
fixture package, may mirror the logical-node organization needed for deterministic adapters
alongside its package-level catalog, scenario, routing, and gate modules, and SHALL not be
included in the production distribution, Gateway editable installation, or Docker source mount.
The structural registry SHALL enumerate both roots and their one-way dependency rule. No Deep
Research source SHALL be added under `backend/` or `frontend/`.

Current repository-owned consumers of the production physical root, including active
specs, guides, scripts, CI path filters and working directories, Docker inputs, profiles,
tests, and generated evidence, SHALL use that canonical production root. Historical
archives SHALL retain historical paths unless they actively navigate to, command, or
validate the current checkout. Generic DeerFlow uses of "agent" or `agents/` SHALL not
be rewritten merely because this root changes. All owned runtime templates and launch
tooling SHALL live under `deerflow_research/`; the registered fixture source is a
non-production implementation tree, not runtime launcher tooling. The documented
production ownership layers SHALL remain `runtime`, `domain`, `engine`, `agents`, and
`graph`.

Real HITL1 SHALL retain the canonical downstream production paths
`deerflow_research/src/deerflow_deep_research/domain/profile.py`,
`deerflow_research/src/deerflow_deep_research/graph/nodes/hitl1/prompts.py`, and
`deerflow_research/src/deerflow_deep_research/runtime/request_bundle.py`. These paths
SHALL remain registered in `openspec/governance/project-structure.toml` and reflected in
the generated `deerflow_research/AGENTS.md` block.

Real topic planning SHALL retain
`deerflow_research/src/deerflow_deep_research/domain/topics.py` and
`deerflow_research/src/deerflow_deep_research/graph/nodes/topic_planning/prompts.py`.
Real Wave0 SHALL retain
`deerflow_research/src/deerflow_deep_research/graph/nodes/wave0/prompts.py` and its
existing package-local source-intake result contract. These paths SHALL remain registered
in `openspec/governance/project-structure.toml` and reflected in the generated
`deerflow_research/AGENTS.md` block. topic_planning and wave0 remain non-HITL nodes and
their production modules import only `domain`/`engine` under the existing policy.

Local profile resolution SHALL remain only at
`deerflow_research/scripts/local_profiles.py`; its deterministic tests SHALL remain at
`deerflow_research/tests/contract/test_local_profiles.py`. The project-owned `profiles/`
directory SHALL continue to contain only its committed `README.md` and `.gitignore`, plus
ignored materialized profile directories. It remains local configuration data rather than
source or launcher tooling. These paths SHALL remain registered in
`openspec/governance/project-structure.toml` and reflected in the generated
`deerflow_research/AGENTS.md` block. No shell hook, source interception, profile
implementation, command adapter, documentation, or ignore rule SHALL modify a
pre-existing root DeerFlow file or directory. The resolver remains pre-process
operations tooling, not graph/runtime source: it SHALL not be placed under
`deerflow_research/src`, `backend`, `frontend`, or a generic helpers/utils/common module.

#### Scenario: Production root passes structural governance
- **WHEN** the folder contract inspects the repository
- **THEN** it finds the required production package and tests at their canonical paths, and
  no production source appears under an upstream module

#### Scenario: Canonical HITL1 paths pass
- **WHEN** the folder contract inspects the repository
- **THEN** the profile, HITL1 prompt, and `runtime/request_bundle.py` paths remain under the
  canonical production package and no Deep Research source appears under `backend/` or
  `frontend/`

#### Scenario: Canonical topic planning paths pass
- **WHEN** the folder contract inspects the repository
- **THEN** the `domain/topics.py` and `topic_planning/prompts.py` paths remain under the
  canonical production package, topic_planning imports only `domain`/`engine`, and no
  Deep Research source appears under `backend/` or `frontend/`

#### Scenario: Canonical Wave0 paths pass
- **WHEN** the folder contract inspects the repository
- **THEN** the `wave0/prompts.py` path remains under the canonical production package,
  wave0 imports only `domain`/`engine`, and no Deep Research source appears under
  `backend/` or `frontend/`

#### Scenario: Canonical local profile tooling passes
- **WHEN** architecture governance scans local profile support
- **THEN** the resolver and tests remain under `deerflow_research/`, profile data is only
  under the `profiles/` directory, and no upstream-owned root, `backend/`, or `frontend/`
  path is changed

#### Scenario: Existing canonical production paths pass
- **WHEN** the folder contract inspects HITL1, topic-planning, Wave0, and local-profile
  support
- **THEN** their existing production paths and tests remain registered under
  `deerflow_research/`, retain their existing import rules, and no source appears under
  `backend/` or `frontend/`

#### Scenario: Registered fixture root is accepted without becoming production source
- **WHEN** the folder contract finds the registered `src_fake` fixture package
- **THEN** it accepts its distinct package name and mirrored fixture layout while confirming
  that production build and deployment paths exclude it

#### Scenario: Unregistered second production source tree is rejected
- **WHEN** a fixture places `deerflow_deep_research` source at repository root, under an
  upstream tree, or under an unregistered source root
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

### Requirement: Run-session ownership is canonical and runtime-bound

The run-session contracts SHALL live at
`deerflow_research/src/deerflow_deep_research/domain/run_session.py`, while frozen
session-discovery and operation projections SHALL live at
`deerflow_research/src/deerflow_deep_research/domain/session_operations.py`. The manifest,
lifecycle-trace, retention, locking, diagnostic binding, and inspection operations
SHALL live at `deerflow_research/src/deerflow_deep_research/runtime/run_session.py`; the trusted
historical resolver and authorized operation broker SHALL live at
`deerflow_research/src/deerflow_deep_research/runtime/session_operations.py`. These paths and
their focused contract, resolver, lifecycle, and file-SQLite restart tests SHALL be
registered in `openspec/governance/project-structure.toml` and the generated
`deerflow_research/AGENTS.md` block. Domain contracts depend only on stdlib/Pydantic/domain;
runtime is the only layer that receives trusted host workspace or lifecycle facts.

Frozen local-workbench contracts SHALL live at
`deerflow_research/src/deerflow_deep_research/domain/session_workbench.py`, and the broker-bound
timeline, catalog, and contained artifact reader SHALL live at
`deerflow_research/src/deerflow_deep_research/runtime/session_workbench.py`. The dedicated
`deerflow_research/scripts/session_workbench.py` entry is permitted only as a thin terminal
presentation adapter over that runtime surface. Its contract, runtime, containment,
and terminal integration tests SHALL be registered in the same structure registry and
generated guide block.

No run-session domain, storage, inspection, retention, lock, workbench contract, or
workbench runtime implementation shall be placed under `deerflow_research/scripts`, `backend`,
`frontend`, or a generic helpers/utils/common module. `deerflow_research/scripts/demo_sessions.py`
and `deerflow_research/scripts/session_workbench.py` are permitted only as thin presentation
adapters over runtime operations. The downstream-owned `deerflow_research/.gitignore` SHALL be
registered in the same structure registry/generated block and contain only the project-local
generated paths `.deep-research-demo-runs/`, `.reports/`, `.pytest_cache/`, `.ruff_cache/`, and
`.node-prompt-review/`; it SHALL not restore superseded profile ignore rules or alter the
upstream-owned root `.gitignore`. (`PRS-006`)

#### Scenario: Run-session and local-output paths pass structural governance
- **WHEN** the architecture checker scans the implemented run-session capability and the
  project-owned ignore rules
- **THEN** canonical contracts, runtime stores, the owned `deerflow_research/.gitignore`, thin
  adapters, and focused session-operation tests appear in the registry, while the ignored
  node-prompt review workspace is not a required project path or a source authority

### Requirement: Prompt catalog paths have canonical ownership and registration

The project structure registry SHALL register the agents-owned final-prompt renderer, the
graph-owned canonical prompt-case registry, the prompt-dump script, and its focused deterministic
tests. It SHALL not register `deerflow_research/node_prompts/` or
`deerflow_research/.node-prompt-review/` as a required path: the former is removed, and the
latter is an ignored optional review workspace. The agents renderer SHALL retain its existing
allowed import direction and SHALL not import graph or runtime code; the graph case registry
SHALL not render or invoke an agent. The local generated workspace SHALL remain a review
projection rather than a source or runtime authority. (`PRS-011`)

#### Scenario: Architecture governance recognizes prompt catalog ownership without a generated root
- **WHEN** the architecture checker scans the prompt renderer, graph catalog, generator, tests,
  and a clean checkout with no local prompt-review workspace
- **THEN** it accepts their registered paths and import directions, does not require a generated
  Markdown directory, and grants no generated Markdown execution authority
