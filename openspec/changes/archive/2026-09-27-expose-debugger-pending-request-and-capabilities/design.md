# Design

## Context

The workbench drives the real graph through the closed command set and renders
from `DebugSessionSnapshot`. The pending human request exists in the Bundle's
checkpoint interrupt (`pending_from_snapshot`) and is currently used only to sync
graph progress; RED-014 forbids panes from rebuilding prompts, so the content must
travel through the driver. `drive_until`'s stop policy (`StopPolicy`) already
declares `stop_on_hitl`, `stop_on_failure` and `stop_on_terminal`, and `LDD-001`
already requires `pause_request` to take effect at the next committed boundary.

## Goals / Non-Goals

**Goals:** the operator always knows what is being asked and what they may do; every
driver capability has a discoverable entry; the drive stops where its policy says.

**Non-Goals:** no new lifecycle authority, no prompt rebuilding, no changes to the
node-authored request shape or to the experience/gateway observer.

## Decisions

1. **Carry the request, never rebuild it.** `PendingRequestView` is projected from
   the checkpoint interrupt (`_pending_request_view`) on the invocation path and read
   once, read-only, on attach (`_read_pending_request`). Alternative — rebuilding a
   title/guidance in the pane — rejected: RED-014 forbids it and it would drift.
2. **The additive field rides the session, not eleven call sites.** `_snapshot`
   reads `session["pending_request"]`; alternative — threading a parameter through
   every `_snapshot` caller — rejected as churn without benefit. The field is
   additive, so existing readers are unaffected.
3. **`drive_until` stops at a HITL boundary and honours a pending pause at the next
   committed boundary.** Measured before the fix: one `drive_until` from a fresh
   session called `_advance` 64 times (the loop cap) because the HITL check was
   missing; measured after: one call. `_invoke_once` no longer clears
   `pause_requested`, because that silently dropped a pause requested while a
   boundary was in flight.
4. **The pause command is honest about a terminal session.** There is no next
   boundary, so the workbench says so instead of promising a pause point.
5. **Both start compositions over one draft.** `New Run` = Start Step, `Start Run` =
   Start Run (`open_start(mode="run")` + `drive_until`); `/run [node]` continues an
   existing session (optional breakpoint), and a session-less `/run` explains the
   start entries rather than failing silently.
6. **`/help` is the capability map**, so discoverability does not depend on reading
   a runbook.

## Risks / Trade-offs

- [Attach performs one extra read-only checkpoint compile] → accepted: attach is
  rare and the operator otherwise cannot see what a paused Bundle waits for; a read
  failure leaves the request unknown rather than failing the attach.
- [A long node-authored `context` could fill the log] → bounded to 400 characters
  with an explicit truncation marker.
- [Exposing `drive_until` makes it easy to blow past interesting boundaries] →
  `stop_on_hitl` and `stop_on_terminal` remain the defaults, and a breakpoint node
  is available through `/run <node>`.
