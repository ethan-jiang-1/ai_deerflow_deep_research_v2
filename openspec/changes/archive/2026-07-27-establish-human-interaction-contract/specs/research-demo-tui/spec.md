> req: RED-007

## ADDED Requirements

### Requirement: Demo TUI submits visible controls without text aliases

The standalone demo TUI SHALL render shared `VisibleControl` values and submit their
control ids through `SelectControlRun`. Its input field SHALL forward ordinary HITL1
text unchanged for semantic intake. It SHALL not recognize an acceptance phrase,
construct an action id, or inspect raw prompt context. (`RED-007`)

#### Scenario: TUI control has no text equivalent
- **WHEN** a shared prompt exposes the current-proposal control
- **THEN** pressing its button submits that control id while entering a natural
  confirmation remains ordinary text
