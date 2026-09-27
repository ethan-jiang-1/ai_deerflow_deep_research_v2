# Design

## Context

The workbench is a Textual app in `scripts/demo_tui.py` that shares a shell with
the demo TUI. It reuses the shared `#inspect` pane, the shared pending indicator
(`_echo_input` starts a one-second timer that re-renders "已收到，正在处理…"),
the shared entry buttons, and the shared hint. The shared render path queries the
shared buttons by id, so they must stay in the DOM even when hidden. Terminal
size is not under our control, and the operator may be on an 80×24 window.

## Goals / Non-Goals

**Goals:**

- What the operator sees is true, actionable, and stable over time.
- The workbench is usable at common terminal sizes and honest when it is not.
- The verification method can catch this class of defect without a human.

**Non-Goals:**

- No driver/lifecycle/spec-behaviour changes beyond the workbench presentation
  clauses; no attempt to make 80×24 show every pane at once.

## Decisions

1. **The workbench state machine is explicit, not inherited.** `awaiting_hitl`,
   `paused_at_boundary` and `terminal` each map to a prompt line naming the next
   legal composer action; detach, cancel and a refused start render an explicit
   no-session posture. Alternative — leaving the last rendered posture on screen
   — rejected: a stale posture is indistinguishable from a live one, which is
   exactly what misled the operator.
2. **The shared pending indicator is stopped for workbench input.** The debug
   path clears `_last_typed`, stops the timer, and echoes the operator's input to
   the log. Alternatives: making the timer state-aware (spreads debug knowledge
   into shared code) or letting both write `#inspect` (they race; that was the
   bug).
3. **The shared entry buttons stay in the DOM but are hidden in the workbench.**
   The shared render path queries `#start-research`, `#accept` and `#cancel`; a
   first attempt that omitted them broke the render path and the app never
   reached Ready — recorded here so a future editor does not repeat it. Hidden is
   honest: they are inert in the workbench.
4. **Panes are on demand and bounded; the implementation declares 100×30 as its
   supported minimum, while the spec pins only the declare/report/degrade
   behaviour and the non-clipping invariant.** At 80×24 the operator keeps a readable log, the entries and the
   composer, the panes stay folded, and the hint states the limitation.
   Alternatives: cramming every pane into 24 rows (clips or starves the log), or
   refusing to start below the minimum (hostile for a read-only look).
5. **Slash commands clear the composer.** Otherwise the next Enter silently
   repeats the last command — the operator's "Enter to step" rhythm becomes an
   accidental `/detach`.
6. **Verification is part of the contract, not an afterthought.** Every
   checkpoint is asserted after a ≥1.3 s dwell (the UI's own timer period must be
   shorter than the assertion's patience), the layout is asserted at a degraded
   and a supported tier, and the operator-eye capture is recorded as the
   procedure for finding what assertions still miss.

## Risks / Trade-offs

- [Hidden-but-present shared buttons could be shown again by a future layout
  edit] → the tiered layout test asserts they are hidden in the workbench and
  still present in the DOM; the reason is documented in the code comment.
- [The dwell adds roughly a second per checkpoint to the harness] → accepted:
  the harness takes about twenty seconds instead of five, and it is the only
  thing that catches a one-second re-render.
- [Declaring a minimum could look like an excuse for a cramped small-size
  layout; keeping the number out of the spec could let it drift] → the degraded tier is explicitly tested (entries and composer usable,
  panes folded, limitation stated), so 80×24 stays honest rather than broken, and the reported minimum is asserted
  against the implementation's declared value.
