## ADDED Requirements

### Requirement: Scripted-real run publishes its terminal observation into the bundle journal

The debug command SHALL publish a terminal lifecycle observation into the completed
run bundle's journal so that `diagnostics/run-summary.json` reflects the terminal
state (status, phase, generation, terminal outcome) and the journal contains the
matching terminal event, exactly as the demo entry-point experience wrapper does for
fixture-graph and real runs. The operator workflow drives the public tool surface
directly and therefore SHALL perform this publication itself, through the existing
observation publisher, using only the trusted run bundle and scope already resolved
by the command. The publication SHALL remain observation-only: it SHALL NOT change
Bundle State, lifecycle authority, or any control result. (`SCR-006`)

#### Scenario: Completed run reaches a terminal journal summary
- **WHEN** the baseline scripted-real command completes with terminal status `completed`
- **THEN** the run bundle's `run-summary.json` reports `status=completed` with the
  terminal phase and the journal contains a terminal completed event, so a subsequent
  read-only inspection reports the terminal observed summary

#### Scenario: Blocked run publishes its blocked terminal observation
- **WHEN** the repair-targeted scripted-real scenario completes with terminal status `blocked`
- **THEN** the run bundle's journal summary reports the blocked terminal state with the
  matching terminal event

#### Scenario: Publication never alters lifecycle authority
- **WHEN** the command publishes the terminal observation
- **THEN** Bundle State, the lifecycle result, and the command's exit behavior are
  unchanged by the publication
