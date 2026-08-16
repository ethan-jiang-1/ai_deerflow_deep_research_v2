# Design: wave1-question-handoff-and-critic-observability

## Verified Current Behavior

- `graph/nodes/wave1/review.py::_dispatch_missing_reviews` runs each missing critic,
  and both `InvocationFailure` and parse/build `ValueError` end in a bare `continue`
  (lines 404-415). Nothing is recorded; the gate later sees only a missing artifact.
- The Wave1 gate (`engine/real_gates.py`) carries `work_unit_completion`,
  `wave1_new_source_floor`, and `wave1_review_presence` rules. The removed
  `wave1_open_question_disposition` rule is the BUG-028 mitigation; the owning spec
  text still promises repair for `targeted_search` (WON-004), which is why
  `tests/integration/test_wave1_work_units.py::test_real_wave1_review_gate_enforces_question_floor_and_review_integrity`
  is red.
- `Wave1GateReviewRow.open_question_states` keeps only the closed state enum; the
  review projection has no question text or ids for a handoff
  (`domain/wave1.py:360-368`).
- `graph/nodes/gate_adapter.py::evaluate_gate_for_node` writes the gate-owned
  `unresolved_gaps` projection only for `wave2_synthesis`, using
  `apply_research_update(state, {...}, writer=WriterRole.GATE)` — the pattern this
  design mirrors for Wave1.
- `graph/nodes/wave2_synthesis/node.py` reads `accepted_submission_refs` and evidence
  but never receives Wave1 open questions; `build_synthesis_prompt` has no question
  assignment, and `_validate_synthesis_semantics` performs no question coverage
  check. The Wave2 gate (`_wave2_searchable_gap_rule`, `default_budget=1`) already
  routes searchable gaps to `evidence_needed` and exhausts after its bound.
- `graph/nodes/targeted_evidence` declares `NodeCapability.WORK_UNIT_CONTROLLER` but
  its node never returns `WORK_UNIT_GATE_VIEW_KEY`, so any routed visit raises
  `work_unit_gate_view_inconsistent` in the wrapper (`graph/builder.py:229-237`);
  `run_gap_workers` discards the `WorkUnitComponentResult.gate_view` it already
  computed.

## Approved Decisions

1. **BUG-028 option B** (explicit traceable handoff through Wave2 synthesis) over
   option A (a new Wave1→targeted_evidence route): topology stays unchanged (WON-005),
   the `targeted-evidence-loop` gap-router contract (TEL-001) is untouched, and
   retrieval reuses the validated `wave2 gate → evidence_needed → targeted_evidence`
   loop. Option A would have rewritten TEL-001's "current Wave2 gate only" input rule
   and reordered the first synthesis pass.
2. **WS1 reuses the existing Journal contract** rather than a new event category:
   invalid typed critic results are `post_candidate` VALIDATION facts (the REJ-002
   "later deterministic validation boundary" family); invocation failures are closed
   MODEL_TOOL failed facts. The only new Journal surface is the bounded optional
   `critic_kind` field (REJ-008).
3. **The projection carries question ids and work ids only — never question text, and
   it merges across Wave1 visits.** Measured fact: a 500-character question is up to
   1,500 UTF-8 bytes (CJK), so a 64-entry projection with text would reach ~200 KB,
   far past the hard `MAX_CHECKPOINT_STATE_BYTES` bound of 65,536 bytes
   (`domain/state.py::MAX_CHECKPOINT_STATE_BYTES`). Ids-only entries are ~160 bytes,
   so the 64-entry cap costs ~10 KB of the checkpoint. The owning synthesis node
   resolves question text verbatim from the accepted Wave1 result documents (the
   same accepted-evidence authority it already reads), and an unresolvable id fails
   closed — text is never fabricated or summarized from another source.
   The gate adapter merges the current review's refs with the already-projected refs
   (dedupe by question id) because a Wave1 repair visit's gate view reconciles only
   the work planned on that visit — a plain overwrite would silently drop earlier
   accepted works' open questions (verified by the scripted-real named case).
   Cap 64, fail closed on overflow (`wave1_open_question_projection_overflow`): the
   cap is plan-scale (32 accepted works × 16 questions is the model bound, 28 was
   the real incident), not model-scale, and an over-cap projection is a degenerate
   provider output that fails honestly.
