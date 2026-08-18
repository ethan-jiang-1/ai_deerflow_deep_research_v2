# Design — Low-Scale Real-Auto Runs (Profile-Driven, v5)

## Context

See `proposal.md`. v1 modified product defaults directly and was reverted. v2
moved intent into an envelope field but still required capability-construction
wiring. v3/v4 converged intent consumption toward existing channels; **v5 adds
the gate budget resolver (gate READS the HITL-owned profile intent fields) after
discovering that `repair_budget_by_phase` is GATE-owned and cannot be written by
HITL1**, and classifies the budget headroom as scale-independent real-model
adaptation.

Verified facts (2026-08-18 code walkthrough + real runs):

- **Profile is globally visible.** `ResearchProfile` is written by HITL1 into the
  Bundle request store; `topic_planning/prompts.py::planner_assignment_from_state`
  reads it and already derives `single_topic` from
  `quick_overview + minimal + very_quick`. This is the existing
  "profile intent → node behavior" pattern.
- **Gate budget resolution reads state.** `gate_kernel._resolve_budget` reads
  `state["repair_budget_by_phase"]` (GATE-owned writer role — HITL1 cannot write
  it; `state.py` FieldOwnership) and falls back to the gate definition's default.
  The HITL-owned profile intent fields (`cost_tolerance`, `time_budget`, written
  by `profile_state_fields`) are present in graph state at gate evaluation time,
  so a gate budget resolver can READ them without any writer-role change.
- **Capability budgets cannot see the run's profile.** The recipe is built before
  the run; capabilities are rebuilt per graph invoke by
  `bundle_graph._context(envelope, bundle)`, and the profile is written mid-run by
  HITL1 — so any budget tiering at capability construction either defaults forever
  or needs envelope plumbing. v5 deliberately avoids both.
- **Real-run observations:** under the minimal intent, wave0/wave1 pass with one
  work unit each (real content); wave2 first exhausted its scripted-template
  budget on real output (`budget.exhausted`), then failed on provider shapes
  (string `priority`, prose `source_questions`); after shape fixes it produced
  real findings plus one honest gap, and gate budget 1 blocked after one evidence
  round. Wave workers used 1-3 tool calls per work unit — the worker budget caps
  (50 calls / 200 tools / 900 s) never bind in bounded single-topic runs.
- **Auto profiles lack `must_answer`.** The auto branch writes only
  comparison/language fields, so `state.must_answer_questions` is empty, the
  readiness critic produces no per-question verdicts, and `final/report.md` is an
  empty shell (observed). The `must_answer` contract bounds each question to
  `MAX_QUESTION_CHARS = 256`, while a non-interactive request may be up to 16K —
  so a naive `must_answer=(request_text,)` can fail validation for long questions.
- **Provider hang risk:** DeepSeek SDK occasionally blocks inside `ainvoke` such
  that `asyncio.timeout` cannot interrupt it. Out of scope here (independent
  bridge hardening); runbook notes Ctrl-C + retry.

## Goals / Non-Goals

**Goals:**
- Mode 003 completes: `RESULT: PASS`, real `final/report.md`, one wave0 + one
  wave1 work unit, real source URLs.
- Intent flows through existing channels (profile → planner; profile intent
  fields in state → wave2 gate budget resolver); every absent-intent value stays
  byte-identical.
- Real-model provider shapes normalize at the deterministic contract boundary;
  wave2 repair failure is a bounded terminal, never a graph crash.

**Non-Goals:**
- No `deerflow/` gitlink changes; no product `deep_research` tool schema change.
- No envelope/recipe/capability API changes for intent transport.
- No wave worker budget tiering (worst-case caps; bounded runs never bind them).
- No bridge timeout hardening against a hung provider SDK (independent concern).
- No interactive HITL1 change; no Gateway observer route; no runbook 004.

## Decisions

### D1: Intent declaration → profile (mechanism, not a test branch)

`non_interactive_policy` gains an optional `profile_intent` (`minimal`; absent =
today, except the `must_answer` product fix below). `tool.py::_admitted_start_action_input`
admits it as a closed value, `NonInteractivePolicy` carries it, and
`hitl1/node.py` auto branch constructs the profile from the declaration: `minimal`
seeds `depth=ResearchDepth.QUICK_OVERVIEW`,
`cost_tolerance=CostTolerance.MINIMAL`, `time_budget=TimeBudget.VERY_QUICK` (still
degraded; typed-fact blocked path unchanged); absent keeps the current degraded
profile. In both cases the profile seeds `must_answer=(request_text,)` (product
fix: automatic runs currently write an empty `must_answer`, which empties the
readiness per-question verdicts and the final report — observed). Because the
`must_answer` contract bounds each question to `MAX_QUESTION_CHARS = 256`, a
request longer than 256 characters SHALL fail closed through the same blocked
path as missing typed facts (no silent truncation of user intent). The existing
`single_topic` derivation then forces exactly one topic under the minimal intent.

