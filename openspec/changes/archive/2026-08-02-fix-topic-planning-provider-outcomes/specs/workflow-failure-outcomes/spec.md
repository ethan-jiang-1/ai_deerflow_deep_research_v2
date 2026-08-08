## MODIFIED Requirements

### Requirement: Production model invocation failures preserve one phase-owned safe outcome

Every production graph-node package that invokes `run_agent` SHALL normalize a
successful result, a safe classified non-success result, a local unknown failure, and
cancellation through one workflow-outcome seam. A known `NodeProblem` SHALL retain its
closed code, certainty, provider observation when present, and originating phase until
its owning phase records either a terminal incident or a classified work-attempt
result. The newly closed `provider.usage_unavailable`, `budget.exhausted`, and
`policy.denied` categories are known invocation failures and SHALL be retained exactly;
they SHALL not be replaced by `tool.execution_failed`, `research.blocked`, or an
unclassified local failure. A direct phase SHALL retain a supplied safe diagnostic
reference when present and SHALL derive or publish diagnostic identity only from typed
safe fields, never from a raw exception or stop detail. Cancellation SHALL propagate.
Raw exceptions, provider bodies, and generic replacement `ValueError` values SHALL NOT
be the durable or user-facing representation of a known invocation failure.

#### Scenario: A direct phase preserves a known provider timeout
- **WHEN** a direct real phase receives a non-successful result with a
  `provider.timeout` problem
- **THEN** its phase-owned recovery or terminal update receives that same safe
  classification and the lifecycle can project a terminal incident without fabricating
  raw provider detail

#### Scenario: A direct phase preserves a closed phase-agent stop
- **WHEN** topic planning receives a non-successful result with
  `provider.usage_unavailable`, `budget.exhausted`, or `policy.denied`
- **THEN** its terminal incident and later diagnostic/presentation projection retain
  that same code and phase without attaching provider recovery facts or replacing it
  with a tool failure

#### Scenario: A worker phase preserves a known failure through its controller
- **WHEN** a real worker phase receives a non-successful result with a safe invocation
  problem
- **THEN** it produces the closed work-attempt classification required by its
  controller and retains the safe invocation category in the bounded attempt/event
  observation rather than raising an unclassified generic error

#### Scenario: An unmapped local failure remains honest
- **WHEN** a phase boundary catches a non-cancellation failure without a safe
  classified node problem
- **THEN** it fails closed with an explicit bounded unknown outcome and does not label
  it as provider timeout, provider unavailable, structured output failure, or a known
  phase-agent stop
