> req: RER-012

## ADDED Requirements

### Requirement: Shared confirmation prompts display all material proposal constraints

When a typed complete HITL1 interaction presents a current proposal, the shared
`PromptView` SHALL render a bounded, safe representation of every material proposal
constraint before a person can accept it: depth, audience, format, cost tolerance,
time budget, every must-answer question, non-empty scope boundaries, non-empty custom
notes, comparison subjects when required, and the accepted output language. The
projection SHALL have capacity for at least seventeen labeled lines, derived from the
current maximum of eight must-answer questions plus the five scalar dimensions and
four remaining material values. It SHALL not silently discard a typed field through a
global line cap or a shorter per-value display cap; it may normalize whitespace and
control characters within the existing typed field bounds. The projection SHALL be
derived from the existing typed interaction contract, retain its current visible
controls, and remain compatible with the existing legacy-context fallback. It SHALL
not expose raw model output, raw user text, hidden action ids, or new lifecycle
authority. (`RER-012`)

#### Scenario: A source-restricted proposal is visible before confirmation
- **WHEN** HITL1 presents a complete typed proposal whose scope boundary limits
  research to Python official documentation and whose output language is Chinese
- **THEN** the shared confirmation prompt visibly includes both constraints alongside
  its existing current-proposal control before the Primary User confirms or revises it

#### Scenario: Material values do not disappear from a revised proposal
- **WHEN** a complete revised typed proposal has multiple must-answer questions,
  comparison subjects, scope boundaries, and custom notes
- **THEN** the shared prompt preserves a labeled safe line for every material value,
  including all eight permitted must-answer questions and the full normalized typed
  scope/note values, and leaves the interaction/control identity unchanged
