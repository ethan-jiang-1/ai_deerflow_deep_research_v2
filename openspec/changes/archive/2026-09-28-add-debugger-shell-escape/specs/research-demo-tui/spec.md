## ADDED Requirements

### Requirement: Operator shell escape at the workbench

The debugger workbench SHALL let the operator run a bounded one-shot shell command
from the composer by prefixing it with `!`, at any posture, without the line being
consumed as a research answer or a debug command. The command SHALL run
non-interactively with the operator's own privileges — the escape grants no new
authority — under a runtime bound that terminates an overrun command, with captured
output bounded in size and truncation stated. Its working directory SHALL anchor to
the live session's Bundle directory when a session is open, else to the workspace
bundle root. The output SHALL be rendered verbatim in the log, labelled as
operator-invoked content with the command and the working directory; it is not a
workbench projection, and no graph state, admission decision, route, or tool
authority is derived from it. The capability SHALL be listed by `/help`.

#### Scenario: Inspecting the filesystem at a paused boundary
- **WHEN** the workbench is paused at any boundary and the operator submits a
  `!`-prefixed command
- **THEN** the command runs with the anchored working directory and its bounded
  output appears in the log as operator-invoked content, while the pending HITL
  request stays open

#### Scenario: A runaway command is bounded
- **WHEN** the command exceeds the runtime bound
- **THEN** the escape terminates it, states the timeout, and the workbench stays
  responsive

#### Scenario: The escape is not graph authority
- **WHEN** any shell escape runs
- **THEN** no admission, tool, route, or graph state changes because of it, and the
  rendered output is presented as operator-invoked content rather than a projection
