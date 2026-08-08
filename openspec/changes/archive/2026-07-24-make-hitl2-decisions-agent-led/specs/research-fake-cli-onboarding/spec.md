> req: FCO-001

## ADDED Requirements

### Requirement: Fake CLI onboarding is paste-safe and does not outsource graph control

`agent/README.md` SHALL provide a repository-root quick-start sequence and a clearly
separate sequence for users already in `agent/`; neither user-copyable command line
may contain an inline shell comment. The credential-free standalone fake CLI SHALL
collect only required scope input, render returned progress and terminal truth, and
never ask a user to select an internal HITL2 graph route. Fake output SHALL remain
explicitly labelled as a lifecycle fixture rather than research findings or a report.

#### Scenario: Quick-start commands work in interactive zsh
- **WHEN** a user copies the documented setup command line into an interactive zsh
  without `INTERACTIVE_COMMENTS`
- **THEN** Make receives no `#` target or prose token

#### Scenario: Ordinary fake lifecycle does not ask for a route
- **WHEN** the fake graph returns an autonomous HITL2 continuation
- **THEN** the CLI reports progress and does not ask the user to type an internal
  control-flow identifier
