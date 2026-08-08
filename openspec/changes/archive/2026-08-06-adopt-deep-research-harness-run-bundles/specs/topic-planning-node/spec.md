> req: TOP-008

## ADDED Requirements

### Requirement: Topic planning consumes Bundle-local profile and writes Bundle-contained planning facts

Topic planning SHALL consume confirmed profile and planning State only through the
selected Run Bundle's bound graph/store interfaces. Its durable topic plan, coverage
facts, and artifact references SHALL remain in that Bundle. It SHALL not recover a
profile from an external checkpoint, derive a research identity, or select an artifact
root. (`TOP-008`)

#### Scenario: Planning refuses a missing selected Bundle
- **WHEN** topic planning is invoked after its selected Bundle becomes unavailable
- **THEN** it does not read a former external checkpoint or publish a plan elsewhere and returns the Bundle-unavailable lifecycle outcome
