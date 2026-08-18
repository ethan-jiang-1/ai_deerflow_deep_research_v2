# run-event-journal Specification

> req: REJ-001, REJ-002, REJ-003, REJ-004, REJ-005, REJ-006, REJ-007, REJ-008, REJ-009

## Purpose

Define one bounded, redacted, read-only, Bundle-local process-fact Journal for an
admitted Deep Research Run, so contributors can investigate material execution outcomes
without using logs or diagnostics as a second lifecycle authority.

## Requirements

### Requirement: An admitted Run has one correlated event journal before execution

After the Bundle lifecycle has admitted a valid Run and before any graph producer can
execute, the system SHALL establish that Run's Event Journal in the selected Bundle's
protected diagnostics subtree. The Journal shares the Bundle's lifetime: it SHALL NOT
be persisted as an external Run observation, read after Bundle deletion, or presented to
a participant after Bundle loss. Its identity is the admitted opaque `bundle_id`; it does
not prove the Bundle exists, select a Bundle, or authorize execution. Every retained
event SHALL have a schema version, a stable monotonically increasing Bundle-local journal
sequence, timestamp, refinement generation, phase, and bounded event kind. Where a work
item or attempt exists, the event SHALL retain its bounded `work_id` and `attempt_id`.
The Event Journal SHALL distinguish a process fact from a terminal diagnostic conclusion
and from ephemeral progress rendering. This requirement does not assert physical secure
erasure or that storage has no residual bytes; residual bytes, if any, are not a
supported Journal reader or participant presentation. (`REJ-001`)

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
an `initial`, `repair`, or `post_candidate` validation and retain its bounded collection
of exact canonical rule codes, including an empty collection for a successful
initial/repair validation. For a Wave0 or Wave1 `initial` or `repair` candidate boundary,
the validation result SHALL also retain exactly one closed final response shape:
`empty`, `prose`, `fenced`, `embedded_json`, or `json_object`. A `post_candidate`
validation result SHALL carry only the existing canonical codes from the named
deterministic validation boundary and no response-shape value. A known failure SHALL
retain its existing closed category; a repair attempt SHALL retain its own validation
result rather than overwrite or collapse the initial one. An unclassified boundary
failure SHALL retain only a bounded unknown category. The Journal SHALL NOT retain raw
exception text, stack traces, prompts, answers, model/tool bodies, provider payloads,
credentials, full URLs, host paths, checkpoints, or internal wires. (`REJ-002`)

Newly established Journal events and manifests SHALL use schema version 3. The current
Run Summary representation SHALL remain schema version 2. Version-1 Journal data has
no migration route. A version-2 manifest and its complete correlated event set may be
migrated to version 3 only by the separately invoked offline route when it is explicitly
registered in the source-controlled migration inventory and its exact Bundle identity,
sequence, and retained facts validate. The migration SHALL produce current v3 records
without inferring response shape, `post_candidate` stage, watermark, generation, or
validation provenance that was not retained. It SHALL preserve the current Summary v2
representation without upgrading it.

After cutover, the runtime reader SHALL accept only v3 Journal manifest/event records.
An old, unregistered, malformed, partial, stale, replayed, or failed-migration Journal
SHALL be unavailable or unsupported observation before append or participant
projection. The runtime SHALL not append a v3 event to it, rewrite it, derive current
facts from it, or change graph, recovery, terminal, publication, or lifecycle truth.

#### Scenario: A validation repair preserves both observed rule results
- **WHEN** a work attempt fails an initial validation rule and its repair also fails a
  validation rule
- **THEN** the retained journal exposes the canonical rule code or codes and closed
  response shape for each observed initial/repair result, their common
  Run/work/attempt correlation, and no raw validation message or response body

#### Scenario: A parser-accepted candidate preserves its later closed result
- **WHEN** a Wave0 or Wave1 candidate reaches a later deterministic submission or
  artifact validation boundary and that boundary rejects it
