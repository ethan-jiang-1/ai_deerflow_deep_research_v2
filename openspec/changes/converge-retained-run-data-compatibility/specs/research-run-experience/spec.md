> req: RER-009

## MODIFIED Requirements

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