4. **Every projected question must be disposed in synthesis** — a searchable gap or an
   explicit resolution — enforced by the deterministic materializer, not by a new gate
   rule. Gate rules stay pure; the Wave2 gate keeps routing only searchable gap ids.
5. **targeted_evidence always returns a valid gate view.** A gap visit returns the
   shared component's reconciled view; a gap-less visit returns the canonical empty
   drained view directly, because the shared component's plan bound
   (`work_intents_bound_invalid`, 1..32 intents) rejects zero intents by contract.
   The empty view is definitionally correct — nothing is planned or reconciled — and
   the wrapper admits it. No component change and no removal of the
   `WORK_UNIT_CONTROLLER` declaration.

## WS1 Design: critic dispatch observations

### Typed input/output and writer

- `domain/run_observation.py::RunEvent` gains `critic_kind: Literal["source_diagnostic",
  "claim_verifier"] | None = None` (optional, additive). Validator additions: the
  field is allowed only when `category == VALIDATION`, `phase == "wave1"`,
  `schema_version == 3`, and `validation_stage == "post_candidate"`; otherwise raise
  `journal_critic_kind_unexpected`. Legacy v1/v2 and pre-change v3 records stay
  readable with the field absent.
- `runtime/run_observation.py::RunObservationStore.record_event` (and its sync
  writer `_bundle_record_event_sync`) accept `critic_kind` and pass it through to the
  `RunEvent` construction; `RunObservationRecorder.record(**event)` forwards it
  unchanged. The `RunEventRecorderProtocol.record` signature in
  `domain/invocation.py` gains the same optional keyword with a default. The Journal
  inspection projection needs no new field — `critic_kind` surfaces through the
  existing event records.
- `graph/nodes/wave1/node.py` passes `dependencies.event_recorder` into
  `build_wave1_gate_review(controller, gate_view, policy, event_recorder=...)`;
  `review.py` threads it into `_dispatch_missing_reviews`.

### Event taxonomy and canonical codes

- Parse/build `ValueError` → `record(category=VALIDATION, phase="wave1",
  work_id=record.work_id, attempt_id=record.attempt_id,
  validation_stage="post_candidate", validation_codes=(canonical_code,),
  critic_kind=kind)`. No `response_shape` (forbidden for `post_candidate` per the
  existing contract), no raw output.
- Canonical mapping `_canonical_critic_code(error)` mirrors
  `wave1/subgraph.py::_canonical_validation_code`: keep a message matching
  `^wave1_[a-z0-9_]+$` verbatim, otherwise `wave1_review_output_invalid`. The closed
  table is the set the review boundary already raises
  (`wave1_source_diagnostic_coverage_invalid`,
  `wave1_claim_verifier_coverage_invalid`, `wave1_claim_verifier_ref_invalid`,
  `wave1_review_assignment_kind_invalid`) plus the parser boundary's bounded codes.
- `InvocationFailure` → `record(category=MODEL_TOOL, outcome="failed", phase="wave1",
  work_id, attempt_id, failure_category=<closed category>,
  provider_category=<closed value when known>)`. The closed category derives from the
  existing `invoke_and_normalize` problem projection; no exception text or provider
  payload.
- The recorder call is wrapped like `_observe_validation` (swallow recorder absence
  and recorder exceptions). Observation is best-effort and never changes the
  dispatch's `continue` control flow, the gate's `wave1_review_presence` repair loop,
  or any verdict.

### StateGraph transition / predicate

None. No node, gate, route, or state transition changes in WS1; the owning
transition that consumes the outcome (missing artifact → `wave1_review_presence` →
repair → Wave1 re-dispatch) already exists.