- **THEN** the Journal retains one correlated `post_candidate` validation fact with
  only the boundary's canonical codes and never treats the projection as repair or
  lifecycle authority

#### Scenario: A known provider failure remains a process fact
- **WHEN** a node-agent invocation produces a safe classified provider failure
- **THEN** the journal retains its phase, attempt correlation, and safe category while
  the existing phase/controller remains the only owner of recovery and terminal routing

#### Scenario: An unexpected shared-boundary failure remains honest
- **WHEN** a shared execution boundary catches a non-cancellation failure without a
  known safe classification
- **THEN** the journal retains a bounded unknown outcome and never labels it as a
  provider, validation, or tool failure from exception text

#### Scenario: Registered v2 Journal migrates without upgrading provenance
- **WHEN** the offline migration route processes a registered valid v2 manifest and complete matching event set
- **THEN** it writes a v3 Journal whose retained facts and sequence remain valid, preserves Summary v2, and does not infer unavailable v3-only provenance

#### Scenario: Legacy Journal cannot be read or silently upgraded after cutover
- **WHEN** inspection or a producer encounters a v1, v2, partial, or unregistered Journal after cutover
- **THEN** it returns only the bounded unavailable or unsupported observation outcome, appends and rewrites nothing, and leaves the Run outcome unchanged

#### Scenario: Older Journals remain readable and are never silently upgraded
- **WHEN** the approved offline migration decoder receives a registered complete v2 Journal before cutover
- **THEN** it reads only the retained source facts to create its separately validated v3 output, while the post-cutover runtime reader rejects the old source and never silently upgrades it

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

Supported inspection SHALL expose only an available selected Bundle's bounded Journal
health, sequence, generation, phase, event kind, work/attempt correlation, validation
stage, closed final response shape when present, canonical validation codes, safe
failure category, and opaque diagnostic reference when independently available. It
SHALL derive no lifecycle state from event ordering and SHALL not use a journal,
diagnostic, or progress event to start, resume, cancel, refine, route, recover, or
recreate a Run. A missing, malformed, foreign, or post-loss Journal produces an
unavailable bounded observation result; inspection SHALL NOT seek, read, or present an
external historical Journal, diagnostic, or Support Handoff. Support Handoff remains a
planned capability and, if implemented, SHALL not create a post-loss Journal reader.
The absence of a supported reader or participant presentation does not assert that
physical storage contains no residual bytes. (`REJ-004`)

#### Scenario: Operator inspection explains a failed attempt without granting control
- **WHEN** an operator inspects a retained Run with a failed validated work attempt
- **THEN** the inspection displays its safe correlation, validation stage, applicable
  response shape, and canonical facts but offers only the legal action supplied by the
  typed Bundle lifecycle result

#### Scenario: Bundle loss removes retained diagnostic evidence
- **WHEN** an admitted Bundle is deleted or becomes unavailable
- **THEN** inspection reports the Bundle and its Event Journal unavailable, does not
  read or present an external Journal, diagnostic, or Support Handoff, and offers no
  journal-derived recovery

### Requirement: DeerFlow runtime context is a non-controlling projection boundary

The system SHALL treat DeerFlow runtime context and configured standard Python logging
only as best-effort ingress and projection boundaries for an already-safe Deep
Research fact. A standard log SHALL not imply that a Bundle-local Event Journal append
succeeded, and it SHALL not become a Journal record, replay source, Bundle identity,
or lifecycle authority. Trusted DeerFlow runtime context MAY supply safe correlation,
but an outer DeerFlow run identifier SHALL NOT become a Bundle or Event Journal
identity.

Log absence, filtering, reordering, malformed-observation rejection, or delivery
failure SHALL NOT change Journal persistence, Journal health, graph execution,
checkpointed State, retry policy, terminal classification, or a legal lifecycle
action. The system SHALL not use a raw stream writer, custom event, or private Gateway
store as a Journal-adjacent progress transport. (`REJ-005`)

