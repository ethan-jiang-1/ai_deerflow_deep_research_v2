> req: LCP-001, LCP-002, LCP-003, LCP-005, LCP-006

## ADDED Requirements

### Requirement: Local profile commands and state references use the canonical Harness root

Project-owned local profile commands, templates, diagnostics, writable runtime roots,
and test fixtures SHALL resolve the downstream project through
`deep_research_harness/`. They SHALL preserve the existing profile isolation and secret
handling contract, but SHALL not use `deerflow_research/` as a working directory,
configuration path, diagnostic root, or fallback. Profile configuration and external
checkpointer settings SHALL not become Deep Research Run lifecycle authority. (`LCP-006`)

#### Scenario: Selected profile does not restore the old root
- **WHEN** a named local profile initializes or launches Deep Research
- **THEN** every project-owned path resolves beneath `deep_research_harness/` and the profile cannot select a legacy root or recover a deleted Run Bundle from its state store

## MODIFIED Requirements

### Requirement: Agent commands adapt the unchanged upstream launcher

The `deep_research_harness/Makefile` SHALL provide `profile-setup`, `profiles`,
`profile-init`, `profile-check`, and `profile-dev`. `profile-dev` SHALL be the only
profile launch mode; production and daemon profile modes are out of scope.
`profile-setup` SHALL first invoke the unchanged root `make install` and then
explicitly synchronize the locked `deep_research_harness/` operations environment.
Every other profile command SHALL use that environment with sync disabled and SHALL
preflight a missing `deep_research_harness/.venv/` before invoking `uv`. A missing
environment SHALL report `make profile-setup` before a launcher, service stop, or
profile-state creation occurs. `profile-dev` SHALL invoke the unchanged root launcher
only as `--dev --skip-install`; ordinary profile commands SHALL NOT install or
synchronize dependencies implicitly. Valid profile commands SHALL validate before
launcher execution.

The resolver SHALL use DeerFlow's documented configuration-path environment variables
directly and SHALL not add a shell hook, source interception, or root file
modification. Before launch, it SHALL parse root `.env` key names without printing
values. Profile mode SHALL accept only comments, blank lines, and one direct literal
`NAME=value` assignment per line, with an optional `export ` prefix. A value SHALL be
an unquoted shell-safe literal or a single-quoted literal and SHALL NOT use `$`
expansion, backticks, command substitution, shell control operators, or command
separators. It SHALL reject shell commands, control operators, indirect assignment, or
other non-dotenv syntax before launcher execution. It SHALL also fail when the parsed
file defines any of `DEER_FLOW_CONFIG_PATH`, `DEER_FLOW_EXTENSIONS_CONFIG_PATH`,
`DEER_FLOW_HOME`, `DEER_FLOW_PROJECT_ROOT`, or `DEER_FLOW_SKILLS_PATH`. The outcome
SHALL identify the key to remove and state that ordinary API-key/secret entries remain
in `.env`. Root DeerFlow commands retain their native behavior, and root `make stop`
remains profile-agnostic. (`LCP-002`, `LCP-005`)

#### Scenario: Root dotenv remains the secret source
- **WHEN** root `.env` conflicts with the selected demo paths
- **THEN** `make profile-dev PROFILE=demo` reports the setting that must be removed before it invokes the unchanged launcher

#### Scenario: Shell-like root environment input fails before source
- **WHEN** root `.env` contains a shell command, control operator, indirect assignment, or shell expansion rather than a direct literal dotenv value
- **THEN** profile launch reports a safe environment-setup outcome and does not invoke the shell-based upstream launcher

#### Scenario: A missing operations environment gives one setup command
- **WHEN** a beginner uses a profile command before the locked operations environment has been installed
- **THEN** it reports `make profile-setup`, and no launcher, service stop, dependency synchronization, or profile runtime state is created

