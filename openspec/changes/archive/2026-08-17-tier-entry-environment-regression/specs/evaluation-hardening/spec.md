> req: EVH-032

## MODIFIED Requirements

### Requirement: Release gate combines deterministic CI with optional LLM canary

The existing five pairwise-disjoint rapid or credentialed evidence selections, offline/no-implicit-sync rapid deterministic gate, strict selected live/release lanes, and stable existing workflow/status identity guarantees remain unchanged. Their canonical rapid deterministic command is `cd deep_research_harness && UV_OFFLINE=1 make verify`. A sixth, pairwise-disjoint `periodic` selection SHALL contain maintained deterministic public-entry scenarios whose clean-copy setup cost is intentionally excluded from the rapid gate. The periodic selection SHALL be credential-free, offline-capable after its explicit setup, and represented by a first-class pytest marker and test-evidence selection; `make test`, `make verify`, and every rapid focused target SHALL exclude it. Test-asset governance SHALL collect and validate periodic selectors and their central claims without executing their process bodies as part of the rapid gate. `tests/scenarios_suspended/` remains distinct: it contains only credentialed release diagnostics that are not active supported-contract evidence. A dedicated CI workflow SHALL run the periodic target when a pull request or `master` push changes the declared entry-environment dependency surface: `deep_research_harness/Makefile`, `pyproject.toml`, `uv.lock`, `run/**`, `scripts/**`, `src/**`, `src_fake/**`, `tests/scenarios_periodic/**`, or the periodic workflow definition. It SHALL also run daily and by manual dispatch; its result SHALL be visible as a distinct CI job, without claiming repository branch-protection configuration. The periodic target SHALL write a machine-readable duration report and enforce a declared per-scenario budget or an explicit owner/reason/expiry waiver. CI path filters, working directories, artifacts, release-attestation scopes, and protected-path checks for the existing rapid workflow SHALL continue to use `deep_research_harness/`, while `backend/`, `frontend/`, and `openspec/` boundary checks remain repository-root checks. A filesystem-root change SHALL not rename the existing rapid workflow display name, job/status identity, test lane, or evidence semantic. (`EVH-005`, `EVH-032`)

#### Scenario: Canonical verification starts from the Harness root
- **WHEN** a developer runs the complete rapid deterministic verification gate
- **THEN** `cd deep_research_harness && UV_OFFLINE=1 make verify` performs the existing local aggregate without resolving a former downstream root

#### Scenario: Unrelated product change avoids expensive clean-copy setup
- **WHEN** a Harness pull request changes no declared entry-environment dependency path
- **THEN** the rapid deterministic gate runs without executing `tests/scenarios_periodic/`, while its required fast, governance, lint, asset, integration, and workflow evidence remains unchanged

#### Scenario: Entry-environment change runs maintained process evidence
- **WHEN** a pull request or `master` push changes a declared entry-environment dependency path
- **THEN** the dedicated periodic workflow explicitly prepares the project and runs the periodic target, including the clean-copy public-entry scenarios

#### Scenario: Periodic evidence is not suspended evidence
- **WHEN** test collection inspects maintained periodic and suspended scenario directories
- **THEN** periodic scenarios are collected by their dedicated deterministic target without a `release_e2e` marker, while suspended scenarios remain excluded from all ordinary and periodic targets by their declared credentialed release markers

#### Scenario: Asset governance retains periodic public-entry claims
- **WHEN** test-asset governance validates the focused selections
- **THEN** it collects the periodic selector and validates its central claims and requirement impacts without executing the clean-copy process body as part of `make test-assets`
