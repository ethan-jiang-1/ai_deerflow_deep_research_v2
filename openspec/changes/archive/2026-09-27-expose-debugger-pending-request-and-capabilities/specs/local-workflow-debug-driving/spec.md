# Spec Delta

> req: LDD-001

## MODIFIED Requirements

### Requirement: Closed debug commands drive one exact Bundle at-most-once

The debug driver SHALL expose a closed command set — `advance_one`,
`drive_until`, `pause_request`, `answer`, `cancel`, `detach` — where every
mutation carries the exact `bundle_id`, an `expected_cursor`, and a unique
`command_id`. A command whose cursor is stale SHALL receive a typed stale
denial; a replayed `command_id` SHALL receive a typed duplicate denial with the
original effect (at-most-once); a command against a Bundle holding another
writer's live control SHALL receive a typed busy denial. `answer` SHALL reuse
the existing typed human-response correlation; `cancel` SHALL reuse lifecycle
cancel; `pause_request` SHALL take effect only at the next committed boundary
and never claim a model/tool call was interrupted. Session snapshots SHALL
report exact bundle, generation, cursor, drive mode, stop policy, pause state,
and control ownership. A session snapshot SHALL also report the Bundle's pending human request as a
bounded projection carried from the Bundle's own checkpoint interrupt - the
request id, phase, mode, node-authored title and guidance, and advertised
options - so an operator can see exactly what a HITL stop is asking without
the caller rebuilding a prompt.
(`LDD-001`)

#### Scenario: Double-submit commits one boundary
- **WHEN** the same `advance_one` command id, or two commands sharing one
  expected cursor, race against the driver
- **THEN** at most one boundary commits, one caller sees success, and the other
  receives a typed duplicate or stale denial

#### Scenario: Pause honesty during a long node
- **WHEN** `pause_request` arrives while a node is executing
- **THEN** the session reports pause-requested, the node runs to its boundary,
  and the drive stops at the next committed boundary without fabricating an
  interruption
