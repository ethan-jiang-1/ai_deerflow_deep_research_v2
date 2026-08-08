## ADDED Requirements

### Requirement: Topic planning separates provider recovery from structured-output repair

Real topic planning SHALL use its independently bounded execution policy and a
phase-owned outcome table. A malformed but successful planner result SHALL consume
only the existing one-shot structured-output repair. A safe transient provider
timeout or unavailable result SHALL consume at most one declared provider recovery
attempt and record its observed disposition. Authentication, configuration,
non-retryable provider, and unknown failures SHALL fail closed without a fabricated
repair. Any terminal exhaustion SHALL retain the safe terminal incident and SHALL
not write topic authority.

#### Scenario: A timeout receives bounded provider recovery
- **WHEN** the first topic-planning model invocation returns a safe
  `provider.timeout` with an eligible observation
- **THEN** the node records one bounded provider recovery attempt and either accepts
  the recovered validated plan or blocks with a topic-planning provider incident

#### Scenario: Invalid planner JSON does not masquerade as provider recovery
- **WHEN** a successful topic-planning result fails schema or coverage validation
- **THEN** the node issues its one structured-output repair prompt and records no
  provider recovery unless a later invocation independently returns a safe provider
  failure
