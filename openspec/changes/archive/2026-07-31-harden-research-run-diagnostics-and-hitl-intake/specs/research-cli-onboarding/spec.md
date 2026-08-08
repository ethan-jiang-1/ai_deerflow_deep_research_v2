## ADDED Requirements

### Requirement: Retained-diagnostic command is executable and read-only

Whenever CLI or TUI renders a retained-session inspection action, it SHALL render the
same documented command shape that is executable from the `deerflow_research/` module
directory: `make demo-sessions DEMO_ARGS="inspect <run-reference>"`. The command SHALL
be presented only for an exact verified terminal/session diagnostic correlation, remain
explicitly read-only, and never claim retry, resume, cross-process continuation, or a
provider conclusion. The adapters SHALL render each supplied closed timeout origin next
to its existing retry-trigger or final-observation role, not as prose attribution to the
configured service.
(`REC-005`, `REC-006`)

#### Scenario: Rendered command runs in the documented module context
- **WHEN** a correlated retained provider terminal is rendered from
  `deerflow_research/`
- **THEN** the displayed inspection command runs against the current checkout layout
  and returns only a read-only session observation, including only its exact-reference
  verified trigger/final closed timeout origins

#### Scenario: Timeout origin is not provider blame
- **WHEN** a terminal carries a bridge-budget timeout origin
- **THEN** the rendered safe diagnostic identifies the bridge-budget observation and
  does not state that the configured provider failed to respond

#### Scenario: Unverified diagnostic has no inspection command
- **WHEN** a provider terminal has `support_journal` or `unavailable` diagnostic
  location
- **THEN** CLI and TUI omit the retained-session inspection command and retain only the
  existing legal fresh-start or diagnostic fallback guidance
