> req: RER-003, RER-009

## MODIFIED Requirements

### Requirement: Failures are safe, categorized, and diagnosable

The runtime SHALL classify failures at their source into the existing closed
run-failure registry. A user-visible `Fault` or terminal outcome SHALL identify the
safe category, known phase when available, certainty, a concrete next action,
retryability, and an opaque diagnostic reference when a record exists; it SHALL never
print only "retry". Unknown exceptions remain `internal-unexpected`, and a terminal
checkpoint retains only the existing compact safe incident projection.

Before a record-bearing bind exists, a warranted standalone-demo diagnostic record
SHALL remain in the documented project-relative support journal. A bind requires a
validated returned result with non-null research id, status, phase, and generation; an
id alone is insufficient. After bind, including a later local transport fault while the
session remains bound, a warranted diagnostic record SHALL normally be bounded and
redacted at `diagnostics/records.jsonl` beneath that retained bundle. Each record
contains only opaque reference, time, action/phase, closed category, certainty, and a
fingerprint derived exclusively from those closed safe fields plus run mode. It SHALL
not incorporate raw exception/message text, prompt or answer text, provider content,
URLs, paths, credentials, or a hash of any such value.

The sole exception is a provider-diagnostic terminal whose validated retained-session
publication is unavailable. A provider-diagnostic terminal is blocked and carries
either a recovery projection or a final safe `ProviderObservation`. It SHALL preserve
the already-derived terminal diagnostic reference and attempt the documented
project-relative support-journal publication with that exact reference; if that write
also fails, the terminal outcome SHALL report the record as unavailable. Neither
outcome may claim that a retained-bundle record or research record was created. The
typed provider-diagnostic location rules remain owned by `RER-009`; this exception
never authorizes a new diagnostic reference or lets a journal projection decide
lifecycle control. (`RER-009`)

After `ResearchRunExperience` has returned a validated `AwaitingInput` HITL2 choice
prompt, it SHALL recognize a recoverable invalid choice only for the result of its
own immediately preceding `resume` dispatch. The decoded result SHALL have action
`resume`, code `response_invalid`, the current research ID, an empty execution trace,
and no bundle directory, status, phase, generation, request/pending projection, or
terminal projection. The experience SHALL also still hold the validated HITL2 choice
request and the complete prior `AwaitingInput` update. The denial SHALL be an ordinary
mapping result, not a `Command` carrying a new human-input artifact; the cached
snapshot pending projection, prompt, and request SHALL still agree on request ID and
choice mode. Before ordered trace validation or trace mutation, it SHALL return an
immutable copy of that update with `rejection_category=choice_input_invalid` and an
empty trace delta; it SHALL NOT reconstruct its snapshot from the denial or current
mutable fields.

This re-prompt path SHALL not decode or display raw rejected input, accept a route,
publish a session fact, change durability, mutate the previously verified trace,
create checkpoint state, invoke graph nodes, or create a diagnostic record. A later
canonical response SHALL continue through normal lifecycle transport and graph-owned
human-input validation.

Any denial with an unexpected outbound action, result action, code, research ID,
trace, record-bearing field, missing cached complete update/request, non-choice
prompt, new request artifact, malformed wire shape, or correlation error SHALL retain
the normal fail-closed protocol/failure handling. In particular, `response_mismatch`
SHALL NOT be re-presented as a user-correctable choice prompt. (`RER-003`, `RER-009`)

#### Scenario: A post-bind diagnostic is discoverable with its retained run
- **WHEN** a record-bearing validated lifecycle result binds a research id and then a
  classified terminal or local failure is projected while retained publication is
  available
- **THEN** its opaque diagnostic reference is retained under that bundle's
  `diagnostics/records.jsonl`, while preflight/no-record failures remain only in the
  global support journal

#### Scenario: Provider-diagnostic fallback never impersonates a retained record
- **WHEN** a bound provider-diagnostic terminal cannot publish its retained
  session record
- **THEN** the exact incident reference is written to the support journal when possible
  and otherwise reported unavailable, without creating a new reference or claiming a
  retained bundle or research record

#### Scenario: Changing a raw source cannot change the persisted fingerprint
- **WHEN** two otherwise identical classified failures carry distinct sentinel
  exception messages, prompts, answers, paths, or provider bodies
