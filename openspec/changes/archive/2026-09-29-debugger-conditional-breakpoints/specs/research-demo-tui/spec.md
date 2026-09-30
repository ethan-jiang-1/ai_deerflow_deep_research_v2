# Spec Delta

> req: RED-018

## ADDED Requirements

### Requirement: The workbench accepts conditional run targets with parse-time denials

The debugger workbench's `/run` command SHALL accept an optional typed
condition suffix — `/run [node] if <field><op><value> (and <field><op><value>
...)` — where field names come from the same typed State allowlist as
`/state`. A condition naming an unknown field, using an unsupported operator,
or carrying an unparseable value SHALL be rendered back as a typed rejection
that names the problem and the available fields, without starting any drive;
a valid conditional run SHALL state the active condition when the drive is
accepted. `/help` SHALL list the conditional run syntax. (`RED-018`)

#### Scenario: A conditional run states its condition and honors it
- **WHEN** the operator enters `/run <node> if <field> >= <value>` with a
  valid allowlisted field
- **THEN** the workbench states the accepted condition and the drive stops
  only at a boundary satisfying it

#### Scenario: A bad condition is refused before any drive
- **WHEN** the operator enters `/run <node> if <unknown-field> == 1`
- **THEN** the workbench renders a typed rejection naming the unknown field
  and the available fields, and no drive starts

#### Scenario: Help documents the conditional syntax
- **WHEN** the operator enters `/help`
- **THEN** the conditional run syntax is listed among the capabilities
