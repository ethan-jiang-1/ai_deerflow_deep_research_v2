# Tasks: wave1-question-handoff-and-critic-observability

Declared order: ws1-critic-observability, then ws2-question-handoff. Each task pairs
changed behavior with a red-before-green deterministic test and its narrowest
verification command. All commands run from `deep_research_harness/`.

## Registry

- [x] 1. Confirm the four pending requirement IDs are registered in
  `openspec/governance/req-registry.yaml` with descriptions matching the deltas
  (REJ-008, WON-013, WSN-009, TEL-007 were registered at proposal time; WON-004 and
  WON-012 descriptions were updated for the modified contracts). Correct any drift
  before touching implementation.
  Done: `python3 openspec/governance/check_project_reqs.py .` passes.

## WS1: critic observability (BUG-029)

- [x] 2. RED — add `tests/integration/test_wave1_work_units.py` cases: scripted
  invalid claim-verifier payload asserts exactly one `post_candidate` VALIDATION
  Journal fact (canonical code, `critic_kind="claim_verifier"`, work/attempt
  correlation) via a recorder spy; scripted critic invocation failure asserts one
  closed MODEL_TOOL failed fact; recorder `None` and recorder raising keep the
  existing dispatch behavior. Add the `_canonical_critic_code` mapping table test in
  `tests/unit/test_wave1_review.py`. Run
  `UV_OFFLINE=1 .venv/bin/python -m pytest tests/integration/test_wave1_work_units.py tests/unit/test_wave1_review.py -q`
  and confirm the new cases fail on missing events.
- [x] 3. GREEN — thread `event_recorder` through `graph/nodes/wave1/node.py` →
  `build_wave1_gate_review` → `_dispatch_missing_reviews`; emit the two fact kinds
  with the closed canonical-code mapping; wrap recording like `_observe_validation`
  (never crash the gate path). Re-run the Step 2 command until green.
- [x] 4. GREEN — add `RunEvent.critic_kind` (`source_diagnostic` | `claim_verifier`,
  optional) with the validator constraint (only wave1 `post_candidate` VALIDATION
  facts, schema version 3); extend the `RunEventRecorderProtocol.record` keyword in
  `domain/invocation.py` and the `record_event` / sync-writer passthrough in
  `runtime/run_observation.py`; unit cases for allowed/forbidden placements in
  `tests/unit/test_events.py` or the owning journal test file. Run
  `UV_OFFLINE=1 .venv/bin/python -m pytest tests/unit/test_events.py tests/integration/test_observation_lifecycle_separation.py -q`.

## WS2: question handoff (BUG-028)

- [x] 5. RED — rewrite
  `tests/integration/test_wave1_work_units.py::test_real_wave1_review_gate_enforces_question_floor_and_review_integrity`
  to the new contract: `targeted_search` routes `pass` (no question rule), the gate
  adapter writes the bounded `wave1_open_questions` projection (id + work id refs
  only, no question text), an empty review clears it, and the over-bound projection
  raises `wave1_open_question_projection_overflow`; keep the review-integrity
  assertions. Add adapter-level projection cases (empty, overflow, non-gate writer
  rejected) and a worst-case serialization case: 64 maximum-length refs over a
  representative post-wave1 state stay under `MAX_CHECKPOINT_STATE_BYTES`. Run
  `UV_OFFLINE=1 .venv/bin/python -m pytest tests/integration/test_wave1_work_units.py tests/unit/test_state_contracts.py tests/unit/test_state_bounds.py -q`
  and confirm red on the projection behavior.
- [x] 6. GREEN — `domain/wave1.py` `Wave1OpenQuestionRef {question_id, work_id}` +
  additive `Wave1GateReviewRow.open_questions` filled by `review.py`; `domain/state.py`
  `wave1_open_questions` field with `unresolved_gaps`-mirrored GATE ownership;
  `graph/nodes/gate_adapter.py` Wave1 projection branch (64-entry cap, fail closed).
  Re-run the Step 5 command until green.
- [x] 7. RED — add `tests/graph/test_wave2_synthesis_real.py` cases: the synthesis
  prompt renders the resolved id-and-text assignment when the projection is
  non-empty and the text read resolves from accepted Wave1 result documents; a
  projected id with no resolvable text fails with `synthesis_question_coverage_invalid`
  before any model call; the coverage validator rejects a missing, duplicated,
  cross-referenced, or foreign question id; a repaired draft closes coverage; an
  empty projection is a no-op; legacy artifacts without the new fields still
  validate. Run
  `UV_OFFLINE=1 .venv/bin/python -m pytest tests/graph/test_wave2_synthesis_real.py -q`
  and confirm the new cases fail.