- Why: the product gains one capability — non-interactive automatic runs can
  express research intent — and mode 003 merely declares `minimal`, exercising
  the real product path. No test-only branch logic lives in product code.
- Evidence: `tests/graph/test_hitl1_node.py` (declared minimal → trio + must_answer;
  absent → current degraded profile + must_answer).

### D2: Wave2 gate budget resolver (gate reads state, no writer-role conflict)

`GateDefinition` gains an optional `budget_resolver: Callable[[Mapping], int |
None] | None`; `_resolve_budget` consults it first (resolver returning `None`
falls back to `default_budget`; a resolver result outside the same [0, 10] bound
as `default_budget` is rejected the same way; a raising resolver is treated as a
gate failure, never an unchecked crash). The wave2 gate defines a resolver
that reads the HITL-owned profile intent fields in graph state
(`cost_tolerance == "minimal"` and `time_budget == "very_quick"`) and yields 2
evidence rounds for the minimal pair, `None` otherwise (default 1).

- Why: `repair_budget_by_phase` is GATE-owned (`state.py` FieldOwnership), so the
  HITL node cannot write it — the gate must READ the HITL-owned intent fields it
  already writes (`profile_state_fields`). No writer-role change, no
  construction-timing problem (state is present at gate evaluation).
- The mapping is an explicit product decision (a quick minimal run tolerates one
  extra evidence round to converge on an honest gap), specified in
  `execution-intent`/`wave2-synthesis-node`.
- Evidence: gate resolver tests (default 1; minimal pair → 2); `_resolve_budget`
  fallback tests.

### D3: Wave worker budgets stay default

No tiering. They are worst-case caps; bounded single-topic runs use 1-3 calls per
work unit (observed). Tiering them would require capability-construction plumbing
for no observed benefit.

### D4: Wave2 synthesis budget gets real-output headroom (evidence-driven, product fix)

`runtime/research.py` raises only the wave2 synthesis node budget from
scripted-template calibration to bounded real-output values: ≈ `max_model_calls=4,
total_token_budget=64_000, per_call_output_token_cap=16_384,
structured_result_bytes=16_384, wall_time_seconds=300`. This is a product default
because a real run exhausts the scripted-calibrated budget on real output
(observed `budget.exhausted`); it remains a hard, positive, admission-controlled
cap. **readiness and final-delivery budgets stay unchanged** until real runs
demonstrate exhaustion (evidence-driven; no observed failure yet). No test pins
the wave2 values.

### D5: Wave2 provider-shape normalization (scale-independent)

`domain/synthesis.py`: `_normalize_priority` (labels → int 1-5) applied to
findings and gaps; gap `source_questions` keeps only `q:w1_*` ids and folds prose
into the description; `resolved_questions` keeps only `q:w1_*` ids.

### D6: Wave2 repair path bounded

`wave2_synthesis/node.py`: wrap the repair-path second parse+semantic validation
in `try/except ValueError` and return `_exhausted_update(NodeProblem(
OUTPUT_STRUCTURED_INVALID, phase="wave2_synthesis", DIRECT))`. Existing tests that
asserted the old uncaught-raise behavior are updated to assert the `exhausted`
terminal.

### D7: Targeted provider-shape normalization (scale-independent)

`domain/targeted.py::TargetedWorkerSource`: before-validator maps `url` →
`canonical_url`, derives `source_id`, absorbs `observed_relevance`/`snippet`;
`targeted_evidence/prompts.py` declares the source-item fields in the expected
schema.

### D8: Operator entry and docs

`soft_bundle.py` mode 003 (`MODE_QUESTIONS["003"]`, `cmd_run` branch delegating to
`make demo-real-scripted --question "<fixed>"`, `_verify_bundle` requires
`final/report.md` for 003, `cmd_inspect` routes 003 to the recorded-diagnostics
render). `demo_real --embedded-smoke --scripted` declares `profile_intent=minimal`
(and soft-bundle mode 003 inherits it), so the run exercises the real product
path under the minimal intent. New runbook-003 and the local-demo README row
document `.env` prerequisites incl. `DEERFLOW_DEMO_MODEL`.

## Alternative considered

- v1 (change defaults to make the test pass): rejected — tested path diverges
  from production.
- v2 envelope intent field: rejected — works but adds envelope API surface and
  "entry-declared" semantics; v3 shows the only intent-conditional point (gate
  budget) can ride the existing state mechanism.
- Capability laziness / `_context` reading the profile from checkpoint: rejected —
  large surface (work-unit resolution + bridge runtime budgets) for one gate
  budget that state already covers.
- Skipping provider-shape normalization: rejected — shape defects crash/block
  runs regardless of budgets.
