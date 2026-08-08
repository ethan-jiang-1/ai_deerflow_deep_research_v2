> req: PRS-002
> structure: openspec/governance/project-structure.toml

## MODIFIED Requirements

### Requirement: Import and shared-code boundaries are mechanical

The project SHALL enforce import direction with an AST-based contract. Domain code
SHALL depend only on the standard library and Pydantic; engine code SHALL depend only
on domain; agents SHALL depend only on domain plus public DeerFlow/LangChain APIs;
ordinary node modules SHALL depend only on domain/engine, except that graph-owned HITL
node modules (`fake.py` or `node.py` under HITL packages) MAY import exactly public
`langgraph.types.interrupt`. A node package's optional phase-local `subgraph.py` MAY
additionally import public LangGraph APIs required for its internal `Send`
fan-out/fan-in and reusable cross-node subflows under `graph/components/`. Reusable
graph components MAY depend on domain, engine, and public LangGraph APIs. None of these
exceptions MAY import other graph implementation modules, agents, runtime, or sibling
nodes. Runtime SHALL be the only layer allowed to bind graph execution to raw DeerFlow
context, request-bundle host I/O, and the embedded-agent factory. Its only direct
provider-classifier namespace exception is `httpx` and `openai` in
`runtime/node_agent_bridge.py`; those packages SHALL be direct `agent/` dependencies,
listed in the exact structural import registry, and mechanically rejected from every
other runtime module or layer. Production downstream code SHALL not import `app.*`; and
generic shared modules named `utils`, `helpers`, or `common` SHALL be rejected.

#### Scenario: Valid dependency direction passes
- **WHEN** the contract scans the canonical downstream package including a node-owned phase-local subgraph using public LangGraph and a HITL fake importing only public `interrupt`
- **THEN** every import resolves within the allowed layer direction and the subgraph does not gain access to other graph implementation modules, runtime, agents, or sibling nodes

#### Scenario: Direct provider classifier imports stay at the raw binding
- **WHEN** architecture governance scans direct `httpx` or `openai` imports
- **THEN** it accepts them only from `runtime/node_agent_bridge.py` and rejects the same imports from every other runtime module or layer

#### Scenario: Real HITL interrupt import passes narrowly
- **WHEN** the contract scans `agent/src/deerflow_deep_research/graph/nodes/hitl1/node.py` and it imports exactly `langgraph.types.interrupt`
- **THEN** the import is accepted as a graph-owned HITL interrupt boundary, while other LangGraph imports from ordinary node modules remain rejected

#### Scenario: Reverse dependency fails closed
- **WHEN** a fixture makes domain code import runtime code, an ordinary non-HITL node module import LangGraph or `graph/components/`, a HITL node import LangGraph APIs other than `langgraph.types.interrupt`, a node-local `subgraph.py` import graph implementation outside `graph/components/`, a node import agents/runtime, or one node import another node
- **THEN** the contract fails with the importing and imported module names
