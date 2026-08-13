# hitl1-node Specification

> req: HIN-001, HIN-002, HIN-003, HIN-004, HIN-005, HIN-006, HIN-007, HIN-008, HIN-009, HIN-010, HIN-011, HIN-012, HIN-013, HIN-014, HIN-015, HIN-016

## Purpose

The real HITL1 node is the first model-calling node in the Deep Research graph. It
generates a validated structured research brief from the original question through the
runtime node-agent bridge using closed-enum profile dimensions and fail-closed schema
validation, presents the brief and follow-up prompts through the existing graph-owned
interrupt protocol with bounded compact context and deterministic request ordinals,
parses JSON or free-text human responses deterministically with restart-durable
partial-profile accumulation and bounded follow-up rounds, records the validated profile
as request-bundle `profile.json` plus checkpoint short fields and a `ContentRef` without
bumping the `ResearchState` schema version, and integrates into the mixed graph with
explicit follow-up and blocked routes while preserving full-fake behavior and the
backend/frontend boundary.
## Requirements

### Requirement: HITL1 generates a validated structured brief from the original question

The existing bounded zero-tool brief-generation, schema validation, redaction, and
blocked-route guarantees remain unchanged. Any durable incident or correlation emitted
by real HITL1 SHALL bind only the selected Bundle-local State and opaque `bundle_id`;
it SHALL not write or expose a conversation-derived `research_id`, external checkpoint
identity, or Bundle path. (`HIN-001`)

#### Scenario: Brief failure cannot create legacy Run identity
- **WHEN** real HITL1 records a bounded brief-generation failure for an available Bundle
- **THEN** its State/result correlation uses the selected Bundle fact and does not add a
  research-id or checkpoint-based lifecycle reference

### Requirement: HITL1 presents structured brief and profile dimensions through durable interrupts

The real HITL1 node SHALL present a validated structured brief and profile dimensions
through `interrupt(PendingResearchInterrupt(...))` with `mode=TEXT` when a supported
output/interaction language is accepted. When the bounded request-language detector is
`unspecified` and no output language is accepted, HITL1 SHALL issue one correlated
`mode=CHOICE` interrupt advertising exactly `zh` and `en`. That choice SHALL carry no
interaction or action ids, and its selection SHALL be a typed `OPTION` response rather
than a text or action alias. The wire schemas for `PendingResearchInterrupt`,
`HumanInputRequest`, `AcceptedHumanResponse`, and `InternalCancelDecision` SHALL remain
version-compatible with the lifecycle contract.

`HumanInputRequest.context` SHALL be bounded to 2,048 characters and contain compact
JSON with at minimum `context_schema_version: 1`, `brief_summary`,
`proposed_dimensions`, `required_dimensions`, `missing_dimensions`, `valid_options`,
and `instructions`. `request_id` SHALL be derived with
`make_hitl_request_id(bundle_id, phase="hitl1", generation, ordinal)`. The ordinal
comes from the Bundle-local logical HITL1 visit count, so first visit uses ordinal 1 and
each durable follow-up uses the next ordinal. The suspension cursor SHALL reference the
latest consumed message id, falling back to the start message id.

The graph interrupt remains the in-invocation delivery mechanism, but the selected
Bundle-local State is the sole durable pending-interaction authority. HITL1 SHALL retain
exactly one bounded, correlation-valid pending descriptor there and SHALL not create a
second mutable copy in an external checkpoint, session, or adapter. Durable follow-up
facts needed to build the next prompt remain bounded profile-progress data. (`HIN-002`)

#### Scenario: First-visit interrupt with full brief
- **WHEN** HITL1 visits a Bundle for the first time, brief generation succeeds, and a supported output language is accepted
- **THEN** the node calls `interrupt()` with a `PendingResearchInterrupt` containing `phase="hitl1"`, the current generation, `mode=TEXT`, and compact structured context for all required dimensions

#### Scenario: Unsupported language evidence uses the bounded choice
- **WHEN** HITL1 needs an output language but its bounded request-language detector is `unspecified`
- **THEN** it calls `interrupt()` with a current `phase="hitl1"` `mode=CHOICE` request that advertises exactly `zh` and `en`, no interaction, and no action ids

