> req: RER-014

## ADDED Requirements

### Requirement: Active Bundle results remain safe non-terminal projections

When a shared typed Bundle lifecycle result identifies an available active Bundle,
including a different `start` denied with `active_bundle_exists`,
`ResearchRunExperience` SHALL return a safe `research.active` `Fault` rather than
constructing a terminal outcome or reporting a protocol fault. The fault SHALL retain
only the selected result's bounded Bundle identity, known phase, durability, and
available observation projection. It SHALL not infer a pending input, resume the
Bundle, cancel it, change its State, or claim that the graph has stopped. Its next
action SHALL direct the consumer to query or explicitly cancel the selected Bundle
through lifecycle control.

#### Scenario: A different start encounters an active Bundle

- **WHEN** a `start` dispatch returns the typed `active_bundle_exists` result for an
  available Bundle
- **THEN** the shared experience returns a `research.active` fault with that Bundle's
  safe snapshot and does not report `protocol.invalid_result` or present a terminal
  completion state

#### Scenario: Status observes an active Bundle

- **WHEN** a status dispatch returns an available active Bundle result
- **THEN** the shared experience returns the same bounded `research.active` fault and
  does not infer a resume prompt or a terminal outcome
