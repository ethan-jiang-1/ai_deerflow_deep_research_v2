## Why

EVH-024's full-real credentialed selector has failed twice before producing a report
or citations and a recent selected run took more than eight minutes. It remains
valuable future acceptance evidence, but it is presently an expensive diagnostic
problem rather than an executable release gate; keeping it in the ordinary E2E
surface invites accidental execution and obscures that distinction.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/tests/assets/selection.py` and its release-lane contracts, which own executable test selection and evidence classification.
- **Question:** How can the repository retain the EVH-024 full-real selector for a later authorized diagnosis without exposing it to ordinary pytest discovery, Make targets, or CI workflows, while preserving the deterministic Bundle-authority proofs that remain useful now?
- **Necessary adjacent/external contracts:** `evaluation-hardening` defines exact active-lane/evidence semantics and prevents a suspended selector from masquerading as current release evidence; `tests/assets/requirement_evidence.py` currently makes a `FULL_REAL_PIPELINE` claim mandatory for `EVH-005` and therefore must distinguish active proof from retained historical material; `tests/scenarios/release.py` supplies the still-active deterministic control-plane adapter; `_backlog/plans/evh-024-release-acceptance-diagnosis.md` is the single issue record that names the future diagnosis and reactivation condition.
- **Evidence seam:** focused collection contracts prove ordinary pytest paths, all active Make lanes, evidence registries, and GitHub workflows select no suspended selector; the existing release control-plane unit suite proves the retained deterministic boundary still runs.
- **Not in scope:** diagnosing or repairing model/provider/source failures; running a credentialed selector; changing Deep Research runtime behavior, public APIs, Bundle lifecycle, test counts, or upstream `backend/` / `frontend/`; recreating the release workflow under another automatic name.
- **Triggered review policies:** change-admission

## What Changes

- Move only the full-real EVH-024 acceptance selector from `tests/e2e/` to the
  tracked but non-default-discoverable `tests/scenarios_suspended/` surface. Its
  non-test filename shall keep generic `pytest` collection from running it, while its
  retained marker remains a defense-in-depth exclusion from active lanes; a short local
  record shall link to the existing diagnosis issue and state the condition for
  reactivation.
- Remove its automatic/manual Make and GitHub workflow entry points, the complete
  active release-lane/evidence category, and the full-real evidence-policy requirement.
  The active records shall say that the selector is suspended, rather than claiming a
  passing or current release acceptance. The versioned redacted attestation remains
  historical material, not a substitute for current active evidence.
- Retain `tests/scenarios/release.py`, `scripts/release_preflight.py`, and the
  deterministic Bundle-authority release control-plane evidence in their current
  active locations. The suspended selector is not a substitute for those assertions.
- Update contributor-facing testing guidance to distinguish active deterministic
  proof, suspended full-real evidence, and the later diagnostic issue that may
  reactivate it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `evaluation-hardening`: Defines the suspended full-real selector's collection,
  evidence, workflow, documentation, and reactivation boundaries while retaining its
  deterministic release evidence.

## Impact

This affects the release E2E test file, test-lane selection/evidence registries,
Makefile, release workflow, focused test contracts, and testing documentation under
`deep_research_harness/`, plus the existing EVH-024 issue plan. It adds no runtime
dependency and makes no change under `backend/` or `frontend/`.
