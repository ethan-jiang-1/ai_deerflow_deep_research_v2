> req: REJ-006, REJ-007

## ADDED Requirements

### Requirement: Admitted all-real demo Bundles retain trusted redacted profile provenance

For an admitted all-real demo Run whose composition has resolved one explicit profile,
the Bundle-local Event Journal SHALL retain the same trusted execution-profile evidence
in its admission fact and summary. The evidence SHALL contain only a bounded registered
profile identity and its version-controlled safe revision declared by the trusted
registry. It SHALL be produced by the trusted demo composition boundary before graph
execution, not by a model, node, checkpoint, provider response, or inspection caller.

The profile evidence SHALL exclude credentials, environment values, raw endpoint URLs,
provider request or response bodies, prompts, and model output. A profile identity or
revision SHALL be an observation only: it SHALL NOT authorize a Bundle, select a model,
alter a lifecycle action, change a retry or route, or establish a model-quality claim.
The evidence SHALL be permitted only on the Journal admission fact and its summary;
the two retained values SHALL match. Non-demo and legacy Bundles remain readable without
a profile fact; absence SHALL mean only that this provenance was not retained, never
that a particular model was used.
(`REJ-006`)

#### Scenario: Admitted real-demo Journal preserves safe profile provenance
- **WHEN** the lifecycle admits an all-real demo that was composed from one explicit
  registered profile
- **THEN** its admission event and summary expose matching bounded profile identity and
  revision, while their serialized Journal data contains no credential, raw endpoint,
  prompt, provider body, or model output

#### Scenario: Profile evidence is unavailable before admission
- **WHEN** an all-real demo prerequisite rejects an absent, unknown, or non-unique
  profile selection
- **THEN** no Bundle, summary, admission event, or Journal profile evidence exists for
  that rejected request

#### Scenario: Older and non-demo Journals do not invent profile provenance
- **WHEN** read-only inspection opens a legacy, fixture, or non-demo Bundle with no
  trusted real-demo profile evidence
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

When Wave0 or topic planning reaches its existing parser or deterministic
materialization boundary, the Journal SHALL retain one `initial` or `repair`
validation fact with an empty canonical-code collection on success or the applicable
closed canonical code collection on failure. A validation fact SHALL be emitted only
after that candidate reaches the named boundary; an invocation failure before the
boundary remains the existing invocation fact. These observations SHALL not change
existing repair counts, provider recovery, controller ownership, routing, terminal
classification, checkpoint state, or legal lifecycle action. (`REJ-007`)

#### Scenario: A known budget stop is attributable without raw detail
- **WHEN** a bridge stops an invocation at a known model, token, tool, or bridge
  wall-time budget boundary
- **THEN** its Journal invocation event retains the unchanged safe failure category and
  exactly one allowed budget-stop reason, without the middleware detail or provider
  payload

#### Scenario: Initial and repair validation facts remain distinct
- **WHEN** a Wave0 or topic-planning candidate fails initial validation and its one
  existing repair reaches validation
- **THEN** the Journal retains separate ordered `initial` and `repair` validation
  facts with their own canonical code collections and no raw draft or exception text

#### Scenario: Observation failure cannot alter the existing outcome
- **WHEN** persistence of one profile, budget, or validation fact fails
- **THEN** the Journal reports its existing incomplete or unavailable observation state
  and the Run preserves its current graph, checkpoint, recovery, route, terminal, and
  lifecycle behavior
