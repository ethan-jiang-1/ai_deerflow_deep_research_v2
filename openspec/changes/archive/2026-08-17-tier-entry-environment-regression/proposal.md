## Why

The two clean-copy entry-environment tests prove active supported-command contracts, but each copies the Harness and runs a complete `make install`. Keeping them in the mandatory `test-integration` lane makes every unrelated Harness pull request pay that setup cost, while the current gate has no integration duration budget or ownership-sensitive routing. The test is valid; its default execution tier is not.

## What Changes

- Create a maintained `tests/scenarios_periodic/` surface for deterministic, credential-free regression scenarios that are expensive because they construct an isolated project environment.
- Move the clean-copy local-entry-environment scenarios to that surface without changing their supported-entry, dependency-state, profile-check, or credential-preflight assertions.
- Keep the ordinary deterministic PR gate fast by excluding periodic scenarios from `make test-integration` and its canonical aggregate.
- Add an explicit periodic entry-environment target and a dedicated CI workflow that runs it for relevant entry/environment paths, on pushes to `master`, on a daily schedule, and on manual dispatch.
- Add executable contracts distinguishing maintained periodic scenarios from `scenarios_suspended/`, which remains exclusively for no-longer-default-supported credentialed release diagnostics requiring approved reactivation.
- Record and enforce a duration budget/report for the periodic lane so further cost growth is visible rather than silently inherited by every PR.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `evaluation-hardening`: Define the maintained low-frequency deterministic regression tier, its selection and CI cadence, and its separation from suspended release scenarios and the rapid PR gate.

## Impact

- `deep_research_harness/Makefile`, test selection assets, test-evidence registries, and test-directory contracts.
- `.github/workflows/` gains a dedicated entry-environment regression workflow; the existing deterministic workflow retains its identity and rapid gate role.
- `deep_research_harness/tests/integration/test_local_entry_environment.py` moves to `deep_research_harness/tests/scenarios_periodic/` with its assertions preserved.
- No runtime `src/` behavior, credentials, external services, or `deerflow/` source change.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/Makefile` and CI test selection, which decide the execution frequency and scope of maintained deterministic evidence.
- **Seam classification:** deterministic-guardrail — this change separates execution tiers while preserving the same public-entry contract and deterministic evidence.
- **Question:** How can a deterministic clean-copy entry-environment scenario remain maintained and discoverable while no longer imposing full-install setup cost on every unrelated PR?
- **Necessary adjacent/external contracts:** `evaluation-hardening` defines lane semantics, canonical gates, and evidence claims; `demo-pipeline` owns supported-entry setup/no-sync behavior; `local-configuration-profiles` supplies the profile-check prerequisite exercised by the scenario; `src/`, `scripts/`, `run/`, dependency, and CI workflow changes form the entry-environment dependency surface selected by GitHub Actions path and schedule triggers.
- **Evidence seam:** collection and asset-governance contracts prove rapid, periodic, and suspended selections are disjoint while periodic claims remain registered; an exact path-trigger workflow contract proves relevant changes and periodic cadence execute the periodic target; the relocated process scenario remains green; rapid `make verify` remains green without executing it.
- **Not in scope:** weakening or deleting the clean-copy assertions; moving the maintained scenario to `scenarios_suspended/`; credentialed release reactivation; changing runtime adapters, providers, or DeerFlow source; broad reclassification of unrelated integration tests.
- **Triggered review policies:** change-admission
