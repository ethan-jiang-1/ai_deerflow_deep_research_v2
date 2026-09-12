## Context

See proposal.md — Why. `tests/assets/` mixes one collected pytest file with a test-owned
support library that 34 test modules and `scripts/checks/check_test_assets.py` import.
The directory name is not the problem — "asset" is the project's own closed term for
test-evidence assets (`AssetClass`, `make test-assets`, `check_test_assets.py`). The
problem is that a directory under `tests/` containing a `test_*.py` file reads as "a test
lane", so the support-library role is invisible before opening files. The fix must not
rename the vocabulary or churn the 34 import sites.

## Goals / Non-Goals

**Goals:**
- Make `tests/assets/` unambiguously a non-collected support library.
- Keep every existing import, governance term, gate name, marker, and lane expression intact.
- Surface the role at the coding-agent focus gate and in the test-lane docs.

**Non-Goals:**
- Renaming `tests/assets`, `AssetClass`, `make test-assets`, or `check_test_assets.py`.
- Changing the content, behavior, or coverage of the support library.
- Introducing new governance requirements or a second authority document.

## Decisions

**Relocate the one collected test instead of renaming the directory.**
`tests/assets/test_main_spec_requirement_sources.py` is a governance contract regression;
`tests/contract/` already holds its siblings and is in the fast lane, and the move keeps
`parents[3]` pointing at the repository root, so the sys.path bootstrap into
`openspec/governance/` is unchanged. Renaming the directory was rejected: it would touch
34 import sites plus the `test-assets` gate identity while losing the project's own
"asset" vocabulary.

**Drop `tests/assets` from the fast lane.**
The path entry exists only to collect the relocated test (introduced by
`restore-deterministic-gate-contracts`). Removing it keeps the lane honest and is paired
with the exact-path assertions in `test_verification_gate_contract.py` and the
`FAST_PATHS` partition test.

**A router README, not an authority.**
`tests/assets/README.md` states the role and points at the owning requirement/checker; it
adds no behavior and no new source of record, consistent with the "no second authority"
boundary. A one-line Information Map pointer in `deep_research_harness/AGENTS.md` is the
focus-gate hook; the AGENTS.md hard line budget (>160 lines fails) leaves room for one row.

## Risks / Trade-offs

- [Fast-lane partition or Makefile-path contract assertions break on the moved path] → Update `tests/assets/selection.py`, `Makefile`, and `test_verification_gate_contract.py` together, and let `make test-fast` plus `test_test_lane_selection.py` gate it.
- [`docs/testing-and-evaluation.md` silently drifts from the lane contents] → Update the lane description in the same change and keep the doc as a projection of `FAST_PATHS`.
- [A new README is mistaken for a governance authority] → Keep it to a role/navigation statement that explicitly defers to the owning requirements and checker.

## Migration Plan

1. `git mv` the single test into `tests/contract/`.
2. Remove `tests/assets` from `FAST_PATHS` and the Makefile `test-fast` path list; update the exact-path contract assertion.
3. Add `tests/assets/README.md` and the `AGENTS.md` Information Map row.
4. Update `docs/testing-and-evaluation.md`.
5. Run `make test-fast`, `make test-assets`, and `make verify`. Rollback is `git revert`; no runtime or persisted state is affected.
