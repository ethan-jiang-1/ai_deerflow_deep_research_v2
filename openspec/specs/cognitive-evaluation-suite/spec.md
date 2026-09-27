# cognitive-evaluation-suite Specification

> req: CES-001, CES-002, CES-003, CES-004, CES-005, CES-006, CES-007, CES-008, CES-009

## Purpose

Provide a manually orchestrated, Local-First evaluation surface that executes bounded
production node branches once, preserves objective evidence in isolated Bundles, and lets
an independent review workflow assess cognitive behavior without becoming production control.

## Requirements


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

### Requirement: Bundles preserve objective observations

Each accepted invocation SHALL produce an immutable Evaluation Run Bundle containing the
declared Case and control identity, observed inputs, actual outputs and artifacts, chronological
events and logs, observable tool/model calls, resource use, and typed diagnostics. If execution
fails after observations begin, the Bundle SHALL retain every material observation obtained
before the stop and SHALL identify the failed phase or reason. A Bundle SHALL contain no
cognitive quality verdict and SHALL not be used as a lifecycle checkpoint. Its finalized
manifest SHALL declare a digest for each required evidence record; review admission SHALL
reload the manifest and verify those digests before treating the Bundle as reviewable evidence.
The manifest SHALL also retain the exact Case, Node Cognitive Control Contract, Rubric, and
Review Protocol identities selected for that execution. When the executing repository is a git
worktree, the manifest SHALL also record that worktree's code revision at execution time, so a
retained Bundle always names the code that produced it; the revision is provenance for review
and reproduction and SHALL NOT gate review admission. Every finalized manifest SHALL carry an
explicit valid evidence layer. Review admission SHALL reject a retained Bundle whose manifest
omits that field or supplies an unknown value before any Review Record, quality claim, default,
backfill, or mutation is produced.

#### Scenario: Successful execution has inspectable evidence
- **WHEN** a node or bounded flow completes
- **THEN** its Bundle contains the declared input identity, actual output/artifact references, Observation Trace, resource observations, and `completed` status

#### Scenario: Failed execution retains partial observations
- **WHEN** a provider, tool, bridge, parser, timeout, or cancellation failure stops execution after observable work
- **THEN** the Bundle retains the observations collected before the stop, a typed failure reason, and `failed` status without fabricating a cognitive result

#### Scenario: Bundle finalization is immutable
- **WHEN** a Bundle is finalized
- **THEN** later review writes cannot modify its evidence, identity, status, or trace; an incomplete finalization is a failed execution rather than reviewable success

#### Scenario: Altered or incomplete Bundle is rejected before review
- **WHEN** a retained Bundle is missing a manifest-declared record or any declared digest no longer matches
- **THEN** review admission rejects that Bundle, creates no Review Record, and leaves its historical execution status unchanged

#### Scenario: Missing or unknown evidence layer is rejected before review
- **WHEN** a retained Bundle manifest omits `evidence_layer` or declares a value outside the supported layers
- **THEN** review admission rejects that Bundle before a Review Record or quality claim is created and does not write, backfill, default, or otherwise change the retained Bundle

#### Scenario: Explicit evidence layer remains reviewable
- **WHEN** a retained Bundle manifest declares a supported explicit evidence layer and its other integrity checks pass
- **THEN** review admission preserves that declared layer in the resulting Review Record without inferring another layer

#### Scenario: Changed control cannot reinterpret a retained Bundle
- **WHEN** a review submits a Case, Contract, Rubric, or Protocol identity that does not resolve to the identity retained in the Bundle manifest
- **THEN** review admission rejects that submission and creates no Review Record for the substituted control

#### Scenario: Manifest names the code that produced the execution
- **WHEN** a Runner finalizes an Evaluation Run Bundle in a git worktree
- **THEN** the manifest records the worktree's code revision, and a retained Bundle whose manifest predates this obligation and carries no revision stays reviewable when its other integrity checks pass

### Requirement: Review is explicitly human initiated

The Suite SHALL expose a separate review operation that accepts a retained, integrity-verified Bundle reference,
the relevant Node Cognitive Control Contract, its Case-linked Rubric, and the versioned
Evaluation Review Protocol. Only an explicit person or approved human-controlled interface
may initiate that operation. The review workflow SHALL be read-only with respect to the Bundle,
production code and prompts, Rubric, production state, and execution environment, and SHALL
never start a new execution. Before review begins, the operation SHALL resolve those inputs
against the exact control identities retained in the Bundle manifest and reject a stale or
substituted control input.

#### Scenario: A person submits a retained Bundle for review
- **WHEN** a person explicitly selects a Bundle and invokes an approved review interface
- **THEN** the review workflow receives that Bundle and declared review inputs without rerunning the subject

#### Scenario: Deferred review leaves execution untouched
- **WHEN** a person does not request review after a Runner invocation
- **THEN** the Bundle remains retained with its execution status and no review record is created automatically

#### Scenario: Review cannot mutate execution or production
- **WHEN** a review workflow inspects a Bundle and source seam
- **THEN** it cannot alter the Bundle, production prompt/code, checkpoint, route, artifact admission, or provider state

### Requirement: Review records are separate and traceable

Every completed review SHALL produce a separate immutable Review Record that references the
Bundle without modifying it. The record SHALL identify the integrity-verified Bundle, Case and
control versions, Node Cognitive Control Contract, Rubric, Review Protocol, evaluator or
interface, review time, and the explicit valid evidence layer retained in the verified Bundle
manifest. Its Case and control identities SHALL exactly match the retained Bundle manifest. It
SHALL include the four-state Cognitive Evaluation Result, rubric evidence, confidence, unknowns,
likely owning layer, first source seam, and proposed follow-up. A Review Record supplied for
validation with a missing or unknown evidence layer SHALL be rejected; it SHALL not be defaulted
or upgraded to a live-quality claim. Multiple records MAY reference the same Bundle.

