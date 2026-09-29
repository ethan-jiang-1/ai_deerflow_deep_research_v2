# Spec Delta

> req: RED-017

## ADDED Requirements

### Requirement: The workbench answers where-am-I, what-is-this-field, and watch requests

The debugger workbench SHALL provide three bounded introspection entries, listed by
`/help`: `/bt` states the walked node path from the session's durable trace (grouping
consecutive revisits, marking the node currently awaited, if any); `/state [field]`
renders one typed State field's bounded value, or the field-name list when no field is
given, and rejects unknown names with a typed line; `/watch [field]` and
`/unwatch <field>` manage the session's watch set against the same typed field
allowlist. When a drive stops on a watch hit, the workbench SHALL state which watched
fields changed. (`RED-017`)

#### Scenario: The walked path is answerable at any stop
- **WHEN** the operator enters `/bt` at any session posture
- **THEN** the workbench renders the walked node path with revisit counts and the
  current position, derived from the session's durable trace

#### Scenario: A single field is answerable without machine JSON
- **WHEN** the operator enters `/state <field>` for a typed State field
- **THEN** the workbench renders that field's bounded value, and an unknown field
  name renders a typed rejection instead of any payload

#### Scenario: A watch hit is stated, never silent
- **WHEN** a drive stops because a watched field changed
- **THEN** the workbench names the changed fields in the log
