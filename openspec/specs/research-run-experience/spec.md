# research-run-experience Specification

> req: RER-001, RER-002, RER-003, RER-004, RER-005, RER-006, RER-007, RER-008, RER-009, RER-010, RER-011, RER-012, RER-013, RER-014

## Purpose

Provide one runtime-owned, safe lifecycle-to-presentation and diagnostics contract
for standalone Deep Research entry points without creating a second graph authority
or claiming a durable product session.
## Requirements

### Requirement: One runtime Module owns lifecycle-to-presentation interpretation

`ResearchRunExperience` SHALL retain one runtime-owned shared presentation interface
with the existing safe `Ready`, `Working`, `AwaitingInput`, `Terminal`, and `Fault`
updates. Its closed input vocabulary SHALL distinguish `Start`, correlated response/
visible-control submission for `resume`, `Cancel`, `Status`, and a separate bounded
`Refine` intent. The module consumes one shared typed Bundle lifecycle result; it does
not derive a `research_id`, keep a durable session or Bundle cache, construct a Bundle
path, or create an alternative graph/state authority.

A scripted `Start` intent SHALL project the explicit trusted
`non_interactive=true` marker and the complete closed non-interactive policy to its
single `start` transport dispatch. It SHALL not synthesize a human response, select a
HITL route, write checkpoint state, or attach policy to later `resume`, `refine`,
`status`, or `cancel` dispatches. The reflected lifecycle boundary remains the sole
admission point and the selected Bundle checkpoint remains the later policy owner.
When the checkpointed graph trace contains the bounded `hitl1_auto_profile` or
`hitl2_auto_proceed` policy observation marker, the module SHALL accept and project it
as an observation only; the marker SHALL NOT become lifecycle, route, profile, or
checkpoint authority.
(`RER-001`)

#### Scenario: Run experience keeps refine distinct from a response
- **WHEN** an available Bundle awaits input and a presentation adapter submits a
  refinement
- **THEN** the module dispatches the separate `refine` intent and leaves the correlated
  pending response available only to its resume path

#### Scenario: Scripted start projects explicit intent only once
- **WHEN** a standalone adapter submits a scripted `Start` intent
- **THEN** its one `start` transport dispatch contains `non_interactive=true` and both
  closed policy values, while the adapter has not created a Bundle, graph route,
  profile, response, or checkpoint mutation

#### Scenario: Subsequent dispatches do not reproject policy
- **WHEN** a scripted start has produced an available Bundle and the adapter later
  dispatches resume, refine, status, or cancel
- **THEN** the later transport context contains only that action's existing bounded
  input and does not supply a non-interactive policy as a new lifecycle authority

#### Scenario: Policy observations remain presentation-only
- **WHEN** a record-bearing lifecycle result includes either bounded policy observation
  marker in its checkpointed execution trace
- **THEN** the module accepts the trace as a safe observation and does not derive a
  lifecycle result, graph route, profile, or checkpoint mutation from the marker

### Requirement: Public lifecycle projection distinguishes committed state from pending input

The public lifecycle projection SHALL retain the existing phase/pending-input
distinction, but both committed and pending facts are derived from the selected
Bundle-local Research State. The graph interrupt remains the delivery artifact; it is
not a durable source independent of that State. A projection never includes a path,
raw context, or external-checkpoint data and cannot override Bundle lifecycle truth.
(`RER-002`)

#### Scenario: Pending projection cannot survive Bundle loss as authority
- **WHEN** a presentation cache still contains an earlier pending-input projection after
  the selected Bundle is deleted
- **THEN** the next status/control result is unavailable and the cache cannot re-present
  a legal resume action

### Requirement: Failures are safe, categorized, and diagnosable

The existing source-owned closed failure categories, safe diagnostic references,
redaction, and legal-next-action guarantees SHALL remain unchanged. A record-bearing
observation is correlated only from a shared typed Bundle lifecycle result and, where
valid, its `bundle_id`; it cannot bind a `research_id`, session, path, or checkpoint as
a replacement Run authority. A supported retained diagnostic artifact is readable and
presentable only from an available Bundle. Its safe category, opaque reference, recovery
facts, and legal action remain fields of the typed terminal lifecycle result, not a read
of a diagnostic artifact. After Bundle loss, no external diagnostic, Journal, or Support
Handoff is a supported diagnostic reader or participant presentation source; a later
inspection or lifecycle result follows its shared unavailable outcome. This requirement
does not assert that physical storage contains no residual bytes after deletion. Such
bytes, if any, are outside the supported diagnostic contract and cannot establish a
supported retained record, reader, or presentation. (`RER-003`, `RER-009`)

