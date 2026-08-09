# local-configuration-profiles Specification

> req: LCP-001, LCP-002, LCP-003, LCP-004, LCP-005, LCP-006

## Purpose

Project-owned local DeerFlow configuration selection, initialization, isolation,
launch adaptation, and redacted observability without modifying upstream-owned
root surfaces.

## Requirements


### Requirement: Project-owned profiles select isolated local configuration

The project SHALL place each local profile pair only under
`profiles/<profile>/`, with profile-managed runtime data only under
`profiles/<profile>/.deer-flow/`. Valid names match
`[a-z][a-z0-9-]{0,31}`. The resolver SHALL reject missing, partial,
non-regular, symlinked, or escaping pairs before it launches DeerFlow.

The selected process SHALL use the repository root as `DEER_FLOW_PROJECT_ROOT`
and the project-owned contained paths for configuration, extensions, DeerFlow
home. It SHALL accept either SQLite with an exact absolute
`profiles/<profile>/.deer-flow/data` directory or a memory backend with no
persistence claim for database/checkpoint state. It SHALL reject legacy
`checkpointer`, Postgres, relative, external, or other-profile SQLite
configuration. (`LCP-001`, `LCP-003`)

Profiles SHALL use the shared repository `skills/` root when their selected
configuration omits `skills.path`. The launch environment SHALL remove an
inherited `DEER_FLOW_SKILLS_PATH`; an alternate skills root, when intentionally
needed, SHALL be declared as `skills.path` in the selected profile config and
is outside profile-managed writable-state isolation.

This capability SHALL NOT claim or validate isolation for sandbox-provider
storage, host mounts, or Docker volumes. Those settings may remain in a selected
profile config as ordinary DeerFlow configuration, but their external paths are
outside this local profile isolation contract.

#### Scenario: Profiles do not overlap mutable state
- **WHEN** normal and demo are initialized and validated
- **THEN** their pairs, homes, and SQLite directories are non-overlapping
  project-owned locations beneath their respective `profiles/<profile>/`

#### Scenario: A memory profile is intentionally ephemeral
- **WHEN** a valid test or demo profile selects `database.backend: memory`
- **THEN** it launches with its contained DeerFlow home, reports ephemeral
  memory database state rather than SQLite durability, and does not claim that
  database/checkpoint state persists

#### Scenario: Unsafe profile inputs fail before launch
- **WHEN** a name or any pair/state component is malformed, symlinked, or
  escaping
- **THEN** initialization, validation, and launch fail closed without writing an
  external target or starting a process

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

### Requirement: Agent commands adapt the unchanged upstream launcher

The `deep_research_harness/Makefile` SHALL provide `profile-setup`, `profiles`,
`profile-init`, `profile-check`, and `profile-dev`. `profile-dev` SHALL be the only
profile launch mode; production and daemon profile modes are out of scope.
`profile-setup` SHALL first invoke the unchanged root `make install` and then
invoke the explicit downstream `make install` environment setup. That downstream setup
SHALL prepare the reviewed locked project environment with every optional dependency
set required by the supported local demo and workbench commands: `operations`,
`demo-tui`, and `demo-real`. Every other profile command SHALL use that environment
with sync disabled and SHALL preflight a missing `deep_research_harness/.venv/` before
invoking `uv`. A missing environment SHALL report `make profile-setup` before a
launcher, service stop, or profile-state creation occurs. `profile-dev` SHALL invoke
the unchanged root launcher only as `--dev --skip-install`; ordinary profile commands
SHALL NOT install or synchronize dependencies implicitly. Valid profile commands SHALL
validate before launcher execution.

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

#### Scenario: Profile setup prepares the profile-gated workbench dependencies
- **WHEN** a beginner runs `make profile-setup` and then starts the supported
  profile-gated local workbench
- **THEN** the workbench's declared optional dependencies are already present in the
  prepared locked project environment, and the workbench does not synchronize them
  itself

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

### Requirement: Profile observability is safe and restart-honest

Agent profile list/check/launch output SHALL identify only a safe profile label,
readiness, either isolated local SQLite or ephemeral memory state, and
restart-required state. It SHALL not expose paths, raw configurations,
environment values, secrets, mounts, connection strings, or parser/provider
detail. Profile selection starts a fresh process and creates no graph, lifecycle,
checkpoint, ledger, sandbox-content, run-session, Agent, skill, MCP, or ACP
authority. (`LCP-004`, `LCP-005`)

#### Scenario: Diagnostics remain redacted and authority-neutral
- **WHEN** a profile contains sentinel paths, credentials, or malformed provider
  details
- **THEN** normal diagnostics expose only safe profile facts and neither create
  nor interpret a downstream runtime authority

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
