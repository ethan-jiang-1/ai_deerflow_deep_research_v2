## ADDED Requirements

### Requirement: Operator side-chat at the workbench

The debugger workbench SHALL let the operator converse with a chat model from the
composer by prefixing the line with `?` (or the full-width `？`), at any posture.
A side-chat turn SHALL NOT be consumed as a research answer or a debug command,
SHALL NOT consume a pending HITL request or its revision rounds, and SHALL NOT
change any graph state, admission decision, route, or tool authority. The
conversation SHALL use the operator's own chat model with the same read-only
workspace tools as the recon chat, and its output SHALL render in the log as
operator-invoked content while the debug posture pane keeps ownership of the
posture display. The capability SHALL be listed by `/help`.

#### Scenario: Conversing at a HITL stop without consuming the round
- **WHEN** the workbench is waiting at a HITL request and the operator submits a
  `?`-prefixed line
- **THEN** the chat model answers in the log, the pending HITL request stays open
  with its revision rounds untouched, and the next unprefixed line is still the
  formal answer

#### Scenario: The side chat holds no graph authority
- **WHEN** any side-chat turn runs
- **THEN** no admission, tool, route, or graph state changes because of it, and the
  rendered output is presented as operator-invoked content rather than a projection