#### Scenario: Same Bundle supports independent reviews
- **WHEN** two approved reviewers inspect one retained Bundle
- **THEN** two distinct Review Records may be stored, each retaining its own identity and conclusion while the Bundle remains unchanged

#### Scenario: Missing provenance cannot form a valid review
- **WHEN** a review result omits its Bundle, Case, control, Rubric, Protocol, evaluator, evidence identity, or evidence layer
- **THEN** Review Record validation rejects it rather than storing detached evaluator prose or inferred provenance

#### Scenario: Unknown evidence layer cannot form a valid review
- **WHEN** a Review Record input supplies an evidence layer outside the supported layers
- **THEN** Review Record validation rejects it rather than storing or upgrading the claimed provenance

#### Scenario: Review provenance must match the execution control
- **WHEN** a Review Record supplies a Case or control identity that differs from its referenced Bundle manifest
- **THEN** Review Record validation rejects it rather than letting a later control reinterpret the execution

#### Scenario: Review follow-up is advisory
- **WHEN** a Review Record proposes a source seam, new scenario, or OpenSpec change
- **THEN** the proposal remains advice for a person or coding agent and cannot change production state or schedule a Runner invocation

### Requirement: Evaluation contracts have one supported runtime facade

The Cognitive Evaluation Suite SHALL expose supported Python runtime contract imports only through
`deerflow_deep_research.runtime.evaluation`. That facade SHALL project the contracts whose facts
remain owned by the evaluation domain; its projection SHALL not create a second fact authority.
Runtime implementation modules SHALL consume those domain-owned contracts directly without
creating another supported consumer route. The legacy
`deerflow_deep_research.runtime.evaluation.contracts` module SHALL be absent and SHALL not retain
an alias, fallback, or compatibility reader.

#### Scenario: Supported facade projects domain-owned contracts
- **WHEN** an application consumer imports an Evaluation contract through the supported runtime facade
- **THEN** it receives the domain-owned contract without a competing runtime contract definition

#### Scenario: Retired compatibility module is not importable
- **WHEN** a consumer imports the retired `runtime.evaluation.contracts` module
- **THEN** the import fails and the consumer must use the supported runtime facade

### Requirement: Execution status and cognitive result remain independent

The Runner SHALL report exactly two execution statuses: `completed` when the declared subject
finishes, or `failed` otherwise. The review workflow SHALL report one of `pass`, `limited`,
`inconclusive`, or `failed` according to the Case Rubric. Execution failure SHALL not be
converted into a cognitive result, and `limited` or `inconclusive` SHALL never count as `pass`.

#### Scenario: A completed run can have a non-pass review
- **WHEN** execution completes but the Bundle lacks enough evidence or misses a Rubric criterion
- **THEN** the Bundle remains `completed` and the Review Record is `inconclusive` or `limited`, never silently `pass`

#### Scenario: A failed run has no fabricated quality grade
- **WHEN** execution fails before a candidate can be assessed
- **THEN** the Bundle is `failed` with diagnostics and no cognitive result is recorded for that execution

#### Scenario: A critical cognitive criterion fails
- **WHEN** a review can assess the Bundle and a critical Rubric criterion fails
- **THEN** the Review Record is `failed` while execution status remains unchanged

### Requirement: V1 provides bounded node smoke cases

V1 SHALL register at least one Node Cognitive Smoke Scenario for the production HITL1 brief
branch and at least one for the production Wave0 worker branch. Each Case SHALL invoke the
declared production branch through its existing bridge, parser, tool policy, and deterministic
admission boundary, and SHALL preserve a private Bundle for later human-initiated review.
V1 SHALL not register a complete Flow Evaluation Run, routine CI collection, automatic review,
or automatic retry as a prerequisite for these cases.

#### Scenario: HITL1 smoke isolates the brief branch
- **WHEN** the HITL1 brief Case is explicitly run
- **THEN** the Bundle identifies the HITL1 branch and its existing no-tool/call-bound posture without claiming whole-graph or report quality

#### Scenario: Wave0 smoke observes real retrieval behavior
- **WHEN** the Wave0 worker Case is explicitly run with required model and web prerequisites
- **THEN** the Bundle records the bounded production retrieval/tool observations and existing candidate boundary without admitting evidence outside the production controller

#### Scenario: V1 excludes a flow claim
- **WHEN** only the V1 node Cases have been registered and executed
- **THEN** the Suite does not report complete-flow quality or Research Outcome acceptance

### Requirement: Cognitive Evaluation Bundles remain a separate domain after the Harness move

The Cognitive Evaluation Suite SHALL retain its distinct evaluation control surface,
evaluation-run workspace, and immutable Evaluation Run Bundle semantics under the
canonical `deep_research_harness/` project root. A Cognitive Evaluation Bundle SHALL
not be a Deep Research Run Bundle, Current Bundle Handle target, scoped discovery
candidate, lifecycle State source, or recovery source. Deep Research Bundle loss SHALL
not alter evaluation records, and evaluation records SHALL not restore a lost Deep
Research Run. (`CES-008`)

#### Scenario: Separate evaluation record cannot recover Deep Research
- **WHEN** an Evaluation Run Bundle contains observations about a Deep Research execution whose Run Bundle was deleted
- **THEN** Deep Research control returns unavailable and evaluation data remains read-only evaluation evidence