#### Scenario: Diagnostic fallback does not create a live Run projection
- **WHEN** a Bundle becomes unavailable after a safe provider diagnostic was associated
  with its terminal lifecycle result
- **THEN** presentation returns the shared unavailable outcome and its legal next
  action without reading or presenting an external diagnostic artifact, Journal, or
  Support Handoff; it does not infer a retained artifact from a previously typed terminal
  category or opaque reference

### Requirement: Shared failure updates expose bounded provider diagnostics and recovery disposition

`ResearchState.latest_incident` SHALL remain the owner of terminal provider-recovery
facts. Its frozen, extra-forbid `ProviderRecoveryProjection` from
`domain/run_experience.py` SHALL contain the retry-eligible trigger category, its
required safe `ProviderObservation`, trigger invocation ordinal, bridge/model-invocation
count, automatic-retry count, and disposition.
`TerminalIncidentProjection` SHALL retain that projection plus the final call's
optional safe `ProviderObservation` whenever the bridge supplied one, including a
non-retryable direct public HTTP response. A provider-diagnostic terminal is a blocked
incident with either projection or final safe observation. `ResearchRunExperience` SHALL
always copy a supplied final safe provider observation with the exact final failure
category and phase into `RunFailure`. Each validated observation, including its optional
`configured_service_label` and `configured_endpoint_authority`, SHALL be copied
unchanged rather than normalized, reconstructed, or inferred at this layer. When the
validated incident also contains recovery data, it SHALL copy the recovery projection;
its nested recovery projection preserves the trigger observation even when the final
category is not provider-specific. For every provider-diagnostic terminal, it SHALL
copy the pre-derived diagnostic reference. It SHALL not reconstruct any of them from the
event journal.

`RunFailure` SHALL expose an optional closed `recovery_action` with the sole value
`fresh_start`. It SHALL be `fresh_start` exactly for `exhausted` and
`retry_not_started_budget_consumed`, whose final categories remain retry-eligible
transient provider failures, and absent for `retry_followed_by_terminal_failure`.
When `recovery_action=fresh_start`, its human-readable `next_action` SHALL be congruent
explanatory text only, and CLI/TUI SHALL not render it as a second action. `retryable`
means a distinct new start may be attempted and never means the failed graph can resume.
Every current terminal `RunFailure` SHALL carry `diagnostic_location` as exactly one of
`bundle_journal` or `unavailable`. A provider-diagnostic terminal SHALL carry its
diagnostic reference; `research_record_created` SHALL be true only for verified
`bundle_journal` publication and false for `unavailable`. A current non-provider
terminal with no published diagnostic SHALL report `diagnostic_location=unavailable`
without inventing a diagnostic reference. The shared `Terminal` update is the only
source used by CLI and TUI; neither opens a retained bundle or uses an observation as
lifecycle authority. A matching retained-session inspection command is a read-only
diagnostic observation, not a `recovery_action`, retry, resume, or competing next
action.

A persisted or public terminal result that lacks `diagnostic_location` SHALL be rejected
before participant projection, even when it is explicitly registered for the cutover.
There is no migration route that guesses `bundle_journal`, synthesizes `unavailable`,
uses an external diagnostic/Journal/Support Handoff, or derives resume/retry truth from
that absence. Registration may record its rejection disposition only. (`RER-009`)

The frozen provider-recovery projection SHALL permit only these valid combinations:

- every tuple: trigger category is `provider.timeout` or `provider.unavailable`.
  A timeout trigger has `no_response` and no HTTP status; an unavailable trigger has
  either `no_response` and no HTTP status or `http_response` with one of `408`, `429`,
  `500`, `502`, `503`, or `504`. If a final provider observation is present, the final
  category is `provider.timeout`, `provider.unavailable`, or
  `provider.authentication_failed` and uses that same timeout/unavailable pairing or,
  for authentication, `http_response` with `401` or `403`. For any other final
  category, an optional final observation is only a direct public `http_response`
  with its bounded non-retryable status. No observation is fabricated for a final
  branch that did not supply one;
- `exhausted`: `model_attempts=2`, `automatic_retries=1`, trigger ordinal one, and a
  retry-eligible transient final category;
