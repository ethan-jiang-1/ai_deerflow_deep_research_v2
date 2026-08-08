## 1. Prove the suspension boundary

- [x] 1.1 Add focused red deterministic collection and asset-contract cases proving that the retained EVH-024 selector is absent from ordinary pytest discovery, every active focused lane, active evidence claim, Make target, and GitHub workflow invocation; prove that `release_e2e` remains only a defense-in-depth exclusion marker.
- [x] 1.2 Extend the focused contracts to prove the active release control-plane suite and `tests/scenarios/release.py` remain collected and available after the full-real selector is suspended.

## 2. Retain the scenario without an execution path

- [x] 2.1 Move only `tests/e2e/test_release_acceptance.py` to `tests/scenarios_suspended/evh_024_release_acceptance.py`, retaining its source definition and marker while keeping its filename outside default pytest discovery.
- [x] 2.2 Add `tests/scenarios_suspended/README.md` that points to `_backlog/plans/evh-024-release-acceptance-diagnosis.md`, states the less-than-ten-second deterministic diagnostic-loop precondition, and names a new approved OpenSpec change as the reactivation path.
- [x] 2.3 Preserve `tests/scenarios/release.py`, `scripts/release_preflight.py`, and deterministic Bundle-authority/source-containment release control-plane evidence; revise only command-specific cases that currently require the removed Make target or workflow.

## 3. Remove active release selection and claims

- [x] 3.1 Remove the dedicated release-lane constants, focused release-selection enum member, release-acceptance evidence class, and `release-full-real-acceptance` active claim; revise the asset checker and its contracts so they validate only active evidence categories.
- [x] 3.2 Remove the `FULL_REAL_PIPELINE` release requirement from `EVH-005`'s active requirement-evidence policy and revise its red/green policy cases without treating the suspended source or historical attestation as a lower-authenticity replacement.
- [x] 3.3 Remove the `test-release-e2e` Make target and the `agent-release-e2e.yml` workflow, including workflow-trigger and contract references that would leave either one as an executable or required release surface.
- [x] 3.4 Update contributor testing guidance to distinguish active deterministic Bundle-authority evidence and historical attestation from retained suspended full-real material, without publishing a command that can run the suspended selector.

## 4. Verify and close out

- [x] 4.1 Run the new focused collection/asset, requirement-evidence, and documentation contracts plus `tests/unit/test_release_control_plane.py`; confirm the red cases are green and ordinary collection does not discover `tests/scenarios_suspended/evh_024_release_acceptance.py`.
- [x] 4.2 Run `cd deep_research_harness && UV_OFFLINE=1 make verify`; do not run `make test-release-e2e`, any credentialed selector, or an equivalent direct pytest command.
  - Executed 2026-08-07: the command stopped before project tests at pre-existing main-spec `> req:` header governance errors. Suspension-specific focused checks and the normal fast lane passed; this change neither repairs nor masks that unrelated baseline condition.
- [x] 4.3 Run `openspec validate suspend-credentialed-release-selector --strict` and `git diff HEAD --check`, then record `git status --porcelain=v1 --untracked-files=all` and confirm `backend/` and `frontend/` remain clean before archive.
