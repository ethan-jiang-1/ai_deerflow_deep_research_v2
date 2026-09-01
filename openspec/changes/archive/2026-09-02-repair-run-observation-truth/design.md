## Context

See `proposal.md`. Verified current chain (2026-09-02, re-produced on this tree):

1. `graph/builder.py` `_node_wrapper.observed_run` emits `outcome="suspended"`
   on `GraphInterrupt` to the durable recorder, and `outcome="failed"` (coerced
   at the projection boundary, builder.py line 69) to the live observation
   projection.
2. `domain/run_observation.py` `RunEvent.outcome` is
   `Literal["started", "completed", "failed"] | None` (schema version
   `Literal[1, 2, 3]`, persisted as v3), so the durable suspension is dropped by
   a silent `except ValueError: return` inside `_bundle_record_event_sync`
   (runtime/run_observation.py) — it does not reach `events.jsonl` and does not
   count as a persistence failure.
3. REJ-011 (accepted) already requires the journal to distinguish suspension,
   reusing existing fields and schema version. The persisted model simply never
   implemented it; the fake-recorder test at `tests/graph/test_node_wrapper.py`
   cannot see the model-level drop.
4. `scripts/demo_tui.py` live narration (`live_progress_lines`,
   `_render_live_activity`, `_last_model_call_state`) selects its source via
   `_latest_active_bundle` — the most recently updated active/suspended bundle
   in the whole workspace. The attach candidate listing (`_scan_recoverable_run`)
   already goes through the lifecycle workbench and does not use this scan.

## Goals / Non-Goals

**Goals:**

- Make the persisted journal carry suspension truth exactly as REJ-011 already
  requires: closed value `suspended`, existing v3 fields/version, durable
  round trip proven through the real store.
- Make the live observation projection carry the same fact (no relabel to
  `failed`), via the existing live outcome vocabulary.
- Bind live narration to the session's exact Bundle and fail closed (static)
  without an id; narrate a suspended visit as awaiting recovery.
- Prove the coordinated cutover with an enumerated reader/writer inventory and a
  red/green integration test through the real store.

**Non-Goals:**

- No schema version bump, no new event category, no migration (REJ-002/REJ-011).
- No retention priority changes (C3 owns finalized-node-fact retention).
- No TraceFrame/projector, driving, lease, or attach-listing behavior change.
- No change to `soft_bundle.py` completion verification semantics (a suspended
  visit is not a completed visit; resume/re-completion remains the owner).

## Decisions

### D1. Value-level extension on schema v3 with a declared local coordinated cutover

`RunEvent.outcome` becomes
`Literal["started", "completed", "failed", "suspended"] | None`. The live
vocabulary `runtime/events.py::ObservationOutcome` gains `SUSPENDED = "suspended"`,
and `_record_node_event`'s projection passes `suspended` through instead of
coercing. No version bump, no new category, no field — REJ-011 binds this
explicitly.

Reader/writer inventory (full list in `evidence.md`): durable writers are the
three `RunEvent` constructors in `runtime/run_observation.py` fed by
`RunObservationRecorder.record` / `record_event`; producers are
`graph/builder.py` (node started/completed/suspended/failed),
`runtime/node_agent_bridge.py` (model/tool started/completed/failed), and
outcome-less node facts (work units, validation, readiness, targeted evidence).
Durable readers all go through `_read_lines` → `RunEvent.model_validate_json`;
live consumers are the projection streams and the demo TUI narration. After this
change every in-repo reader accepts `suspended`; suspended is only ever emitted
with `category=NODE` and never with model-tool-only fields (the
`budget_stop_reason`/`usage_tokens` cross-field validators keep their existing
outcome guards, so no interaction arises).

Compatibility declaration: new code reads old journals unchanged (no migration).
Pre-change readers reject a new suspended line at `model_validate_json`, which
fails that journal's read as unavailable — the same closed behavior the journal
already defines for unreadable records. This is a local coordinated cutover in one
commit: every reader/writer ships together, the rollback is reverting the commit,
and no retained data migration exists in either direction.

### D2. Live narration exact-binds the session Bundle and fails closed

The TUI records the latest Bundle id carried by its shared updates
(`snapshot.bundle_id`) as the session narration id. `live_progress_lines`,
`_render_live_activity`, and `_last_model_call_state` resolve that id through the
existing `find_bundle_dir` and read only that journal; with no id they return
nothing so the heartbeat stays static. `_latest_active_bundle` loses its live
narration role and is deleted together with the dead `_event_feed_lines` helper.
The startup attach listing (`_scan_recoverable_run`, RED-011) is untouched.
A suspended node visit renders in narration as awaiting recovery and is not
counted as completed.

### D3. Evidence: real store round trip replaces fake-only proof

The integration test drives a fixture-graph node into `GraphInterrupt`, through
`RunObservationRecorder`/`RunObservationStore`, and asserts the serialized
`events.jsonl` and the runtime reader expose `started` then `suspended` with no
`internal.unexpected`; a sibling assertion proves a genuine unexpected exception
still persists `failed` + `internal.unexpected` and propagates. The fake-recorder
unit test remains as a wrapper-behavior test only. TUI adapter tests prove
isolation (two bundles, narration shows only the bound one), unbound static
behavior (no scan read), and the suspended narration line.

## Risks / Trade-offs

- **[Risk] Extending a persisted closed set breaks an unknown out-of-tree
  reader.** -> Declared in D1: pre-change readers already fail closed on unknown
  records; the repo has no other consumer, and the value is additive on v3.
- **[Risk] Live narration binding hides progress if updates lack a Bundle id.**
  -> The heartbeat already degrades to a static message today when no bundle is
  readable; the bound path only narrows the source, and the first Working update
  carries the id in every real dispatch.
- **[Risk] Suspended narration is misread as completion.** -> The progress chain
  counts only `completed`; suspended renders as an explicit awaiting-recovery
  marker, and the checkpoint remains the only commit authority.
- **[Risk] Removing `_latest_active_bundle` breaks an unknown caller.** -> The
  inventory enumerated all callers (live narration only); attach listing never
  used it, and tests cover the remaining paths.

## Migration Plan

1. Red: integration test expects `started -> suspended` in a real store run and
   fails on current code (silent drop); TUI tests expect exact-bind narration and
   fail on the latest-scan.
2. Extend `RunEvent.outcome`, `ObservationOutcome`, the projection mapping, and
   the narration binding; delete the dead helpers.
3. Green: focused unit/integration/graph tests, then the full gate; sync the two
   deltas and archive.

No data migration; revert is the rollback.