#### Scenario: A logging failure cannot erase diagnostic evidence
- **WHEN** configured logging cannot accept a safe material observation for an
  admitted Run
- **THEN** the Bundle-local Journal still follows its own persistence and health
  contract, and the Run follows its existing lifecycle behavior

#### Scenario: A log is not a second Journal record
- **WHEN** an already-safe domain fact is logged
- **THEN** the record carries no Journal sequence or persistence claim, cannot be
  used to recover or control a Bundle, and does not replace the Journal's bounded
  retained evidence

### Requirement: Admitted all-real demo Bundles retain trusted redacted profile provenance

For an admitted all-real demo Run or an explicitly selected live evidence-intake
calibration whose composition has resolved one explicit profile, the Bundle-local Event
Journal SHALL retain the same trusted execution-profile evidence in its admission fact
and summary. The evidence SHALL contain only a bounded registered profile identity and
its version-controlled safe revision declared by the trusted registry. It SHALL be
produced by the trusted demo or selected-calibration composition boundary before graph
or direct-branch execution, not by a model, node, checkpoint, provider response, or
inspection caller.

The profile evidence SHALL exclude credentials, environment values, raw endpoint URLs,
provider request or response bodies, prompts, and model output. A profile identity or
revision SHALL be an observation only: it SHALL NOT authorize a Bundle, select a model,
alter a lifecycle action, change a retry or route, or establish a model-quality claim.
The evidence SHALL be permitted only on the Journal admission fact and its summary;
the two retained values SHALL match. Non-demo, unselected calibration, and legacy
Bundles remain readable without a profile fact; absence SHALL mean only that this
provenance was not retained, never that a particular model was used. (`REJ-006`)

#### Scenario: Admitted explicit-profile calibration preserves safe provenance
- **WHEN** the lifecycle admits one selected evidence-intake calibration that was
  composed from one explicit registered profile
- **THEN** its admission event and summary expose matching bounded profile identity and
  revision, while their serialized Journal data contains no credential, raw endpoint,
  prompt, provider body, or model output

#### Scenario: Profile evidence is unavailable before admission
- **WHEN** a demo or selected calibration prerequisite rejects an absent, unknown, or
  non-unique profile selection
- **THEN** no Bundle, summary, admission event, or Journal profile evidence exists for
  that rejected request

#### Scenario: Other Journals do not invent profile provenance
- **WHEN** read-only inspection opens a legacy, fixture, non-demo, or unselected
  calibration Bundle with no trusted profile evidence
- **THEN** it preserves its existing Journal availability behavior and exposes no
  inferred selected profile

### Requirement: Journal attribution keeps closed budget stops and parser validation facts

For a node-agent invocation that reaches a known execution-budget stop, the Event
Journal SHALL retain the existing safe failure category together with one closed safe
budget-stop reason. The allowed reasons are `request_content_unestimable`,
`model_call_limit`, `token_admission`, `per_call_output_cap`,
`total_token_budget`, `tool_calls_per_response`, `parallel_tool_calls`,
`total_tool_calls`, `bridge_wall_time`, and `unknown`. The reason SHALL be absent from
unrelated failures and SHALL NOT be derived from or retain raw exception detail. It
SHALL be permitted only on the existing model/tool invocation event: a middleware
budget stop retains its current `budget.exhausted` failure category, and a bridge
deadline retains its current `provider.timeout` failure category with
`bridge_wall_time`. The bridge's existing normalized timeout origin remains unchanged
outside this Journal field.

A budget-stop event SHALL additionally retain the closed arithmetic operands the
middleware already computed when they exist and are relevant to the stop reason:
a `token_admission` stop carries the projected request byte count, the total token
budget, and the per-call output token cap that failed the admission inequality; a
`per_call_output_cap` stop carries the observed output token count and the cap; a
`total_token_budget` stop carries the cumulative token use and the budget. Operand
fields SHALL be absent when their stop reason does not define them, SHALL be plain
non-negative integers, and SHALL NOT carry request content, prompt text, or any raw
exception detail.