#### Scenario: Follow-up interrupt has a new ordinal
- **WHEN** a prior incomplete response has been consumed and HITL1 loops back to ask only for missing dimensions
- **THEN** the next `request_id` encodes ordinal 2, is distinct from the first visit's `request_id`, and the Bundle-local completed-visit count for `hitl1` is 1 at entry time

#### Scenario: Interrupt context is bounded and parseable
- **WHEN** the interrupt is constructed from a generated brief or follow-up prompt
- **THEN** `HumanInputRequest.context` is valid compact JSON, includes the required keys, advertises stable enum machine values, and does not exceed 2,048 characters

#### Scenario: One Bundle-local pending authority survives restart
- **WHEN** a lifecycle is suspended at HITL1 and the process later restarts while the Bundle remains available
- **THEN** only the Bundle-local pending descriptor supplies the correlation/lifecycle fact; graph delivery state may be rebuilt from it but no external checkpoint or duplicate descriptor can authorize resume

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

### Requirement: HITL1 stores recorded profile facts in Bundle-local State and contained content

The real HITL1 node SHALL write the final recorded profile to the selected Bundle's
contained `request/profile.json` through a runtime-owned request-bundle capability and
reference it from Bundle-local State via `profile_ref`. The capability SHALL be attached
only when the selected real factory declares it. It SHALL use the preselected Bundle
reference, perform host-side containment, write atomically, compute the content hash
from canonical JSON bytes, and return a bounded `ContentRef`. Nodes SHALL receive only
the pure protocol, not host paths or raw runtime authority.

Bundle-local State SHALL additionally store the bounded fields needed by topic planning:
`research_depth`, `target_audience`, `output_format`, `cost_tolerance`, `time_budget`,
`must_answer_questions`, and `degraded_profile`, plus bounded transient progress
`pending_profile` and `profile_followup_round`. Those fields SHALL be cleared when
HITL1 accepts or cancels, owned by `WriterRole.CONTROLLER`, listed in the ownership
table, and protected by controller-authorized reducers. Final profile publication SHALL
be atomic from the graph perspective: `accepted` produces the artifact and final fields
together; follow-up writes only transient progress; cancel or brief-generation failure
writes no final profile fields. (`HIN-004`)

#### Scenario: Profile written to contained ContentRef
- **WHEN** a complete valid human response is accepted
- **THEN** HITL1 writes canonical `profile.json` under the selected Bundle's `request/` subtree, receives a bounded `ContentRef`, and sets Bundle-local `profile_ref`

#### Scenario: Partial progress is not final profile state
- **WHEN** the first answer is incomplete
- **THEN** `pending_profile` and `profile_followup_round` are written, but `profile_ref`, final short dimension fields, and `profile.json` are not written until an accepted final profile exists

#### Scenario: Cancel route writes no profile
- **WHEN** the user cancels at HITL1
- **THEN** no final profile fields, `profile_ref`, or `profile.json` are written, and transient profile progress is cleared

### Requirement: HITL1 integrates into the mixed graph with explicit lifecycle and governance updates

The real HITL1 SHALL retain its existing mixed-graph selection, full-fake isolation,
declared `accepted`, `cancel`, `needs_followup`, and `exhausted` routes, bounded
follow-up loop, and no-upstream/UI-change boundary. A real HITL1 factory SHALL receive a
preselected available Bundle context rather than require real Bootstrap to create or
select a root. The normalized topology snapshot and route-contract tests SHALL be
updated for Bundle-local pending/refinement State without adding an undeclared route.
The project-structure registry and generated
`deep_research_harness/AGENTS.md` locator SHALL retain the narrow graph-owned
`langgraph.types.interrupt` exception. (`HIN-005`)

#### Scenario: Mixed graph keeps its declared routes
- **WHEN** the implementation map sets `hitl1=real` with a valid preselected Bundle and every later phase fake
- **THEN** the graph compiles, runs only its declared HITL1 routes, preserves the mixed implementation result, and HITL1 cannot create a second Bundle or external lifecycle authority