- [x] 8. GREEN — `domain/synthesis.py` `GapRecord.source_questions` and
  `SynthesisResult.resolved_questions` (bounded, sorted, unique, `q:w1_` pattern);
  `SynthesisBundleStoreProtocol.read_wave1_open_questions` plus its
  `runtime/work_unit_store.py` implementation (load accepted WAVE1 records, read
  full result docs bounded by `MAX_RESULT_BYTES`, validate
  `Wave1SourceIntakeResult`, return sorted `(question_id, question)` pairs);
  `prompts.py` assignment block and output contract; `node.py` resolves the
  projection text, passes the id-and-text assignment to the prompt and the ids to
  the coverage step of `_validate_synthesis_semantics` (existing one-shot repair and
  exhausted terminal stay the only recovery owners). Re-run the Step 7 command until
  green.
- [x] 9. RED — add targeted_evidence gate-view conformance cases (non-empty gap visit
  returns the reconciled view; empty-gap visit returns a drained view; reserved key
  never reaches checkpoint) at the lowest graph seam (extend
  `tests/graph/test_wave2_synthesis_real.py` or a focused targeted_evidence test
  file). Run the file's pytest and confirm red on
  `work_unit_gate_view_inconsistent` for the routed visit.
- [x] 10. GREEN — `graph/nodes/targeted_evidence/subgraph.py` returns the component
  result (gate view included) and `node.py` returns
  `WORK_UNIT_GATE_VIEW_KEY` plus `{"route": "next"}` on every visit: the
  component-built reconciled view for gap visits, and the canonical empty drained
  `WorkUnitGateView` for gap-less visits (the shared component's 1..32 intent bound
  rejects zero intents by contract; the empty view is the node-local degenerate
  case). Re-run the Step 9 command until green.
- [x] 11. GREEN — scripted-real repair/targeted named case: extend the fixed scenario
  in `src_fake/deerflow_deep_research_fixtures/scripted_real/baseline.py` (or its
  registered sibling) and `tests/integration/test_scripted_real_workflow_debug.py`
  with a run that carries one `targeted_search` question through
  `wave1 → projection → wave2 gap → evidence_needed → targeted_evidence → wave2`
  and terminates at the existing bounded blocked terminal; assert per-wave counters,
  accepted records, the journal critic facts, and that no
  `work_unit_gate_view_inconsistent` occurs. Run
  `UV_OFFLINE=1 .venv/bin/python -m pytest tests/integration/test_scripted_real_workflow_debug.py -q`
  until green, then `UV_OFFLINE=1 make debug-scripted-real-workflow` once.

## Backlog and program obligations

- [x] 12. Update `_backlog/bugs/BUG-028-*` and `_backlog/bugs/BUG-029-*` to fixed
  status with this change named, move or index them under `_backlog/_done/_fixed_bugs/`
  per the existing backlog convention, and refresh the bug README index. Done: both
  cards state the owning change and the red lines they owned are green.
- [x] 13. Control-placement plan-review obligation (current apply agent): re-read the
  proposal's Control Placement Review and the selected policies before each target
  edit; verify the three placement rows (projection writer, disposition validator,
  gate-view conformance) still match the diff; add any actionable finding as an
  unchecked task. Done: the apply agent records the re-read in the session and no
  finding remains unaddressed.
- [x] 14. Control-placement archive-closeout-review obligation (current archive
  agent): re-read the Control Placement Review against the final diff and evidence;
  confirm the frozen budget IDs (REJ-008, WON-012, WON-013, WON-004, WSN-009,
  TEL-007) are all closed by deltas, tasks, and tests, and that no runtime authority
  was granted. Done: the archive agent records the closeout review and no placement
  drift remains.

## Whole-change verification (before archive)

- [x] 15. Run `cd deep_research_harness && UV_OFFLINE=1 make verify`, then from the
  repo root `openspec validate wave1-question-handoff-and-critic-observability
  --strict` and `git diff HEAD --check`; record
  `git status --porcelain=v1 --untracked-files=all`, `git ls-files --stage deerflow`,
  `git submodule status -- deerflow`,
  `git -C deerflow status --porcelain=v1 --untracked-files=all`, and review
  `git diff --submodule=short` as supplementary gitlink scope evidence. Done: verify
  green, validate green, diff check clean, and the gitlink records show no
  `deerflow/` change.
