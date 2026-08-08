> req: REC-005

## ADDED Requirements

### Requirement: Real CLI makes profile confirmation and run state actionable

The real standalone CLI SHALL render the shared HITL1 proposal, recognized fields, missing fields including `must_answer`, rejection feedback, remaining accepted-answer and rejection-retry budgets, and visible advertised `accept_suggestion` action. It SHALL offer a stable complete JSON example and SHALL not imply that a vague sentence accepts a proposal.

During returned-only waiting the CLI SHALL render bounded recurring local state including run reference when known, elapsed time, last committed phase, and the fact that it is waiting for a lifecycle return rather than observing background execution. Every terminal outcome SHALL render its outcome, phase, safe diagnostic reference/category when known, durability-specific recovery truth, and exact inspection command. (`REC-005`)

#### Scenario: A first-time user can see every required intake field
- **WHEN** real HITL1 returns its first prompt
- **THEN** CLI shows the proposal, `must_answer`, accepted/missing fields, a visible acceptance action, and a complete JSON example

#### Scenario: A completed background-looking call is not misrepresented
- **WHEN** a retained same-process run has already returned a terminal result
- **THEN** CLI prints the terminal receipt and says the retained bundle is inspectable but not proof of a live or cross-process-resumable run

#### Scenario: CLI never echoes unsafe diagnosis data
- **WHEN** a diagnostic fixture contains exception text, a secret, path, or raw answer
- **THEN** terminal and inspect guidance omit those values while retaining safe category and opaque reference