- `retry_followed_by_terminal_failure`: `model_attempts=2`,
  `automatic_retries=1`, trigger ordinal one, and a non-transient or structured-output
  final category; or
- `retry_not_started_budget_consumed`: `model_attempts=2`,
  `automatic_retries=0`, trigger ordinal two, and a retry-eligible transient final
  category after a structured-output repair consumed the other visit slot.

Recovery facts SHALL be absent when no retry-eligible transient provider result was
observed. For every provider-diagnostic terminal, `ResearchRunExperience` SHALL put the
terminal incident reference unchanged into `RecordBearingLifecycleFact` before session
publication, together with the copied retained recovery summary when present. It SHALL
validate the terminal incident and construct that fact before calling the retained
publisher; it SHALL not enter a generic diagnostic path that creates a new reference.
If the retained publisher reports availability, it SHALL return a terminal
`RunSessionView` whose `terminal_diagnostic_ref` exactly matches the incident reference,
replace any stale suspended-session projection, and set
`diagnostic_location=bundle_journal`. Otherwise it SHALL set
`diagnostic_location=unavailable` and SHALL NOT persist, read, or present the reference
through a support journal, external diagnostic, external Journal, or Support Handoff.
Only after that publication outcome is known shall it construct the final shared
`RunFailure` with its typed location and `research_record_created` truth. It SHALL never
derive a replacement reference. Returned-only `Working` updates SHALL not add or imply
an in-flight retry state.

#### Scenario: Exhausted timeout has an actionable bounded projection
- **WHEN** a blocked HITL1 terminal incident reports `provider.timeout`, two attempts,
  and one exhausted retry
- **THEN** the resulting safe terminal update exposes those exact bounded facts and
  its `fresh_start` action with the existing diagnostic reference and its actual
  diagnostic location, without provider exception text, payload, URL, or question

#### Scenario: Fresh start does not introduce a competing next action
- **WHEN** an exhausted or repair-slot-budget-consumed terminal has
  `recovery_action=fresh_start`
- **THEN** its `next_action` is congruent explanatory text rather than a different
  action, and the shared terminal exposes only the closed fresh-start action

#### Scenario: Retry history survives a different final category
- **WHEN** a first HITL1 timeout causes its automatic retry and that second invocation
  ends in `output.structured_invalid` or provider authentication failure
- **THEN** the terminal update retains the final category and exposes
  `retry_followed_by_terminal_failure` with two model attempts and one automatic retry
  rather than hiding that retry history, and leaves `recovery_action` absent

#### Scenario: Repair-slot transient offers a distinct new start
- **WHEN** a malformed first HITL1 output uses the repair slot and that repair
  invocation ends in `provider.unavailable`
- **THEN** the terminal update exposes
  `retry_not_started_budget_consumed`, two model attempts, zero automatic retries,
  and the closed `fresh_start` action without claiming that the failed graph resumes

#### Scenario: Failed session publication keeps the original diagnostic reference
- **WHEN** a blocked provider-recovery incident has an opaque diagnostic reference but
  retained-session publication is unavailable
- **THEN** the terminal update carries that same reference, reports
  `diagnostic_location=unavailable`, and does not write, read, or present an external
  diagnostic while preserving the original terminal category and legal next action

#### Scenario: Current non-provider terminal records unavailability explicitly
- **WHEN** a current terminal has no provider diagnostic or verified Journal publication
- **THEN** its terminal result carries `diagnostic_location=unavailable` and does not create a diagnostic reference, retry, or resume action

#### Scenario: Legacy non-provider failures do not invent provider history
- **WHEN** a current non-provider terminal has no recovery facts or final safe provider observation
- **THEN** its result preserves the absent provider/retry facts, records `diagnostic_location=unavailable`, and does not fabricate a diagnostic reference, retry, or guessed record location

#### Scenario: Missing diagnostic location is rejected before participant projection
- **WHEN** a persisted or public terminal result lacks `diagnostic_location`
- **THEN** the reader rejects it before CLI, TUI, machine participant, lifecycle, or Journal projection and does not infer a record location or legal recovery

#### Scenario: Non-retryable HTTP observation survives without recovery history
- **WHEN** a blocked terminal incident has a safe final `400` HTTP observation but no
  retry-eligible transient provider result
- **THEN** the terminal update copies that final observation and its final category,
  leaves recovery projection, retry counts, and `recovery_action` absent, and retains
  one exact diagnostic reference plus its actual diagnostic location

