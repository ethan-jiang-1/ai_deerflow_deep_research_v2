# Tasks: fix-wave1-critic-label-shapes (BUG-058)

## 1. Contract-boundary label normalization (red-first)

- [x] 1.1 Add red tests in the critic domain contract test file (`deep_research_harness/tests/unit/test_critic_contracts.py` or the file currently owning `CriticSourceAssessment` tests): every closed-map label (`high/yes/true/elevated/needed/required` → `True`; `low/none/no/false/minimal/minor/unlikely/not_needed` → `False`, each also in mixed case) normalizes on both flag fields; JSON booleans pass through; `medium`, novel tokens, numbers, and non-strings raise the typed validation error. Verify with `cd deep_research_harness && UV_OFFLINE=1 .venv/bin/python -m pytest tests/unit/test_critic_contracts.py -k label`. (`EVC-001`)
- [x] 1.2 Implement the normalization in `deep_research_harness/src/deerflow_deep_research/domain/critics.py`: a shared `field_validator(mode="before")` on `CriticSourceAssessment.marketing_risk`/`cross_verification_need` applying the casefolded closed map (design D2), leaving unmapped values to fail exactly as today. Task 1.1 turns green. (`EVC-001`)

## 2. Wave1 prompt parity and failure-code split

- [x] 2.1 Add red tests: (a) the wave1 SourceDiagnostic prompt's expected-output declares the `bounds` block with `"marketing_risk": "boolean"` and `"cross_verification_need": "boolean"` plus the trust/materiality enums (mirror the targeted-critic assertion); (b) `_canonical_critic_code` maps a pydantic `ValidationError` to `wave1_review_output_shape_invalid` while JSON-decode/non-object errors keep their existing codes and unknown ValueErrors keep `wave1_review_output_invalid`. Verify with `cd deep_research_harness && UV_OFFLINE=1 .venv/bin/python -m pytest tests/graph -k "source_diagnostic and (bounds or code)"`. (`EVC-001`)
- [x] 2.2 Implement in `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave1/prompts.py` (bounds block + objective wording per design D3) and `wave1/review.py` (`_canonical_critic_code` split per D4). Task 2.1 turns green. (`EVC-001`)

## 3. Regression and evidence

- [x] 3.1 Full deterministic gate: `cd deep_research_harness && UV_NO_CACHE=1 make verify` stays green (the targeted critic path, wave1 review tests, and existing critic contract tests unchanged in behavior). Confirm the diff touches only `domain/critics.py`, `wave1/prompts.py`, `wave1/review.py`, and tests. (`EVC-001`)
- [x] 3.2 Update the bug record `_backlog/bugs/BUG-058-wave1-critic-bool-fields-string-labels.md` (fix关联 → fixed with this change) and keep the bug active until the real 004 rerun passes; the rerun itself is owned by change `hard-real-auto` task 4.3. (`EVC-001`)
