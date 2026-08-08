## ADDED Requirements

### Requirement: TUI renders shared workflow-failure outcomes without inference

For every terminal or fault update carrying a workflow incident, the demo TUI SHALL
render only the shared safe category, phase, bounded recovery disposition, diagnostic
reference, durability truth, and legal next action. It SHALL not replace a known
incident with generic blocked text, infer a retry from elapsed time, or present an
inspection reference as a recovery control.

#### Scenario: A provider timeout is distinguishable from generic blocking
- **WHEN** the shared run update carries a terminal topic-planning timeout incident
- **THEN** the TUI shows the timeout category and phase from that update alongside
  the one legal action and does not offer an inferred resume or local retry
