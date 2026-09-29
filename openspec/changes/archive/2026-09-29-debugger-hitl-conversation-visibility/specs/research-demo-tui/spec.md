# Spec Delta

> req: RED-015

## ADDED Requirements

### Requirement: The debugger workbench renders HITL stops as a typed conversation, never as machine JSON

At a HITL stop the debugger workbench SHALL render the pending request's typed prompt
card when the session projection carries one — the node's heading, goal summary,
proposed dimensions, missing fields, remaining accepted-answer rounds, and localized
guidance — together with the request's own title, mode, and advertised options. It
SHALL NOT print the request's raw machine context payload. When the projection carries
no prompt card, the workbench SHALL state the title, mode, and a bounded
unparsed-context note instead of the raw payload.

When the session projection carries the node's last feedback for the pending
conversation, the workbench SHALL render it as the node's visible reply. After an
operator answer is consumed and the session re-stops at the same node's HITL request,
the workbench SHALL state that the answer was consumed but not accepted, including the
remaining accepted-answer rounds when the card carries them.

A plain-text submit in the debugger SHALL clear the composer, so a repeated Enter
cannot resubmit the same text as another answer or as an unintended advance. The HITL
card and the capability listing SHALL name the fastest legal confirm input and the
single-field revision format. (`RED-015`)

#### Scenario: A HITL stop shows the card, not the payload
- **WHEN** a debug session stops at a HITL request whose projection carries a parsed
  prompt card
- **THEN** the workbench renders the card's goal, proposed dimensions, missing fields,
  remaining rounds, and guidance, and the raw context JSON appears nowhere in the log

#### Scenario: The node's reply is visible
- **WHEN** the projection carries the node's last feedback after a consumed answer
- **THEN** the workbench renders that feedback message as the node's reply together
  with the consumption outcome and remaining rounds when known

#### Scenario: An unparsed context degrades honestly
- **WHEN** a HITL request's projection carries no prompt card
- **THEN** the workbench states the request's title and mode with a bounded
  unparsed-context note and prints no raw machine payload

#### Scenario: A repeated Enter cannot double-consume
- **WHEN** the operator submits plain text in the debugger and presses Enter again
- **THEN** the composer no longer holds the submitted text, and the second Enter
  produces no second answer submission and no unintended node advance beyond the
  documented empty-submit behavior for the current posture

#### Scenario: The fastest path out is advertised
- **WHEN** the workbench shows a HITL card or its capability listing
- **THEN** the fastest legal confirm input and the single-field revision format are
  named in operator-readable text
