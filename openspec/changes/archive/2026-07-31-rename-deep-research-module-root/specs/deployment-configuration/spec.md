## MODIFIED Requirements

### Requirement: Gateway loads one downstream package in every supported environment

The project SHALL provide local-development, local-production, and Docker assembly
that resolves `deerflow_deep_research` from the checked-out or mounted
`deerflow_research/src` source while leaving upstream source unchanged. Each start
SHALL inject a secret-free, canonical, strictly parsed `v1:<64 lowercase hex>`
fingerprint of the effective startup-only provider/sandbox/normalized-worker inputs
for runtime drift detection; missing, malformed, or unknown-version fingerprints SHALL
fail closed and launch code SHALL NOT evaluate fingerprint command output as shell
source. Host package source SHALL NOT be mounted into the research sandbox.

The loadable-source mechanism is verified with contract tests: the `prepare.py`
preparation core performs upstream-equivalent sync plus `--no-deps` editable
installation into the backend environment, validates config-target agreement and
version, verifies harness/module origin, and computes a secret-free startup candidate.
The Docker Compose override read-only mounts `deerflow_research/src` at the private
container target `/app/deerflow_research/src`, exports that target as the Gateway-only
`PYTHONPATH`, and exports the container-effective candidate. Project-owned live launch
automation and deployment verification require a provisioned deployment environment
and remain outside this downstream package's scope.

#### Scenario: Editable source is resolved by the preparation core
- **WHEN** the preparation core runs against a caller-quiesced backend environment
- **THEN** it proves the AppConfig and upstream config-upgrade targets are the same
  canonical file, passes exact-current-version preflight, runs upstream-equivalent
  dependency sync before the `--no-deps` editable install, verifies compatible
  DeerFlow 2.1 harness and module origin, computes a secret-free startup candidate,
  and Python resolves `deerflow_deep_research` from the current
  `deerflow_research/src` tree

#### Scenario: Mismatched upstream config is refused before fingerprinting
- **WHEN** the effective config version is missing, invalid, older, or newer than
  `config.example.yaml.config_version`
- **THEN** preparation performs no shared backend-environment mutation or fingerprint
  and directs the operator to upgrade an older config or reconcile the config/checkout
  pair for any other mismatch

#### Scenario: Ambiguous config targets are refused
- **WHEN** AppConfig resolution and the current upstream config-upgrade search order
  select different canonical files, including an unqualified root/backend shadow pair
- **THEN** preparation performs no shared backend-environment mutation or fingerprint
  and reports the conflicting paths without exposing their contents

#### Scenario: Docker exports the container-effective candidate
- **WHEN** the base-first Docker override renders the Gateway command
- **THEN** it read-only mounts `deerflow_research/src` at
  `/app/deerflow_research/src`, sets that exact Gateway-only `PYTHONPATH`, and
  computes and exports the candidate inside the container from the mounted source and
  effective config before the unchanged uvicorn tokens, without mounting host source
  into the research sandbox

#### Scenario: Startup-only drift requires restart
- **WHEN** live config reload changes effective database/checkpointer or sandbox
  values after the launcher captured the process-start fingerprint
- **THEN** doctor and runtime integration report `restart_required` before nested
  provider or sandbox access

