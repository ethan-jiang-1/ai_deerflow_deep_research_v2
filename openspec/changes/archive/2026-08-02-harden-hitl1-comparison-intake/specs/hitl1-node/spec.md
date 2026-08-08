## ADDED Requirements

### Requirement: HITL1 requires typed comparison scope and language facts before profile acceptance

HITL1 SHALL treat a supported explicit Chinese or English comparison signal in the
original request as requiring a typed `comparison_subjects` pair. The pair SHALL have
exactly two nonempty normalized distinct subjects and SHALL be an explicit validated
profile fact, never an implied value in a question, scope, note, prompt, or model
default. A proposal missing a required pair SHALL remain incomplete, SHALL not
advertise `accept_suggestion` or a current-proposal acceptance control, and SHALL
issue a correlated bounded follow-up that requests the pair.

HITL1 SHALL derive supported Chinese or English request-language evidence locally and
use it as the initial output/interaction-language preference. When the bounded
detector cannot determine one supported language, HITL1 SHALL present a correlated
explicit choice between the supported languages and SHALL not let brief generation or
semantic intake choose a fallback. The accepted output/interaction language and
immutable request-language evidence SHALL be included in the visible profile material,
the final profile, its request-bundle content, and checkpoint profile fields. A
profile may be materialized only when its required comparison and language facts are
complete and the response remains correlated to the current HITL1 request.

#### Scenario: Generic comparison cannot start from an invented pair
- **WHEN** a supported comparison request asks to compare two energy-storage routes
  but identifies no two subjects
- **THEN** HITL1 presents a focused comparison-subject follow-up in the derived
  language, publishes no profile artifact, and exposes no generic acceptance action

#### Scenario: Explicit pair and language become durable profile facts
- **WHEN** a correlated user response supplies lithium-ion batteries and vanadium
  redox flow batteries as the two comparison subjects and accepts the supported
  Chinese language preference
- **THEN** HITL1 records those exact typed facts in the accepted profile, checkpoint,
  and request bundle before taking only the legal accepted route

#### Scenario: Unsupported language evidence requires an explicit selection
- **WHEN** the original request does not satisfy the bounded Chinese or English
  language detector
- **THEN** HITL1 presents the explicit correlated language choice and does not accept
  a model-selected or default English preference

### Requirement: HITL1 retains explicit profile-schema compatibility

HITL1 SHALL read retained profile and checkpoint records that predate typed comparison
and language facts through a documented compatibility representation. A legacy record
shall remain explicitly legacy or unspecified for the absent facts; HITL1 SHALL NOT
derive a pair, request language, or output language from its prose, hash, prompt, or
prior acceptance. Newly accepted profiles SHALL use the current profile schema and
canonical content representation, while retained legacy content remains verifiable by
its recorded schema and bytes.

#### Scenario: Legacy profile does not acquire inferred facts
- **WHEN** HITL1 reloads a valid retained profile from before comparison and language
  fields existed
- **THEN** it remains readable with its absence marked by the compatibility contract
  and no current comparison or language fact is invented

## MODIFIED Requirements

### Requirement: HITL1 generates a validated structured brief from the original question

The real HITL1 node SHALL call `capabilities.run_agent()` with a bounded zero-tool
`NodeExecutionRequest` derived from `state["request_text"]` and validate the result
summary as one `StructuredBrief` JSON object before presenting it to a user. Both the
initial request and the existing malformed-output repair request SHALL set
`tools_enabled=false`. The frozen extra-forbid `StructuredBrief` contract SHALL retain
its closed profile enums, existing bounds, and advisory-only status while adding only the typed
comparison and language fields required by the current profile schema. The brief
SHALL NOT select immutable comparison scope or request-language facts, nor may it
default an accepted output language.

