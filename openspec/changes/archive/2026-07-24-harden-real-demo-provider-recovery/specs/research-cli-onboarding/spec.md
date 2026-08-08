> req: REC-006

## ADDED Requirements

### Requirement: Real CLI reports provider diagnostics and honest fresh-start guidance

For every shared provider-diagnostic terminal, the standalone real CLI and TUI SHALL
render only the shared `Terminal` update: its `RunFailure` supplies final category,
known phase, final-category next-action explanation, safe final observation when
present, diagnostic reference, typed diagnostic location, and
`research_record_created` truth, while its snapshot supplies returned durability and
the retained-session projection. A provider-diagnostic terminal has a final safe
provider observation and/or provider-recovery facts. When recovery facts are present,
the adapters SHALL additionally render bridge/model invocations used, automatic retries
used, disposition, and closed `recovery_action`. They SHALL render an inspect command
only when `diagnostic_location=session_bundle`, the same `Terminal.snapshot` contains
an available retained session for that terminal's research id, and that session's
`terminal_diagnostic_ref` exactly matches `RunFailure.diagnostic_ref`; a missing,
stale, unavailable, or differently correlated session projection produces no inspect
command and cannot change the typed location. A rendered inspect command SHALL be
labelled as read-only diagnosis and SHALL not be presented as a recovery, retry, resume,
or next action. They SHALL not inspect a bundle, infer a retry, construct lifecycle
authority, treat a support-journal fallback as a retained research record, or claim that
the support journal contains a session-bundle-only record. When no final observation is
present but recovery facts are present, they SHALL render the nested recovery-trigger
observation labelled as the retry trigger; when both are present they SHALL render both
with distinct labels. Each observation may show only its vetted configured-service label
and sanitized configured endpoint authority, plus its bounded HTTP status or
`no_response`.

Only for the shared `fresh_start` action, both adapters SHALL render the static
copyable command `make demo-real`, labelled as a distinct fresh run from `agent/`.
When they render that command, they SHALL suppress `next_action` as a separate command,
link, or alternative recommendation; the static fresh-start command is the one legal
action. They SHALL not render that command for `retry_followed_by_terminal_failure`. A
`support_journal` location SHALL use the fixed project-relative support-journal path;
`unavailable` SHALL say that no local record could be retained. The command SHALL not
contain the original question, answer, prompt, raw diagnostic content, full provider or
base URL, shell interpolation, or a resume claim. Shell display remains
control-character-safe.
(`REC-006`)

#### Scenario: Exhausted timeout gives a user a concrete next action
- **WHEN** real CLI receives a terminal HITL1 `provider.timeout` with two attempts
  and one exhausted automatic retry
- **THEN** it states the bounded attempt summary and prints a labelled fresh
  `make demo-real` command for `agent/`, plus an inspect command only from the matching
  available terminal-session projection, diagnostic reference, and session-bundle
  location, without echoing the research question

#### Scenario: Fresh start remains the only rendered action
- **WHEN** a terminal has `recovery_action=fresh_start`
- **THEN** CLI/TUI render only the static `make demo-real` command as an actionable
  recovery control and suppress the generic `next_action` rather than presenting a
  competing retry, resume, support, or configuration action; a separately labelled
  matching inspect command, when present, remains read-only diagnosis

#### Scenario: CLI does not falsely offer resume
- **WHEN** the retained result has `same_process` durability after provider recovery
  exhaustion
- **THEN** CLI states that inspection is available but process exit does not make the
  failed graph resumable, and its command starts a distinct run

#### Scenario: A different final failure retains history without a false command
- **WHEN** a first provider timeout is retried and the second invocation ends in
  provider authentication failure or invalid structured output
- **THEN** CLI/TUI render the final category and recovery history, retain its normal
  final-category action, label the trigger and final provider observations when both
  are available, and do not print `make demo-real` as a recovery action

#### Scenario: Diagnostic location is not guessed
- **WHEN** a provider-diagnostic terminal reports
  `diagnostic_location=support_journal` or `unavailable`
- **THEN** CLI/TUI show the fixed support-journal path only for the former and state
  that no local diagnostic record was retained for the latter

#### Scenario: Failure rendering remains redacted
- **WHEN** a terminal fixture carries unsafe exception, credential, path, URL, prompt,
  answer, or provider body data beside the closed recovery facts
- **THEN** CLI/TUI output omits the unsafe value while retaining only the permitted
  category, vetted service label, sanitized endpoint authority, observed
  status/no-response fact, bounded counts, diagnostic reference/location, and
  applicable fresh-start guidance

#### Scenario: Safe endpoint feedback identifies the observed boundary without a full URL
- **WHEN** a terminal provider fixture contains the vetted label `deepseek-v4-pro` and
  authority `https://api.example.test` and observed HTTP status `503`
- **THEN** CLI and TUI render that label, authority, and `503`, but omit any base-URL
  path/query/fragment/user info, exception, provider response body, and credential

#### Scenario: Non-retryable HTTP response remains actionable
- **WHEN** a terminal fixture has a final non-retryable `400` HTTP observation without
  provider-recovery facts
- **THEN** CLI and TUI render the final category, safe `400` status, and normal
  final-category next action, its exact diagnostic reference and typed diagnostic
  location, without inventing retry counts or a fresh-start command

#### Scenario: Stale session does not create an inspect command
- **WHEN** a provider-diagnostic terminal reports `session_bundle` but its snapshot
  session has a different research id, is unavailable, or lacks/mismatches the terminal
  diagnostic reference
- **THEN** CLI and TUI render no inspect command and do not replace the typed diagnostic
  location with a guessed session result
