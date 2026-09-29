# Spec Delta

> req: LDD-009

## ADDED Requirements

### Requirement: Session watchpoints stop the drive when a watched state field changes

A debug session SHALL accept a set of watch fields, each of which SHALL be a typed
field of the Bundle's durable State; an unknown field name SHALL be rejected with a
typed failure rather than silently ignored. During a continuous drive, after each
committed boundary the driver SHALL compare the watched fields against the values
captured when the drive started, and SHALL stop the drive when any watched field has
changed, carrying the changed field names on the session snapshot as watch hits. The
watch configuration is session-scoped operator state, never a graph write, and the
baseline SHALL advance to the current values after a hit. (`LDD-009`)

#### Scenario: A changed field stops the drive
- **WHEN** a drive with a watch on a state field observes that field change during a
  boundary commit
- **THEN** the drive stops, the snapshot carries the changed field name as a watch
  hit, and the session stays steppable

#### Scenario: An unknown field is rejected
- **WHEN** the operator watches a name that is not a typed State field
- **THEN** the driver rejects it with a typed failure and the watch set is unchanged

#### Scenario: The baseline advances after a hit
- **WHEN** a watch hit stops the drive and the operator drives again
- **THEN** the same value no longer trips the watch until the field changes again
