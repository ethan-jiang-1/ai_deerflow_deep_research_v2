## 1. Navigation and command contracts

- [x] 1.1 Add focused red documentation contracts in `tests/contract/test_documentation_integrity.py` for the existing DeerFlow guide targets (`deerflow/AGENTS.md`, `deerflow/backend/AGENTS.md`), no-digest disclosure, current checkout-relative backlog references, `PROFILE=<name>` demo command, embedded-smoke wording, and `openspec/README.md` active-delta wording consistent with the current change store. Derive each expected command from the authoritative Makefile/local-operations text rather than hardcoding a duplicated string; verify the contracts fail before documentation edits and name the authoritative source for each command claim. Annotate each contract with the `@impl` IDs of the requirements it evidences (e.g. `DPL-005`, `DPL-006`, `LCP-002`, `EVH-009`) where the claim matches.
- [x] 1.2 Correct `AGENTS.md`, root `README.md`, `_backlog/README.md`,
  `deep_research_harness/README.md`, `deep_research_harness/docs/local-operations.md`,
  `deep_research_harness/run/README.md`, and `openspec/README.md` only where their
  active navigation or command wording is stale; preserve the
  no-upstream-modification boundary and do not create digest or compatibility paths.
  Also sync the DPL-012 exact-command contract in `tests/contract/test_demo_commands.py`
  to the corrected `PROFILE=<profile>` calibration command it pins (discovered during
  apply: the same stale command was duplicated in `run/README.md` and pinned there by
  that contract).

## 2. Test-surface orientation

- [x] 2.1 Add focused red contracts in `tests/contract/test_test_surface_orientation.py` for documented top-level test taxonomy, autouse deterministic public-network denial with `requires_llm`/`release_e2e` exceptions, and the helper-module (not pytest-fixture) status of `tests/fixtures/`; verify each documented directory name exists and each disclosed boundary matches `tests/conftest.py` and the marker registration, annotating `@impl EVH-009`/`EVH-031` where the claim matches.
- [x] 2.2 Update `docs/testing-and-evaluation.md` with a concise placement taxonomy,
  network-boundary explanation, and fixture-helper clarification; retain the test-owned
  selector/evidence registries as the exact catalog authority.

## 3. Verification and closeout

- [x] 3.1 Run the focused documentation contracts, path/reference audit, and
  `cd deep_research_harness && make governance`; confirm no named active entry document
  retains the repaired missing digest path, old checkout root, unsupported demo command,
  or misleading real-flow wording.
- [x] 3.2 Run `openspec validate fix-agent-facing-documentation-integrity --strict`
  and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all`,
  `git ls-files --stage deerflow`, `git submodule status -- deerflow`,
  `git -C deerflow status --porcelain=v1 --untracked-files=all`, and review
  `git diff --submodule=short`.
