## MODIFIED Requirements

### Requirement: Topic planning separates provider recovery from structured-output repair

Real topic planning SHALL use its independently bounded execution policy and a
phase-owned outcome table. A malformed but successful planner result SHALL consume
only the existing one-shot structured-output repair. A safe transient provider timeout
or unavailable result with an eligible safe provider observation SHALL consume at most
one declared provider recovery attempt and record its observed disposition. The bridge
only returns that typed result from one invocation; topic planning alone SHALL decide
whether to make the second planner invocation. Authentication, configuration,
`provider.usage_unavailable`, `budget.exhausted`, `policy.denied`, non-retryable
provider, and unknown failures SHALL fail closed without a fabricated repair or
provider recovery. Any terminal exhaustion SHALL retain the safe terminal incident and
SHALL not write topic authority.

The initial topic-planning request SHALL remain zero-tool and use the explicitly
admitted topic-planning execution policy. A direct transient provider result produced
by that real bridge path SHALL enter the same existing recovery table as an equivalent
typed result from another safe invocation source. The recovery request SHALL be the
identical initial planner request, not a structured-output repair request. A second
eligible transient provider result SHALL produce the existing exhausted recovery
projection; a second non-provider result SHALL retain its actual category with the
existing `retry_followed_by_terminal_failure` disposition. Cancellation during either
invocation or the bounded backoff SHALL propagate and SHALL not record a retry or
terminal incident after cancellation.

#### Scenario: A bridge-produced timeout receives bounded provider recovery
- **WHEN** the first topic-planning model invocation through its explicitly admitted
  zero-tool bridge returns a safe `provider.timeout` with an eligible observation
- **THEN** the node records one bounded provider recovery attempt, calls the planner at
  most once more with the same initial request, and either accepts the recovered
  validated plan or blocks with a topic-planning provider incident

#### Scenario: A second timeout reaches the exhausted provider terminal
- **WHEN** the first and second topic-planning bridge invocations both return eligible
  transient provider failures
- **THEN** the node makes exactly two bridge calls, records one attempt, one scheduled
  retry, a second attempt, and one exhaustion fact, and retains the second category
  with the existing exhausted recovery projection

#### Scenario: A non-provider stop does not gain provider recovery
- **WHEN** the initial topic-planning invocation returns
  `provider.usage_unavailable`, `budget.exhausted`, or `policy.denied`
- **THEN** the node makes no provider retry, writes no topic authority, and retains that
  exact closed category in its terminal incident

#### Scenario: A provider retry followed by a closed stop retains both facts
- **WHEN** an eligible initial provider result causes the one declared retry and that
  second invocation returns `provider.usage_unavailable`, `budget.exhausted`, or
  `policy.denied`
- **THEN** the node makes exactly two invocations, retains the actual second closed
  category with the existing `retry_followed_by_terminal_failure` history, attaches no
  final provider observation to that stop, and makes no third invocation

#### Scenario: Invalid planner JSON does not masquerade as provider recovery
- **WHEN** a successful topic-planning result fails schema or coverage validation
- **THEN** the node issues its one structured-output repair prompt and records no
  provider recovery unless a later invocation independently returns a safe provider
  failure

#### Scenario: Provider recovery does not turn into structured-output repair
- **WHEN** an initial eligible provider timeout is followed by a successful but invalid
  retry result
- **THEN** the node records `retry_followed_by_terminal_failure`, makes no third planner
  invocation, and does not use the structured-output repair path

#### Scenario: Cancellation remains outside the recovery table
- **WHEN** topic planning is cancelled during an initial provider invocation or the
  recovery backoff
- **THEN** cancellation propagates without another bridge call, recovery event, or
  terminal incident
