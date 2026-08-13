## MODIFIED Requirements

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
For every provider-diagnostic terminal, `diagnostic_location` SHALL be exactly one of
`bundle_journal` or `unavailable` and its diagnostic reference SHALL be present.
`diagnostic_location` SHALL be absent for legacy terminals with neither recovery
projection nor final safe provider observation. `research_record_created` SHALL be true
only for `bundle_journal` publication and false for `unavailable`. The shared `Terminal`
update is the only source used by CLI and TUI; neither opens a retained bundle or uses
an observation as lifecycle authority. A matching retained-session inspection command
is a read-only diagnostic observation, not a `recovery_action`, retry, resume, or
competing next action.

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
derive a replacement reference. Legacy and non-provider incidents SHALL remain valid
with the new recovery and diagnostic-location fields absent. Returned-only `Working`
updates SHALL not add or imply an in-flight retry state. (`RER-009`)

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
  `bundle_journal` inspection availability for that diagnostic reference

#### Scenario: Returned-only waiting does not fabricate retry progress
- **WHEN** a real dispatch has not returned a lifecycle result while HITL1 may be
  awaiting a provider call or its bounded backoff
- **THEN** the shared `Working` update reports only its existing local wait facts and
  does not claim that a retry has started, completed, or remains available

### Requirement: Provider terminal diagnostic location is verified publication truth

For a provider-diagnostic terminal, `ResearchRunExperience` SHALL report
`diagnostic_location=bundle_journal` and `research_record_created=true` only when the
returned retained-session projection verifies that the exact terminal diagnostic
reference was published in its available Bundle. When that verification is absent or
the Bundle publisher cannot publish the record, it SHALL report
`diagnostic_location=unavailable` and `research_record_created=false`. It SHALL NOT use
an exact-reference support journal fallback or any external diagnostic, Journal, or
Support Handoff as a supported reader or participant presentation. The shared terminal
SHALL preserve the original category, phase, recovery disposition, trigger/final timeout
origins, and lifecycle authority; it SHALL not create a replacement reference or turn
inspection into retry/resume control. This requirement does not assert secure erasure or
the absence of physical residual bytes after Bundle loss. (`RER-009`)

#### Scenario: Verified bundle record enables session-bundle location
- **WHEN** a provider terminal's returned session projection verifies the same opaque
  diagnostic reference as the terminal incident
- **THEN** the shared terminal reports `bundle_journal` and record-created truth

#### Scenario: Stale reference cannot qualify a bundle as diagnostic storage
- **WHEN** a session is available but cannot verify the terminal's exact diagnostic
  record or carries a different reference
- **THEN** the shared terminal does not report `bundle_journal`, reports
  `unavailable`, and performs no external diagnostic fallback

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
