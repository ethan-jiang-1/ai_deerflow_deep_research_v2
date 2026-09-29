# Spec Delta

> req: RED-016

## ADDED Requirements

### Requirement: The workbench exposes node rerun and states every policy auto-answer

The debugger workbench SHALL expose the node-rerun entry at a stopped boundary as a
slash command listed by `/help`, with a visible cost note that the embedded
composition re-bills the real model call. When the drive policy auto-answers a hitl1
request, the workbench SHALL state each auto-answer in the log as operator-policy
content, and a policy stop SHALL render the node's reply and remaining rounds exactly
like a human-facing HITL card. (`RED-016`)

#### Scenario: Rerun is reachable and honest about cost
- **WHEN** the operator reruns the last committed node at a boundary
- **THEN** the log states the rerun, its node, and — in embedded compositions — that
  the model call is billed again

#### Scenario: Auto-answers are never silent
- **WHEN** the drive policy answers a hitl1 request
- **THEN** the log states that the answer came from the drive policy, and a policy
  stop renders the standard HITL conversation card for the human
