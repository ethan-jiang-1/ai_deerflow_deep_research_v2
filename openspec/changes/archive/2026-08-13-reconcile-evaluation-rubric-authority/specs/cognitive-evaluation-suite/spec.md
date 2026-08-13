## MODIFIED Requirements

### Requirement: Evaluation cases bind execution inputs

The Cognitive Evaluation Suite SHALL execute only a named, versioned, registered Evaluation
Execution Case. A Case SHALL declare a finite node branch or bounded flow subject, fixed
inputs or fixtures, required service prerequisites, resource and timeout bounds, and the
control-version identity. The execution interface SHALL reject free-form prompts, arbitrary
paths, model overrides, and resume or checkpoint state supplied by the caller.

A Case-linked Rubric has five distinct roles. Its case/version identity and the set of
unique criterion IDs declared by its source-controlled control artifact are
case-control-integrity metadata. Deterministic admission SHALL read only that identity
and criterion-ID set to verify that the selected Case and its scenario declarations name
the same closed control. Criterion prose, weights, thresholds, evaluator guidance, and
any cognitive result are review-only content. They SHALL NOT enter a subject fixture,
model-facing execution input, execution output, or Runner completion status. The Runner
and its execution subject SHALL not interpret criterion IDs as a quality judgment or
produce a cognitive quality verdict.

#### Scenario: Unknown or malformed Case is rejected before invocation
- **WHEN** a caller supplies an unknown Case id, stale Case version, invalid fixture, or an out-of-bound resource declaration
- **THEN** the Suite rejects the invocation before invoking a production node or flow and records no completed execution

#### Scenario: Free-form execution parameters cannot bypass the Case
- **WHEN** a caller supplies an ad-hoc prompt, filesystem path, model override, or resume state in addition to a registered Case
- **THEN** the Suite rejects the extra authority rather than widening the declared execution

#### Scenario: Case and control identity are retained
- **WHEN** a registered Case is accepted
- **THEN** the resulting execution evidence identifies the Case version and every control artifact version required to interpret it

#### Scenario: Criterion-ID integrity is verified before subject construction
- **WHEN** the declared Rubric identity/version is stale or its unique criterion-ID set is missing, duplicated, or differs from the selected Case's scenario declarations
- **THEN** deterministic admission rejects the Case before a model/tool invocation, execution subject, artifact, Bundle, or review is created

#### Scenario: Rubric content does not become an execution-quality input
- **WHEN** a Case is accepted after its identity and criterion-ID set are verified
- **THEN** criterion prose, weights, thresholds, evaluator guidance, and any quality disposition remain absent from model-facing execution input, execution output, and Runner completion status

### Requirement: The Runner executes one fresh isolated attempt

The Python Cognitive Evaluation Runner SHALL create a new private Evaluation Run Workspace
for each accepted invocation and SHALL execute the declared subject exactly once. It SHALL
not retry, resume, queue another attempt, invoke an evaluator, or alter production recovery
behavior. A caller that wants another attempt SHALL start a separate invocation, which SHALL
receive a different workspace and Bundle. The Runner SHALL report only `completed` or
`failed`; verified case-control-integrity metadata SHALL not produce or change a cognitive
quality verdict.

#### Scenario: Concurrent or repeated invocations do not share execution state
- **WHEN** two invocations use the same Case, or one Case is invoked again after failure
- **THEN** each invocation receives a distinct workspace and cannot read or write the other's checkpoint, artifact, or Bundle namespace

#### Scenario: Runner completion does not start review
- **WHEN** the declared subject finishes and the Runner materializes its Bundle
- **THEN** the Runner returns the Bundle reference and execution status without invoking, queuing, or selecting a review workflow

#### Scenario: Runner does not hide a retry
- **WHEN** the declared subject times out, is cancelled, or returns an execution failure
- **THEN** the Runner stops that invocation once, reports `failed`, and leaves any later attempt to an explicit fresh invocation

#### Scenario: Verified criterion IDs do not create a quality result
- **WHEN** deterministic admission accepts a Case after verifying its Rubric identity and criterion-ID set
- **THEN** the Runner still reports only the execution's `completed` or `failed` status and leaves every cognitive disposition to a separate review