### Deterministic tests (red first)

- Unit: `_canonical_critic_code` mapping table in `tests/unit/test_wave1_review.py`.
- Integration: extend `tests/integration/test_wave1_work_units.py` — scripted invalid
  claim-verifier payload with a recorder spy asserts exactly one `post_candidate`
  VALIDATION fact with the canonical code, `critic_kind="claim_verifier"`, and the
  work/attempt correlation; a scripted invocation failure asserts the closed
  MODEL_TOOL fact; a `None` recorder and a raising recorder keep the dispatch's
  existing behavior (artifact absent, second dispatch succeeds after capability
  recovery).

## WS2 Design: question handoff and targeted gate-view conformance

### Typed contracts and writers

- `domain/wave1.py`:
  - New `Wave1OpenQuestionRef {question_id: ^q:w1_[A-Za-z0-9_-]{1,64}$; work_id}` —
    ids only, no text (see Approved Decision 3).
  - `Wave1GateReviewRow` gains `open_questions: tuple[Wave1OpenQuestionRef, ...]`
    (default `()`, at most `MAX_OPEN_QUESTIONS`, sorted by question id, only
    `targeted_search` states). `review.py::build_wave1_gate_review` fills it from the
    accepted `Wave1SourceIntakeResult.open_questions`. The review stays
    non-checkpointed; the row addition is additive for existing test fixtures.
- `domain/state.py`:
  - `ResearchState.wave1_open_questions: tuple[Wave1OpenQuestionRef, ...] = ()`.
  - Field ownership mirrors `unresolved_gaps` exactly: GATE owner, `last_write_wins`,
    registered in the same non-authority-writer allowlist. No reducer or preview
    change.
- `graph/nodes/gate_adapter.py`:
  - New Wave1 branch in `evaluate_gate_for_node`: when `logical_name == "wave1"` and
    the injected review is a validated `Wave1GateReview`, merge the review rows' refs
    with the checkpointed projection (`state.get("wave1_open_questions")`), dedupe by
    question id, order by `(work_id, question_id)`; if the merged count exceeds 64
    raise `ValueError("wave1_open_question_projection_overflow")` before any state
    write; otherwise `apply_research_update(state, {"wave1_open_questions": refs},
    writer=WriterRole.GATE)`. Existing checkpoint entries round-tripping as dicts are
    re-validated into `Wave1OpenQuestionRef` before merging.
  - `engine/real_gates.py` is unchanged: no rule is added or removed; the projection
    never feeds a verdict.
- `domain/synthesis.py`:
  - `GapRecord.source_questions: tuple[str, ...] = ()` (≤ 16, sorted, unique,
    `^q:w1_...` pattern).
  - `SynthesisResult.resolved_questions: tuple[str, ...] = ()` (≤ 64, sorted,
    unique, `^q:w1_...` pattern).
  - Both default to `()` so artifacts persisted before this change remain valid.
  - `SynthesisBundleStoreProtocol` gains one bounded read:
    `read_wave1_open_questions(accepted_refs) -> tuple[tuple[str, str], ...]`
    returning `(question_id, question)` pairs for `targeted_search` questions in
    accepted WAVE1 records, implemented by `runtime/work_unit_store.py` with
    `load_records` + `read_canonical_bytes(result_ref, max_bytes=MAX_RESULT_BYTES)`
    + `Wave1SourceIntakeResult` validation; ordered by `(work_id, question_id)`,
    naturally bounded by accepted count × `MAX_OPEN_QUESTIONS`. The read is the same
    accepted-evidence authority as `read_synthesis_evidence`, not a new one.
- `graph/nodes/wave2_synthesis/prompts.py`:
  - `build_synthesis_prompt(..., open_questions=())` renders the resolved assignment
    (id and verbatim question text pairs resolved by the node from accepted
    documents, no work ids) into the trusted assignment section and states the
    closed output contract: each question id appears exactly once — in a
    `search_required=true` gap's `source_questions` or in `resolved_questions`.
  - The repair prompt is unchanged: the coverage error feeds only the existing closed
    validation category (`synthesis_question_coverage_invalid` maps to
    `semantic_invalid` through the existing prefix rule).
