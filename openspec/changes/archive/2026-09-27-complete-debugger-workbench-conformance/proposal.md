# Proposal

## Why

The debugger workbench's documented surface is only partially implemented. The
most visible gap is the entry itself: the bare invocation
(`./run/tui-workflow-debugger.sh`) reaches Gateway mode with no profile and
fails with "A selected local Gateway profile is required." instead of the
composition chooser RED-013 requires. The workbench's core value — seeing what
a node actually did — is still a log line rather than the RED-014 Node Context
pane with its fixed coverage strip, attach takes a hand-pasted bundle id with no
candidate or posture surface, and the command palette does not exist. BUG-071
tracks all of it; this change implements it.

## What Changes

- **Composition chooser (RED-013)**: a bare launcher invocation presents a
  composition chooser (fixture debugger / embedded smoke / Gateway profile) and
  forwards the matching flags; non-interactive invocations take a documented
  default; `--fixture` / `--embedded-smoke` still pre-select.
- **Node Context pane (RED-014)**: a dedicated pane (replacing the log dump)
  renders the selected frame's node-agent invocations with the fixed coverage
  strip derived from `NodeContextView` (INITIAL CAPTURED, RUNTIME ENFORCED,
  ACTIVITY BOUNDED, OUTCOME OBSERVED/UNAVAILABLE, FILES CURRENT, raw provider
  histories NOT RETAINED), and states coverage honestly when empty.
- **Attach candidates and postures (RED-014)**: the Attach entry presents a
  bounded operator-view candidate list (never a silent "latest"), validates each
  candidate through the lifecycle before use, and shows the busy / read-only /
  takeover posture derived from the control lease.
- **Command palette entries (RED-014)**: New Run / Attach / Replay become command
  palette actions that dispatch the same typed methods as the buttons and slash
  commands.
- **Files pane (RED-014)**: a Files pane consumes `OperatorWorkspaceReader`
  typed pages instead of exposing host paths.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. RED-013 and RED-014 already require this surface; this change implements
  them (conformance, `skip_specs`). Any wording adjustment to RED-013's chooser
  clause is a spec-semantics question and is out of scope here.

## Impact

- Primary implementation: `deep_research_harness/run/tui-workflow-debugger.sh`
  (chooser), `deep_research_harness/scripts/demo_tui.py` (panes, palette,
  candidates).
- Verification: `scripts/tui_journey_probe.py` gains per-item assertions, and
  `make tui-journey` stays wired into `make verify`; the launcher chooser is
  tested through the existing `DEBUGGER_PYTHON` argv seam.
- Ledger: BUG-071 closes when every item lands; the deferred mechanism-level
  borrow items stay in `_backlog/todos/todo-adopt-framework-engineering-protocols.md`.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink; this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/demo_tui.py`
  (workbench panes, entries, palette) and `run/tui-workflow-debugger.sh` (the
  composition chooser that RED-013 owns).
- **Seam classification:** wiring — the driver, lifecycle, admission, and
  authority boundaries are unchanged; this change completes presentation and
  entry surfaces over already-specified behaviour.
- **Question:** How can the documented workbench surface be completed without
  creating a second authority, scanning for a "latest" bundle, or leaking host
  paths?
- **Necessary adjacent/external contracts:** `research-demo-tui` RED-013/RED-014
  own the required surface; `NodeContextView` (domain/node_context.py) answers
  the coverage labels; `runtime/workspace_reader.py` answers the bounded Files
  pages; `ControlLease` snapshots answer the attach postures; `_backlog` BUG-071
  answers the deferred-face inventory.
- **Evidence seam:** `make tui-journey` asserts the chooser's forwarded flags,
  the pane's existence and strip labels, the candidate postures, palette
  dispatch, and Files pages — all headless through the real script entry.
- **Not in scope:** runtime/lifecycle API additions (candidates stay an operator
  view validated through existing APIs), spec wording changes, embedded/real
  debug driving (deferred B1), and anything under `deerflow/`.
- **Triggered review policies:** none: presentation and entry-surface conformance with no candidate, human judgment, control fact, admission/recovery boundary, node-agent role, or lifecycle output change.
