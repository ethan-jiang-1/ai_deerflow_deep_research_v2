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
an explicit no-session posture instead of the previous session's posture. The
Node Context and Files panes SHALL be on demand — folded until the operator asks
for them and bounded so the log keeps readable room. The workbench SHALL declare
a supported minimum terminal size and, below it, state the limitation while
keeping the entries and the composer usable rather than clipping content or
silently squeezing the log.
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

#### Scenario: Panes are on demand and the log keeps its room
- **WHEN** an operator opens the Node Context or Files pane
- **THEN** that pane appears with its content while the log retains readable
  height at the supported minimum size

#### Scenario: A small terminal degrades honestly
- **WHEN** the terminal is below the workbench's declared supported minimum
- **THEN** the workbench states the limitation, keeps the entries and composer
  usable, and folds the on-demand panes instead of clipping content