- `graph/nodes/wave2_synthesis/node.py`:
  - Reads `state["wave1_open_questions"]` (default `()`), resolves text through
    `read_wave1_open_questions`, and passes the id-and-text assignment to the prompt
    and the ids to the coverage check. A projected id with no resolved text fails
    with `synthesis_question_coverage_invalid` before any model invocation.
  - `_validate_synthesis_semantics` gains the coverage step: expected ids =
    `wave1_open_questions` ids; actual = `(gaps with search_required).source_questions
    ∪ resolved_questions`; require exact set equality plus per-question uniqueness
    (a question may not appear in two gaps or in both collections); reject foreign
    ids. Raise `synthesis_question_coverage_invalid` on any violation. The existing
    one-shot repair loop and the existing exhausted terminal are the only recovery
    and terminal owners — no new retry or route.

### Owning transition, evaluator, recovery

- The owning StateGraph transition is unchanged:
  `wave2_synthesis → evidence_needed → targeted_evidence → wave2_synthesis`, bounded
  by the existing `default_budget=1` gate budget, terminating in the existing
  blocked/exhausted terminal when gaps persist.
- Evaluators: the synthesis materializer coverage validator admits question
  dispositions; `_wave2_searchable_gap_rule` (unchanged) admits the route. No second
  controller or authority is created.
- Recovery: one closed-category structured repair; repair failure follows the
  existing exhausted path. `wave1_open_questions` is rewritten on each Wave1 gate
  evaluation (`last_write_wins`), so a rerun reaching Wave1 refreshes it honestly.

### targeted_evidence conformance

- `subgraph.py::run_gap_workers` returns the component result (parent update plus
  `gate_view`) instead of discarding the view; `node.py::run` returns
  `WORK_UNIT_GATE_VIEW_KEY: result.gate_view` plus `{"route": "next"}` for gap
  visits, and the canonical empty drained `WorkUnitGateView` for gap-less visits
  (the component's `1..32` intent bound makes the empty pass-through a node-local
  degenerate case with nothing to reconcile).
- The red test proves both visits through the real node before the node edit;
  `builder.py` and topology are unchanged: the wrapper's existing
  `work_unit_gate_view_inconsistent` machinery now admits the view.

### Compatibility

| Surface | Before | After |
| --- | --- | --- |
| Graph checkpoints | no `wave1_open_questions` | field defaults `()`; old checkpoints read unchanged |
| Synthesis artifacts | no `source_questions`/`resolved_questions` | defaults `()`; old artifacts validate unchanged |
| Run Event Journal | no `critic_kind` | optional field; v1/v2 and pre-change v3 records read with it absent |
| Wave1 review projection | states only | additive `open_questions` refs; not checkpointed, no artifact schema change |
| Wave1 gate rules/routes | completion + floor + presence; `{PASS, REPAIR, BLOCKED}` | unchanged; projection write changes no verdict |
| Graph topology | wave1→(repair self-loop)→wave2→targeted | unchanged |

## Cross-Workstream Interaction

WS1 and WS2 share the Wave1 review→gate seam but no code path: WS2's projection is
derived from review rows (not from critic outcomes), and the critic-missing repair
loop that WS1 makes diagnosable remains the sole `wave1_review_presence` behavior.
WS1 lands first so the scripted-real repair/targeted named case (WS2 evidence) can
assert both the new handoff and the critic diagnostics in one run.

## Unresolved Questions

- The shared component rejects zero intents by contract (`1..32` plan bound), which
  the apply phase verified; the gap-less visit therefore returns the canonical empty
  drained view at the node, and the TEL-007 delta records that decision. No
  component change enters scope.
- The exact closed provider categories available on `InvocationFailure` problems are
  consumed as-is from `invoke_and_normalize`; WS1 adds no new category.
