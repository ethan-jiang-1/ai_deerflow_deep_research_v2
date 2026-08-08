## Context

The existing root checkout is upstream DeerFlow and is read-only for downstream
work. `profiles/` is a new downstream-owned root-level directory, explicitly
separate from those existing upstream paths.
DeerFlow already supports selecting an arbitrary complete YAML config with
`DEER_FLOW_CONFIG_PATH`, the paired extensions JSON with
`DEER_FLOW_EXTENSIONS_CONFIG_PATH`, and writable state with `DEER_FLOW_HOME`.
Those supported pre-process inputs are exactly what named local profiles need.

The earlier design incorrectly treated root `.env` loading as a launcher problem
to intercept with a Bash hook. It is not needed: root `.env` is the secret
source, while explicit profile selection is a separate startup environment
choice. A root `.env` that itself selects an AppConfig is ambiguous; the profile
command must identify that setup conflict before launch.

## Decisions

### Profiles are complete configuration-and-state units in the project-owned root

```text
profiles/
  README.md                    # committed guide
  .gitignore                   # committed; ignores materialized profiles
  <name>/
    config.yaml                # local, ignored
    extensions_config.json     # local, ignored
    .deer-flow/
      data/deerflow.db         # local, ignored
      ...                      # profile-selected DeerFlow runtime data
```

`profiles/` is a downstream-owned root-level data directory, not a DeerFlow
upstream directory and not Deep Research source. It gives a beginner one visible
place per scenario: deleting `profiles/demo/` removes that local demo entirely.
Its committed `.gitignore` uses `*`, `!.gitignore`, and `!README.md`, so those
two guide surfaces remain tracked while every materialized profile directory is
local only.
The resolver remains in `agent/scripts/` because it is command tooling, but it
accepts `[a-z][a-z0-9-]{0,31}`, reads the root config and optional extensions
file only as seeds, and writes profile material only under `profiles/`. Its
seed is explicitly the repository-root `config.yaml`, matching the project-root
configuration selected by the profile launch; it does not guess from a legacy
`backend/config.yaml` fallback. When that root file is absent, initialization
reports the existing `make setup`/`make config` action without creating a
profile. It
removes a copied legacy `checkpointer` and initially selects contained SQLite
at `database.sqlite_dir`. Initialization creates only the two configuration
files; DeerFlow creates its home and database on first launch. A user may change
an initialized local test or demo profile to `database.backend: memory` for an
ephemeral process-local database mode; its profile-owned DeerFlow home remains
separate and may still contain other runtime data. No profile name has magic
behavior: the validated config, not its label, selects SQLite versus memory. No
upstream file changes.

Initialization is a one-time snapshot, not a profile inheritance mechanism.
Later root configuration edits never overwrite a complete profile, and rerunning
`profile-init` reports it ready without changing either file. A user changes the
specific scenario's profile files deliberately; the unchanged upstream launcher
may still apply its normal config-version upgrade to the selected profile before
service start. This preserves scenario independence without inventing a YAML
merge language or a second upgrade mechanism.

### Agent commands use the documented DeerFlow configuration interface

From `agent/`:

```text
make profile-setup
make profile-init PROFILE=demo
make profile-check PROFILE=demo
make profile-dev PROFILE=demo
```

`profile-setup` is the only command allowed to install or synchronize
dependencies. It first invokes the unchanged root `make install`, then creates
the locked `agent/` operations environment that supplies `ruamel.yaml` for the
resolver. This is an explicit one-time prerequisite because root install does
not install that downstream extra. Every ordinary profile command first checks
that `agent/.venv/` exists, before invoking `uv`; if setup is missing, it
reports that one command and does not start, stop, or alter DeerFlow. The
resolver command uses `uv run --locked --no-sync`, and `profile-dev` invokes the
upstream launcher with `--dev --skip-install`. This lets a beginner finish setup
once, then init/check/launch without hidden installation or synchronization work.

The profile command surface deliberately stops at local development:
`profile-dev` is the only launch command. The upstream root launcher continues
to own production and daemon modes directly; profile selection does not create a
second deployment interface or make Docker/daemon behavior part of this change.

The resolver validates before `exec` and constructs:

```text
DEER_FLOW_PROJECT_ROOT=<repository root>
DEER_FLOW_CONFIG_PATH=<profiles/name/config.yaml>
DEER_FLOW_EXTENSIONS_CONFIG_PATH=<profiles/name/extensions_config.json>
DEER_FLOW_HOME=<profiles/name/.deer-flow>
```

