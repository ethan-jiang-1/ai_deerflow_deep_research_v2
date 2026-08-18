# Design: fix-wave2-synthesis-bounded-input

## Context

See proposal.md — Why. BUG-046 verified against the crashed real run
(events.jsonl tail: `node wave2_synthesis failed internal.unexpected`,
pre-model, no model_tool) and reproduced in code: with an uncovered
`wave1_open_questions` id in state, `wave2_synthesis/node.py:213` raises a raw
`ValueError("synthesis_question_coverage_invalid")` that escapes the node →
`graph/builder.py` `observed_run` records `internal.unexpected` and re-raises →
graph dies → `bundle.unavailable` (no report, no typed incident, not retryable).

The node already has the bounded-failure pattern for the post-model phase
(BUG-040/041): `_validate_synthesis_semantics` raises typed
`SynthesisValidationFailure` → one-shot repair → final failure becomes
`_exhausted_update(NodeProblem(code=OUTPUT_STRUCTURED_INVALID,
validation_category=...))` → journal/demo render the concrete category. The
pre-model input phase has no equivalent guard.

## Goals / Non-Goals

Goals:
- Every pre-model input-condition failure (projection parse, coverage, record
  resolution, evidence read) terminates the node through the typed `exhausted`
  route with its concrete category — never an uncaught exception, never a graph
  crash, never `bundle.unavailable`.
- Keep post-model behavior byte-identical; keep non-ValueError exceptions
  (CancelledError and friends) propagating as today.

Non-Goals:
- No gate/budget/route-map changes; no behavior change for the happy path.
- No change to `_validate_synthesis_semantics` or the repair loop.
- No attempt to make the coverage mismatch "converge" — the mismatch is a
  data inconsistency; blocked-with-diagnostics is the honest terminal.

## Decisions

### D1. Wrap the pre-model phase; convert ValueError to a typed exhausted update

In `build_real(...).run`, wrap the input-derivation block (topic_registry
through `build_synthesis_prompt`) in `try/except ValueError as input_error`:
build `NodeProblem(code=RunFailureCode.OUTPUT_STRUCTURED_INVALID,
phase="wave2_synthesis", certainty=FailureCertainty.DIRECT,
validation_category=<category>)` and return
`_exhausted_update(problem, state=state, dependencies=dependencies)`.

Category derivation: the four pre-model raise sites use closed, self-describing
messages (`synthesis_question_coverage_invalid`,
`synthesis_accepted_record_missing`, `wave1_open_question_read_invalid`,
`wave1_open_question_projection_invalid`). Use the message itself as the
concrete `validation_category` when it matches the closed `NodeProblem`
category pattern (`^[a-z]+(?:[._][a-z0-9_]+)*$`); otherwise fall back to
`_synthesis_validation_category(input_error)` (semantic_invalid /
parser_invalid / candidate_invalid). NOTE: `_synthesis_validation_category`
alone does NOT carry the concrete category — it returns generic buckets — so
the message-first derivation is required to honor the concrete-category
promise in the spec delta.

Rationale:
- The journal/demo rendering (BUG-041) keys on `validation_category` first, so
  the concrete category (`synthesis_question_coverage_invalid`) is what shows
  up in diagnostics — exactly the diagnosability the bug demands.
- `_exhausted_update` writes the blocked terminal + typed incident + diagnostic
  reference — the same bounded outcome the post-model path produces.
- Only `ValueError` is caught: `asyncio.CancelledError` (BaseException in
  modern Python) and programming errors keep propagating; the outer
  `observed_run` wrapper still records `internal.unexpected` for genuinely
  unexpected exceptions.

Why not alternatives:
- *Fail-soft (drop uncovered ids and proceed)* — rejected: the coverage check
  is a deliberate contract (projection ids must resolve to Wave1 document
  texts); silently degrading hides an inconsistency the fix pipeline needs to
  see, and it changes synthesis input semantics.
- *New RunFailureCode for input failures* — rejected: the rendering pipeline
  keys on `validation_category` first (BUG-041); reusing the established
  `OUTPUT_STRUCTURED_INVALID` + category keeps journal/demo/tests consistent.
- *Guard only the coverage check* — rejected: all four pre-model failure sites
  have the same defect class; one guard covers all.

### D2. Spec delta on `wave2-synthesis-node` (WSN-001) only

The accepted spec already promises "SHALL NOT escape as an uncaught exception"
for the post-model validation path; the delta extends the same promise to the
pre-model input phase with its scenarios. No other capability changes.

## Risks / Trade-offs

- [Risk] Catching ValueError too broadly could mask a programming error that
  happens to raise ValueError → mitigated: the guard is scoped to the
  input-derivation block whose every failure mode is a data condition; the
  concrete category is projected, so the failure stays diagnosable; genuine
  bugs still surface in the journal as a typed incident with category
  `output.structured_invalid` fallback rather than a silent crash.
- [Risk] A blocked terminal for a transient ledger read failure is harsh →
  mitigated: ledger reads are deterministic post-submit; a missing record is an
  inconsistency, not transient I/O (I/O errors surface as
  `WorkUnitStoreError`/`FileNotFoundError`, which are not ValueError and keep
  today's behavior).

## Verification

- New tests in `tests/graph/test_wave2_synthesis_real.py`:
  (1) state with an uncovered open-question id → node returns `route=exhausted`,
  `terminal_status=blocked`, incident carries
  `validation_category=synthesis_question_coverage_invalid`, and no exception
  escapes;
  (2) malformed `wave1_open_questions` projection entry → same bounded outcome
  with `wave1_open_question_projection_invalid`;
  (3) happy path unchanged (existing tests keep passing).
- Full gate `UV_NO_CACHE=1 make verify` + `openspec validate --strict`.
- Real 003 run afterwards: any coverage/read inconsistency now yields a
  diagnosable blocked terminal instead of `bundle.unavailable`.
