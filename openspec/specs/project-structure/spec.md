# project-structure Specification

> req: PRS-001, PRS-002, PRS-003, PRS-004, PRS-005, PRS-006, PRS-007, PRS-009, PRS-010, PRS-011, PRS-012, PRS-013, PRS-014, PRS-015, PRS-016, PRS-017, PRS-018, PRS-019, PRS-020, PRS-021, PRS-022
> structure: openspec/governance/project-structure.toml

## Purpose
The canonical downstream package structure, mechanically enforced import directions and node surface, and archive-durable architecture governance.

## Requirements

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

### Requirement: Registered ignore policy mirrors the harness gitignore

The project-structure manifest's registered ignore policy (`[ignored_paths].entries`
in `openspec/governance/project-structure.toml`) SHALL mirror the effective
`deep_research_harness/.gitignore` directory entries exactly — same lines, same
order — and the architecture checker SHALL fail closed (`ignore.entries`) on any
drift between the two. The `.gitignore` remains the fact source for locally ignored
paths; the manifest remains the single registered policy the checker compares
against, and neither surface SHALL be synchronized by editing only one side.
(`PRS-022`)

#### Scenario: Registered ignore policy matches the harness gitignore
- **WHEN** the architecture checker compares `[ignored_paths].entries` with `deep_research_harness/.gitignore`
- **THEN** the comparison passes only on exact ordered equality, and the governance gate exits 0 on a clean working tree

#### Scenario: Ignore policy drift fails closed
- **WHEN** `.gitignore` gains, loses, or reorders an ignored directory without a synchronized manifest entry (as happened when `.uv-cache/` landed in commit `07a7a1c` without a registry sync — BUG-066)
- **THEN** the checker reports `ignore.entries` and exits nonzero instead of accepting a partially synchronized policy

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
SHALL remain limited to `httpx` and `openai` in `runtime/node_agent_bridge.py`; the
structured-SSE Gateway observer in `runtime/gateway_observer.py` SHALL be the only other
runtime module permitted to import `httpx` and `httpx_sse`; those packages SHALL be
mechanically rejected from every other production layer.

The per-layer import matrix SHALL separate internal-layer import directions from external
namespaces. Internal-layer import directions — which internal layers each layer MAY import —
SHALL be a fixed, non-weakenable constraint enforced by the architecture checker; the
`[imports]` table SHALL NOT be able to add an internal layer to a layer that the
import-direction rules above exclude. External namespaces — packages outside the internal
layers — SHALL be authorized by the `[imports]` table for per-layer assignment and by a
closed top-level-namespace whitelist for namespace legality; a genuinely new external
namespace SHALL require a one-time entry in that whitelist, while assigning an
already-whitelisted namespace to a layer SHALL require only a TOML edit. The checker SHALL
NOT hard-code a per-layer external-namespace set. The import-boundary keys SHALL be `domain`,
`engine`, `agents`, `graph`, `nodes`, and `runtime`, where `nodes` is the graph-owned
node-package import sub-layer; this does not change the five documented production ownership
layers (`runtime`, `domain`, `engine`, `agents`, `graph`).

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

#### Scenario: Internal-layer import directions are non-weakenable
- **WHEN** the `[imports]` table adds an internal layer (for example `runtime`) to a layer
  whose import-direction rules exclude it (for example `domain`)
- **THEN** the architecture checker rejects the manifest

#### Scenario: External namespace assignment is single-source
- **WHEN** an already-whitelisted external namespace is assigned to a declared layer in the
  `[imports]` table
- **THEN** the architecture checker accepts it for those layers without editing any per-layer
  set in checker source, and checker source contains no per-layer external-namespace set

#### Scenario: A genuinely new external namespace requires a one-time whitelist entry
- **WHEN** an external namespace not present in the closed whitelist is added to the
  `[imports]` table
- **THEN** the architecture checker rejects the manifest until that namespace is added to the
  whitelist

#### Scenario: Import-boundary layers remain distinct from ownership layers
- **WHEN** architecture governance validates the `[imports]` table
- **THEN** it requires the six import-boundary keys (including `nodes`) while the documented
  production ownership layers remain five (`runtime`, `domain`, `engine`, `agents`, `graph`)

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

### Requirement: Run-experience contracts use the canonical domain and runtime ownership layers

The existing run-experience domain and runtime contracts SHALL remain under
`deep_research_harness/src/deerflow_deep_research/` at their registered canonical
paths. The public Gateway observation boundary SHALL live at the registered runtime
path
`deep_research_harness/src/deerflow_deep_research/runtime/gateway_observer.py`, and
its deterministic contract evidence SHALL remain under registered
`deep_research_harness/tests/` paths. Its dependency direction SHALL permit only the
existing domain contracts plus approved public HTTP/SSE libraries and SHALL not import
presentation scripts or private DeerFlow Gateway modules.