#### Scenario: Ordinary profile commands do not synchronize dependencies
- **WHEN** a prepared beginner runs list, init, check, or launch
- **THEN** that command uses the locked environment with synchronization disabled; only the explicit `profile-setup` command may install or synchronize dependencies, and launch passes `--skip-install` to the upstream launcher

#### Scenario: Standard environment selection reaches the upstream launcher
- **WHEN** root `.env` contains only secret values and demo is selected
- **THEN** `make profile-dev PROFILE=demo` starts the unchanged launcher with the validated standard DeerFlow configuration and home environment values

#### Scenario: Inherited skills environment cannot silently change a profile
- **WHEN** the parent environment or root `.env` provides `DEER_FLOW_SKILLS_PATH`
- **THEN** profile launch either reports the root dotenv selector conflict or removes the inherited value, so the selected config's `skills.path` or the shared repository skills root is the only skills-root decision

#### Scenario: Profiles do not imply concurrent local stacks
- **WHEN** a profile is launched while local DeerFlow services are already running
- **THEN** the unchanged launcher retains ownership of its fixed ports, root logs, compatibility directories under `backend/`, and stop-then-start behavior; profile isolation does not claim to run a second stack concurrently

#### Scenario: Profiles do not define deployment modes
- **WHEN** a user seeks production or daemon launch behavior
- **THEN** this capability exposes no profile production/daemon command and does not claim to configure Docker or deployment behavior

#### Scenario: A profile does not certify sandbox/mount isolation
- **WHEN** a selected profile contains sandbox provider or mount configuration
- **THEN** profile validation does not present those settings as isolated, inspected, or Docker-ready; only the profile configuration, `DEER_FLOW_HOME`, and permitted database classification are covered by this capability

### Requirement: Initialization preserves upstream root ownership

`profiles/README.md` SHALL document normal, development, test, and demo.
`make profile-init PROFILE=<name>` from `deep_research_harness/` SHALL seed an absent
complete pair from repository-root `config.yaml`, remove copied legacy `checkpointer`,
select contained SQLite, and preserve every root file. An absent root config SHALL
report the existing `make setup`/`make config` action without creating profile material.
Absent root extensions produce a minimal empty extensions document. Initialization is
byte-stable for an existing pair and refuses partial pairs. `profiles/.gitignore` SHALL
use `*`, `!.gitignore`, and `!README.md`, leaving only itself and the guide tracked
while ignoring materialized profile pairs and state. (`LCP-001`, `LCP-003`)

An initialized profile pair SHALL be an independent snapshot: later changes to the root
pair SHALL NOT be copied or merged into it, and re-running profile initialization SHALL
leave a complete existing pair byte-for-byte unchanged. The unchanged upstream launcher
may apply its normal config-version upgrade to the selected profile before service
start; this capability adds no overlay or second upgrade mechanism. That upstream
upgrade and any backup it creates SHALL apply only to the selected ignored profile pair,
never to the root seed files.

#### Scenario: Root configuration remains an input only
- **WHEN** a beginner initializes demo
- **THEN** the root config, root extensions, root ignore rules, root launcher, and root documentation remain unchanged, and no runtime/database is created

#### Scenario: Missing root configuration does not create a partial profile
- **WHEN** a beginner runs profile initialization before repository-root `config.yaml` exists
- **THEN** the command directs the beginner to `make setup` or `make config`, and creates neither a profile directory nor runtime/database state

#### Scenario: A completed profile remains an independent scenario
- **WHEN** root configuration changes after demo has been initialized and the beginner runs demo initialization again
- **THEN** demo's complete configuration pair is unchanged; it is updated only by deliberate profile editing or the unchanged upstream config-version upgrade

#### Scenario: Upstream config upgrade stays inside the selected profile
- **WHEN** a selected profile needs the unchanged upstream config-version upgrade
- **THEN** any updated config and backup are under that ignored profile directory, while repository-root `config.yaml` remains unchanged
