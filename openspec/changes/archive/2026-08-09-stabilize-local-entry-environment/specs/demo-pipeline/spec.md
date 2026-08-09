## MODIFIED Requirements

### Requirement: Makefile provides targets for all demo variants

The `deep_research_harness/Makefile` SHALL retain the existing fake and real CLI/TUI
demo targets, `DEMO_ARGS` forwarding, and direct-extra selection. It SHALL add the
explicit `make demo-fixture-graph` verification target, which enables fixture source
only for its child process and selects the fixture-graph composition route. Its
`--help` and README command description SHALL identify that route as deterministic
graph-composition verification, not as a replacement for `make demo`,
`make demo-scripted`, or `make demo-tui-fake`.

`make install` SHALL be the explicit project-environment synchronization owner for
every supported demo CLI, TUI, fixture-graph, retained-observation, and workbench
target, and for the documented prepared all-real launcher. It SHALL synchronize the
reviewed locked environment with the `operations`, `demo-tui`, and `demo-real`
optional dependency sets. A reviewed dependency-metadata or lockfile change occurs
outside ordinary target execution; `make install` SHALL use the locked state and SHALL
fail rather than refresh it implicitly.

Real targets SHALL load `deep_research_harness/.env` when present; full-fake targets
retain their credential-free behavior. No target SHALL use `deerflow_research/` as a
working directory or fallback, and no `backend/` or `frontend/` file is changed.
(`DPL-005`)

#### Scenario: Demo target loads the renamed local environment
- **WHEN** `make demo-real` runs from the canonical downstream module
- **THEN** it loads `deep_research_harness/.env` when present and does not resolve an
  old-root environment file

#### Scenario: Explicit install prepares every supported demo extra
- **WHEN** a clean checkout runs `make install` followed by a supported real CLI, real
  TUI, fake TUI, fixture-graph, retained-observation, workbench, or documented
  prepared all-real launcher entry
- **THEN** the entry can use its declared optional dependencies from the prepared
  locked project environment without synchronizing a dependency set itself

#### Scenario: Fixture-graph command is not a full-fake alias
- **WHEN** an operator reads the fixture-graph command help or the README entry map
- **THEN** it identifies `make demo-fixture-graph` as graph verification and retains
  the existing full-fake command names for their separate zero-credential contract

### Requirement: Command boundary selects a comprehensible project environment

Supported demo CLI, TUI, fixture-graph, retained-observation, and workbench Make
targets, plus the documented prepared all-real launcher, SHALL deliberately select the
agent project environment or fail before Python begins with a concise
command-environment explanation. A stale active environment from another project SHALL
not produce an unexplained `uv` `VIRTUAL_ENV` mismatch warning as the first
user-visible result, and the entry SHALL not silently execute dependencies from an
unrelated environment.

Before ordinary execution, each entry SHALL run a deterministic local preflight for
the complete optional dependency set prepared by `make install`. If the project
environment is missing or lacks a required distribution, it SHALL exit nonzero before
the adapter begins and identify only `make install` as the corrective setup command. A
prepared ordinary entry SHALL use the locked project environment with synchronization
disabled. It SHALL neither resolve nor update `uv.lock` nor create, remove, or change
the project `.venv`; declared ignored run-bundle, retained-observation, and diagnostic
artifacts remain permitted target outputs. `make lock-check` SHALL remain the separate
lock-freshness assertion; no ordinary entry's no-sync execution SHALL claim to validate
or refresh lock freshness.
(`DPL-006`)

#### Scenario: Foreign active environment is handled before onboarding
- **WHEN** a shell has `VIRTUAL_ENV` set to a different project environment and a user
  runs `make demo-real` or `bash run/real-research.sh`
- **THEN** the entry uses the agent project environment deliberately or stops with a
  clear `make install` setup message, rather than leaving a warning followed by an
  unrelated lifecycle failure

#### Scenario: Incomplete prepared environment fails before the entry adapter
- **WHEN** a user runs a supported target or the documented launcher while a
  distribution required by the complete `make install` environment is absent
- **THEN** it exits nonzero before Python adapter execution, does not synchronize or
  mutate dependency state, and names `make install` as the only corrective action

#### Scenario: Ordinary entries preserve dependency state
- **WHEN** a clean prepared copy runs supported help, full-fake, fixture-graph,
  retained-observation, bounded profile/workbench, and launcher credential-preflight
  commands
- **THEN** the tracked lockfile and project environment state remain unchanged across
  every ordinary command, except for the target's declared ignored run or diagnostic
  artifacts

#### Scenario: Concurrent read-only entries do not contend over setup
- **WHEN** independently started supported help or read-only entry commands overlap in
  a prepared project environment
- **THEN** each uses synchronization-disabled execution and neither command mutates
  `uv.lock` or the project `.venv`

#### Scenario: Lock freshness remains independently checkable
- **WHEN** a user needs to verify whether dependency metadata and the tracked lock
  agree
- **THEN** `make lock-check` performs that assertion independently of ordinary target
  execution and a no-sync target does not report lock freshness by implication
