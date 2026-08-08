> req: DPL-002

## MODIFIED Requirements

### Requirement: Demo progress display uses shared verified run updates

Demo scripts SHALL render phase progress only from a shared verified returned trace
delta and labels supplied by the run experience. They MAY preserve repeated
logical-phase visits. A suspended marker SHALL identify
`pending_input.pending_phase`, not `control.phase`, because `control.phase` is the
last committed checkpoint fact. No demo script shall hardcode a phase sequence,
infer current phase from action or request options, or update a tracker before a
valid returned event/result proves it.

For a shared `PromptView` in `choice` mode, standalone demo adapters SHALL
distinguish the canonical option ID from its bounded human-readable consequence and
direct a CLI user to enter one advertised ID rather than its rendered consequence.
They SHALL submit the entered value only through `AnswerRun` and SHALL NOT parse a
rendered `<id>: <consequence>` line as an alternate graph-control protocol.

When `ResearchRunExperience` re-presents an unchanged `AwaitingInput` prompt with
`rejection_category=choice_input_invalid`, the adapter SHALL render fixed safe
feedback and the same advertised choices without echoing the rejected value,
inferring graph progress, changing the request ID, or constructing a lifecycle
result. CLI adapters SHALL continue their existing awaiting-input loop so the user
can submit a later canonical ID; the Textual adapter SHALL present the same safe
feedback through its existing prompt state. (`DPL-002`)

#### Scenario: First HITL phase is not confused with checkpoint phase
- **WHEN** a suspended run has execution trace `bootstrap`, checkpoint phase `bootstrap`, and pending-input phase `hitl1`
- **THEN** a demo marks bootstrap as completed and renders HITL-1 as the current requested interaction without treating the result as inconsistent

#### Scenario: Fake demo shows phases that actually executed
- **WHEN** `make demo --scripted` runs the fake lifecycle
- **THEN** it renders the actual trace order before, between, and after HITL points

#### Scenario: Fake CLI corrects a pasted display line without restarting the run
- **WHEN** a fake `make demo` HITL2 prompt displays `proceed` and its consequence,
  and the user enters the entire displayed line rather than the ID
- **THEN** the CLI states that an advertised option ID is required, re-renders the
  same pending choice without the rejected text or new phase progress, and accepts a
  later `proceed` response through the shared lifecycle loop

#### Scenario: Standalone adapter keeps presentation text out of decision authority
- **WHEN** a standalone adapter displays an advertised HITL2 option and its bounded
  human-readable consequence
- **THEN** only the option ID is sent as the answer value, and neither CLI nor TUI
  derives a route by parsing its own rendered consequence text

#### Scenario: Shared invalid-choice feedback remains redacted in every adapter
- **WHEN** the shared prompt carries invalid-choice feedback after a rejected value
- **THEN** CLI and TUI show fixed actionable feedback and never display the raw
  rejected value, exception text, lifecycle wire data, or a fabricated diagnostic
  record
