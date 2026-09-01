> req: RED-013, RED-014

## ADDED Requirements

### Requirement: Canonical launcher entry reaches the debugger workbench

The repository SHALL ship an executable `run/tui-workflow-debugger.sh` that
resolves the harness root from any working directory without dependency
sync/install and without Bundle discovery or lifecycle logic. With no arguments
it SHALL start the debugger TUI composition chooser; `--fixture` and
`--embedded` SHALL pre-select the composition; `--attach <bundle_id>` and
`--replay <bundle_id>` SHALL carry explicit intent that the TUI and lifecycle
still validate; `--help` SHALL print usage and the equivalent Make commands;
unknown flags SHALL exit non-zero with usage. The launcher SHALL NOT scan the
workspace, select a latest Bundle, read checkpoints, or acquire leases.
(`RED-013`)

#### Scenario: Explicit intents reach the validated workbench
- **WHEN** an operator runs the launcher with `--fixture`, `--embedded`,
  `--attach <id>`, or `--replay <id>` from an arbitrary cwd
- **THEN** the debugger workbench starts with the requested composition or
  intent, and every Bundle reference is validated by the lifecycle before use

#### Scenario: Unknown flags fail without starting the TUI
- **WHEN** the launcher receives an unknown flag
- **THEN** it prints usage and exits non-zero without starting a session

### Requirement: Workbench opens with three entries and a Node Context pane

The debugger workbench first screen SHALL present three explicit entries — New
Run (Start Step or Start Run over a validated question draft), Attach (bounded
lifecycle-verified candidates with busy/read-only versus takeover postures),
and Replay (read-only) — normalized so buttons, command palette actions, and
slash commands produce the same typed adapter action. The workbench SHALL
present a Node Context pane listing the selected frame's node-agent invocations
from the C3 context inspector with the fixed coverage strip, and SHALL consume
`OperatorWorkspaceReader` typed pages in the Files pane. No pane SHALL scan the
workspace for a latest bundle, rebuild prompts, or expose host paths.
(`RED-014`)

#### Scenario: Three entries are explicit and equivalently reachable
- **WHEN** an operator triggers New Run, Attach, or Replay by button or by
  slash command
- **THEN** both paths normalize to the same typed adapter action and produce
  the same update or typed denial

#### Scenario: Node Context pane discloses coverage honestly
- **WHEN** an operator opens the context pane for a frame with captured
  invocations
- **THEN** invocations list from the C3 context store with the coverage strip
  (INITIAL CAPTURED, RUNTIME ENFORCED, ACTIVITY BOUNDED, OUTCOME
  OBSERVED/UNAVAILABLE, FILES CURRENT) and raw provider histories marked
  NOT RETAINED
