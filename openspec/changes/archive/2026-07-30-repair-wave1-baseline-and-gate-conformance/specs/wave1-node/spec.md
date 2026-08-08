> req: WON-001, WON-002, WON-003, WON-004, WON-007

## MODIFIED Requirements

### Requirement: Wave1 planner materializes per-topic evidence WorkSpecs

The Wave1 planner SHALL read profile constraints and Wave0 accepted submission
records for the same research generation to materialize one immutable evidence
`WorkSpec` per topic through the existing work-unit controller. Each WorkSpec SHALL
carry search dimensions derived from the topic's must-answer bindings and Wave0
coverage gaps. Before every real Wave1 worker request, the phase SHALL derive its
Wave0 baseline from canonical URLs in those accepted records, not from checkpoint
hashes or an empty replacement set. An empty or absent Wave0 topic registry, an
unavailable required accepted record, or a cross-generation record SHALL fail closed
before worker dispatch.

#### Scenario: One WorkSpec per topic from planner
- **WHEN** real Wave1 runs after real Wave0 produced accepted submissions
- **THEN** the controller allocates one WorkSpec per topic with search dimensions and a derived spec_hash

#### Scenario: Empty Wave0 registry fails closed
- **WHEN** real Wave1 runs but Wave0 produced no accepted submissions
- **THEN** the planner fails before allocating work rather than inventing topics

#### Scenario: Top-level worker receives the accepted Wave0 baseline
- **WHEN** real Wave1 invokes a worker after Wave0 accepted a canonical source URL for the same research generation
- **THEN** the worker receives that URL in its bounded baseline and a duplicate returned URL is not admitted as new coverage

#### Scenario: Baseline cannot be reconstructed from checkpoint hashes
- **WHEN** the checkpoint contains an accepted-record hash but its authoritative Wave0 submission record is unavailable or belongs to another generation
- **THEN** the real phase fails before worker dispatch and does not substitute an empty baseline

### Requirement: Submit validation enforces new-source floor and invokes critics

Before any source/result artifact or candidate is written, Wave1 SHALL canonicalize
the worker draft's URLs, reject duplicate canonical URLs, derive newness from its
assigned Wave0 baseline, and require both claim provenance and at least two distinct
canonical new URLs. A provenance, uniqueness, or floor violation SHALL enter the
existing bounded structured repair; an inadequate repaired draft emits no source/result
or candidate artifact. Contract-specific submit validation SHALL independently parse
the persisted `Wave1SourceIntakeResult`, reconstruct same-generation accepted Wave0
URLs from its supplied accepted records, verify each persisted `is_new_vs_wave0`
marker against that baseline, and repeat canonical uniqueness, provenance, and the
two-new-URL floor before a `SubmissionRecord` is appended. Its failure SHALL use the
existing typed validation outcome and append no record. After a Wave1 candidate is
accepted, the Wave1 phase SHALL invoke independent local SourceDiagnostic and
ClaimVerifier critics for that accepted work/attempt. Each critic SHALL receive only a
bounded assignment reconstructed from the accepted Wave1 result: SourceDiagnostic
receives ordered new-source observations and ClaimVerifier receives ordered claims
plus assigned new-source identities. Tool results, candidate bodies, artifact paths,
checkpoint fields, and route data SHALL NOT be critic inputs.

Each typed critic result SHALL be materialized only after deterministic validation of
the accepted research/generation/work/attempt identity, record binding, input hash,
and exact source or claim coverage. The immutable review artifacts SHALL be scoped to
the accepted Wave1 work/attempt; they SHALL NOT be submission records, candidate
outputs, checkpoint state, or route authority. A failed, malformed, unbound, or
conflicting critic result SHALL produce no valid artifact. SourceDiagnostic and
ClaimVerifier SHALL use distinct required forbidden-tool capabilities, and the
existing runtime bridge SHALL remain the tool/budget/cancellation enforcer.

#### Scenario: Insufficient new sources reject candidate
- **WHEN** a candidate has fewer than two distinct canonical new-source URLs after deduplication
- **THEN** submit validation fails with a typed code and no SubmissionRecord is appended

#### Scenario: Pre-persistence semantic rejection writes no evidence
- **WHEN** an initial or repaired Wave1 draft has a foreign claim source reference, duplicate canonical URL, or fewer than two distinct new canonical URLs
- **THEN** the bounded structured repair receives the draft before any source/result or candidate artifact is written

#### Scenario: Critics invoked on accepted evidence
- **WHEN** a Wave1 submission is accepted
- **THEN** SourceDiagnostic and ClaimVerifier each receive only its accepted bounded assignment and write independently bound verdict artifacts when their typed result validates

#### Scenario: Invalid critic cannot publish authority
- **WHEN** a Wave1 critic invocation fails, returns malformed data, or references a source or claim outside its accepted assignment
- **THEN** no valid review artifact, submission record, checkpoint update, or route is published by that critic

