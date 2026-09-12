# Tasks

## 1. Relocate the one collected test

- [x] 1.1 `git mv deep_research_harness/tests/assets/test_main_spec_requirement_sources.py deep_research_harness/tests/contract/test_main_spec_requirement_sources.py` and verify `uv run pytest tests/contract/test_main_spec_requirement_sources.py -q` still passes (its `parents[3]` sys.path bootstrap into `openspec/governance/` is unchanged).
- [x] 1.2 Confirm `tests/assets/` contains no collected test with `uv run pytest tests/assets --collect-only -q` returning an empty collection.

## 2. Synchronize fast-lane selection

- [x] 2.1 Remove `"tests/assets"` from `FAST_PATHS` in `tests/assets/selection.py`.
- [x] 2.2 Remove `tests/assets` from the `test-fast` path list in `deep_research_harness/Makefile` and update the exact-list assertion in `tests/contract/test_verification_gate_contract.py`.
- [x] 2.3 Run `UV_OFFLINE=1 make test-fast` and `uv run pytest tests/contract/test_test_lane_selection.py tests/contract/test_verification_gate_contract.py -q`; confirm the moved test is still selected and executed by the fast lane and the partition assertions pass.

## 3. Surface the support-library role

- [x] 3.1 Add `deep_research_harness/tests/assets/README.md` stating the directory is not tests, lists the test-owned evidence/inventory vocabularies and validators, names the importing callers (`tests/**` and `scripts/checks/check_test_assets.py`), and defers to the owning requirements/checker; verify it adds no behavior claim.
- [x] 3.2 Add one Information Map row in `deep_research_harness/AGENTS.md` pointing at `tests/assets/README.md`, and verify `python3 openspec/governance/check_doc_hygiene.py` passes and the AGENTS.md line count stays under the hard budget (160).
- [x] 3.3 Update `docs/testing-and-evaluation.md`: in the command table drop `asset/` from the `make test-fast` category description, and in the Test Directory Taxonomy make `assets/` explicit ("contains no collected test; the former sole test moved to `tests/contract/`"), then verify `rg -n "tests/assets" docs/testing-and-evaluation.md` shows only support-library module references and no fast-lane path entry.

## 4. Verification and closeout

- [x] 4.1 From `deep_research_harness/`, run `UV_OFFLINE=1 make verify` and confirm lock-check, lint, test-assets, test-fast, test-integration, and test-workflow all exit 0.
- [x] 4.2 From the repository root, run `python3 openspec/governance/check_project_gate.py --phase closeout`, then `openspec validate clarify-test-assets-role --strict`, then `git diff HEAD --check`, and record each exit code directly (no pipes).