Each fresh brief-generation visit SHALL perform at most two total bridge/model
invocations.
Only a retry-eligible `provider.timeout` or `provider.unavailable` returned from the
first invocation SHALL record its scheduled observation through the optional injected
event recorder, wait exactly 1,000 milliseconds through a cancellable backoff, and
repeat the identical initial brief request once. Retry eligibility requires the
bridge-supplied valid `ProviderObservation` for that zero-tool HITL1 result; a matching
code without it, a tools-enabled result, authentication, configuration, tool, policy,
unknown, and cancellation paths SHALL not receive this retry. Recorder absence or
failure SHALL not change this control path. The retry consumes the second and last
invocation slot. The count is a graph bridge/model-invocation count, not a physical
provider HTTP-request count; provider SDK retry policy remains outside this requirement.
`CancelledError` SHALL propagate without awaiting, shielding, or forcing a
post-cancellation recorder write.

When a retry-eligible transient provider result occurs, HITL1 SHALL write a validated
`ProviderRecoveryProjection` only if the visit subsequently blocks. That projection
SHALL contain the trigger category, its required safe `ProviderObservation`, trigger
invocation ordinal, model invocation count, automatic retry count, and exactly one disposition:
`exhausted`, `retry_followed_by_terminal_failure`, or
`retry_not_started_budget_consumed`. `exhausted` requires two invocations and one
automatic retry, a trigger ordinal of one, and both calls ending in retry-eligible
transient provider categories.
`retry_followed_by_terminal_failure` requires two invocations and one automatic retry,
with a trigger ordinal of one, where the second invocation ends in a non-transient
typed failure or invalid structured output. `retry_not_started_budget_consumed`
requires two invocations, zero automatic retries, and a trigger ordinal of two, where
a successful but malformed first output consumed the repair slot and that repair
invocation then returns a retry-eligible transient provider result. The projection
SHALL be absent when no retry-eligible transient provider result occurred. A
repair-slot transient requires the same bridge-supplied valid `ProviderObservation`;
a matching code without it SHALL not create this projection.

For every blocked result, HITL1 SHALL retain a final safe provider observation whenever
the bridge supplied one, including a non-retryable direct public HTTP response; it
SHALL not fabricate one for a legacy authentication mapping. A provider-diagnostic
terminal is a blocked incident with either a recovery projection or a final safe
provider observation. For every provider-diagnostic terminal, HITL1 SHALL derive one
safe opaque diagnostic reference from only a canonical subset of terminal-safe facts
before writing `ResearchState.latest_incident`: research id, generation, stable HITL1
node-attempt identity, final category, and, when present, recovery trigger
category/ordinal, model-invocation count, automatic-retry count, disposition, and the
trigger/final observation response kind plus bounded HTTP status. The subset SHALL
exclude configured-service label, configured endpoint authority, question, prompt, raw
exception, provider body, full URL, credential, and every other presentation field.
Changing only the label or authority SHALL not change the diagnostic reference. That
checkpointed incident remains the sole terminal owner; the event journal and
presentation consume it as projections.

A successful response that fails `StructuredBrief` validation may receive the existing
single repair request only when the two-invocation visit budget remains available. If
the budget has been consumed or the repair response is invalid, HITL1 SHALL fail
closed with `output.structured_invalid`. Any non-success result that is not covered by
the transient-provider policy SHALL preserve its typed category through the existing
blocked path. No failure path may call `interrupt()` or write profile state.

The real recipe SHALL continue to inject the existing zero-tool,
one-bridge/model-invocation-per-call node-agent bridge. Full-fake paths SHALL never
call a model. (`HIN-001`, `HIN-008`)

#### Scenario: Successful brief generation
- **WHEN** HITL1 enters with `state["request_text"]` = "Compare renewable energy storage technologies for grid-scale deployment" and a fake node-agent capability returns a valid `StructuredBrief` JSON in `NodeExecutionResult.summary`
- **THEN** the node calls `run_agent` once with a bounded request that includes the original question, validates the JSON, and proceeds to the user interrupt with the validated brief embedded in `HumanInputRequest.context`

