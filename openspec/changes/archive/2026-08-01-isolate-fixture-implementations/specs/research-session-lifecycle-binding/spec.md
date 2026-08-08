> req: RES-001, RES-002, RES-005

## ADDED Requirements

### Requirement: Retired fixture sessions remain non-operable compatibility records

A binding or retained record associated with the retired full-fixture public recipe SHALL
remain validation and inspection data only. It SHALL not select a fixture adapter, cause a
fixture package import, or authorize a real recipe to resume, cancel, or reinterpret that
checkpoint. A current public real operation access SHALL reject a retired fixture binding
before provider, sandbox, or graph access; retained inspection MAY expose only existing
bounded legacy facts and the documented next action.

#### Scenario: Recipe mismatch cannot revive a fixture adapter
- **WHEN** a current real operation access encounters a binding for the retired fixture
  recipe revision
- **THEN** it returns bounded non-operability before provider or graph access and does not
  use the stored fingerprint to choose a recipe

#### Scenario: Legacy inspection remains read-only
- **WHEN** an owner inspects a retained fixture session through an existing inspection path
- **THEN** the path returns only validated bounded retained facts and cannot resume, cancel,
  migrate, or create a new public lifecycle
