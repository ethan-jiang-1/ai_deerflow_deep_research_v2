## MODIFIED Requirements

### Requirement: A canonical Deep Research Agent Charter is discoverable

The project SHALL maintain `openspec/agent-charter/` as the permanent home for the
Deep Research Agent Charter. Its index SHALL route contributors to every canonical
policy in the `openspec/policies/` library whose route-table trigger applies to the
change, while the change retains exactly one primary causal owner. The index SHALL
distinguish durable charter principles, focused policies, owning capability
specifications, scoped operational procedures, and current runtime facts. The Charter
and every policy SHALL state that they are design/admission guidance and do not create
runtime authority. The Charter tree SHALL contain only its routing index and durable
principles; it SHALL not contain a second nested policy directory or compatibility copy
of policy prose. (`DRC-001`, `DRC-005`)

#### Scenario: Contributor routes a local change without scanning the repository
- **WHEN** a contributor begins a Deep Research change affecting one owned module
- **THEN** the Charter index identifies the local-context policy in the canonical
  policy library and directs the contributor to the owning capability specification
  and local evidence seam rather than requiring an undifferentiated read of root
  DeerFlow documentation

#### Scenario: Multiple applicable policy triggers are all selected
- **WHEN** one change affects both a participant-visible lifecycle output and a
  bounded retry or recovery path
- **THEN** its Charter route selects both `participant-outcomes` and
  `control-and-recovery` because both triggers apply, records them as canonical names
  on the same Focus Card field, and retains one primary causal owner for the change

#### Scenario: Multiple selected policies do not create runtime authority
- **WHEN** a contributor selects more than one triggered policy for a change
- **THEN** those policies remain design/admission guidance and the contributor still
  places any lifecycle action, state field, graph route, permission, or provider
  behavior in its owning capability delta rather than treating the policy selection as
  runtime authority

#### Scenario: Charter and policy library are discoverable from OpenSpec root
- **WHEN** a contributor opens `openspec/` to begin a Deep Research change
- **THEN** it can discover `agent-charter/` as the one routing entry and `policies/`
  as the one complete policy library without traversing a governance subtree or
  choosing between duplicate policy homes

#### Scenario: A behavior proposal is placed in its owning contract
- **WHEN** a proposed policy would add a lifecycle action, state field, graph route,
  permission, or provider behavior
- **THEN** the charter index directs the change to an owning capability delta and
  the policy does not claim to establish that behavior by itself