#### Scenario: Model output fails schema validation once
- **WHEN** the first `run_agent` call returns JSON missing a required dimension and the retry returns valid JSON
- **THEN** the node re-prompts exactly once, never presents the invalid output, and proceeds with the valid retry output

#### Scenario: Model output fails schema validation twice
- **WHEN** both the initial `run_agent` call and the retry return malformed or schema-invalid output
- **THEN** the node sets `phase_status=TERMINAL`, `terminal_status=BLOCKED`, `terminal_reason=GATE_BLOCKED`, and `route=exhausted`, and no interrupt or profile artifact is produced

#### Scenario: Runtime injects the real node-agent bridge only for real HITL1
- **WHEN** the mixed implementation recipe selects `hitl1=real`
- **THEN** `RuntimeNodeDependencyResolver` provides a real `RuntimeNodeAgentBridge` with no allowed tools and a one-model-call-per-invocation budget for HITL1, while the full-fake recipe keeps unavailable capabilities and any fake HITL node call to `run_agent` fails the test

#### Scenario: Agent failure does not create partial state
- **WHEN** `capabilities.run_agent()` raises or returns a non-success `NodeExecutionResult`
- **THEN** HITL1 fails before `interrupt()`, leaves `pending_profile`, `profile_ref`, and all dimension fields unset, and does not consume a human response

#### Scenario: One timeout recovers within the visit budget
- **WHEN** the first HITL1 brief invocation returns `provider.timeout` and the next
  identical invocation returns valid structured brief JSON
- **THEN** HITL1 records one bounded retry observation, calls the agent exactly twice,
  and proceeds to the existing profile interrupt

#### Scenario: Initial and repair brief requests are both zero-tool
- **WHEN** HITL1 builds either its initial brief request or its malformed-output repair
  request
- **THEN** each request has `tools_enabled=false`, so the trusted HITL1 bridge policy
  can classify only those two bounded bridge/model invocations

#### Scenario: Second transient failure is exhausted safely
- **WHEN** the first and second HITL1 brief invocations return either
  `provider.timeout` or `provider.unavailable`
- **THEN** HITL1 emits one exhaustion observation and follows its existing blocked
  route without an interrupt or partial profile, preserving the final provider
  category, model_attempts=2, automatic_retries=1, `exhausted`, and one terminal
  diagnostic reference in the terminal incident

#### Scenario: Non-transient failure is not retried
- **WHEN** the first brief invocation returns authentication, configuration, tool,
  policy, structured-output, or unknown failure
- **THEN** HITL1 takes the existing failure route after one invocation and emits no
  provider retry/backoff observation

#### Scenario: Unproven provider code is not admitted to recovery
- **WHEN** the first brief invocation returns `provider.timeout` or
  `provider.unavailable` without the bridge-supplied valid `ProviderObservation`
- **THEN** HITL1 takes the existing fail-closed route after one invocation and emits
  no provider retry/backoff observation or recovery projection

#### Scenario: Non-retryable HTTP response remains safe terminal feedback
- **WHEN** the first brief invocation returns a non-retryable direct public HTTP
  response with a safe `400` observation
- **THEN** HITL1 blocks after one invocation, retains that final observation in its
  terminal incident with one safe diagnostic reference, and writes no recovery
  projection or retry/backoff observation

#### Scenario: Label and authority do not affect terminal correlation
- **WHEN** two otherwise identical provider-diagnostic HITL1 terminals differ only in
  their vetted configured-service label or sanitized endpoint authority
- **THEN** they derive the same diagnostic reference and retain neither value as a
  diagnostic-reference input

#### Scenario: Structured repair and transient recovery share one ceiling
- **WHEN** a transient provider failure consumes the second permitted invocation and
  that retry returns malformed structured output
- **THEN** HITL1 blocks with `output.structured_invalid` and does not issue a third
  repair request, preserving `retry_followed_by_terminal_failure` with two model
  attempts and one automatic retry

#### Scenario: Repair-slot provider failure cannot create a third call
- **WHEN** the first invocation returns a successful but malformed structured brief
  and its second repair invocation returns `provider.unavailable`