#### Scenario: Stale suspended session cannot satisfy terminal inspection
- **WHEN** a provider-diagnostic terminal has a retained session for the same research
  id but that view lacks or has a different `terminal_diagnostic_ref`
- **THEN** the shared terminal does not treat it as the terminal record or report
  `bundle_journal` inspection availability for that diagnostic reference

#### Scenario: Returned-only waiting does not fabricate retry progress
- **WHEN** a real dispatch has not returned a lifecycle result while HITL1 may be
  awaiting a provider call or its bounded backoff
- **THEN** the shared `Working` update reports only its existing local wait facts and
  does not claim that a retry has started, completed, or remains available

### Requirement: First-run prompts and waiting states explain user intent truthfully

The shared run experience SHALL perform non-network preflight before an interactive
question is collected or graph construction begins. It SHALL report the selected
real/fake mode, model and web-tool readiness, local environment problems, and that a
standalone demo retains an inspectable local bundle only after a record-bearing result
but does not promise cross-process execution recovery. Preflight failure creates no run
reference or retained bundle.

HITL-1 presentation SHALL decode only the recognized versioned research-brief context
into goal, proposed scope, missing information, supported values, and a concise answer
example. Malformed or unknown context SHALL use a safe generic scope request and SHALL
not print machine JSON. HITL2 SHALL be projected only as graph-owned autonomous phase
progress from a verified trace/result; the run experience SHALL NOT render an HITL2
decision prompt, route menu, Answer action, or pending-input recovery.

Working state SHALL show the dispatch action, elapsed local time, and actual observed
activity only. With no stream writer it SHALL identify delivery as `returned_only` and
say it is waiting for the lifecycle result. It SHALL not emit a percentage, infer a
node phase, or claim model/web progress before a valid returned event or result proves
it. (`RER-004`)

#### Scenario: Preflight does not promise a session before one exists
- **WHEN** a real standalone demo has passed preflight but has not received a
  record-bearing lifecycle result
- **THEN** it explains that a local bundle becomes inspectable only after a run is
  identified and does not display an inspect command or promise restart recovery

#### Scenario: Missing prerequisite stops before the user supplies a question
- **WHEN** a real standalone demo lacks a required model or web-search prerequisite
- **THEN** preflight identifies the missing prerequisite, its purpose, and the next action before the question prompt, model request, or graph construction

#### Scenario: HITL-1 is not a truncated machine object
- **WHEN** a valid versioned HITL-1 brief is returned
- **THEN** the user sees a semantic research-scope prompt with the known proposed values and missing fields rather than a truncated JSON line or an internal lifecycle/gate label

#### Scenario: Waiting makes no false progress claim
- **WHEN** a lifecycle dispatch has begun but no graph event or result has been observed
- **THEN** the entry point shows only elapsed local waiting and does not advance its pipeline tracker or claim that any graph node completed

#### Scenario: Autonomous HITL2 creates no second prompt
- **WHEN** a verified returned trace records HITL2 after the accepted Wave2 path
- **THEN** the shared run experience projects phase progress without `AwaitingInput`,
  an Answer action, or any advertised internal route

### Requirement: Verification protects the production-shaped first interaction

The change SHALL include deterministic tests at the run-experience Interface and a
`SCRIPTED_REAL_WORKFLOW` using the real bootstrap, real HITL-1, interrupt,
checkpointer, and reflected lifecycle projection with replayed external dependencies.
It SHALL cover first HITL-1 suspension, HITL-1 follow-up, autonomous HITL2 without a
second pending input, status, trace repetition/divergence, malformed wire values,
source failure categories, redaction, diagnostic records, cancellation outcome
distinction, and CLI/TUI shared adapter fixtures.

A stubbed top-level lifecycle result may supplement adapter tests but SHALL NOT be the
only proof of the first real suspension. Credentialed provider/tool acceptance is
supplemental live evidence and SHALL preserve only redacted category/reference data.
(`RER-005`)

#### Scenario: A favorable stub cannot hide the phase-lag regression
- **WHEN** a test suite exercises the standalone first interaction
- **THEN** at least one deterministic collected test reaches the production interrupt projection with checkpoint phase `bootstrap` and pending phase `hitl1`, so a fixture that manually sets phase `hitl1` cannot be the sole regression proof

