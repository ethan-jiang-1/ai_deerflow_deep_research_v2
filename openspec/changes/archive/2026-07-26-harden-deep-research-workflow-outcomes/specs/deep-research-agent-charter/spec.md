## ADDED Requirements

### Requirement: Workflow-affecting changes record a triggered outcome review

The Agent Charter SHALL provide a `workflow-outcome-review` policy for changes that
add or modify a model, tool, provider, worker, retry, terminal, diagnostic, or
lifecycle-projection path. `openspec/config.yaml` and its governance checker SHALL
require every active Deep Research proposal to record triggered charter policies in
its Change Focus. A proposal selecting `workflow-outcome-review` SHALL include a
bounded failure-outcome table naming the fact owner, recovery owner and bound,
terminal disposition, legal next action, and deterministic evidence seam. A proposal
selecting no policy SHALL state a short rationale. This record SHALL guide design and
review only; it SHALL not create runtime authority.

#### Scenario: A provider-recovery change is admitted with its outcome contract
- **WHEN** a proposal changes a phase's provider timeout or retry behavior
- **THEN** governance requires the workflow-outcome review record before the change
  is considered admission-complete

#### Scenario: A non-workflow documentation change remains bounded
- **WHEN** a proposal changes only human documentation and declares no triggered
  workflow policy with a rationale
- **THEN** governance accepts the bounded declaration without requiring a fabricated
  failure-outcome table
