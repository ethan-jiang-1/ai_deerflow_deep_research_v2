# research-demo-tui Delta

> req: RED-009

## ADDED Requirements

### Requirement: Demo TUI answers advertised CHOICE prompts with typed options

The standalone demo TUI in fixture and embedded-smoke modes SHALL render the
options of the current advertised HITL1 CHOICE prompt and submit a user's
selection as the shared typed option answer carrying that advertised option id
for the prompt's current request. It SHALL NOT submit a text-kind answer for a
prompt whose shared contract requires an option, and SHALL NOT invent an option
id, construct a response envelope, or admit the answer itself — legality remains
with the shared run experience. Ordinary TEXT-mode HITL1 prompts SHALL keep
forwarding free text unchanged for semantic intake, and non-language CHOICE
prompts SHALL keep forwarding composer text to the shared graph-owned
validation unchanged. (`RED-009`)

#### Scenario: User selects an advertised language option
- **WHEN** a HITL1 CHOICE prompt advertises language options and the user selects one
- **THEN** the demo TUI submits the typed option answer carrying that advertised
  option id, and the shared run experience accepts it without the
  language-answer rejection reserved for text-kind answers

#### Scenario: Composer entry during a HITL1 CHOICE prompt
- **WHEN** a HITL1 CHOICE prompt is current and the user submits composer text
- **THEN** an exact match of one advertised option id is submitted as the typed
  option answer for that advertised id, while any other text is not dispatched
  as a text-kind answer and fabricates no option id, leaving the prompt awaiting
  a real selection

#### Scenario: TEXT prompts keep free-text semantic intake
- **WHEN** the current HITL1 prompt is TEXT mode and the user submits free text
- **THEN** the demo TUI forwards it unchanged as the shared text answer for
  semantic intake, exactly as before this requirement
