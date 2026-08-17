> req: EVH-031

## Purpose

Make deterministic lane selection reference only live registered markers, keep suspended release material collectable-but-excluded, and guarantee the documented deterministic gate is green from a clean checkout.

## ADDED Requirements

### Requirement: Deterministic test selection references only live markers and passes from a clean checkout

The deterministic verification gate SHALL pass from a clean checkout (no local `profiles/` state, `.env`, or `config.yaml`). The retired `postgres` marker SHALL be absent from pytest marker registration, from every deterministic lane expression, and from every exact-string lane assertion; no lane SHALL exist that fails collection because it selects a retired marker. Suspended release-acceptance material SHALL remain pytest-collectable under `tests/scenarios_suspended/` (file name matches `test_*.py`) while excluded from every deterministic lane by its declared `requires_llm`/`release_e2e` markers, so suspension is visible to collection tooling rather than hidden by an uncollectable file name. Deterministic integration tests SHALL construct the profile state they check themselves and SHALL NOT depend on gitignored local state under `profiles/`.

#### Scenario: Retired marker has no live reference

- **WHEN** a lane expression, a lane-selection constant, or a contract-test assertion references the `postgres` marker
- **THEN** the reference SHALL be absent, and no `test-postgres` target SHALL exist

#### Scenario: Suspended release material stays collectable but excluded

- **WHEN** pytest collects the suspended directory
- **THEN** it SHALL find the release-acceptance file by its `test_*.py` name, and every deterministic lane SHALL deselect it through its declared markers

#### Scenario: Deterministic gate passes from a clean checkout

- **WHEN** the repository is checked out cleanly (no local profile, env, or config state) and `UV_OFFLINE=1 make verify` runs
- **THEN** the gate SHALL complete successfully, including lint, asset coverage, and integration lanes

#### Scenario: Integration tests construct their own profile state

- **WHEN** a deterministic integration test prepares a copied project and checks a profile entry
- **THEN** the test SHALL construct the checked profile state itself and SHALL NOT read or copy gitignored local `profiles/` content