- **THEN** HITL1 blocks after exactly two invocations with
  `retry_not_started_budget_consumed`, zero automatic retries, and no third call

#### Scenario: Cancellation during provider backoff remains cancellation
- **WHEN** the first brief invocation returns `provider.timeout` and the outer task is
  cancelled during the 1,000 millisecond backoff
- **THEN** `CancelledError` propagates, no second invocation or exhaustion incident is
  created, no post-cancellation recorder write is required, and no interrupt or
  profile state is written

#### Scenario: Cancellation during the automatic retry remains cancellation
- **WHEN** the first brief invocation returns `provider.unavailable`, the fixed backoff
  completes, and the outer task is cancelled while the second invocation is in flight
- **THEN** `CancelledError` propagates, no terminal recovery incident or exhaustion
  event is created, and no interrupt or profile state is written

### Requirement: HITL1 presents structured brief and profile dimensions through durable interrupts

The real HITL1 node SHALL present a validated structured brief and profile dimensions
through the existing `interrupt(PendingResearchInterrupt(...))` mechanism with
`mode=TEXT` when a supported output/interaction language is already accepted. When the
bounded request-language detector is `unspecified` and no output language has yet been
accepted, HITL1 SHALL instead issue one correlated `mode=CHOICE` interrupt that
advertises exactly the closed supported-language options `zh` and `en`. That choice
SHALL carry neither `interaction` nor `action_ids`, and its selection SHALL be a typed
`OPTION` response rather than a text or action alias. The wire schemas for
`PendingResearchInterrupt`, `HumanInputRequest`, `AcceptedHumanResponse`, and
`InternalCancelDecision` SHALL remain version-compatible with the existing lifecycle
contract.

The `HumanInputRequest.context` string SHALL be bounded to 2,048 characters and SHALL
contain a compact JSON object with at minimum:

- `context_schema_version: 1`
- `brief_summary`
- `proposed_dimensions`
- `required_dimensions`
- `missing_dimensions`
- `valid_options`
- `instructions`

The `request_id` SHALL be derived with `make_hitl_request_id(research_id,
phase="hitl1", generation, ordinal)`. The ordinal SHALL come from the checkpointed
logical HITL1 visit count, so first visit uses ordinal 1 and each durable re-entrant
follow-up uses the next ordinal. The `suspension_cursor` SHALL reference the latest
consumed message id, falling back to the start message id.

HITL1 SHALL not store a duplicate mutable pending descriptor in `ResearchState`; the
LangGraph checkpoint interrupt remains the only pending-request authority. Durable
follow-up state that is needed to build the next prompt SHALL be stored separately as
bounded profile-progress state, never as a pending interrupt copy.

#### Scenario: First-visit interrupt with full brief
- **WHEN** HITL1 visits a research for the first time, brief generation succeeds, and a supported output language is accepted
- **THEN** the node calls `interrupt()` with a `PendingResearchInterrupt` containing `phase="hitl1"`, the current generation, `mode=TEXT`, and compact structured context for all required dimensions

#### Scenario: Unsupported language evidence uses the bounded choice
- **WHEN** HITL1 needs an output language but its bounded request-language detector is `unspecified`
- **THEN** it calls `interrupt()` with a current `phase="hitl1"` `mode=CHOICE` request that advertises exactly `zh` and `en`, no interaction, and no action ids

#### Scenario: Follow-up interrupt has a new ordinal
- **WHEN** a prior incomplete response has been consumed and HITL1 loops back to ask only for missing dimensions
- **THEN** the next `request_id` encodes ordinal 2, is distinct from the first visit's `request_id`, and `completed_visits(state, "hitl1")` returns 1 at entry time

#### Scenario: Interrupt context is bounded and parseable
- **WHEN** the interrupt is constructed from a generated brief or follow-up prompt
- **THEN** `HumanInputRequest.context` is valid compact JSON, includes the required keys, advertises stable enum machine values, and does not exceed 2,048 characters

