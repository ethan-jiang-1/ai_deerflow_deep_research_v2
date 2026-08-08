> req: DEC-003, DEC-006

## ADDED Requirements

### Requirement: Deployment loads the downstream package from the canonical Harness root

Local, production, and Docker launch paths SHALL load
`deerflow_deep_research` from `deep_research_harness/src/`. Docker mounts, image build
inputs, `PYTHONPATH`, configuration materialization, public-skill source, and readiness
checks SHALL use the canonical Harness root and SHALL not retain an old-root fallback.
They SHALL preserve the distribution/import/public-tool identities and SHALL not require
changes under upstream `backend/` or `frontend/`. (`DEC-006`)

#### Scenario: Docker mount uses the new root without a second source path
- **WHEN** deployment configuration is rendered for a supported environment
- **THEN** it mounts only `deep_research_harness/src` as the downstream source and resolves the unchanged Python package without a `deerflow_research` fallback

## MODIFIED Requirements

### Requirement: Gateway loads one downstream package in every supported environment

The project SHALL provide local-development, local-production, and Docker assembly that
resolves `deerflow_deep_research` from the checked-out or mounted
`deep_research_harness/src` source while leaving upstream source unchanged. Each start
SHALL inject a secret-free, canonical, strictly parsed `v1:<64 lowercase hex>`
fingerprint of the effective startup-only provider/sandbox/normalized-worker inputs for
runtime drift detection; missing, malformed, or unknown-version fingerprints SHALL fail
closed and launch code SHALL NOT evaluate fingerprint command output as shell source.
Host package source SHALL NOT be mounted into the research sandbox.

The loadable-source mechanism is verified with contract tests: the `prepare.py`
preparation core performs upstream-equivalent sync plus `--no-deps` editable
installation into the backend environment, validates config-target agreement and
version, verifies harness/module origin, and computes a secret-free startup candidate.
The Docker Compose override read-only mounts `deep_research_harness/src` at the private
container target `/app/deep_research_harness/src`, exports that target as the
Gateway-only `PYTHONPATH`, and exports the container-effective candidate. Project-owned
live launch automation and deployment verification require a provisioned deployment
environment and remain outside this downstream package's scope.

#### Scenario: Editable source is resolved by the preparation core
- **WHEN** the preparation core runs against a caller-quiesced backend environment
- **THEN** it proves the AppConfig and upstream config-upgrade targets are the same canonical file, passes exact-current-version preflight, runs upstream-equivalent dependency sync before the `--no-deps` editable install, verifies compatible DeerFlow 2.1 harness and module origin, computes a secret-free startup candidate, and Python resolves `deerflow_deep_research` from the current `deep_research_harness/src` tree

#### Scenario: Mismatched upstream config is refused before fingerprinting
- **WHEN** the effective config version is missing, invalid, older, or newer than `config.example.yaml.config_version`
- **THEN** preparation performs no shared backend-environment mutation or fingerprint and directs the operator to upgrade an older config or reconcile the config/checkout pair for any other mismatch

#### Scenario: Ambiguous config targets are refused
- **WHEN** AppConfig resolution and the current upstream config-upgrade search order select different canonical files, including an unqualified root/backend shadow pair
- **THEN** preparation performs no shared backend-environment mutation or fingerprint and reports the conflicting paths without exposing their contents

#### Scenario: Docker exports the container-effective candidate
- **WHEN** the base-first Docker override renders the Gateway command
- **THEN** it read-only mounts `deep_research_harness/src` at `/app/deep_research_harness/src`, sets that exact Gateway-only `PYTHONPATH`, and computes and exports the candidate inside the container from the mounted source and effective config before the unchanged uvicorn tokens, without mounting host source into the research sandbox

#### Scenario: Startup-only drift requires restart
- **WHEN** live config reload changes effective database/checkpointer or sandbox values after the launcher captured the process-start fingerprint
- **THEN** doctor and runtime integration report `restart_required` before nested provider or sandbox access

### Requirement: Public entry skill is committed and enabled

The project SHALL keep the `deep-research-controller` skill source under
`deep_research_harness/config/public-skill/`, materialize it under `skills/public/`, and
store its enabled state in `extensions_config.json`. The skill MAY route research
requests to the `start | resume | status | cancel | refine` lifecycle. It SHALL describe
the public entry as an all-real lifecycle, distinguish a typed blocked, unavailable,
conflict, or ended outcome from completed research, and direct configuration/readiness
failures through documented legal lifecycle controls. It SHALL NOT contain graph
topology, phase prompts, fixture controls, answer payloads, exclusive tool claims, or
security-isolation claims. (`DEC-003`)

#### Scenario: Public skill is available
- **WHEN** configuration is materialized and enabled skills are loaded
- **THEN** the public Deep Research entry skill is discoverable with content matching its committed source beneath the canonical Harness root

#### Scenario: Real lifecycle is represented honestly
- **WHEN** the entry skill handles a research request or lifecycle result
- **THEN** it preserves the returned real lifecycle mode and terminal status, distinguishes `resume` from `refine`, does not fabricate findings or report completion after a blocked/unavailable outcome, and does not describe a fixture path as a public research capability

#### Scenario: Legacy custom path is rejected
- **WHEN** validation finds the project entry skill under `skills/custom/deep-research-controller/` instead of the public path
- **THEN** the configuration check fails and identifies the legacy location
