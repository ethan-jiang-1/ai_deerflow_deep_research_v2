> req: REC-007

## ADDED Requirements

### Requirement: Real CLI makes natural proposal interaction and fallback controls discoverable

The real standalone CLI SHALL render the shared proposal and bounded feedback in normal
human language. A user may submit ordinary confirmation, revision, question, or
clarification text; the CLI SHALL not require a JSON object or hidden acceptance phrase
for those intents. It SHALL render each shared visible control with a stable number and
submit the selected number as `SelectControlRun`, never as an action id or magic text.
On semantic failure it SHALL state the non-terminal condition, retain the proposal, and
render the current-proposal fallback control. (`REC-007`)

#### Scenario: First-time confirmation needs no protocol knowledge
- **WHEN** a user sees the initial complete proposal
- **THEN** the CLI explains that they can confirm, revise, or ask a question in normal
  language and also shows `1. Start with the current proposal`

#### Scenario: Semantic failure stays actionable
- **WHEN** semantic intake cannot interpret or reach its provider for a reply
- **THEN** CLI shows bounded feedback and the same numbered current-proposal control
  instead of JSON-only recovery or a terminal input error
