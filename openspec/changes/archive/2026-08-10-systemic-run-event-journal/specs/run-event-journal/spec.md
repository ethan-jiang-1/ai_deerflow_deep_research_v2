# run-event-journal Specification

> req: REJ-001, REJ-002, REJ-003, REJ-004, REJ-005

## Purpose

Define one bounded, redacted, read-only, Bundle-local process-fact Journal for an
admitted Deep Research Run, so contributors can investigate material execution outcomes
without using logs or diagnostics as a second lifecycle authority.

## ADDED Requirements

### Requirement: An admitted Run has one correlated event journal before execution

After the Bundle lifecycle has admitted a valid Run and before any graph producer can
execute, the system SHALL establish that Run's Event Journal in the selected Bundle's
protected diagnostics subtree. The Journal shares the Bundle's lifetime: it SHALL NOT
be persisted as an external Run observation or survive Bundle deletion. Its identity is
the admitted opaque `bundle_id`; it does not prove the Bundle exists, select a Bundle,
or authorize execution. Every retained event SHALL have a schema version, a stable
monotonically increasing Bundle-local journal sequence, timestamp, refinement
generation, phase, and bounded event kind. Where a work item or attempt exists, the
event SHALL retain its bounded `work_id` and `attempt_id`. The Event Journal SHALL
distinguish a process fact from a terminal diagnostic conclusion and from ephemeral
progress rendering. (`REJ-001`)

#### Scenario: First graph event is retained for a newly admitted Run
- **WHEN** a newly admitted Run starts graph execution before its first returned
  lifecycle projection
- **THEN** read-only inspection can find the journal's admitted execution and first
  graph event with the same Bundle correlation, generation, and phase

#### Scenario: A later refinement does not merge with an earlier generation
- **WHEN** one retained Bundle begins a later legal refinement generation
- **THEN** events from both generations remain distinguishable by their retained
  generation facts without creating a new lifecycle identity or Bundle locator

#### Scenario: A rejected request does not create a ghost journal
- **WHEN** a request is rejected before the Bundle lifecycle admits a Run
- **THEN** the caller receives only its immediate safe result and no Bundle or persistent
  Event Journal is created for that request

### Requirement: Material execution outcomes retain canonical safe evidence

The Event Journal SHALL retain a bounded process fact at the shared lifecycle,
graph-node, work-attempt, model/tool invocation, deterministic validation, retry,
exhaustion, and terminal-result seams. A validation result SHALL identify whether it is
an `initial` or `repair` validation and retain its bounded collection of exact canonical
rule codes, including an empty collection for a successful validation. A known failure
SHALL retain its existing closed category; a repair attempt SHALL retain its own
validation result rather than overwrite or collapse the initial one. An unclassified
boundary failure SHALL retain only a bounded unknown category. The Journal SHALL NOT
retain raw exception text, stack traces, prompts, answers, model/tool bodies, provider
payloads, credentials, full URLs, host paths, checkpoints, or internal wires. (`REJ-002`)

#### Scenario: A validation repair preserves both observed rule results
- **WHEN** a work attempt fails an initial validation rule and its repair also fails a
  validation rule
- **THEN** the retained journal exposes the canonical rule code or codes for each
  observed validation result, their common Run/work/attempt correlation, and no raw
  validation message

#### Scenario: A known provider failure remains a process fact
- **WHEN** a node-agent invocation produces a safe classified provider failure
- **THEN** the journal retains its phase, attempt correlation, and safe category while
  the existing phase/controller remains the only owner of recovery and terminal routing

#### Scenario: An unexpected shared-boundary failure remains honest
- **WHEN** a shared execution boundary catches a non-cancellation failure without a
  known safe classification
- **THEN** the journal retains a bounded unknown outcome and never labels it as a
  provider, validation, or tool failure from exception text

### Requirement: Journal health and bounded retention are truthful

The Event Journal SHALL expose whether its retained history is `complete`, `incomplete`,
or `unavailable`. It SHALL preserve its admission anchor and retained terminal, health,
validation-failure, provider/boundary-failure, retry, and exhaustion facts before
ordinary start or success events under capacity pressure. Its bounded retention policy
SHALL preserve the original stable sequence values of retained events and SHALL disclose
the dropped count or sequence interval; it SHALL not silently discard, re-sequence, or
overwrite a material event while reporting a complete Journal. A persistence failure,
corrupted Journal, capacity limit, or known missing interval SHALL result in the
appropriate incomplete or unavailable observation fact. Journal-health failure SHALL
NOT change graph execution, checkpointed State, retry policy, terminal classification,
or a legal lifecycle action. (`REJ-003`)

#### Scenario: Retention capacity cannot masquerade as a full story
- **WHEN** a Run reaches the configured bounded journal capacity before terminal
  projection
- **THEN** inspection reports an incomplete Journal, preserves its diagnostic anchors
  and retained sequence values, discloses the dropped interval or count, and does not
  present the retained suffix as a complete execution history

#### Scenario: Persistence failure cannot change the research outcome
- **WHEN** a journal write fails while a graph producer records an otherwise valid
  process fact
- **THEN** the graph preserves its existing result and lifecycle behavior while the
  subsequent observation truth is incomplete or unavailable

### Requirement: Event journal inspection is read-only and safe for people and agents

Supported inspection SHALL expose only an available selected Bundle's bounded Journal health,
sequence, generation, phase, event kind, work/attempt correlation, canonical validation
codes, safe failure category, and opaque diagnostic reference when independently
available. It SHALL derive no lifecycle state from event ordering and SHALL not use a
journal, diagnostic, or progress event to start, resume, cancel, refine, route, recover,
or recreate a Run. A missing, malformed, foreign, or post-loss Journal produces an
unavailable bounded observation result; inspection SHALL NOT seek an external historical
Journal or Support Handoff. (`REJ-004`)

#### Scenario: Operator inspection explains a failed attempt without granting control
- **WHEN** an operator inspects a retained Run with a failed validated work attempt
- **THEN** the inspection displays its safe correlation and validation facts but offers
  only the legal action supplied by the typed Bundle lifecycle result

#### Scenario: Bundle loss removes retained diagnostic evidence
- **WHEN** an admitted Bundle is deleted or becomes unavailable
- **THEN** inspection reports the Bundle and its Event Journal unavailable, does not read
  an external Journal or Support Handoff, and offers no journal-derived recovery

### Requirement: DeerFlow live progress is a best-effort projection

The system SHALL use DeerFlow's public `custom` stream writer only as an optional
best-effort live projection of already-safe Event Journal facts. Trusted DeerFlow runtime
context MAY supply ingress correlation, but an outer DeerFlow run identifier SHALL NOT
become a Bundle or Event Journal identity. Absence, filtering, reordering, or failure of
the live projection SHALL NOT change Journal persistence, Journal health, graph
execution, checkpointed State, retry policy, terminal classification, or a legal
lifecycle action. (`REJ-005`)

#### Scenario: A live subscriber failure cannot erase diagnostic evidence
- **WHEN** a DeerFlow `custom` stream subscriber is unavailable while an admitted Run
  emits a safe material event
- **THEN** the Bundle-local Journal still follows its own persistence and health contract,
  and the Run follows its existing lifecycle behavior
