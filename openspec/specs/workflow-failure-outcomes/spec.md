# workflow-failure-outcomes Specification

> req: WFO-001, WFO-002

## Purpose

Define the bounded, phase-owned handling and deterministic conformance evidence for
non-successful production model invocations across the Deep Research workflow.

## Requirements

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
  classification and the lifecycle can project a terminal incident without
  fabricating raw provider detail

#### Scenario: A direct phase preserves a closed phase-agent stop
- **WHEN** topic planning receives a non-successful result with
  `provider.usage_unavailable`, `budget.exhausted`, or `policy.denied`
- **THEN** its terminal incident and later diagnostic/presentation projection retain
  that same code and phase without attaching provider recovery facts or replacing it
  with a tool failure

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
  label it as provider timeout, provider unavailable, structured output failure, or a
  known phase-agent stop

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

### Requirement: Provider diagnostic reference identity retains observed timeout roles

The shared `workflow_outcomes.derive_provider_diagnostic_reference()` helper SHALL
remain the sole canonical identity owner for provider-diagnostic terminal references
used by all existing callers, including direct phase and controller-derived worker
incidents. When a recovery trigger or final provider observation carries a closed timeout
origin, the helper SHALL include that exact origin in its corresponding trigger or final
safe identity role. It SHALL not merge roles, infer an absent origin, or include raw
exceptions, provider bodies, prompts, credentials, full URLs, host paths, or request
payloads.

When neither observation carries an origin, the helper SHALL retain its exact current
version-one identity payload and resulting reference: it SHALL not add a null origin
field, change the payload version, or otherwise churn origin-absent references. HITL1,
topic planning, Wave2, and controller-derived worker incidents SHALL continue to use
this helper rather than define a local reference identity. (`WFO-001`)

#### Scenario: Distinct observed roles produce distinct safe references
- **WHEN** two otherwise identical provider-diagnostic terminals differ only in a
  trigger or final timeout origin
- **THEN** their references differ only through the corresponding safe role input, with
  no raw/provider material represented in either identity

#### Scenario: Origin-absent reference remains compatible
- **WHEN** the trigger and final observations both carry no timeout origin
- **THEN** the helper produces the exact current version-one reference for the same
  existing safe inputs