### Requirement: Deep evidence worker with new-source floor

For each in-flight WorkSpec, Wave1 SHALL run one bounded web worker agent through
`capabilities.run_agent()` under a real `ExecutionPolicy` with web search tools and
attempt-scoped roots. The initial request SHALL require exactly one web search tool
call, use its multiple returned candidates as the evidence set, and retain later model
turns for a final structured answer. The worker SHALL produce a versioned
`Wave1WorkerOutput` carrying claims (each with `claim_id`, `statement`, `support_refs`,
`counter_refs`), open questions (with resolution states), and per-source
`is_new_vs_wave0` marking. Before writing any source/result artifact, the Wave1-local
semantic validator SHALL require every claim support/counter reference to identify a
source declared by that same worker output, each canonical URL to occur exactly once,
and the assigned-baseline new-source floor to be met. A draft that violates those
conditions SHALL enter the existing bounded structured repair path; a tool/budget stop
or still-inadequate repair SHALL fail closed. All fetched content is untrusted data,
and the worker SHALL NOT write phase, gate, ledger, or another attempt's state.

#### Scenario: Tool window reserves a final answer turn
- **WHEN** the Wave1 worker invokes its initial bounded request
- **THEN** it requires and permits exactly one web search call and retains the existing separate zero-tool structured repair

#### Scenario: Tool-only exhaustion publishes no authority
- **WHEN** the provider returns only tool calls through the bounded request without a successful structured draft
- **THEN** the attempt fails without source/result artifacts or a submission-ledger record

#### Scenario: Worker produces structured claims with provenance
- **WHEN** a Wave1 worker fetches new sources and extracts claims
- **THEN** each claim carries support_refs and counter_refs referencing only sources declared by this worker, and is_new_vs_wave0 distinguishes new from Wave0-duplicate URLs

#### Scenario: Foreign claim source reference is repaired before admission
- **WHEN** a worker output names a support_ref or counter_ref absent from its declared sources
- **THEN** no candidate or source/result artifact is admitted from that draft and the existing zero-tool structured repair receives the bounded malformed draft

#### Scenario: Wave0-duplicate URL does not count as new
- **WHEN** a worker fetches a URL already present in Wave0 accepted submissions
- **THEN** the source is marked is_new_vs_wave0=false and does not count toward the two-source floor

#### Scenario: Open questions have resolution states
- **WHEN** a worker identifies an open question
- **THEN** it is recorded with a state of resolved, targeted-search, deferred, or requires-internal-data

### Requirement: Wave1 gate with provenance, coverage, and critic verdicts

The real Wave1 gate SHALL evaluate the shared `WorkUnitCompletionRule` before its
Wave1-specific review conditions. When structural work completion is satisfied, it
SHALL evaluate a bounded, validated, non-checkpointed review projection for every
accepted topic. The projection SHALL prove: at least two distinct canonical URLs with
`is_new_vs_wave0=true`; presence of both identity-bound SourceDiagnostic and
ClaimVerifier artifacts; and an open-question disposition in which every question is
`resolved`, `deferred`, or `requires_internal_data`. The projection SHALL contain no
candidate body, source body, artifact location, critic reason, checkpoint field, or
route authority, and gate rules SHALL perform no filesystem or network I/O.

The Wave1-specific rules SHALL make no independent decision while structural
completion is absent. A missing review artifact, insufficient new-source floor, or
`targeted_search` question SHALL produce the existing repairable gate outcome. A
malformed or unreconciled review projection SHALL fail before a business-gate pass,
repair, or route is emitted. Critic prose or verdict value SHALL not select a route.
The route map SHALL remain `{PASS: pass, REPAIR: repair, BLOCKED: exhausted}`.

#### Scenario: Missing critic verdict routes repair
- **WHEN** a topic has accepted submissions but lacks one valid bound SourceDiagnostic or ClaimVerifier artifact
- **THEN** the gate routes repair without admitting a pass

#### Scenario: Two distinct new sources satisfy the floor
- **WHEN** an accepted topic has two distinct canonical sources marked new versus Wave0, both valid review artifacts, and only allowed open-question states
- **THEN** the real Wave1 gate may pass after structural completion

#### Scenario: Unresolved question routes repair
- **WHEN** an accepted Wave1 result contains an open question in `targeted_search`
- **THEN** the gate routes repair without changing a worker or critic tool posture

#### Scenario: Review projection is bounded and validated before gate evaluation
- **WHEN** a review projection omits an accepted topic, exposes a disallowed field, or cannot reconcile with accepted records and their bound review artifacts
- **THEN** the phase fails at the deterministic validation boundary before a pass, repair, or route is emitted

#### Scenario: Repeated floor failure exhausts to blocked
- **WHEN** repair budget is exhausted and the new-source floor remains unmet
- **THEN** the gate routes exhausted and the lifecycle terminates
