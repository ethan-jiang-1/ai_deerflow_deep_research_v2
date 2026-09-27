# Spec Delta

> req: CES-003

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