#### Scenario: A synthetic HITL2 prompt cannot be production-shaped evidence
- **WHEN** CLI, TUI, or run-experience adapter tests need a choice-mode pending input
- **THEN** they use the current typed HITL1 choice contract, while autonomous HITL2
  evidence proves graph continuation without constructing an HITL2 `AwaitingInput`

### Requirement: Shared run updates expose safe Bundle inspection observations

Shared run updates SHALL expose a bounded inspection observation only after the Bundle
lifecycle boundary returns an available selected Bundle result. The view uses the
opaque `bundle_id`, availability/retention fact, durability fact, and at most one
closed observation failure; it contains no session reference, host path, checkpoint
payload, or lifecycle authority. Publication/inspection failure cannot replace a valid
pending or terminal result, retry a lifecycle action, or alter Bundle-local State.
(`RER-006`)

#### Scenario: Inspection observation cannot revive a lost Bundle
- **WHEN** a previously published inspection observation refers to a deleted Bundle
- **THEN** both presentation adapters suppress control/inspection actions and display the
  typed unavailable result

### Requirement: Shared run updates project bounded intake feedback and observed run state

The existing bounded HITL1 feedback and returned-only progress guarantees remain
unchanged. Every shared update SHALL use an opaque `bundle_id` only where it is present
in the typed lifecycle result; it SHALL not expose or derive a `research_id`, session
reference, checkpoint key, or Bundle path. (`RER-007`)

#### Scenario: Shared update does not expose retired identity
- **WHEN** a lifecycle update is rendered for an available or unavailable Run
- **THEN** the adapter receives only its permitted `bundle_id` and typed outcome, not a
  conversation-derived identity or storage locator

### Requirement: Terminal incidents preserve Wave0 diagnosis separately from route code

For a terminal Wave0 work exhaustion, the frozen terminal-incident and safe run-update
contracts SHALL carry an optional closed exhausted-work diagnosis aggregate separately
from the existing `RunFailureCode.RESEARCH_BLOCKED` route code. The value SHALL be one
per-attempt worker category from `WFC-001` or `mixed`; absent legacy state remains
unavailable. Presentation and session publication SHALL consume only this validated
field and SHALL NOT infer it from exception text, event ordering, model/tool bodies, or
raw checkpoint state. (`RER-008`)

#### Scenario: Blocked route remains stable while diagnosis is visible
- **WHEN** Wave0 exhausts work with a `structured_output` aggregate
- **THEN** the terminal route code remains `research.blocked` and the safe terminal
  projection separately exposes `structured_output`

#### Scenario: Legacy terminal remains honest
- **WHEN** a legacy blocked checkpoint has no worker diagnosis aggregate
- **THEN** presentation marks the optional diagnosis unavailable and does not invent a
  category

### Requirement: Shared terminal outcomes retain incident truth across all real phases

`ResearchRunExperience` SHALL derive a terminal or fault presentation only from the
typed lifecycle result and its checkpointed terminal incident or controller-derived
worker diagnosis. For every retained known incident it SHALL expose the safe category,
phase, certainty, observed recovery disposition, opaque diagnostic reference,
durability, and exactly one legal next action. When the incident has no supplied
diagnostic reference, it SHALL use the existing shared diagnostic-publication seam to
derive that reference only from typed terminal facts. It SHALL preserve the closed
`provider.usage_unavailable`, `budget.exhausted`, and `policy.denied` categories in
`RunFailure` and use category-specific safe copy for them; it SHALL not display the
tool-execution message or tool-service next action for any of those categories. It
SHALL not downgrade a known incident to generic `research.blocked`, invent provider
history for an unknown failure, or offer retry/resume contrary to the lifecycle
contract.

#### Scenario: A topic-planning timeout has the same typed outcome in every adapter
- **WHEN** lifecycle returns a blocked topic-planning terminal incident for an
  exhausted provider timeout
- **THEN** the shared update supplies its category, phase, bounded recovery facts,
  diagnostic reference, durability truth, and one legal action to both CLI and TUI
  adapters

#### Scenario: A zero-tool usage stop is not presented as a tool failure
- **WHEN** lifecycle returns a blocked topic-planning terminal incident with
  `provider.usage_unavailable`, `budget.exhausted`, or `policy.denied`
- **THEN** the shared update preserves that exact category, phase, and certainty;
  derives or preserves its opaque diagnostic reference only from typed terminal facts;
  and renders its category-specific safe message and legal action without a provider
  retry, resume action, or tool-failure wording

