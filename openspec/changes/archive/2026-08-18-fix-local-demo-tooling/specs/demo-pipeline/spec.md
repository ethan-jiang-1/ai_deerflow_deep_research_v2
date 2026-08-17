## MODIFIED Requirements

### Requirement: Makefile provides targets for all demo variants

The `deep_research_harness/Makefile` SHALL retain its fixed fixture-graph and all-real
CLI/TUI demo targets, `DEMO_ARGS` forwarding, and direct-extra selection. It SHALL
enable fixture source only for the child process of a fixture route. Its `--help` and
README command description SHALL identify every credential-free route as deterministic
fixture-graph composition verification.

The Makefile's operator demo, session, soft-bundle, and profile entry commands SHALL
invoke `uv` with `UV_NO_CACHE=1` by default, so restricted/sandboxed environments
cannot be blocked by uv global-cache permission errors; callers MAY override the
default with `UV_NO_CACHE=0`. Test, install, and build targets SHALL keep normal uv
caching so the offline verification gate can still resolve build backends from the
cache. The `demo-real` and `demo-tui` targets SHALL default `PROFILE` to `demo`
when the caller omits it, so runbook and script callers that pass only `DEMO_ARGS`
still launch with the standard demo profile; an explicitly empty `PROFILE=` SHALL
remain rejected by the target's preflight guard.

`make install` SHALL be the explicit project-environment synchronization owner for
every supported demo CLI, TUI, fixture-graph, retained-observation, and workbench
target, and for the documented prepared all-real launcher. It SHALL synchronize the
reviewed locked environment with the `operations`, `demo-tui`, and `demo-real`
optional dependency sets. A reviewed dependency-metadata or lockfile change occurs
outside ordinary target execution; `make install` SHALL use the locked state and SHALL
fail rather than refresh it implicitly.

Real targets SHALL load `deep_research_harness/.env` when present; fixture-graph
targets remain credential-free. No target SHALL use `deerflow_research/` as a working
directory or fallback, and no `backend/` or `frontend/` file is changed.
(`DPL-005`)

#### Scenario: Local uv invocations default to no cache
- **WHEN** an operator runs a supported local demo target without `UV_NO_CACHE` set in an environment where the global uv cache is not readable
- **THEN** the target runs without touching the global uv cache and does not fail with a cache `Operation not permitted` error

#### Scenario: Cache default remains overridable
- **WHEN** an operator runs a supported local demo target with `UV_NO_CACHE=0`
- **THEN** the target uses the normal uv cache behavior instead of the default no-cache setting

#### Scenario: Real demo targets default the profile
- **WHEN** an operator runs `make demo-real` or `make demo-tui` with `DEMO_ARGS` but without `PROFILE`
- **THEN** the target launches with the default `demo` profile instead of failing with a Usage error

#### Scenario: Explicitly empty profile is still rejected
- **WHEN** an operator runs `make demo-real PROFILE=` with an explicitly empty profile
- **THEN** the target rejects the invocation with the Usage error and exits without launching

#### Scenario: Demo target loads the renamed local environment
- **WHEN** `make demo-real` runs from the canonical downstream module
- **THEN** it loads `deep_research_harness/.env` when present and does not resolve an
  old-root environment file

#### Scenario: Explicit install prepares every supported demo extra
- **WHEN** a clean checkout runs `make install` followed by a supported real CLI, real
  TUI, fixture-graph TUI, fixture-graph CLI, retained-observation, workbench, or documented
  prepared all-real launcher entry
- **THEN** the entry can use its declared optional dependencies from the prepared
  locked project environment without synchronizing a dependency set itself

#### Scenario: Credential-free commands are fixture-graph routes
- **WHEN** an operator reads the fixture-graph command help or the README entry map
- **THEN** it identifies the route as fixture-graph verification and names no
  full-fake/no-graph lifecycle or command alias
