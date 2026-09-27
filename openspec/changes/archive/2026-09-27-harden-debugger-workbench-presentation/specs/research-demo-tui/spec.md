# Spec Delta

> req: RED-014

## MODIFIED Requirements

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
The workbench SHALL always state the current session posture and the next legal
composer action, and after a detach, a cancel, or a refused start it SHALL state
an explicit no-session posture instead of the previous session's posture. It
SHALL declare the minimum terminal size it supports and report that minimum to
the operator; on a smaller terminal it SHALL state the limitation and keep the
three entries, the composer, and the log usable. Opening the Node Context or
Files pane SHALL not clip pane content or reduce the log below a readable
height.
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

#### Scenario: The workbench never shows a stale session state
- **WHEN** an operator detaches, cancels, or is refused a start because another
  bundle is active
- **THEN** the workbench states an explicit no-session posture with the legal
  next actions instead of the previous posture

#### Scenario: Panes never starve the log or clip
- **WHEN** an operator opens the Node Context or Files pane
- **THEN** the pane shows its content and the log retains a readable height

#### Scenario: A small terminal degrades honestly
- **WHEN** the terminal is smaller than the declared supported minimum
- **THEN** the workbench reports that minimum and the limitation, keeps the
  entries and the composer usable, and clips no content
