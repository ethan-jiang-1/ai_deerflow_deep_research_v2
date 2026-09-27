# Proposal

## Why

The debugger workbench passed its automated checks while still handing the
operator a misleading screen. Three defects reached a human first:

- the shared one-second "已收到，正在处理…" indicator hijacked the workbench's own
  pane, so the operator never saw the HITL prompt and the tool looked stuck;
- after detach / cancel / a refused start the pane kept showing the previous
  session's posture (with a meaningless `下一节点: —`), so the operator could not
  tell whether a session was live;
- the first screen showed shared entry buttons that are inert in the workbench,
  a prompt line that always said "Enter a research question", and a hint that
  did not mention a single workbench command — while the Context/Files panes, once
  opened, squeezed the log to two rows on a 24-row terminal.

Root cause: the workbench's presentation was verified by assertions that ran
faster than the UI's own timers and only read widget text; nothing checked what
the operator sees over time, at a real terminal size, or after a state ends.
Feasibility of fixing that verification gap is now established (see Impact), so
this change formalises both the presentation contract and the verification
method it must satisfy.

## What Changes

- **Truthful session state**: the workbench states the current posture and the
  next legal composer action for `awaiting_hitl`, `paused_at_boundary` and
  `terminal`, and states an explicit no-session posture after detach, cancel or a
  refused start — never a stale one. The first debug screen is actionable.
- **Workbench-only controls**: the shared entry buttons (inert here) are hidden
  while remaining in the DOM for the shared render path; the hint documents the
  workbench commands.
- **On-demand, bounded panes**: the Node Context and Files panes stay folded
  until asked for, are height-bounded, and leave the log readable.
- **Declared supported minimum**: the workbench declares 100×30; below it, it
  states the limitation, folds the on-demand panes and keeps entries/composer
  usable instead of clipping or squeezing.
- **Slash commands clear the composer** so the next Enter is not an accidental
  repeat.
- **Verification method made mandatory** (the hard-won part): the journey harness
  performs a realistic dwell at every checkpoint, the layout tests run the
  workbench at 80×24 (degraded tier) and 100×30 / 120×45 (supported tier), and
  the operator-eye capture is the diagnostic of record for hunting anything the
  assertions still miss.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `research-demo-tui`: `RED-014` gains the truthful-state, on-demand-pane and
  declared-minimum clauses plus three scenarios (no stale state, panes keep the
  log readable, honest degradation).

## Impact

- Primary implementation: `deep_research_harness/scripts/demo_tui.py`.
- Verification: `scripts/tui_journey_probe.py` (dwell at every checkpoint),
  `tests/integration/test_demo_tui.py` (tiered layout visibility), and the
  operator-eye capture procedure recorded in
  `docs/testing-and-evaluation.md`.
- Feasibility evidence already gathered while probing (all measured directly):
  the hijack was reproduced headlessly before the fix; `make verify` 0,
  `make tui-journey` 0, closeout gate 0, doc hygiene clean; the 100×30 captures
  show the truthful postures, and the 80×24 captures show the size notice.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink; this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/demo_tui.py`,
  which owns the workbench's presentation and its operator-facing state machine.
- **Seam classification:** wiring — presentation and layout only; the debug
  driver, lifecycle, admission and authority boundaries are unchanged.
- **Question:** How can the workbench show the operator what is actually true and
  actionable — over time, at a real terminal size, and after a session ends —
  without constraining the driver or inventing a second authority?
- **Necessary adjacent/external contracts:** `research-demo-tui` `RED-014` owns
  the workbench surface this change refines; `DebugSessionSnapshot.posture`
  answers the truthful state; `NodeContextView` and `OperatorWorkspaceReader`
  answer the pane contents; the shared pending indicator
  (`_echo_input`/`_tick_pending`) answers the hint that must not take the pane.
- **Evidence seam:** the journey harness's post-dwell assertions, the tiered
  layout visibility tests, and the operator-eye pane capture recorded as the
  diagnostic procedure — all wired into `make verify` / `make tui-journey`.
- **Not in scope:** driver or lifecycle behaviour, the persisted projections, the
  demo CLI's ambient-workspace coupling (filed separately as BUG-072), embedded
  real-graph semantics, and anything under `deerflow/`.
- **Triggered review policies:** none: presentation truthfulness, layout and verification coverage only, with no candidate, human judgment, control fact, admission/recovery boundary, node-agent role, or lifecycle output change.