#### Scenario: Full-fake graph remains isolated
- **WHEN** the implementation map sets all phases to `fake`
- **THEN** the graph completes the existing deterministic path without a real request-profile writer, external lifecycle recovery, or a production-to-fixture import

### Requirement: Real HITL-1 preserves brief-generation failure category through its blocked route

Real HITL-1 SHALL consume the typed `NodeProblem` returned by the runtime bridge when
brief generation cannot complete. It SHALL retain its existing bounded retry and
exhausted graph route, but SHALL not catch every bridge/model exception and convert
it to an indistinguishable `None` result. A directly known safe category and opaque
diagnostic reference may be recorded as the compact terminal incident when the node
routes blocked; raw error content shall not enter profile state, pending interrupt,
request bundle, or human prompt.

Malformed structured brief output SHALL be categorized as a safe output/validation
failure distinct from missing model configuration or provider timeout. A
non-interactive auto-profile path shall retain its current behavior and shall not
construct a failed brief solely to populate presentation diagnostics. (`HIN-006`)

#### Scenario: Real model configuration failure explains the blocked route
- **WHEN** a real interactive HITL-1 run cannot resolve a model before creating its brief
- **THEN** it reaches the existing blocked terminal route with a compact safe configuration category available to lifecycle projection instead of only `gate_blocked` with no causal explanation

### Requirement: HITL1 makes profile proposal acceptance and answer feedback durable

After validating a first-visit `StructuredBrief`, real HITL1 SHALL checkpoint a bounded controller-owned advisory proposal before it interrupts. The proposal SHALL contain only validated profile fields and a schema version; it SHALL not contain raw model output or become final profile authority. A correlated typed closed response action `accept_suggestion` SHALL materialize that proposal only when it is complete and matches the current HITL1 request. The node SHALL not invoke brief generation again when resumed at the same persisted proposal.

HITL1 SHALL parse structured JSON and a documented deterministic Chinese/English alias set into at most one value per profile dimension. `must_answer` SHALL be visible in the prompt projection. A response that recognizes no valid field or answer content SHALL leave profile progress, consumed response ids, and accepted-answer round unchanged; HITL1 SHALL reissue bounded feedback naming the supported input forms. It SHALL checkpoint the rejected message id only as a bounded next-interrupt cursor, so the fresh feedback request starts after that message without treating it as a consumed accepted response. A separate controller-owned rejection counter SHALL permit at most three consecutive rejected responses in the same ongoing HITL1 intake; feedback may issue a new request id while preserving proposal/progress/counter correlation. The third SHALL terminally block using the existing `terminal_reason=gate_blocked` and compact `RunFailureCode.INPUT_INVALID_RESPONSE` incident, with presentation category `profile_input_unrecognized`, a deterministic runtime diagnostic reference, and structured-input recovery guidance. A recognized response, acceptance, cancellation, or terminal result SHALL clear the transient rejection cursor/counter as applicable. A recognized but incomplete response SHALL durably merge only the recognized fields, reset that counter, and consume one accepted-answer round. The bounded final degradation policy applies only to accepted incomplete answers, never to rejected zero-recognition input. (`HIN-007`)

#### Scenario: Explicit acceptance adopts only the checkpointed proposal
- **WHEN** a matching HITL1 response selects `accept_suggestion` for a complete checkpointed proposal
- **THEN** HITL1 writes that proposal as the final profile and clears transient proposal and feedback state without calling a model again

#### Scenario: Localized input receives deterministic feedback
- **WHEN** a user answers `标准深度`
- **THEN** HITL1 recognizes `depth=standard`, reports the remaining required fields including `must_answer`, and consumes exactly one accepted-answer round

#### Scenario: Unrecognized input is not silently degraded
- **WHEN** a user answers `你来定义吧` or another value with no closed accepted meaning
- **THEN** HITL1 keeps the pending profile/proposal and accepted-answer round unchanged, returns a bounded feedback prompt, and does not route toward degraded finalization

#### Scenario: Rejected input cannot replay against a feedback request
- **WHEN** HITL1 rejects one response and reissues feedback with a new request id
- **THEN** the next interrupt cursor starts after the rejected message, that message is not in accepted consumed ids, and only a later matching response is eligible for the fresh request