The existing run-experience dependency-direction, runtime-binding, and presentation-
adapter boundaries remain unchanged; `deep_research_harness/scripts/` remains only a
permitted presentation/launcher-adapter location, not a lifecycle authority. The
structure registry SHALL admit `httpx_sse` only for the bounded runtime Gateway
observer and SHALL continue to reject upstream source placement, private Gateway
imports, and generic `utils`/`helpers`/`common` modules. (`PRS-005`)

#### Scenario: Run-experience paths follow the Harness root
- **WHEN** structural governance inspects the registered run-experience and Gateway
  observer modules
- **THEN** it finds their domain/runtime/test paths beneath `deep_research_harness/`
  and rejects an old-root duplicate, presentation-owned lifecycle module, or upstream
  placement

#### Scenario: Structured SSE dependency remains bounded
- **WHEN** the architecture checker evaluates runtime imports for the Gateway observer
- **THEN** `httpx_sse` is permitted only through the declared runtime dependency rule,
  while private DeerFlow Gateway modules and reverse imports into scripts remain
  rejected

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
registries or storage areas. The exact structural registry SHALL retain the
`runtime/evaluation` directory and its supported `__init__.py` facade, but SHALL not
retain the retired `runtime/evaluation/contracts.py` re-export path. (`PRS-015`)

#### Scenario: Evaluation paths move without joining Deep Research discovery
- **WHEN** structural governance validates evaluation source and `evals/` paths after the move
- **THEN** they resolve beneath `deep_research_harness/` and remain outside Deep Research
  Run Bundle discovery

#### Scenario: Retired evaluation contract path is absent from the registry
- **WHEN** structural governance validates the registered evaluation paths after the compatibility cutover
- **THEN** it requires the supported facade, rejects an unregistered replacement, and does not enumerate `runtime/evaluation/contracts.py`

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

### Requirement: The upstream gitlink boundary is mechanically verified

The exact project-structure registry SHALL declare one `[upstream_gitlink]` table with
only a normalized repository-relative `path` and a full lower-case 40-character Git
`commit` identifier. Full architecture governance SHALL fail closed unless the declared
path is a non-symlink directory whose root Git index contains exactly one stage-zero
gitlink entry (mode `160000`, with no alternate-stage entry) at that path, the entry's
commit identifier equals the declared identifier, the nested worktree's checked-out
`HEAD` equals that identifier, and its porcelain status, including untracked paths, is
empty. A missing, failed, or malformed metadata query SHALL also fail closed.

The checker SHALL inspect only filesystem and Git metadata needed for those facts. It
SHALL NOT read tracked DeerFlow source files, walk the nested worktree, write to either
repository, initialize or update a submodule, or claim runtime compatibility with the
pinned upstream revision. The checker's `--imports-only` mode SHALL validate the static
registry shape but SHALL NOT query the gitlink; it is not full architecture governance.
(`PRS-018`)

#### Scenario: Matching clean gitlink passes architecture governance
- **WHEN** the registry's two-field gitlink lock matches the sole root stage-zero
  gitlink entry, the nested worktree `HEAD`, and an empty nested porcelain status
- **THEN** architecture governance accepts that upstream-boundary fact while retaining
  its existing downstream structure and import checks

#### Scenario: Missing, malformed, or moved boundary fails closed
- **WHEN** the registry entry is malformed, contains an unexpected field, the declared
  path is absent or a symlink, the root index entry is missing/not the sole mode
  `160000` stage-zero entry, or the index or nested `HEAD` commit differs from the
  declared identifier
- **THEN** architecture governance rejects the checkout with a boundary-specific
  diagnostic and does not reset, checkout, stage, or otherwise alter either repository

#### Scenario: Dirty nested worktree fails closed
- **WHEN** the declared gitlink and commit identifiers otherwise match but the nested
  worktree has a modified, deleted, staged, or untracked path
- **THEN** architecture governance rejects the boundary rather than treating the root
  gitlink entry as sufficient evidence of a clean upstream dependency

#### Scenario: Metadata inspection failure fails closed
- **WHEN** the registry lock is structurally valid but any defined Git metadata command
  cannot execute or returns malformed output
- **THEN** full architecture governance rejects the boundary without falling back to a
  guessed commit, stale receipt, source inspection, or a mutating Git command

#### Scenario: Import-only checking does not inspect the gitlink
- **WHEN** the architecture checker is invoked with `--imports-only` against a manifest
  with a valid static gitlink lock
- **THEN** it validates import/registry syntax without issuing a gitlink metadata query
  or treating the result as full architecture-governance validation

#### Scenario: Intentional upstream bump is explicitly declared
- **WHEN** a reviewed owning change updates both the root gitlink index entry and the
  registry's declared commit identifier to the same new full commit identifier, and the
  nested worktree is clean at that commit
- **THEN** architecture governance accepts the new declared boundary without inferring
  that the checker authorized the bump or proved its runtime compatibility

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

### Requirement: Dev-harness doc-layer hygiene occupies a canonical governance path with a deterministic checker

