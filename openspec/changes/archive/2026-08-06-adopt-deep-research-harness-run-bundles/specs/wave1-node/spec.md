> req: WON-009

## ADDED Requirements

### Requirement: Wave1 evidence work remains bound to its selected Run Bundle

Wave1 planning, worker evidence, WorkSpecs, submissions, and contained artifacts SHALL
use the selected runtime-bound Run Bundle context. They SHALL not accept or infer a
legacy research identity/path or use retained session/checkpoint data to select a work
root. Bundle loss SHALL prevent further evidence publication for that Run. (`WON-009`)

#### Scenario: Lost Bundle blocks later Wave1 evidence publication
- **WHEN** Wave1 has an accepted worker result but its selected Bundle is unavailable before publication
- **THEN** it publishes no artifact or replacement State and reports the typed unavailable outcome