#### Scenario: No duplicate pending authority
- **WHEN** a lifecycle is suspended at HITL1
- **THEN** the only pending request descriptor is the LangGraph interrupt task; checkpoint fields may contain bounded profile progress but not another mutable copy of the pending request


### Requirement: HITL1 parses, validates, and durably accumulates human profile answers

On resume, the real HITL1 node SHALL validate that `AcceptedHumanResponse.request_id`
matches the pending HITL1 request id. A mismatch SHALL raise
`ValueError("response_mismatch")`, preserving the existing lifecycle correlation
behavior. `InternalCancelDecision` SHALL route `cancel` to terminal `CANCELLED` with
`terminal_reason=USER_CANCELLED` and SHALL NOT write profile fields.

For a current HITL1 supported-language `CHOICE`, HITL1 SHALL accept only a correlated
`OPTION` response whose option id is one of the two current advertised supported
language options. It SHALL merge only the selected `output_language`, preserve the
immutable `request_language`, consume one accepted-answer round, and resume the
existing incomplete-profile flow. An option response to a HITL1 text request, a text
or action response to that language choice, or any absent, stale, or non-language
option SHALL fail before profile mutation; it SHALL not be interpreted as a free-text
language alias.

The parser SHALL accept either a compact JSON object or free text. Recognized profile
dimension values SHALL be accepted only when they match the closed enum machine values
or an explicitly documented synonym that maps deterministically to one enum value.
Recognized comparison subjects and output language SHALL likewise use only their
documented bounded typed forms. Unrecognized values SHALL be treated as unset, not
coerced by model judgment. The parser SHALL return a frozen partial-profile/progress
contract that permits missing dimensions while still enforcing bounds for supplied
values. A complete current-schema `ResearchProfile` SHALL be constructible only when
all required closed-enum dimensions, at least one `must_answer` question, a required
comparison pair, and an accepted supported output language are present.

Incomplete responses SHALL be durable across process restart. HITL1 SHALL write bounded
profile-progress fields into `ResearchState` before routing back to HITL1 with
`route=needs_followup`; it SHALL NOT rely on Python closure state. The graph SHALL then
enter HITL1 again, compute the next ordinal from the checkpointed trace, and issue a
follow-up interrupt asking only for missing or invalid dimensions. HITL1 SHALL allow at
most three user-answer rounds (ordinals 1, 2, 3). If the third answer is still missing
only degradable legacy profile dimensions after comparison and language facts are
complete, the node SHALL record the best-effort profile with `degraded_profile=True`
and route `accepted`. If the third answer still lacks a required comparison pair or
output language, the node SHALL terminally block with `terminal_reason=GATE_BLOCKED`,
write no profile artifact, and never fabricate a degraded pair or language.

#### Scenario: Complete valid response accepted
- **WHEN** a resume delivers recognizable values for all required dimensions (`depth=standard`, `audience=practitioner`, `format=detailed_report`, `cost_tolerance=moderate`, `time_budget=standard`) plus at least one must-answer question
- **THEN** the node constructs a complete `ResearchProfile`, writes profile state and artifact data, consumes the response ids, and routes `accepted -> topic_planning`

#### Scenario: Free-text response is parsed deterministically
- **WHEN** the human writes "standard depth, for practitioners, detailed report, moderate cost, standard time; must answer Q1 and Q2"
- **THEN** the parser extracts only those stable machine values and must-answer questions, and no LLM is called to reinterpret the answer

#### Scenario: Response with only some dimensions filled
- **WHEN** a resume specifies `depth=quick_overview` and `audience=layperson` but omits `format`, `cost_tolerance`, `time_budget`, or must-answer questions
- **THEN** HITL1 stores durable profile progress, consumes the response ids, routes `needs_followup` back to HITL1, and the next interrupt asks only for the missing fields

