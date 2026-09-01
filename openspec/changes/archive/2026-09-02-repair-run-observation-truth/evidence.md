# C0 Execution Evidence (append-only)

## Task 1.1 — dated evidence re-produced on this tree (2026-09-02)

Durable construction with a fully populated v3 node event:

```
RunEvent(schema_version=3, sequence=1, timestamp=..., category='node',
         generation=0, phase='hitl1', outcome='suspended')
-> ValidationError: outcome
   Input should be 'started', 'completed' or 'failed' [type=literal_error, ...]
```

- Emitter: `graph/builder.py` `_node_wrapper.observed_run` emits
  `outcome="suspended"` on `GraphInterrupt` (BUG-063 comment) to the durable
  recorder; the live projection receives `"failed"` via the coercion at
  `_record_node_event` (`outcome if outcome in {"started", "completed", "failed"}
  else "failed"`).
- Drop path: `runtime/run_observation.py` `_bundle_record_event_sync` constructs
  `RunEvent(...)` and swallows the `ValueError` locally (`except ValueError:
  return`) — the event never reaches `events.jsonl` and does not increment
  `persistence_failure_count`.
- Live vocabulary: `runtime/events.py::ObservationOutcome` has no `suspended`
  member; `tests/live/test_gateway_forwarding_proof.py` pins the live protocol's
  permitted set (separate from `RunEvent`).
- Fake-only proof gap: `tests/graph/test_node_wrapper.py::_JournalRecorder`
  stores raw kwargs and cannot see the model-level drop; no test asserted the
  persisted three-value set.

## Task 1.1 — reader/writer inventory (delegated read-only audit, 2026-09-02)

Writers (durable): `runtime/run_observation.py` constructors at :332 (ADMISSION,
outcome=None), :392 (LIFECYCLE/TERMINAL, outcome="completed"), :523 (generic,
producer-supplied); public writers `record_event` (:192) and
`RunObservationRecorder.record` (:1049); producer seam
`domain/invocation.py:57` (`RunEventRecorderProtocol.record`, open `str | None`).
Producers: `graph/builder.py` :146/:221/:322(suspended)/:333(failed);
`runtime/node_agent_bridge.py` :320/:682/:742 (MODEL_TOOL
started/completed/failed); outcome-less node facts (work_units, wave0 validation,
final_delivery, targeted_evidence, readiness) and wave1 review failure
("failed").

Readers/consumers: `domain/run_observation.py` :317/:324 outcome guards
(MODEL_TOOL-only fields — never interact with NODE suspended);
`runtime/run_observation.py` :131 (category-only), :737 (eviction priority
outcome-blind), :929 (`_read_lines` → `model_validate_json`; unknown values fail
the journal read as unavailable — the declared pre-change-reader behavior);
`scripts/_inspect_view.py` :48 (verbatim, honest); `scripts/demo_tui.py`
:307/:314/:331/:346/:476/:531/:567/:1207/:1622 (live narration; suspended today
invisible or coerced-failed); `scripts/soft_bundle.py` :356/:359/:398/:413
(counts NODE/TERMINAL completed only — suspended-not-completed is correct);
`scripts/experiments/tui_trace.py` :70 (count/keys only). Attach listing
(`_scan_recoverable_run`, demo_tui :1312) uses the lifecycle workbench
`discover()` — no latest scan, no outcome interpretation. `_event_feed_lines`
(demo_tui :507) calls `_latest_active_bundle` but has no production caller
(dead helper, removed by this change).

Live protocol consumers: `tests/unit/test_events.py` parametrizes node outcomes
over the live protocol (not RunEvent); `tests/live/test_gateway_forwarding_proof.py:64`
pins the live permitted set — updated in the same cutover.

Schema/version policy (REJ-002 + REJ-011, `openspec/specs/run-event-journal`):
v3 is the only reader-accepted version; REJ-011 binds "existing fields and
schema version SHALL be reused; no new event category". The change is therefore
a value-level extension of the v3 outcome enumeration with no version bump and
no migration.

Compatibility declaration (design D1): new code reads old journals unchanged.
Pre-change readers fail a new suspended line at `model_validate_json` → journal
read becomes unavailable (existing closed behavior for unreadable records).
Local coordinated cutover in one commit; rollback = revert; no data migration.

## Task 1.2 — red baseline

Recorded after the red tests are written (see task 3.1/3.2 results below).

## Task 1.2 — red baseline captured (2026-09-02, before implementation)

`pytest tests/integration/test_suspended_journal_truth.py tests/graph/test_node_wrapper.py
tests/integration/test_demo_run_update_adapters.py tests/integration/test_demo_tui.py -q`
→ **7 failed, 82 passed**, all seven being the new falsifiable expectations:

1. `test_human_interrupt_suspension_persists_as_suspended_not_failure` — real fixture
   transport/store run: hitl1 attempt has no `suspended` outcome (dropped by the
   `ValueError` swallow), so the persisted round-trip assertion fails.
2. `test_projection_keeps_suspension_distinct_from_failure` — live projection emits
   `"failed"` (coerced) instead of `"suspended"`.
3-5. `live_progress_lines` signature/bind tests — no `bundle_id` keyword, unbound call
   still scans, isolation assertions impossible.
6. `_last_model_call_state` bound-directory form.
7. `test_live_progress_lines_narrates_a_suspended_visit_as_awaiting_recovery` — no
   awaiting-recovery narration exists.

## Section 3 — green run (2026-09-02, after implementation)

- Implementation: `RunEvent.outcome` Literal + `suspended` (v3 unchanged);
  `ObservationOutcome.SUSPENDED` + `_LIVE_OUTCOMES["node"]`; `_record_node_event`
  projection passes `suspended` through (closed set, no relabel); demo TUI live
  narration binds `self._session_bundle_id` from shared updates (Ready resets),
  `live_progress_lines(root, bundle_id=...)` / `_last_model_call_state(bundle)` /
  `_render_live_activity` resolve via `find_bundle_dir` only; `_latest_active_bundle`
  and dead `_event_feed_lines` deleted; suspended visit narrated as
  `（待恢复）`/`⏸ 暂停，等待恢复`, never completed/failed.
- `pytest tests/integration/test_suspended_journal_truth.py tests/graph/test_node_wrapper.py
  tests/integration/test_demo_run_update_adapters.py tests/integration/test_demo_tui.py
  tests/unit/test_run_observation_store.py tests/unit/test_events.py
  tests/unit/test_bundle_graph_journal.py -q` → **181 passed** (red seven now green;
  real fixture transport/store run returns hitl1 started→suspended with no
  internal.unexpected; serialized events.jsonl carries the closed value; narration
  isolation/unbound-static/awaiting-recovery all proven).
- `pytest tests/integration tests/graph tests/contract -q` → 1424 passed, 4 skipped;
  the single failure `test_production_wheel_excludes_fixture_package` is the
  pre-existing sandbox denial of `uv build` cache (`~/.cache/uv` Operation not
  permitted), already recorded in plan §L 2026-08-31 as environmental — reproduced
  identically on untouched trees; `make verify` (the gate) remains the authority.
- Live protocol pin updated: `tests/live/test_gateway_forwarding_proof.py` accepts
  `suspended` in the redaction assertion (test file; not part of make verify lanes).