#### Scenario: Rejection feedback cannot loop forever
- **WHEN** three consecutive responses in one ongoing HITL1 intake have no closed accepted meaning
- **THEN** the first two preserve accepted-answer state and reissue correlated feedback, while the third records blocked `gate_blocked` plus `input.invalid_response` incident with a deterministic `diag_` reference and presentation category `profile_input_unrecognized` with the JSON recovery form and no degraded profile

#### Scenario: Ambiguous phrase cannot populate two dimensions
- **WHEN** an alias phrase could match more than one profile dimension
- **THEN** the parser rejects that phrase rather than guessing, and feedback names the structured JSON alternative

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

### Requirement: HITL1 semantic-intake failure is bounded non-terminal feedback

HITL1 SHALL make at most three semantic bridge/model calls per raw proposal reply. It
MAY make at most two automatic retries only for a valid retry-eligible transient
provider result and at most one structured-output repair, sharing that three-call cap.
Cancellation SHALL propagate. Exhaustion, non-transient provider failure, or invalid
structured output SHALL preserve the current proposal, write closed interaction
feedback, reset no final profile authority, and reissue a request with a visible
fallback control. These outcomes SHALL not increment `profile_rejection_round` or
terminally block the lifecycle. (`HIN-010`)

#### Scenario: Transient semantic failures stop at three calls
- **WHEN** the first three semantic calls for one reply each return a retry-eligible
  provider failure
- **THEN** HITL1 makes exactly three calls, records non-terminal semantic feedback,
  and keeps the current proposal confirmable

#### Scenario: Invalid semantic output has one repair
- **WHEN** the first semantic output is malformed and its one repair is malformed
- **THEN** HITL1 does not issue another repair, preserves the proposal, and returns
  closed feedback with the visible fallback control

### Requirement: HITL1 profile interaction completes bounded human lifecycle journeys

For a complete current HITL1 proposal, the real node SHALL preserve graph-owned
admission through a correlated multi-visit interaction lifecycle. A natural text
confirmation SHALL materialize only the current checkpointed proposal. A valid full
semantic revision that includes first-party-source or citation constraints in the
existing profile values SHALL become a new visible advisory proposal and require a
later confirmation before any profile artifact is written. A bounded proposal
question or ambiguity/clarification SHALL leave the current proposal confirmable and
shall not consume an accepted-answer or rejected-input round.

An exhausted semantic provider/output failure SHALL preserve the same current
proposal, return the existing non-terminal semantic fallback, expose the current
proposal control, and write no profile artifact. Semantic candidates SHALL remain
unable to create an action id, correlation value, graph route, checkpoint mutation,
or final profile without deterministic HITL1/domain admission. (`HIN-011`)

#### Scenario: Confirmation accepts only the current proposal
- **WHEN** a correlated natural confirmation is classified for a complete current proposal
- **THEN** HITL1 writes only that checkpointed proposal as the final profile and routes
  accepted without parsing the reply as profile fields or accepting any model-proposed
  lifecycle value

#### Scenario: Source-constrained revision is visible before acceptance
- **WHEN** a correlated semantic candidate supplies a valid full revision that asks for
  first-party sources and citations through existing profile values
- **THEN** HITL1 checkpoints and renders a new advisory proposal version containing those
  constraints, writes no profile artifact, and requires a later correlated confirmation

#### Scenario: Question and ambiguity preserve a confirmable proposal
- **WHEN** a correlated reply resolves to a bounded proposal question or clarification
- **THEN** HITL1 preserves every current proposal value and its visible control, reissues
  a fresh correlated request with focused feedback, and consumes neither answer nor
  rejected-input round

#### Scenario: Semantic exhaustion leaves a usable fallback
- **WHEN** semantic intake exhausts its existing permitted calls for one correlated reply
- **THEN** HITL1 preserves the current proposal/control, emits non-terminal fallback
  feedback, writes no profile artifact, and does not terminally block the lifecycle

### Requirement: HITL1 calibration policy preserves decision-ready input semantics

