## MODIFIED Requirements

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
