## ADDED Requirements

### Requirement: Persisted composition truth is explicit and closed

Every accepted Bundle-local Research State SHALL carry an explicit composition mode
derived from its selected graph recipe and executor. The supported closed set is
`fixture`, `mixed`, and `all_real`. A missing, `full_fake`, unknown, incompatible, or
otherwise unregistered mode/schema input SHALL fail before lifecycle projection, graph
invocation, State mutation, or a quality/completion claim; it SHALL not default,
backfill, auto-migrate, or strengthen provenance. The fixed production factory remains
all-real and generic test/demo composition remains explicit; no compatibility factory,
no-graph execution path, or caller-selected production mode is retained. (`REG-004`,
`REG-005`, `REG-006`, `REG-011`, `REG-019`)

#### Scenario: Missing mode is rejected without a State write
- **WHEN** a lifecycle reader receives a Bundle State mapping with no explicit
  composition mode
- **THEN** it returns the existing bounded invalid/unsupported State outcome before a
  graph node, State reducer, or lifecycle projection runs and leaves the payload
  unchanged

#### Scenario: Removed full-fake provenance cannot be upgraded
- **WHEN** a State mapping names `full_fake` or an unknown composition mode
- **THEN** the reader rejects it without interpreting it as `all_real`, producing a
  completion claim, or rewriting the mapping

#### Scenario: Trusted executor supplies the initial mode
- **WHEN** a supported graph-backed start publishes a new Bundle
- **THEN** its State receives exactly the selected recipe's explicit mode and no caller
  may replace that fact through a lifecycle action

