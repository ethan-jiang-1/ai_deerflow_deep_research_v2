> req: DPL-013

## ADDED Requirements

### Requirement: All-real standalone demos isolate fresh process runs

Each all-real standalone demo adapter construction SHALL derive a fresh trusted local
scope for that process's new Run Bundle admission. A retained Bundle from an earlier
all-real demo process SHALL remain contained and inspectable only through its supported
typed lifecycle/observation route, but it SHALL not be selected, resumed, cancelled,
or deleted by the new demo process. Fixture-graph and fixed local-session demo profiles
SHALL retain their existing stable scopes. The adapter SHALL not accept a user-supplied
scope, path, session, or checkpoint identity.

#### Scenario: An earlier all-real Bundle remains active

- **WHEN** a prior all-real demo process leaves an available active Bundle in its
  retained local root and a later all-real demo process starts
- **THEN** the later process receives a fresh trusted scope and can admit a distinct
  Run without mutating or reopening the earlier Bundle

#### Scenario: Fixture profile remains stable

- **WHEN** fixture-graph demo or fixed local-session tooling constructs its adapter
- **THEN** it retains the configured stable fixture profile scope and does not gain the
  all-real process-isolation behavior
