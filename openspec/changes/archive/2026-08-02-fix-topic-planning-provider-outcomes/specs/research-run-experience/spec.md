## MODIFIED Requirements

### Requirement: Shared terminal outcomes retain incident truth across all real phases

`ResearchRunExperience` SHALL derive a terminal or fault presentation only from the
typed lifecycle result and its checkpointed terminal incident or controller-derived
worker diagnosis. For every retained known incident it SHALL expose the safe category,
phase, certainty, observed recovery disposition, opaque diagnostic reference,
durability, and exactly one legal next action. When the incident has no supplied
diagnostic reference, it SHALL use the existing shared diagnostic-publication seam to
derive that reference only from typed terminal facts. It SHALL preserve the closed
`provider.usage_unavailable`, `budget.exhausted`, and `policy.denied` categories in
`RunFailure` and use category-specific safe copy for them; it SHALL not display the
tool-execution message or tool-service next action for any of those categories. It
SHALL not downgrade a known incident to generic `research.blocked`, invent provider
history for an unknown failure, or offer retry/resume contrary to the lifecycle
contract.

#### Scenario: A topic-planning timeout has the same typed outcome in every adapter
- **WHEN** lifecycle returns a blocked topic-planning terminal incident for an
  exhausted provider timeout
- **THEN** the shared update supplies its category, phase, bounded recovery facts,
  diagnostic reference, durability truth, and one legal action to both CLI and TUI
  adapters

#### Scenario: A zero-tool usage stop is not presented as a tool failure
- **WHEN** lifecycle returns a blocked topic-planning terminal incident with
  `provider.usage_unavailable`, `budget.exhausted`, or `policy.denied`
- **THEN** the shared update preserves that exact category, phase, and certainty;
  derives or preserves its opaque diagnostic reference only from typed terminal facts;
  and renders its category-specific safe message and legal action without a provider
  retry, resume action, or tool-failure wording

#### Scenario: A closed stop after provider recovery preserves historical recovery only
- **WHEN** lifecycle returns a `retry_followed_by_terminal_failure` topic-planning
  incident whose final code is `provider.usage_unavailable`, `budget.exhausted`, or
  `policy.denied`
- **THEN** the shared update preserves the final closed category and the actual prior
  recovery history, derives or preserves its opaque diagnostic reference only from
  typed terminal facts, and offers no fresh-start or resume action for that final
  non-provider category

#### Scenario: A legacy blocked record remains honestly incomplete
- **WHEN** a readable legacy terminal has no retained incident
- **THEN** the shared update labels it as an unclassified blocked result without
  claiming a provider timeout, retry, recovery, or a newly closed node-agent stop that
  was not observed
