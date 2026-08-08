## ADDED Requirements

### Requirement: Terminal incidents preserve Wave0 diagnosis separately from route code

For a terminal Wave0 work exhaustion, the frozen terminal-incident and safe run-update
contracts SHALL carry an optional closed exhausted-work diagnosis aggregate separately
from the existing `RunFailureCode.RESEARCH_BLOCKED` route code. The value SHALL be one
per-attempt worker category from `WFC-001` or `mixed`; absent legacy state remains
unavailable. Presentation and session publication SHALL consume only this validated
field and SHALL NOT infer it from exception text, event ordering, model/tool bodies, or
raw checkpoint state. (`RER-008`)

#### Scenario: Blocked route remains stable while diagnosis is visible
- **WHEN** Wave0 exhausts work with a `structured_output` aggregate
- **THEN** the terminal route code remains `research.blocked` and the safe terminal
  projection separately exposes `structured_output`

#### Scenario: Legacy terminal remains honest
- **WHEN** a legacy blocked checkpoint has no worker diagnosis aggregate
- **THEN** presentation marks the optional diagnosis unavailable and does not invent a
  category
