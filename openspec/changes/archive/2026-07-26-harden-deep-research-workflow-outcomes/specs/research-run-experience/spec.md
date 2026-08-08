## ADDED Requirements

### Requirement: Shared terminal outcomes retain incident truth across all real phases

`ResearchRunExperience` SHALL derive a terminal or fault presentation only from the
typed lifecycle result and its checkpointed terminal incident or controller-derived
worker diagnosis. For every retained known incident it SHALL expose the safe category,
phase, certainty, observed recovery disposition, safe diagnostic reference,
durability, and exactly one legal next action. It SHALL not downgrade a known
incident to generic `research.blocked`, invent provider history for an unknown
failure, or offer retry/resume contrary to the lifecycle contract.

#### Scenario: A topic-planning timeout has the same typed outcome in every adapter
- **WHEN** lifecycle returns a blocked topic-planning terminal incident for an
  exhausted provider timeout
- **THEN** the shared update supplies its category, phase, bounded recovery facts,
  diagnostic reference, durability truth, and one legal action to both CLI and TUI
  adapters

#### Scenario: A legacy blocked record remains honestly incomplete
- **WHEN** a readable legacy terminal has no retained incident
- **THEN** the shared update labels it as an unclassified blocked result without
  claiming a provider timeout, retry, or recovery that was not observed
