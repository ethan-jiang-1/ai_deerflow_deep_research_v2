## MODIFIED Requirements

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
with that boundary's existing canonical code collection. A validation fact SHALL be
emitted only after that candidate reaches the named boundary; an invocation failure
before the boundary remains the existing invocation fact. These observations SHALL not
change existing repair counts, provider recovery, controller ownership, routing,
terminal classification, checkpoint state, or legal lifecycle action. (`REJ-007`)

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

#### Scenario: Post-candidate evidence does not become recovery input
- **WHEN** a Wave0 or Wave1 candidate fails a later deterministic validation boundary
- **THEN** its correlated `post_candidate` fact contains only canonical codes, invokes
  no structural repair, and leaves the existing controller and lifecycle outcome intact

#### Scenario: Observation failure cannot alter the existing outcome
- **WHEN** persistence of one profile, budget, response-shape, or validation fact fails
- **THEN** the Journal reports its existing incomplete or unavailable observation state
  and the Run preserves its current graph, checkpoint, recovery, route, terminal, and
  lifecycle behavior

## ADDED Requirements

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
