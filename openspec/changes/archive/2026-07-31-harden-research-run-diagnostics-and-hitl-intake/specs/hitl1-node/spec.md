## ADDED Requirements

### Requirement: HITL1 terminal correlation retains only observed timeout origins

When HITL1 receives provider-diagnostic results carrying safe timeout origins, it SHALL
retain each exact origin in the role that owns its `ProviderObservation`: the recovery
trigger or final terminal observation, and SHALL supply those roles unchanged to the
shared `workflow-failure-outcomes` diagnostic-correlation helper. It SHALL preserve
absent legacy origins as absent and SHALL not reconstruct an origin from retry history,
service label, endpoint authority, timestamps, or raw provider data. This diagnostic
fact SHALL not change the existing provider retry bound, graph route, natural proposal
confirmation semantics, or the authority of the semantic candidate/resolution flow.
(`HIN-001`, `HIN-009`)

#### Scenario: Trigger and final timeout origins remain distinct
- **WHEN** a retry-exhausted HITL1 terminal has a bridge-budget recovery trigger and a
  provider-SDK-timeout final observation
- **THEN** its terminal incident retains both origins in their distinct roles and derives
  a safe diagnostic correlation reference without exposing raw failure data

#### Scenario: Trigger-only timeout origin remains absent at the final observation
- **WHEN** a bridge-budget provider timeout triggers the retry and that retry reaches a
  non-timeout terminal failure
- **THEN** the recovery trigger retains its origin, the final observation retains no
  timeout origin, and HITL1 does not infer either value from the recovery disposition

#### Scenario: Natural confirmation remains graph-authorized
- **WHEN** a complete current proposal receives the natural confirmation
  `确认，按这个方案开始吧。`
- **THEN** the existing bounded semantic-intake and graph-admission path accepts only
  the current checkpointed proposal and does not parse that reply as profile fields