The four HITL1 zero-tool policies SHALL expose branch-specific, model-visible criteria
for a conservative research-profile proposal and for one correlated human reply. The
brief policy SHALL derive an advisory `StructuredBrief` only from the bounded original
question and the graph-owned closed output contract; it SHALL make no research finding,
citation, acceptance, route, or checkpoint claim. The semantic-intake policy SHALL
treat the reply as untrusted data against the current proposal and produce only one
candidate intent: confirmation, full constrained revision, proposal question, or
clarification. An ambiguous or unsupported reply SHALL remain a clarification rather
than become a fabricated requirement or an implicit acceptance.

Each repair policy SHALL receive only its same bounded assignment, invalid candidate,
and compact validation fact. It SHALL preserve the original question or current
proposal boundary, shall not add a requirement, research conclusion, action, route,
or checkpoint field, and SHALL return only the existing typed candidate. The existing
HITL1 parser, semantic resolver, human confirmation, retry bounds, and blocked or
non-terminal feedback paths SHALL remain the only acceptance and recovery owners.

#### Scenario: Brief distinguishes a proposal from research output
- **WHEN** the original question contains a request for a research conclusion or
  citation alongside profile preferences
- **THEN** the profile-brief request asks only for an advisory, closed-contract
  research profile and its candidate contains no finding, citation, acceptance, or
  lifecycle authority

#### Scenario: Ambiguous reply remains a clarification
- **WHEN** a correlated human reply neither confirms the current proposal nor supplies
  a complete constrained revision
- **THEN** semantic intake returns only the existing clarification candidate and the
  deterministic HITL1 flow preserves the current proposal for a later human response

#### Scenario: Repair cannot broaden the intake assignment
- **WHEN** a profile-brief or semantic-intake candidate fails structural validation
- **THEN** its one bounded repair request receives no model-visible capability to add
  requirements or lifecycle data and any still-invalid response follows the existing
  non-admission outcome

### Requirement: HITL1 terminal correlation retains only observed timeout origins

When HITL1 receives provider-diagnostic results carrying safe timeout origins, it SHALL
retain each exact origin in the role that owns its `ProviderObservation`: the recovery
trigger or final terminal observation, and SHALL supply those roles unchanged to the
shared `workflow-failure-outcomes` diagnostic-correlation helper. It SHALL preserve
absent legacy origins as absent and SHALL not reconstruct an origin from retry history,
service label, endpoint authority, timestamps, or raw provider data. This diagnostic
fact SHALL not change the existing provider retry bound, graph route, natural proposal
confirmation semantics, or the authority of the semantic candidate/resolution flow.
(`HIN-001`, `HIN-009`)

#### Scenario: Trigger and final timeout origins remain distinct
- **WHEN** a retry-exhausted HITL1 terminal has a bridge-budget recovery trigger and a
  provider-SDK-timeout final observation
- **THEN** its terminal incident retains both origins in their distinct roles and derives
  a safe diagnostic correlation reference without exposing raw failure data

#### Scenario: Trigger-only timeout origin remains absent at the final observation
- **WHEN** a bridge-budget provider timeout triggers the retry and that retry reaches a
  non-timeout terminal failure
- **THEN** the recovery trigger retains its origin, the final observation retains no
  timeout origin, and HITL1 does not infer either value from the recovery disposition

#### Scenario: Natural confirmation remains graph-authorized
- **WHEN** a complete current proposal receives the natural confirmation
  `确认，按这个方案开始吧。`
- **THEN** the existing bounded local-recognition and graph-admission path accepts only
  the current checkpointed proposal and does not parse that reply as profile fields

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

### Requirement: HITL1 brief expected output remains compatible with strict admission

Every initial and structural-repair HITL1 brief request SHALL advertise a JSON output
contract compatible with current strict `StructuredBrief` admission: `required_keys`
SHALL include every parser-required field and name only fields the parser accepts;
advertised closed enum values, canonical schema version, and documented value bounds
SHALL be parser-valid. Parser-defaulted fields need not be advertised as required. The
descriptor SHALL not advertise a model-output field that the parser forbids or cannot
persist. System-owned presentation-language constraints SHALL be expressed as an
instruction and validated from the accepted `brief_summary`; they SHALL not advertise
an unsupported `brief_summary_language` field.

