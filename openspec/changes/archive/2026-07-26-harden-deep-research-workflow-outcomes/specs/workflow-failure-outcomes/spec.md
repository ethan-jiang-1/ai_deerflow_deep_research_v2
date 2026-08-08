> req: WFO-001, WFO-002

## ADDED Requirements

### Requirement: Production model invocation failures preserve one phase-owned safe outcome

Every production graph-node package that invokes `run_agent` SHALL normalize a
successful result, a safe classified non-success result, a local unknown failure,
and cancellation through one workflow-outcome seam. A known `NodeProblem` SHALL
retain its closed code, certainty, provider observation when present, and
originating phase until its owning phase records either a terminal incident or a
classified work-attempt result. Cancellation SHALL propagate. Raw exceptions,
provider bodies, and generic replacement `ValueError` values SHALL NOT be the
durable or user-facing representation of a known invocation failure.

#### Scenario: A direct phase preserves a known provider timeout
- **WHEN** a direct real phase receives a non-successful result with a
  `provider.timeout` problem
- **THEN** its phase-owned recovery or terminal update receives that same safe
  classification and the lifecycle can project a terminal incident without
  fabricating raw provider detail

#### Scenario: A worker phase preserves a known failure through its controller
- **WHEN** a real worker phase receives a non-successful result with a safe
  invocation problem
- **THEN** it produces the closed work-attempt classification required by its
  controller and retains the safe invocation category in the bounded attempt/event
  observation rather than raising an unclassified generic error

#### Scenario: An unmapped local failure remains honest
- **WHEN** a phase boundary catches a non-cancellation failure without a safe
  classified node problem
- **THEN** it fails closed with an explicit bounded unknown outcome and does not
  label it as provider timeout, provider unavailable, or structured output failure

### Requirement: Workflow outcome evidence is complete for every discovered model owner

The deterministic workflow evidence inventory SHALL syntax-discover every production
graph-node package that invokes `run_agent`. Each discovered owner SHALL declare its
applicable closed outcome classes and collected scripted-real-node evidence at its
phase seam, plus a collected lifecycle or work-controller projection assertion. The
inventory SHALL fail when an owner, applicable outcome class, selector, or projection
assertion is missing or stale.

#### Scenario: A new run-agent owner cannot bypass outcome coverage
- **WHEN** production source adds a graph-node package that invokes `run_agent`
- **THEN** deterministic governance fails until that owner has a declared outcome
  coverage entry and collected evidence

#### Scenario: A success-only workflow case is insufficient
- **WHEN** an owner has a scripted successful workflow case but no assertion for
  one of its declared non-success outcome classes
- **THEN** the outcome coverage validator rejects the owner rather than accepting
  success-path evidence as failure-path conformance
