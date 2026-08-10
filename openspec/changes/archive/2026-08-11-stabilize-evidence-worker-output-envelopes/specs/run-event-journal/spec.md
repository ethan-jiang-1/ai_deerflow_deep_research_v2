> req: REJ-002, REJ-004, REJ-006, REJ-007

## MODIFIED Requirements

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

Newly established Journal events and manifests SHALL use schema version 3. Existing
version-1 and version-2 Journals SHALL remain readable as bounded historical evidence
without an inferred response shape or `post_candidate` stage. A writer SHALL NOT append
a version-3 event to an older manifest or rewrite/upgrade older events or manifests. An
attempt to record through an older Journal SHALL use the existing incomplete or
unavailable observation behavior and SHALL NOT change graph, recovery, terminal, or
lifecycle execution. The unchanged summary representation SHALL retain its current
schema version.

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

#### Scenario: Older Journals remain readable and are never silently upgraded
- **WHEN** inspection or a resumed producer encounters a version-1 or version-2 Journal
- **THEN** inspection exposes only its retained historical facts, no new shape or stage
  is inferred or appended, and any observation-write failure leaves the Run outcome
  unchanged

### Requirement: Event journal inspection is read-only and safe for people and agents

Supported inspection SHALL expose only an available selected Bundle's bounded Journal
health, sequence, generation, phase, event kind, work/attempt correlation, validation
stage, closed final response shape when present, canonical validation codes, safe
failure category, and opaque diagnostic reference when independently available. It
SHALL derive no lifecycle state from event ordering and SHALL not use a journal,
diagnostic, or progress event to start, resume, cancel, refine, route, recover, or
recreate a Run. A missing, malformed, foreign, or post-loss Journal produces an
unavailable bounded observation result; inspection SHALL NOT seek an external
historical Journal or Support Handoff. (`REJ-004`)

#### Scenario: Operator inspection explains a failed attempt without granting control
- **WHEN** an operator inspects a retained Run with a failed validated work attempt
- **THEN** the inspection displays its safe correlation, validation stage, applicable
  response shape, and canonical facts but offers only the legal action supplied by the
  typed Bundle lifecycle result

#### Scenario: Bundle loss removes retained diagnostic evidence
- **WHEN** an admitted Bundle is deleted or becomes unavailable
- **THEN** inspection reports the Bundle and its Event Journal unavailable, does not read
  an external Journal or Support Handoff, and offers no journal-derived recovery

### Requirement: Admitted explicit-profile executions retain trusted redacted profile provenance

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
