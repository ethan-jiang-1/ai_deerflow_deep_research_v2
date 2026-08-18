## 1. Intent declaration mechanism (D1)

- [x] 1.1 `runtime/non_interactive.py`: add optional `profile_intent` (`minimal` | None) to `NonInteractivePolicy`; `tool.py::_admitted_start_action_input` admits it as a closed value (absent = today; `auto_profile`/`auto_proceed` stay required, any other unknown key stays rejected).
- [x] 1.2 `hitl1/node.py`: auto branch constructs the profile from the declared intent — `minimal` seeds `depth=quick_overview, cost_tolerance=minimal, time_budget=very_quick` (import the enums; still degraded; typed-fact blocked path unchanged); absent keeps the current degraded profile.
- [x] 1.3 Same auto branch: seed `must_answer=(request_text,)` in both cases (product fix — automatic runs currently write an empty must_answer, which empties the final report; observed). When `request_text` exceeds `MAX_QUESTION_CHARS` (256), the auto branch SHALL fail closed through the same blocked path as missing typed facts (no silent truncation).
- [x] 1.4 Tests: `tests/graph/test_hitl1_node.py` (declared minimal → trio + must_answer; absent → current degraded profile + must_answer; request_text > 256 chars → blocked, no profile written); `tests/unit/test_non_interactive.py` (closed-value admission: `profile_intent=minimal` accepted, `profile_intent=standard`/non-string rejected, unknown keys still rejected, absent stays accepted).

## 2. Wave2 gate budget resolver + wave2 budget headroom (D2, D4)

- [x] 2.1 `domain/gate.py`: `GateDefinition` gains optional `budget_resolver: Callable[[Mapping], int | None] | None`; `evaluate_gate` passes `gate_def.budget_resolver` to `_resolve_budget`, which consults it first (resolver `None` → `default_budget`; resolver results validated against the same [0, 10] bound as `default_budget`; a raising resolver is a gate failure, not an unchecked crash).
- [x] 2.2 `engine/real_gates.py::build_wave2_real_gate_def`: define the resolver — read the HITL-owned state fields `cost_tolerance`/`time_budget`; minimal pair → 2 evidence rounds, else `None` (default 1).
- [x] 2.3 `runtime/research.py`: raise only the wave2 synthesis node budget (≈4 calls / 64K / 16K output / 16K structured / 300 s); readiness/final-delivery budgets stay unchanged (evidence-driven).
- [x] 2.4 Tests: gate resolver two-tier tests (default 1; minimal pair → 2); `test_zero_tool_policies_remain_independently_bounded` still passes.

## 3. Wave2 real-output adaptation (D5, D6)

- [x] 3.1 `domain/synthesis.py`: `_normalize_priority` (labels → int 1-5) applied to findings and gaps; gap `source_questions` keeps only `q:w1_*` ids and folds prose into the description; `resolved_questions` keeps only `q:w1_*` ids.
- [x] 3.2 `wave2_synthesis/node.py`: guard the repair-path second parse with `try/except ValueError` → `_exhausted_update(NodeProblem(OUTPUT_STRUCTURED_INVALID, ...))`.
- [x] 3.3 Tests: `tests/graph/test_wave2_provider_shapes.py` (labels → ints; prose questions folded); update `tests/graph/test_wave2_synthesis_real.py` repair-path tests to assert the `exhausted` terminal (sync selectors in `tests/assets/evidence.py` and `docs/regression-descent.md` if renamed).

## 4. Targeted real-output adaptation (D7)

- [x] 4.1 `domain/targeted.py::TargetedWorkerSource`: before-validator maps `url` → `canonical_url`, derives `source_id`, absorbs `observed_relevance`/`snippet`; `targeted_evidence/prompts.py` declares source-item fields in the expected schema.
- [x] 4.2 Tests: `tests/graph/test_targeted_evidence_real.py` normalization cases.

## 5. Soft-bundle mode 003 and docs (D8)

- [x] 5.1 `scripts/soft_bundle.py`: `MODE_QUESTIONS["003"]`, `cmd_run` mode-003 branch (delegate `make demo-real-scripted --question "<fixed>"`, parse bundle id, record, verify), `_verify_bundle` requires `final/report.md` for 003, `cmd_inspect` routes 003 to the recorded-diagnostics render.
- [x] 5.2 `scripts/demo_real.py` `--embedded-smoke --scripted` declares `profile_intent=minimal` in the non-interactive context (mode 003 inherits it).
- [x] 5.3 Extend `tests/contract/test_soft_bundle_cli.py` (mode-003 run binds; inspect renders recorded diagnostics; verify without report prints FAIL).
- [x] 5.4 Create `_backlog/_local_demo/runbook-003-medium-real-auto.md` (fixed bounded question; `.env` prerequisites incl. `DEERFLOW_DEMO_MODEL`; real-content acceptance; single-work-unit-per-wave; hang/retry note); update `_backlog/_local_demo/README.md` rows 003/004.

## 6. Verification

- [x] 6.1 Focused suites: `tests/graph/test_hitl1_node.py`, `tests/graph/test_wave2_provider_shapes.py`, `tests/graph/test_wave2_synthesis_real.py`, `tests/graph/test_targeted_evidence_real.py`, `tests/unit/test_research_runtime_capabilities.py`, `tests/unit/test_non_interactive.py`, `tests/engine` (gate resolver), `tests/contract/test_soft_bundle_cli.py`; then `tests/unit tests/graph tests/contract` and `ruff` on changed files.
- [x] 6.2 Zero-cost regression: runbook-002 once (`RESULT: PASS`).
- [ ] 6.3 Real end-to-end: `soft-bundle run <root> --mode 003` with `.env` credentials — expect `RESULT: PASS`, `final/report.md` with real content, one wave0 + one wave1 work unit, real source URLs; then `status`/`inspect`/`phases`/`verify` per runbook. If the provider hangs, kill and retry (documented in the runbook).
- [ ] 6.4 `openspec validate low-scale-real-auto --strict`; archive after closeout evidence.