The compatibility relation SHALL have deterministic fixture evidence: a valid object
formed from the advertised expected contract is admitted by the strict parser, while
an advertised-forbidden extra field is rejected before profile or checkpoint state is
written. This requirement preserves the existing two-invocation brief/repair bound,
existing typed `output.structured_invalid` outcome, and graph-owned blocked route.
(`HIN-013`)

#### Scenario: Expected brief fields are admitted by the strict parser
- **WHEN** a deterministic HITL1 fixture constructs a complete brief from the
  model-visible required keys, enum values, and bounds
- **THEN** strict `StructuredBrief` admission accepts it and HITL1 can present the
  resulting advisory proposal without adding a profile artifact

#### Scenario: Language constraint does not invent an output field
- **WHEN** the original request has an accepted Chinese or English output-language
  constraint
- **THEN** the HITL1 request instructs the required `brief_summary` language without
  advertising the unsupported `brief_summary_language` output key

#### Scenario: An unsupported field remains a bounded invalid candidate
- **WHEN** a model candidate contains an extra field not in the strict brief contract
- **THEN** HITL1 admits no partial profile or checkpoint state, follows only its
  existing bounded structural-repair/blocked behavior, and never treats that field as
  a language or lifecycle authority

### Requirement: HITL1 adapts model-led confirmation without granting model authority

For a complete current interactive proposal, real HITL1 SHALL use Research
Confirmation as the deterministic admission boundary for the existing visible-control,
exact clear-confirmation, and semantic-intake reply paths. HITL1 SHALL retain
ownership of response correlation, graph interruption and routing, checkpoint
mutation, profile artifact publication, and the existing bounded provider and
structured-output recovery behavior. The profile artifact may be written only when
the returned confirmation outcome contains Accepted Research Facts for the current
complete proposal. An outstanding User Decision SHALL be rendered through the
existing typed interaction projection and require a later correlated response.
HITL1 SHALL not grant a model brief or semantic candidate a route, checkpoint,
artifact, or accepted profile effect. The pre-existing non-interactive auto-profile
path remains outside this interactive admission boundary and unchanged. (`HIN-014`)

#### Scenario: Model-led natural confirmation starts research through the existing path
- **WHEN** HITL1 has shown a complete model-led proposal and receives a correlated
  natural-language confirmation of that proposal
- **THEN** it writes only the admitted current profile through its existing profile
  publication path and follows its existing accepted route without requiring a JSON
  profile response or an adapter action alias

#### Scenario: A semantic revision remains advisory
- **WHEN** semantic intake returns a valid complete revision for a correlated reply
- **THEN** HITL1 persists and renders the revised proposal as one outstanding User
  Decision, requires a later confirmation, and writes no profile artifact

#### Scenario: Semantic fallback keeps lifecycle ownership unchanged
- **WHEN** the existing semantic-intake bridge reaches its bounded unavailable or
  invalid-output fallback
- **THEN** HITL1 preserves the current outstanding User Decision and its typed
  feedback without delegating retry, terminal disposition, or checkpoint authority
  to Research Confirmation

### Requirement: HITL1 keeps durable interaction facts in the selected Run Bundle

HITL1 SHALL read and persist its accepted profile, pending interaction correlation,
advisory proposal progress, and request-bundle content through the selected Bundle-local
Research State and contained Bundle artifacts. It SHALL not derive a research identity,
choose a path, or use an external checkpoint namespace as a continuation/recovery
authority. The graph-owned interrupt remains the pending-action mechanism, but its
durable lifecycle facts are owned by the Bundle. (`HIN-015`)

#### Scenario: HITL1 follow-up remains in one Bundle after restart
- **WHEN** HITL1 resumes an available suspended Run after restart
- **THEN** it validates the pending interaction from Bundle-local State and writes the follow-up profile artifacts only in that same Bundle

### Requirement: HITL1 runtime capabilities own bounded cognitive methods without control authority

