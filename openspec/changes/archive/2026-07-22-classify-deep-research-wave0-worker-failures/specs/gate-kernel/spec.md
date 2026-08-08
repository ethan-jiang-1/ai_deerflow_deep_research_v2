## ADDED Requirements

### Requirement: Wave0 exhausted incidents carry a pure optional diagnosis

The gate kernel SHALL remain the sole writer of `latest_incident`. Only when the Wave0
gate reaches its existing exhausted route, it SHALL derive the `WFC-001` aggregate from
the checkpointed `AttemptRef` history and write it as an optional diagnosis field on
the existing `research.blocked` incident. The derivation SHALL be pure, SHALL NOT
change verdict, route, generation, budget, failure code, or retry eligibility, and
SHALL produce no diagnosis for legacy/incomplete category history or any other phase.
(`GAK-007`)

#### Scenario: Wave0 blocked incident carries a diagnosis without a route change
- **WHEN** Wave0 exhausts after attempts with the same `tool_execution` category
- **THEN** the gate writes `research.blocked` with optional diagnosis
  `tool_execution` and the route remains `exhausted`

#### Scenario: Other terminal paths do not acquire Wave0 diagnosis
- **WHEN** another phase blocks or Wave0 has no complete persisted failure categories
- **THEN** the gate writes no worker diagnosis and preserves its existing incident
  behavior