- **THEN** their diagnostic fingerprint is identical and neither sentinel nor a
  source-dependent digest appears in the record

#### Scenario: Model configuration failure is actionable without leaking configuration
- **WHEN** the real brief cannot start because no usable model configuration is available
- **THEN** the user sees that model configuration is missing, why it is required, the
  next configuration action, and a diagnostic reference; no key name value, path,
  exception body, provider request, or raw stack is displayed

#### Scenario: Unknown implementation failure is not falsified
- **WHEN** an unrecognized exception escapes a lifecycle source
- **THEN** the outcome category is `internal-unexpected` with unknown certainty and a
  safe support action, not checkpoint-inconsistent or a false provider diagnosis

#### Scenario: Invalid HITL2 choice retains the same safe suspension
- **WHEN** a validated HITL2 `AwaitingInput` prompt has a non-empty verified trace
  and its subsequent resume returns a same-research `response_invalid` denial with
  no record-bearing lifecycle state
- **THEN** the shared experience returns `AwaitingInput` for the same request and
  choices with closed invalid-choice feedback, preserves the prior trace and safe
  snapshot, and does not return `protocol.invalid_result`

#### Scenario: A later valid choice resumes through graph authority
- **WHEN** a recoverable invalid choice has been re-presented and the user later
  submits an advertised option ID
- **THEN** the experience dispatches the later response normally and reports only
  the graph-returned trace/result without treating the prior invalid answer as a
  graph transition

#### Scenario: Correlation or wire anomalies remain fail-closed
- **WHEN** a purported invalid-choice denial follows a non-`resume` dispatch, has a
  different research ID, a non-choice cached prompt, a non-empty trace,
  `response_mismatch` code, record-bearing fields, a new request artifact, or
  malformed control data
- **THEN** the shared experience returns the existing safe non-retryable fault path
  and does not re-present a cached prompt

## ADDED Requirements

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
For every provider-diagnostic terminal, `diagnostic_location` SHALL be exactly one of
`session_bundle`, `support_journal`, or `unavailable` and its diagnostic reference SHALL
be present. `diagnostic_location` SHALL be absent for legacy terminals with neither
recovery projection nor final safe provider observation. `research_record_created` SHALL
be true only for `session_bundle` publication and false for `support_journal` or
`unavailable`. The shared `Terminal` update is the only source used by CLI and TUI;
neither opens a retained bundle or uses an observation as lifecycle authority. A
matching retained-session inspection command is a read-only diagnostic observation, not
a `recovery_action`, retry, resume, or competing next action.

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
validate the terminal incident and construct that fact before calling either publisher;
it SHALL not enter the generic diagnostic path that creates a new reference for this
terminal. If the retained publisher reports availability, it SHALL return a terminal
`RunSessionView` whose `terminal_diagnostic_ref` exactly matches the incident reference,
replace any stale suspended-session projection, and set
`diagnostic_location=session_bundle`. Otherwise it SHALL ask the support journal to
persist the exact existing reference and set `support_journal` or `unavailable`
according to that write. Only after that publication outcome is known shall it construct
the final shared `RunFailure` with its typed location and `research_record_created`
truth. It SHALL never derive a replacement reference. Legacy and non-provider incidents
SHALL remain valid with the new recovery and diagnostic-location fields absent.
Returned-only `Working` updates SHALL not add or imply an in-flight retry state.
(`RER-009`)

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
- **THEN** the terminal update carries that same reference, writes it to the support
  journal when possible, and reports `diagnostic_location=support_journal` or
  `unavailable` without deriving a second reference or claiming that a retained
  research record was created

#### Scenario: Legacy non-provider failures do not invent provider history
- **WHEN** a blocked incident is legacy authentication, configuration, tool, structured
  output, or graph failure with neither recovery facts nor a final safe provider
  observation
- **THEN** the terminal update leaves bridge/model-invocation and retry disposition absent
  along with `recovery_action` and `diagnostic_location`, rather than displaying a
  zero-valued or fabricated retry or a guessed record location

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
  `session_bundle` inspection availability for that diagnostic reference

#### Scenario: Returned-only waiting does not fabricate retry progress
- **WHEN** a real dispatch has not returned a lifecycle result while HITL1 may be
  awaiting a provider call or its bounded backoff
- **THEN** the shared `Working` update reports only its existing local wait facts and
  does not claim that a retry has started, completed, or remains available
