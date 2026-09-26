# Tasks

## 1. Red-first corpus tier test

- [x] 1.1 Add a focused unit test in `tests/unit/test_evidence_judgment_calibration.py` asserting the four `wave2-synthesis` branch cases declare `timeout_seconds == 180` and `max_total_tokens == 32_768` (single model call, zero tools, one attempt unchanged), and that every other non-worker case still declares the `_ZERO` values. Verify: run `cd deep_research_harness && .venv/bin/python -m pytest tests/unit/test_evidence_judgment_calibration.py -q` and watch the new assertion fail red against the current `_ZERO`-for-all fixture. ✓ Red confirmed (assertion failure at the 60 s / 16 384 current values)

## 2. Fixture tier and validator

- [x] 2.1 In `tests/scenarios/evidence_judgment_calibration.py`, add the `_WAVE2` tier (`dict(max_attempts=1, max_model_calls=1, max_tool_calls=0, max_total_tokens=32_768, timeout_seconds=180)`) and switch the validator's expected tier to a branch-keyed map: `targeted-evidence/worker` → `_WORKER`, `wave2-synthesis/synthesis` and `wave2-synthesis/repair` → `_WAVE2`, everything else → `_ZERO`, keeping per-tier equality and the `evidence_judgment_calibration_bounds_invalid` failure code. Verify: the task-1.1 test turns green; `validate_evidence_judgment_calibration_cases()` still passes for the untouched corpus. ✓ Green: 7/7 in the focused file, validator passes for the corpus

## 3. Fail-closed and ceiling-distance guards

- [x] 3.1 Extend `test_evidence_judgment_corpus_fails_closed_on_denominator_or_bound_drift` with a mutation that flips one wave2 case's `timeout_seconds` to `60` and asserts the validator still raises `evidence_judgment_calibration_bounds_invalid`. Verify: the extended test passes red-first style by construction (mutate → raise) in the same focused pytest run. ✓ Mutation-to-60 on the repair-normal case still raises the bounds failure code
- [x] 3.2 Add a static ordering assertion in the focused unit test that the wave2 tier stays no wider than the production branch policy facts (180 ≤ 300 wall seconds, 32_768 ≤ 64_000 total tokens, 1 ≤ 4 model calls), documented as ordering-only documentation of ceiling distance. Verify: same focused pytest run stays green. ✓ `test_wave2_tier_stays_no_wider_than_the_production_branch_policy` green

## 4. Gates

- [x] 4.1 From the repository root, run `python3 openspec/governance/check_project_gate.py --phase closeout`; from `deep_research_harness/`, independently run `UV_OFFLINE=1 make verify`; then, from the repository root, run `openspec validate align-wave2-calibration-case-budget --strict` and `git diff HEAD --check`. Measure every exit code directly (no `| tail` pipelines). Record `git status --porcelain=v1 --untracked-files=all`, `git ls-files --stage deerflow`, `git submodule status -- deerflow`, and `git -C deerflow status --porcelain=v1 --untracked-files=all`, and review `git diff --submodule=short`. Also confirm generation alignment: `openspec --version` equals the `generatedBy` frontmatter in `.agents/skills/*/SKILL.md` (read-only check; `.agents/skills/` is a user-reserved area). Verify: every measured exit code is 0. ✓ All direct exits 0: closeout gate (six checkers), `UV_OFFLINE=1 make verify`, strict validate, `git diff HEAD --check`; version alignment 1.13.1 = 1.13.1; gitlink `ceebf97f` unchanged, submodule clean; porcelain shows only this change's files

## Deferred evidence (not a blocking task)

- The next explicitly selected live window should run the four wave2
  evidence-judgment cases and record their typed rubric dispositions; a
  resource-bound failure at 180 s on a healthy link is new evidence for a
  deeper problem, not a reason to keep raising the tier. This is
  supplemental live evidence under the corpus's existing `requires_llm`
  selection semantics and does not gate this change's archive.