It then executes unchanged root `scripts/serve.sh`. This is DeerFlow's ordinary
path-selection contract, not a private launcher protocol. The root launcher
remains owner of dependency checks, service start/stop, ports, logs, and config
upgrade. Profile development launch passes only the upstream's existing
`--skip-install` flag after explicit setup; root `make` targets otherwise retain
their upstream behavior.

Root `.env` is the source for `$VARNAME` secrets. Before profile launch, the
resolver accepts only dotenv input made of comments, blank lines, and one direct
literal `NAME=value` assignment per line (an optional `export ` prefix is
allowed). The value may be an unquoted shell-safe literal or a single-quoted
literal; it cannot contain substitution/expansion syntax such as `$`, backticks,
`$()`, control operators, or command separators. It rejects shell commands,
control operators, and indirect assignment before the launcher can source the
file, then parses only the direct key names: if it defines
`DEER_FLOW_CONFIG_PATH`, `DEER_FLOW_EXTENSIONS_CONFIG_PATH`, `DEER_FLOW_HOME`,
`DEER_FLOW_PROJECT_ROOT`, or `DEER_FLOW_SKILLS_PATH`, it fails with a safe setup outcome telling the
operator to keep configuration and runtime-root selection in the profile command.
It names only the conflicting key and tells the beginner to retain normal API
keys and other secrets in `.env`; it never prints or modifies `.env`. This makes
the root launcher's later dotenv load unambiguous without a hook, sourcing trick,
or root edit. This deliberately validates the source-safe subset that the
unchanged launcher will later load; profile mode deliberately does not support
shell-computed or environment-expanded secret values in root `.env`.

Profiles do not copy the repository `skills/` source tree: with no explicit
`skills.path`, all local profiles use the shared project-root skills through
`DEER_FLOW_PROJECT_ROOT`. The launch environment removes inherited
`DEER_FLOW_SKILLS_PATH` so it cannot silently override that default. A scenario
that intentionally needs a different skills root declares `skills.path` in its
own profile config; that explicit path is configuration, not profile-managed
writable state, and is not validated or copied by this change.

### Isolation and observability

Validation requires complete regular non-symlinked profile files and no active
legacy checkpointer. It accepts either SQLite with an exact absolute
`profiles/<name>/.deer-flow/data` directory, or a process-local memory backend
with no database-persistence claim. Profile home and SQLite data are therefore a
single contained unit when SQLite is selected; different profiles must not
overlap. Postgres, relative, external, and other-profile SQLite paths fail
closed. Output contains only label, readiness, one of isolated local SQLite or
ephemeral memory database state, and restart-required facts.

Profile selection starts a new process. Database, checkpointer, sandbox,
logging, and other startup-only edits require restart. It creates no graph,
lifecycle, checkpoint, ledger, sandbox-content, run-session, Agent, skill, MCP,
or ACP authority.

The profiles isolate configuration plus runtime data resolved through the
selected `DEER_FLOW_HOME` and profile SQLite directory. They do not move every
upstream-launcher filesystem side effect: the unchanged launcher still owns its
fixed ports, root `logs/`, and compatibility directories it creates under
`backend/`. Starting a profile follows that launcher's normal stop-then-start
behavior and does not create a concurrent local stack. Per-run logs, traces,
and inspectable run bundles are owned by the later run-bundle/session contract,
not invented here.

This is not a sandbox or mount isolation contract. A selected config can choose
a sandbox provider, and that provider can have its own external paths or Docker
mount behavior. The profile resolver neither discovers nor rewrites those paths;
local default behavior that happens to use `DEER_FLOW_HOME` is not generalized
into a guarantee. Docker and arbitrary provider storage need their own
deployment contract.

## Alternatives Rejected

- Editing upstream root files: harms future upstream sync.
- `BASH_ENV`/source interception: replaces a documented configuration mechanism
  with fragile shell behavior coupled to an upstream implementation detail.
- Copying the launcher: duplicates service behavior and introduces drift.
- Profile overlays, Docker profiles, production/daemon profile modes, and
  Postgres: separate contracts.

## Evidence

Tests prove standard DeerFlow environment construction, project-owned containment,
redaction, dotenv selection-key conflict refusal, explicit setup and locked
no-sync ordinary commands, invalid preflight with no launcher execution, and
empty upstream-root diffs. No live model, browser, Docker, database server, or
Docker-mount acceptance is needed.
