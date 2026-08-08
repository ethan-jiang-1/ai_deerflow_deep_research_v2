> req: PRS-012

## ADDED Requirements

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