#### Scenario: A closed stop after provider recovery preserves historical recovery only
- **WHEN** lifecycle returns a `retry_followed_by_terminal_failure` topic-planning
  incident whose final code is `provider.usage_unavailable`, `budget.exhausted`, or
  `policy.denied`
- **THEN** the shared update preserves the final closed category and the actual prior
  recovery history, derives or preserves its opaque diagnostic reference only from
  typed terminal facts, and offers no fresh-start or resume action for that final
  non-provider category

#### Scenario: A legacy blocked record remains honestly incomplete
- **WHEN** a readable legacy terminal has no retained incident
- **THEN** the shared update labels it as an unclassified blocked result without
  claiming a provider timeout, retry, recovery, or a newly closed node-agent stop that
  was not observed

### Requirement: Shared prompt view projects typed interaction facts and visible controls

ResearchRunExperience SHALL construct HITL1 proposal subject, material constraints,
feedback, and visible controls from the pending request's typed controller-owned
interaction projection, not by parsing `HumanInputRequest.context`. It SHALL retain a
safe legacy-context fallback for checkpoints that lack that projection. PromptView
shall expose only adapter-safe visible controls and SHALL not expose action ids; action
ids remain internal `HumanInputRequest` and verifier transport facts. (`RER-010`)

#### Scenario: Follow-up feedback retains its control in every adapter
- **WHEN** HITL1 returns semantic failure or clarification feedback
- **THEN** CLI and TUI receive the same subject, feedback, and current-proposal control
  through PromptView without decoding context or action ids

### Requirement: Runtime resolves generic visible-control selection under current state

ResearchRunExperience SHALL accept `SelectControlRun(control_id)` and, only against its
current pending request and displayed PromptView, bind it to the corresponding
advertised typed response. It SHALL reject a missing, stale, or unadvertised control
without constructing a response message. Existing direct typed `AnswerRun` remains
compatible for trusted transport callers. (`RER-011`)

#### Scenario: CLI control number does not become a magic phrase
- **WHEN** a CLI adapter submits the current numbered control selection
- **THEN** ResearchRunExperience performs the current trusted binding and no adapter
  converts a phrase such as `adopt suggestion` into an action id

### Requirement: Provider terminal diagnostic location is verified publication truth

For a blocked terminal, `ResearchRunExperience` SHALL report
`diagnostic_location=bundle_journal` and `research_record_created=true` only when
the returned retained-session projection verifies that the exact terminal
diagnostic reference was published in its available Bundle. This verified-publication
rule SHALL apply to every blocked terminal that carries a diagnostic reference —
provider-diagnostic terminals and gate/controller blocked terminals alike; the
availability truth is a property of the published reference, not of the incident's
failure class. When that verification is absent or the Bundle publisher cannot
publish the record, it SHALL report `diagnostic_location=unavailable` and
`research_record_created=false`. It SHALL NOT use an exact-reference support journal
fallback or any external diagnostic, Journal, or Support Handoff as a supported
reader or participant presentation. The shared terminal SHALL preserve the original
category, phase, recovery disposition, trigger/final timeout origins, and lifecycle
authority; it SHALL not create a replacement reference or turn inspection into
retry/resume control. A blocked terminal whose diagnostic reference is verified as
published SHALL never render as journal-unavailable in any shared participant
surface. This requirement does not assert secure erasure or the absence of
physical residual bytes after Bundle loss. (`RER-009`)

#### Scenario: Verified bundle record enables session-bundle location
- **WHEN** a provider terminal's returned session projection verifies the same opaque
  diagnostic reference as the terminal incident
- **THEN** the shared terminal reports `bundle_journal` and record-created truth

#### Scenario: A gate-blocked terminal reports its published journal truth
- **WHEN** a gate-derived blocked incident carries a diagnostic reference and the
  retained-session projection verifies that exact reference as published in the
  available Bundle
- **THEN** the shared terminal reports `diagnostic_location=bundle_journal` and
  `research_record_created=true`, and CLI/TUI journal-availability rendering shows
  the journal as created rather than unavailable

#### Scenario: Stale reference cannot qualify a bundle as diagnostic storage
- **WHEN** a session is available but cannot verify the terminal's exact diagnostic
  record or carries a different reference
- **THEN** the shared terminal does not report `bundle_journal`, reports
  `unavailable`, and performs no external diagnostic fallback, regardless of the
  incident's failure class