Every bridge-emitted `model_tool` event SHALL carry a per-attempt call ordinal: a
monotonically increasing integer, starting at 1 within one node-agent attempt, pairing
each `started`/`completed` (or failure) outcome with its request. Work-unit critic
boundary facts that already correlate through their closed `work_id` and `critic_kind`
carry no ordinal. A `completed` invocation
whose provider usage is available SHALL retain the usage token counts
(`input_tokens`, `output_tokens`, `total_tokens`) as plain non-negative integers;
usage SHALL be absent when the provider did not report it, and its absence SHALL NOT
be treated as a failure. These observational fields SHALL NOT change invocation
outcomes, failure categories, budget decisions, routing, or terminal classification.

When topic planning, Wave0, or Wave1 reaches its existing parser, local semantic, or
deterministic materialization boundary, the Journal SHALL retain one `initial` or
`repair` validation fact with an empty canonical-code collection on success or the
applicable closed canonical-code collection on failure. Wave0 and Wave1 candidate
facts SHALL additionally retain their closed final response shape. When a parser- and
where-applicable locally-valid Wave0 or Wave1 candidate later fails a deterministic
post-candidate boundary, the Journal SHALL retain one `post_candidate` validation fact
with that boundary's existing canonical code collection. When the real final-delivery
composer candidate of a non-degenerate visit reaches its parser or admission boundary
and is not admitted, the Journal SHALL retain one `initial` validation fact for that
attempt carrying the boundary's existing closed canonical code collection
(`final_layout_empty`, `final_layout_json_invalid`, `final_layout_not_object`,
`final_layout_shape_invalid`, `final_layout_schema_unsupported`,
`final_layout_conclusions_invalid`, `final_layout_uncertainties_invalid`), where
`final_layout_shape_invalid` collapses typed-candidate validation detail that is not
one of the literal parser/admission codes; the final-delivery fact SHALL carry no response
shape, and a final-delivery composer invocation failure SHALL retain only the existing
invocation fact and no validation fact, consistent with the pre-boundary failure rule.
A validation fact SHALL be emitted only after that candidate reaches the named
boundary; an invocation failure before the boundary remains the existing invocation
fact. These observations SHALL not change existing repair counts, provider recovery,
controller ownership, routing, terminal classification, checkpoint state, or legal
lifecycle action. (`REJ-007`)

#### Scenario: A known budget stop is attributable without raw detail
- **WHEN** a bridge stops an invocation at a known model, token, tool, or bridge
  wall-time budget boundary
- **THEN** its Journal invocation event retains the unchanged safe failure category and
  exactly one allowed budget-stop reason, without the middleware detail or provider
  payload

#### Scenario: An admission stop carries its arithmetic operands
- **WHEN** a `token_admission` stop is recorded
- **THEN** the event retains the projected request bytes, total token budget, and
  per-call output cap whose inequality failed, as plain integers, and no request
  content or prompt text

#### Scenario: Ordinals pair starts with completions within one attempt
- **WHEN** one node attempt performs multiple model invocations
- **THEN** each `model_tool` event carries the attempt-scoped call ordinal, the n-th
  invocation's started and completed events share ordinal n, and ordinals restart per
  attempt

#### Scenario: Usage tokens ride the completed event when available
- **WHEN** a completed invocation's provider usage is available
- **THEN** the completed event retains the input/output/total token counts; when the
  provider reports no usage the fields are absent and the outcome stays `completed`

#### Scenario: Initial and repair validation facts remain distinct
- **WHEN** a topic-planning, Wave0, or Wave1 candidate fails initial validation and its
  one existing repair reaches validation
- **THEN** the Journal retains separate ordered `initial` and `repair` validation
  facts with their own canonical code collections and, for Wave0/Wave1, closed response
  shapes, without a raw draft or exception text

