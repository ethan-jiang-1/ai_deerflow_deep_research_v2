## Why

The observation surface (C3, archived 2026-09-02) can show what happened but
cannot drive: a local contributor/operator still has no legal way to step one
node boundary, continue to a breakpoint, pause, attach a recoverable Bundle
without advancing it, or detach — while keeping second writers, orphan
natural-resume, and concurrent debuggers fenced out. Today the only paths are
`BundleGraphExecutor`'s natural resume (runs to terminal) and per-run
execution exclusion, none of which express intentional boundary ownership. The
progressive plan gate (C4a) requires a headless, interface-tested debug drive
surface before any Textual wiring (C4b).

## What Changes

- Add a new `local-workflow-debug-driving` capability owning: the closed
  `DebugCommand` set (`advance_one`, `drive_until`, `pause_request`, `answer`,
  `cancel`, `detach`) with exact-bundle/expected-cursor/command-id
  idempotency; `DebugSessionSnapshot` and typed denials; the headless
  `DebugRunDriver` (open_start/open_attach/execute over the existing
  `BundleGraphExecutor`, same recipe/compile path, per-invocation
  `interrupt_after`); an expiring Bundle-local debug control lease (owner,
  generation, TTL, heartbeat, stale detection, CAS takeover) that fences
  natural resume and second debuggers while leaving observers unaffected;
  start-composition semantics (Start Step = open + exactly one advance of
  bootstrap; Start Run = open + drive_until); boundary detach; restart
  recovery from durable checkpoints with started-without-outcome uncertainty;
  and a topology guard asserting one logical visit per superstep.

## Capabilities

### New Capabilities

- `local-workflow-debug-driving`: LDD-001 session/commands/cursor contract;
  LDD-002 control lease and fencing; LDD-003 advance/drive execution
  semantics; LDD-004 attach/ detach/restart recovery; LDD-005 topology guard.

### Modified Capabilities

None. `research-graph-lifecycle` REG-023 natural `ContinueRun` keeps its
meaning and is fenced (typed busy) only while a live debug control lease
exists; observation inspection stays unaffected by the lease.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/` owns `DebugRunDriver`, the control lease, and their contracts' implementations; `domain/` owns the typed command/session models.
- **Seam classification:** deterministic-guardrail control surface; no model-visible change.
- **Question:** how can one headless driver advance the real graph boundary-by-boundary with at-most-once semantics, legal pause ownership, and recovery, without becoming a second lifecycle authority or a step-only topology?
- **Necessary adjacent/external contracts:** REG-023 (natural resume fenced, not redefined); `local-workflow-debug-observation` (driver reads cursors via the projector; lease state is a session projection, not a TraceFrame fact); Bundle lifecycle admission and suspension truth.
- **Evidence seam:** headless fixture matrix — start admission, fixture step-through (≥9 boundaries), HITL suspended segment + typed answer, mode switch (step→run→pause→step), post-node breakpoint, intentional pause vs orphan resume, attach listing/busy/takeover CAS, boundary crash and mid-node crash recovery, double-click idempotency, long-node TTL fencing, detach semantics, two-process competition.
- **Not in scope:** Textual panes/slash commands/launcher (C4b), Gateway remote driving, breakpoint persistence, State mutation, checkpoint fork, observation-schema changes.
- **Triggered review policies:** authority-and-projections, change-admission, control-placement, participant-outcomes, local-context

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Who may advance a paused-debug Bundle | operator chooses step/continue | expiring debug control lease + per-invocation execution exclusion | non-bypassable | TTL expiry alone never grants takeover; CAS on generation/cursor | removes orphan-takeover ambiguity and double-writer races | two-process + TTL + crash fixtures |
| Where drive stops | operator sets breakpoint/stop policy | driver stop policy over checkpoint truth | non-bypassable | same graph/recipe/saver; no step topology | no second execution loop | fixture step/mode-switch/breakpoint matrix |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Debugger dies at boundary | durable checkpoint + stale lease | CAS attach after TTL + no live exclusion | paused-at-boundary restored | attach and continue; no auto advance | boundary-crash fixture |
| Debugger dies mid-node | unmatched started fact | existing lifecycle/work-unit recovery | uncertain, not completed | recovery rules converge | mid-node-crash fixture |
| Duplicate/stale command | expected cursor + command id | typed duplicate/stale denial | at-most-once commit | operator re-issues with fresh cursor | double-click fixture |
| Natural resume vs live debug lease | lifecycle admission | typed busy denial while lease live | resume refused, not lost | retry after detach/TTL | orphan-resume fencing fixture |

## Impact

- Apply adds runtime driving modules + tests and domain command/session
  models; registers LDD-001..005; creates
  `openspec/specs/local-workflow-debug-driving/spec.md` at sync. No public
  Gateway surface, no topology/route change, no `deerflow/` change.
