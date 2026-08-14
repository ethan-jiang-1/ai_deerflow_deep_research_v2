> req: CES-009

## MODIFIED Requirements

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
Review Protocol identities selected for that execution. Every finalized manifest SHALL carry an
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
- **THEN** review admission rejects the Bundle before a Review Record or quality claim is created and does not write, backfill, default, or otherwise change the retained Bundle

#### Scenario: Explicit evidence layer remains reviewable
- **WHEN** a retained Bundle manifest declares a supported explicit evidence layer and its other integrity checks pass
- **THEN** review admission preserves that declared layer in the resulting Review Record without inferring another layer

#### Scenario: Changed control cannot reinterpret a retained Bundle
- **WHEN** a review submits a Case, Contract, Rubric, or Protocol identity that does not resolve to the identity retained in the Bundle manifest
- **THEN** review admission rejects that submission and creates no Review Record for the substituted control

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

## ADDED Requirements

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
