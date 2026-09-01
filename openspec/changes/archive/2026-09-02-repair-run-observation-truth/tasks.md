## 1. Baseline And Evidence

- [x] 1.1 Re-produce the dated evidence on this tree before edits: a durable
  `RunEvent` construction with `outcome="suspended"` fails validation, the live
  projection coerces it to `failed` (builder.py), and the store drops it silently;
  record the reproduction and the reader/writer inventory in `evidence.md`.
- [x] 1.2 Capture the red baseline: run the new real-store integration test and the
  new TUI exact-bind tests against the still-stale code and record at least one
  expected deterministic failure each before implementing.
- [x] 1.3 Run `python3 openspec/governance/check_project_gate.py --phase plan --change repair-run-observation-truth` from the repository root and verify exit 0, after registering RED-012 in the requirement registry.

## 2. Contract And Registry

- [x] 2.1 Register RED-012 in `openspec/governance/req-registry.yaml` (no other ID
  added, removed, or reassigned; `check_project_reqs.py` exits 0).
- [x] 2.2 Extend the persisted `RunEvent.outcome` closed set with `suspended`
  (schema version 3 unchanged, no new field/category), keeping the
  `budget_stop_reason`/`usage_tokens` outcome guards intact.
- [x] 2.3 Add `SUSPENDED = "suspended"` to the live `ObservationOutcome`
  vocabulary and stop `_record_node_event` from coercing `suspended` to `failed`
  in the live projection; unexpected exceptions keep `failed` +
  `internal.unexpected` + propagation.
- [x] 2.4 Bind the demo TUI live narration to the session's exact Bundle id from
  shared updates (`live_progress_lines`, `_render_live_activity`,
  `_last_model_call_state` via `find_bundle_dir`); no id degrades to static and
  reads nothing; remove `_latest_active_bundle` and the dead `_event_feed_lines`;
  narrate a suspended visit as awaiting recovery, not completed/failed.

## 3. Test Evidence Migration

- [x] 3.1 Add the real-store integration test: fixture graph node suspension ->
  `RunObservationRecorder`/store -> serialized `events.jsonl` -> runtime reader,
  asserting `started` then `suspended` with no `internal.unexpected`; sibling case
  proves a genuine unexpected exception persists `failed`/`internal.unexpected`
  and propagates; keep the fake-recorder wrapper test as local behavior evidence only.
- [x] 3.2 Add TUI narration isolation tests: two coexisting active/suspended
  bundles, narration bound to one exposes no fact of the other; unbound session
  performs no latest-scan read and stays static; a bound suspended visit is
  narrated as awaiting recovery and not counted completed; rewrite the tests that
  asserted the latest-scan selection (`picks_most_recent_active_bundle`,
  suspended-summary selection, `_last_model_call_state` latest variants).
- [x] 3.3 Run the focused seams: wrapper/unit store tests, the new integration
  test, and the demo TUI/adapter suites from `deep_research_harness/`, all green
  after implementation.

## 4. Closeout And Scope Proof

- [x] 4.1 Verify scope: `git diff --name-only` contains no public API, route/
  topology, checkpoint schema, dependency, or `deerflow/` change beyond the
  declared files; `git diff --submodule=short` shows no gitlink change.
- [x] 4.2 From `deep_research_harness/`, run `UV_OFFLINE=1 make verify` and verify
  exit 0.
- [x] 4.3 From the repository root, run `openspec validate repair-run-observation-truth --strict`, `python3 openspec/governance/check_doc_hygiene.py`,
  and `python3 openspec/governance/check_project_gate.py --phase closeout`;
  verify all exit 0.
- [x] 4.4 Sync the two deltas into their main capabilities (REJ-011 text; RED-012
  requirement + spec header + registry already registered), verify each main spec
  carries the synced text, and archive the change with the dated prefix; update
  the progressive plan ladder and §L with the real results.