#### Scenario: Restart resumes a follow-up
- **WHEN** a process commits the partial profile progress and the follow-up interrupt, then a fresh process resumes with the matching follow-up response
- **THEN** the node loads progress from the checkpoint, merges only newly valid fields, and can route `accepted` without relying on in-memory closure data

#### Scenario: Response with unrecognizable dimension value
- **WHEN** a resume states `depth=superficial`
- **THEN** the parser treats `depth` as unset, preserves any other valid fields, and the follow-up context lists valid `depth` options `quick_overview`, `standard`, `deep_dive`, and `exhaustive`

#### Scenario: Response request_id mismatch
- **WHEN** a resume delivers `AcceptedHumanResponse.request_id` that does not match the pending interrupt's `request_id`
- **THEN** the node raises `ValueError("response_mismatch")`, the lifecycle handler surfaces `ResultCode.RESPONSE_MISMATCH`, and the checkpoint and pending interrupt remain unchanged

#### Scenario: Current language option records only the accepted preference
- **WHEN** a matching current HITL1 language choice receives its advertised `zh` option
- **THEN** HITL1 records `output_language=zh`, preserves its `request_language`, consumes one accepted-answer round, and returns to the incomplete-profile flow without accepting or routing a profile

#### Scenario: Cancel decision during HITL1
- **WHEN** a resume delivers `InternalCancelDecision`
- **THEN** the node routes `cancel` with `terminal_status=CANCELLED` and `terminal_reason=USER_CANCELLED`, and no profile progress or final profile fields are written

#### Scenario: Follow-up rounds are bounded for degradable fields
- **WHEN** HITL1 receives the third user-answer round with comparison and language facts complete but other degradable required fields still missing
- **THEN** the node records the best-effort profile, sets `degraded_profile=True`, clears transient profile-progress fields, and routes `accepted` rather than issuing another interrupt

#### Scenario: Required comparison scope cannot degrade into acceptance
- **WHEN** HITL1 receives the third user-answer round and a supported comparison request still lacks its required pair
- **THEN** the node routes terminal `GATE_BLOCKED`, writes no profile artifact or final profile fields, and does not select a default pair

### Requirement: HITL1 resolves natural proposal replies through bounded semantic intake

For a complete checkpointed HITL1 proposal, HITL1 SHALL first normalize a raw text
reply and compare it with the documented finite Chinese and English clear-confirmation
phrase set. A matching phrase SHALL take the existing correlated
`accept_suggestion` materialization path without a semantic-intake bridge/model call.
The local path SHALL accept only the current complete checkpointed proposal and SHALL
not parse a mixed, modifying, questioning, or ambiguous reply as confirmation.

Any other raw text reply for a complete checkpointed proposal SHALL be passed to a
zero-tool structured semantic-intake request and treated only as a candidate intent.
HITL1 SHALL retain graph authority for correlated acceptance, profile publication,
proposal version, state mutation, and routing. A candidate confirmation SHALL publish
only the current complete checkpointed proposal. A full candidate revision SHALL create
a new visible advisory proposal version and require a new confirmation. A bounded
proposal question or clarification SHALL preserve the proposal and reissue a fresh
correlated request. (`HIN-009`)

#### Scenario: Local natural confirmation is graph-authorized without model use
- **WHEN** a matching current complete HITL1 reply is an exact normalized clear
  Chinese or English confirmation phrase
- **THEN** HITL1 writes the current checkpointed proposal through the existing action
  path, makes zero semantic bridge/model calls, and requires no adapter action alias

#### Scenario: Revision becomes visible before acceptance
- **WHEN** a matching current reply resolves to a full changed proposal
- **THEN** HITL1 checkpoints the new advisory proposal, increments its version, renders
  every material value, and does not write `profile.json` until a later confirmation

#### Scenario: Question leaves a proposal pending
- **WHEN** a matching current reply asks why a suggested value was chosen
- **THEN** HITL1 returns one bounded explanation and a fresh request for the unchanged
  proposal without consuming an accepted-answer or rejection round
