> req: PRS-010

## ADDED Requirements

### Requirement: Human interaction has a registered domain contract seam

The project structure registry SHALL list the domain-owned human-interaction contract
module and its focused deterministic tests under the existing `domain` ownership layer.
The module SHALL not create a new ownership layer or import runtime, graph, or adapter
code. (`PRS-010`)

#### Scenario: Architecture registry recognizes the contract owner
- **WHEN** architecture governance scans the human-interaction source and test paths
- **THEN** it accepts the registered domain seam and retains existing forbidden-layer
  import checks