#### Scenario: A rejected final-delivery layout keeps its canonical code
- **WHEN** a non-degenerate final-delivery visit's composer delivery fails parsing or
  admission after normalization and the visit degrades to the plan-order layout
- **THEN** the Journal retains one correlated `initial` validation fact for that attempt
  with exactly the boundary's closed canonical code, no response shape, and no raw
  model output, while the visit's publication and terminal outcome proceed unchanged

#### Scenario: A final-delivery invocation failure stays an invocation fact
- **WHEN** a non-degenerate final-delivery visit's composer invocation fails before a
  candidate reaches the parser boundary
- **THEN** the Journal retains the existing invocation fact with no validation fact,
  and the visit's plan-order degradation proceeds unchanged

#### Scenario: Post-candidate evidence does not become recovery input
- **WHEN** a Wave0 or Wave1 candidate fails a later deterministic validation boundary
- **THEN** its correlated `post_candidate` fact contains only canonical codes, invokes
  no structural repair, and leaves the existing controller and lifecycle outcome intact

#### Scenario: Observation failure cannot alter the existing outcome
- **WHEN** persistence of one profile, budget, response-shape, or validation fact fails
- **THEN** the Journal reports its existing incomplete or unavailable observation state
  and the Run preserves its current graph, checkpoint, recovery, route, terminal, and
  lifecycle behavior

### Requirement: Wave1 critic boundary facts carry a closed critic kind

The current v3 `RunEvent` contract SHALL gain one bounded optional field
`critic_kind` whose closed values are exactly `source_diagnostic` and
`claim_verifier`. The field SHALL be present only on a `post_candidate` VALIDATION
fact whose phase is `wave1` and whose validation-code collection is drawn from the
named critic review boundary's canonical codes; it SHALL be absent from every other
event, and a Wave1 critic dispatch model/tool invocation-failure fact SHALL NOT carry
it. The critic kind SHALL be derived from the fixed dispatch assignment, never from
model output, prompt content, or validation detail. The Journal SHALL retain no raw
critic output, prompt, tool observation, URL, artifact path, or exception text for
that fact. Version-1 and version-2 records and v3 records written before this change
SHALL remain readable with the field absent, and the field SHALL remain an
observation with no admission, retry, gate, route, terminal, or lifecycle authority.

#### Scenario: A critic-boundary fact carries exactly one closed critic kind
- **WHEN** a Wave1 critic typed result fails the review-artifact validation boundary
- **THEN** the retained `post_candidate` VALIDATION fact carries the canonical code collection, the work/attempt correlation, and exactly one closed `critic_kind` matching the dispatched critic, with no raw output

#### Scenario: The critic kind is rejected outside the critic boundary
- **WHEN** an event for another phase, stage, or category attempts a `critic_kind` value
- **THEN** the Journal append or inspection boundary rejects it before persistence or projection

#### Scenario: Legacy records without the critic kind remain readable
- **WHEN** a Journal retains v3 events written before this change or v1/v2 records
- **THEN** inspection reads them with `critic_kind` absent and performs no migration or rewrite

### Requirement: Run summary retains per-phase policy envelope snapshots

The Journal's run-summary artifact SHALL carry, for every real model-bearing phase
that executed in the run, one closed policy-envelope snapshot: the policy name,
total token budget, per-call output token cap, and declared maximum model calls.
Snapshots SHALL reflect the envelopes actually assembled for the run, SHALL be absent
for phases that did not execute, SHALL contain no prompt text, capability bodies, or
provider credentials, and SHALL NOT be readable as admission, routing, or lifecycle
authority by any component. (`REJ-009`)

#### Scenario: Envelopes answer "what budget did this run give each phase"
- **WHEN** an operator inspects a completed run's summary after a budget-stop incident
- **THEN** each executed phase's total token budget and output cap are present in the
  summary without reading source code or replaying assembly

#### Scenario: Absent phases stay absent
- **WHEN** a phase did not execute in the run
- **THEN** its envelope snapshot is absent from the summary rather than projected from
  defaults
