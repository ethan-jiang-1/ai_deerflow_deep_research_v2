## MODIFIED Requirements

### Requirement: Agent commands adapt the unchanged upstream launcher

The `deep_research_harness/Makefile` SHALL provide `profile-setup`, `profiles`,
`profile-init`, `profile-check`, and `profile-dev`. `profile-dev` SHALL be the only
profile launch mode; production and daemon profile modes are out of scope.
`profile-setup` SHALL first invoke the unchanged root `make install` and then invoke
the explicit downstream `make install` environment setup. That downstream setup SHALL
prepare the reviewed locked project environment with every optional dependency set
required by the supported local demo and workbench commands: `operations`, `demo-tui`,
and `demo-real`. Every other profile command SHALL use that environment with sync
disabled and SHALL preflight a missing `deep_research_harness/.venv/` before invoking
`uv`. A missing environment SHALL report `make profile-setup` before a launcher,
service stop, or profile-state creation occurs. `profile-dev` SHALL invoke the
unchanged root launcher only as `--dev --skip-install`; ordinary profile commands
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