The canonical structure SHALL register `openspec/governance/check_doc_hygiene.py` as
the dev-harness doc-layer hygiene checker. The checker SHALL exit non-zero when a
registered doc-layer rule is violated — an ADR index that lists a missing file or
omits a present ADR, a relative link in an entry-chain document or in a docs-layer
document that does not resolve to an existing file, or an entry-chain document or
docs-layer document that is not UTF-8 or lacks a trailing newline — and SHALL exit
zero on a clean tree. A docs-layer document is a markdown document under
`deep_research_harness/docs/` — the top-level `docs/*.md` documents and the
`docs/adr/*.md` decision records; non-markdown files under that tree are outside the
checker's scope. The checker SHALL compare the markdown documents actually present in
that tree against its registered docs-layer scope and SHALL exit non-zero when a
present markdown document is missing from that scope, so coverage cannot silently
shrink. The checker SHALL provide a `--self-test` negative-control mode that
proves each rule fails on a planted violation, including planted violations located
in the docs-layer scope. The checker SHALL NOT be aggregated into the OpenSpec root
governance gate (the `project-structure` gate requirement owns the six-component
closeout and forbids a separate consistency checker) and SHALL NOT be wired into the
Harness `make verify` gate, which remains application-independent. (`PRS-020`)

#### Scenario: Clean tree exits zero

- **WHEN** the doc layer is clean — every ADR is listed in the index, every relative
  entry-chain and docs-layer link resolves, and the entry-chain and docs-layer
  documents are UTF-8 with a trailing newline
- **THEN** the checker exits zero

#### Scenario: ADR index drift is rejected

- **WHEN** the ADR index lists a file that is absent from `docs/adr/`, or a present ADR
  file is missing from the index
- **THEN** the checker exits non-zero and names the drifted file and the violated rule

#### Scenario: Broken entry-chain link is rejected

- **WHEN** an entry-chain document contains a relative markdown link that does not
  resolve to an existing file
- **THEN** the checker exits non-zero and names the document and the broken target

#### Scenario: Broken docs-layer link is rejected

- **WHEN** a markdown document under `deep_research_harness/docs/` (top level or
  `adr/`) contains a relative markdown link that does not resolve to an existing file
- **THEN** the checker exits non-zero and names the document and the broken target

#### Scenario: Encoding or newline drift is rejected

- **WHEN** an entry-chain document or docs-layer document is not UTF-8 decodable or
  lacks a single trailing newline
- **THEN** the checker exits non-zero and names the document and the violation

#### Scenario: Non-markdown docs files stay out of scope

- **WHEN** the docs tree contains a non-markdown file (for example a JSON attestation)
  with encoding or content that would violate a markdown rule
- **THEN** the checker neither reads nor reports that file, and exits per the markdown
  documents' state alone

#### Scenario: Unregistered docs-layer markdown is rejected

- **WHEN** a markdown document exists under `deep_research_harness/docs/` but is
  missing from the checker's registered docs-layer scope
- **THEN** the checker exits non-zero and names the unregistered document

#### Scenario: Negative control proves each rule

- **WHEN** the `--self-test` mode runs
- **THEN** a clean fixture exits zero, and each rule's planted violation exits non-zero,
  with link, encoding, newline, and unregistered-document violations exercised in the
  docs-layer scope as well as the entry-chain scope

#### Scenario: Gate and Harness composition stay unchanged

- **WHEN** the OpenSpec root governance gate and the Harness `make verify` gate run
- **THEN** neither gate invokes `check_doc_hygiene.py`, and their six-component and
  application-independent composition is unchanged

### Requirement: Architecture checker enforces the generated structure-locator block

The architecture checker SHALL mechanically enforce the generated structure-locator
block in `deep_research_harness/AGENTS.md`. It SHALL require the block's
`begin_marker` and `end_marker`, declared in the `[guide]` registry table, to appear
exactly once each; SHALL require the block content to match the deterministic render
of the current structure registry; and SHALL exit non-zero with the violated rule
named when the block is missing, duplicated, or drifted. The checker SHALL expose a
`--render-guide` mode that prints the deterministic block for regeneration.
(`PRS-021`)

#### Scenario: Locator block matches the registry

- **WHEN** `deep_research_harness/AGENTS.md` contains exactly one generated
  structure-locator block matching the current registry render
- **THEN** architecture governance passes and the block names the current canonical
  roots, ownership layers, node grammar, and validation command

#### Scenario: Missing or duplicated markers are rejected

- **WHEN** the locator markers are absent or appear more than once in
  `deep_research_harness/AGENTS.md`
- **THEN** the architecture checker exits non-zero naming the missing or duplicated
  marker rule

#### Scenario: Registry drift is rejected

- **WHEN** the block content differs from the deterministic render of the current
  structure registry (for example a stale root or layer)
- **THEN** the architecture checker exits non-zero with `guide.drift`, and
  `--render-guide` prints the correct block for regeneration
