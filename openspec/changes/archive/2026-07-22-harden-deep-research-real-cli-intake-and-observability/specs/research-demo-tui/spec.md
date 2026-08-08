> req: RED-006

## ADDED Requirements

### Requirement: Demo TUI consumes shared typed intake actions and safe run updates

The standalone demo TUI SHALL render HITL1 proposal/progress/feedback and an explicit
acceptance control only from shared `PromptView` facts. It SHALL dispatch the same typed
`AnswerRun` action or text response as the CLI, without parsing raw interrupt context,
constructing a human-input envelope, or inferring lifecycle state. Its returned-only
waiting and terminal presentation SHALL consume the existing safe shared run updates.
(`RED-006`)

#### Scenario: TUI action is not a magic text answer
- **WHEN** a shared prompt advertises `accept_suggestion`
- **THEN** the TUI emits the typed action intent rather than a text value and hides the
  control when the shared prompt no longer advertises it
