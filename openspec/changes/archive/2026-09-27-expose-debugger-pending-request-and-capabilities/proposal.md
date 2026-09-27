# Proposal

## Why

The operator reported the workbench as unusable for its actual purpose: after
`你能干什么` it stopped at a HITL prompt and the log said nothing about what was
being asked, so the tool read as stuck ("这是调试，应该什么都能做啊" / "要很好的
UX 的 debugger，别让我猜测"). Three concrete causes:

- **The request was invisible**: the workbench showed only "等待输入（直接输入回答）",
  never the node-authored title/guidance/options, and RED-014 forbids a pane from
  rebuilding a prompt - so the content had to come from the driver.
- **No posture-legal action list**: nothing stated what the operator could do at
  that moment, and there was no capability listing.
- **Capabilities were hidden**: the driver's `drive_until` and `pause_request` had
  no workbench entry at all, so RED-014's own "Start Step or Start Run" wording was
  not met.

Testing the exposure then found three real driver defects, all in spec'd
behaviour: `drive_until` never checked `stop_on_hitl` (one command re-entered the
waiting node until the 64-iteration cap - measured: 64 `_advance` calls), a pending
pause made `_drive_until` return nothing and crash its caller, and `_invoke_once`
cleared `pause_requested` after every commit so a pause requested during a run was
dropped.

## What Changes

- **The driver carries the request**: session snapshots gain an additive
  `pending_request` view (request id, phase, mode, node-authored title, guidance,
  advertised options) taken from the Bundle's own checkpoint interrupt, and
  populated on attach through a read-only checkpoint read.
- **The driver honours its own stop policy**: `drive_until` stops at a HITL
  boundary (`stop_on_hitl`), at a terminal, at a breakpoint, and at a pause request
  honoured at the next committed boundary; it never returns nothing, and a pause
  requested mid-drive is no longer cleared away.
- **The workbench stops making the operator guess**: the log states the request and
  its options, the prompt states the ask plus every action legal at that posture,
  `/help` lists the whole surface, and a `Start Run` button (plus palette action)
  joins `New Run` so both start compositions are reachable over one draft.
- **New commands**: `/run [node]` (drive_until, optional breakpoint) and `/pause`
  (pause_request, honestly refused at a terminal session).

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `local-workflow-debug-driving`: `LDD-001` snapshot projection gains the bounded
  pending-request view (additive).
- `research-demo-tui`: `RED-014` gains the ask/legal-actions, both-start-compositions
  and capability-listing clauses plus two scenarios.

## Impact

- Primary owners: `src/deerflow_deep_research/domain/debug_driving.py`,
  `runtime/debug_driver.py` (carry + stop policy), `scripts/demo_tui.py`
  (presentation and entries).
- Verification: driver matrix tests (17, including two regressions for the
  `stop_on_hitl` and pause-boundary defects), TUI tests (pending-request display,
  `/help`, Start Run + `/run` + `/pause`), and the journey harness (23 checkpoints,
  now including the request-aware HITL display and both start compositions).
- Measured gate state: `UV_OFFLINE=1 make verify` 0, `make tui-journey` 0 (23
  checkpoints), closeout gate 0, doc hygiene clean.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink; this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** the local debug driving surface
  (`domain/debug_driving.py` + `runtime/debug_driver.py`) for what a session
  reports and where it stops, and `scripts/demo_tui.py` for how that reaches the
  operator.
- **Seam classification:** wiring - the request is carried and projected, the stop
  policy is enforced, and presentation exposes it; no new authority, no new
  lifecycle effect, no prompt is rebuilt.
- **Question:** How does a debug run tell the operator exactly what it waits for and
  what they may do, and expose every capability it has, without inventing a second
  authority or a second prompt source?
- **Necessary adjacent/external contracts:** `LDD-001` owns the closed commands and
  the session snapshot (the additive field lives here); the Bundle's own checkpoint
  interrupt is the only request source; the lifecycle's `PendingInputProjection`
  stays untouched; `RED-014` owns the workbench surface.
- **Evidence seam:** the driver matrix (request carried, HITL stop, pause honoured,
  attach read), the TUI tests, and the journey harness checkpoints - all wired into
  `make verify` / `make tui-journey`.
- **Not in scope:** lifecycle/experience behaviour, the pending projection's own
  shape, node prompt authoring, and anything under `deerflow/`.
- **Triggered review policies:** none: driving-observation projection plus presentation, with no candidate, human judgment beyond the existing answer path, control fact, admission/recovery boundary, node-agent role, or lifecycle output change.
