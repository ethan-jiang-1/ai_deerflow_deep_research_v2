## ADDED Requirements

### Requirement: Canonical profile parsing proposes candidates without compatibility inference

The canonical profile parser SHALL return the bounded parse result consumed by current
HITL1 semantic admission. It SHALL not retain a duplicate convenience projection or
use absent/legacy persisted schema conventions to manufacture a current profile,
proposal, visible control, route, or lifecycle fact. Invalid or extra raw input remains
subject to the existing bounded candidate rejection and visible-recovery contract.
(`HIC-001`, `HIC-002`, `HIC-004`)

#### Scenario: Canonical result does not become a lifecycle fact directly
- **WHEN** raw profile text is parsed successfully
- **THEN** the result remains a bounded candidate until the existing HITL1 admission
  path accepts it, and no parser convenience surface creates a checkpoint or control

#### Scenario: Rejected old input preserves current visible recovery
- **WHEN** an unsupported persisted profile/proposal shape is encountered before a
  current semantic interaction can be admitted
- **THEN** it creates no replacement proposal/control or inferred profile fact, while
  the existing legal recovery behavior remains available only from valid current State