The real HITL1 node SHALL bind distinct runtime-loaded local capability resources for
brief generation, brief repair, semantic reply interpretation, and semantic-candidate
repair. Each activated resource SHALL contain the reusable cognitive method for its
one bounded task: input interpretation, decision branches, uncertainty handling,
self-check, repair limits, and completion condition. The final production-rendered
agent context SHALL include the exact activated resource body; reader-only workflow
documentation and an embedded or dynamically assembled duplicate method SHALL not be
required to determine the model's cognitive procedure.

The node SHALL pass only a bounded assignment and closed output contract outside that
method: the original question, current checkpointed proposal, current human reply,
and compact validation facts/draft where applicable are data rather than instruction
authority. The capability resources SHALL remain zero-tool and advisory. They SHALL
not create an action or correlation id, select a route, mutate checkpoint or
Bundle-local State, publish `profile.json`, alter the accepted profile, cite research,
or report a lifecycle outcome. Existing typed parsing, current-proposal confirmation,
profile materialization, correlation, call ceilings, cancellation, provider recovery,
and lifecycle routing remain deterministic HITL1/domain/runtime responsibilities.

The project SHALL retain `hitl1-cognitive-program-v1` beside the existing
`hitl1-brief-v1` compatibility smoke. The cognitive corpus SHALL cover normal
confirmation, complete revision, proposal question, ambiguity, adversarial input,
and malformed candidate repair. Its declared runtime controls SHALL bind the four
HITL1 capability resources and the `StructuredBrief` and `SemanticCandidate` schema
sources by project-relative path and sha256 digest. Every scenario SHALL name its
expected capability ids, bounded assignment fragments, forbidden control effects, and
a non-empty unique set of criterion IDs. Those IDs are Case-control-integrity metadata:
deterministic registry admission validates the selected Rubric's declared
identity/version and the scenarios' unique criterion-ID set before subject
construction. They SHALL NOT carry criterion prose, weights, thresholds, evaluator
guidance, or a quality disposition into the HITL1 execution subject or model-facing
input.
Deterministic cases SHALL establish exact resource loading, bounded input/output,
candidate admission, and legal fallback only.

The immutable evaluation manifest and review record SHALL identify the evidence layer
as exactly `deterministic_handoff` or `credentialed_live_quality`. Ordinary
deterministic execution SHALL record only `deterministic_handoff`. Only the selected
live entrypoint, after its existing strict credential preflight, may record
`credentialed_live_quality`; a reviewer SHALL derive that layer from the verified
manifest. Neither layer nor a review result is a release claim or lifecycle authority.

#### Scenario: Production rendering supplies one exact cognitive method
- **WHEN** real HITL1 prepares an initial or repair brief or semantic-intake invocation
- **THEN** the final rendered context contains the exact corresponding runtime-loaded
  capability method and its closed zero-tool posture, while the bounded assignment and
  output schema remain separate data and contract projections

#### Scenario: HITL1 criterion IDs cannot become quality input
- **WHEN** a HITL1 cognitive-program case is admitted after its criterion IDs match the selected Rubric control
- **THEN** any retained criterion IDs are non-model control metadata and are not
  interpreted as scoring, quality instruction, or a verdict; the subject receives no
  criterion prose, weights, thresholds, evaluator guidance, or quality disposition
  from that Rubric

#### Scenario: Semantic ambiguity stays advisory
- **WHEN** a current correlated proposal receives an ambiguous or adversarial natural-language reply
- **THEN** HITL1 admits at most a closed clarification candidate, preserves the current
  proposal and its visible control, and does not create a profile artifact, State write,
  route, action id, or correlation value from the capability output

#### Scenario: Repair cannot become a parallel control path
- **WHEN** a brief or semantic candidate is malformed
- **THEN** HITL1 applies only its existing bounded repair/recovery path using the same
  task assignment and untrusted draft, and a repaired candidate still requires the
  existing deterministic parser and materializer before it can affect a profile or route

#### Scenario: Deterministic evidence does not overclaim cognitive quality
- **WHEN** the HITL1 cognitive corpus runs without approved live credentials
- **THEN** it records only `deterministic_handoff`; strict live preflight creates no
  live manifest, review, or fabricated rubric result, and the change closeout marks
  live-quality evidence availability `limited` without a live or release pass