#### Scenario: Safe timeout origins reach all shared participants in their roles
- **WHEN** a verified provider terminal carries a bridge-budget retry trigger and a
  provider-SDK-timeout final observation
- **THEN** the shared terminal exposes each exact closed origin through its existing
  trigger/final observation role for CLI/TUI and machine consumers without exposing raw
  diagnostic material

#### Scenario: Support-journal fallback retains observed origins
- **WHEN** a provider terminal carrying closed trigger/final timeout origins cannot
  verify Bundle diagnostic publication
- **THEN** the shared terminal reports `unavailable`, preserves the terminal's existing
  lifecycle authority and legal action, and neither writes nor reads an external
  diagnostic, Journal, or Support Handoff

### Requirement: Shared confirmation prompts display all material proposal constraints

When a typed complete HITL1 interaction presents a current proposal, the shared
`PromptView` SHALL render a bounded, safe representation of every material proposal
constraint before a person can accept it: depth, audience, format, cost tolerance,
time budget, every must-answer question, non-empty scope boundaries, non-empty custom
notes, comparison subjects when required, and the accepted output language. The
projection SHALL have capacity for at least seventeen labeled lines, derived from the
current maximum of eight must-answer questions plus the five scalar dimensions and
four remaining material values. It SHALL not silently discard a typed field through a
global line cap or a shorter per-value display cap; it may normalize whitespace and
control characters within the existing typed field bounds. The projection SHALL be
derived from the existing typed interaction contract, retain its current visible
controls, and remain compatible with the existing legacy-context fallback. It SHALL
not expose raw model output, raw user text, hidden action ids, or new lifecycle
authority. (`RER-012`)

#### Scenario: A source-restricted proposal is visible before confirmation
- **WHEN** HITL1 presents a complete typed proposal whose scope boundary limits
  research to Python official documentation and whose output language is Chinese
- **THEN** the shared confirmation prompt visibly includes both constraints alongside
  its existing current-proposal control before the Primary User confirms or revises it

#### Scenario: Material values do not disappear from a revised proposal
- **WHEN** a complete revised typed proposal has multiple must-answer questions,
  comparison subjects, scope boundaries, and custom notes
- **THEN** the shared prompt preserves a labeled safe line for every material value,
  including all eight permitted must-answer questions and the full normalized typed
  scope/note values, and leaves the interaction/control identity unchanged

### Requirement: Shared run experience projects Bundle-owned outcomes and legal actions

The runtime-owned run-experience module SHALL derive human-readable and AI-consumable
run updates from the shared typed Bundle lifecycle result. It SHALL distinguish active,
awaiting-input, ended, conflict/ambiguous, and unavailable outcomes without exposing a
checkpoint key, session reference, host path, raw exception, or derived `research_id`.
For each outcome it SHALL expose only the legal next action supplied by the lifecycle
contract; presentation text SHALL not authorize, retry, or recover a Run. (`RER-013`)

#### Scenario: Unavailable result has one truthful next action
- **WHEN** the lifecycle result reports an unavailable Bundle
- **THEN** the shared experience identifies that the Run cannot be resumed and offers a fresh independent Run or permitted observation only

### Requirement: Active Bundle results remain safe non-terminal projections

When a shared typed Bundle lifecycle result identifies an available active Bundle,
including a different `start` denied with `active_bundle_exists`,
`ResearchRunExperience` SHALL return a safe `research.active` `Fault` rather than
constructing a terminal outcome or reporting a protocol fault. The fault SHALL retain
only the selected result's bounded Bundle identity, known phase, durability, and
available observation projection. It SHALL not infer a pending input, resume the
Bundle, cancel it, change its State, or claim that the graph has stopped. Its next
action SHALL direct the consumer to query or explicitly cancel the selected Bundle
through lifecycle control. (`RER-014`)

#### Scenario: A different start encounters an active Bundle

- **WHEN** a `start` dispatch returns the typed `active_bundle_exists` result for an
  available Bundle
- **THEN** the shared experience returns a `research.active` fault with that Bundle's
  safe snapshot and does not report `protocol.invalid_result` or present a terminal
  completion state

#### Scenario: Status observes an active Bundle

- **WHEN** a status dispatch returns an available active Bundle result
- **THEN** the shared experience returns the same bounded `research.active` fault and
  does not infer a resume prompt or a terminal outcome
