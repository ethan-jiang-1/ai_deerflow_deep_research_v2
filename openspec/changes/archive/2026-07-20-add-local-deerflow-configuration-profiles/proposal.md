## Why

Selecting only a DeerFlow `config.yaml` does not isolate extensions, writable
state, or SQLite data. Local normal, development, test, and demo work can
therefore contaminate one another.

This downstream repository also tracks DeerFlow upstream. Existing root files
belong to that upstream project and must remain byte-for-byte unchanged so a
future upstream sync stays simple.

## What Changes

- Add named local profiles under the project-owned top-level `profiles/`
  directory: paired configuration files plus isolated DeerFlow home and SQLite
  state, with explicit support for ephemeral in-memory database state in test or
  demo scenarios. Keep the small command resolver and its tests under `agent/`.
- Add `agent/Makefile` commands for list, initialization, validation, and
  launching, plus explicit one-time preparation of their locked environment:
  `make profile-setup`, `make profile-init PROFILE=demo`, `make profile-check
  PROFILE=demo`, and `make profile-dev PROFILE=demo`. Setup uses the standard
  upstream installation path once; profile launch skips installation.
- Seed a profile from the user's existing root DeerFlow configuration without
  changing any root file. Root `.env` remains the common secret source.
- Launch the unchanged upstream `scripts/serve.sh` through DeerFlow's supported
  `DEER_FLOW_CONFIG_PATH`, `DEER_FLOW_EXTENSIONS_CONFIG_PATH`, and
  `DEER_FLOW_HOME` environment variables, with `DEER_FLOW_PROJECT_ROOT` pinned
  to this checkout. Root `.env` remains the secret source and must not select
  an application configuration, runtime root, or alternate skills root.
- Keep normal output redacted and make restart requirements explicit.

## Non-Goals

- Modifying any pre-existing root DeerFlow file or directory, including root
  `Makefile`, `README*`, `.gitignore`, `scripts/`, `backend/`, `frontend/`,
  Docker, config examples, skills, or extensions.
- Docker mounts, Docker profile selection, production/Postgres profiles,
  profile production/daemon modes, configuration overlays, migration, and
  concurrent local stacks. Sandbox-provider or mount-path isolation is also out
  of scope: profiles select their configuration but do not validate arbitrary
  provider-owned external storage.
- Graph, lifecycle, checkpoint, ledger, sandbox-content, run-session, Agent,
  skill, MCP, or ACP changes.

## Capabilities

### New Capabilities

- `local-configuration-profiles`: project-owned local profile selection,
  initialization, isolation, launch adaptation, and observability.
  Requirements: `LCP-001` through `LCP-005`.

### Modified Capabilities

- `project-structure`: register local-profile tooling under `agent/` and the
  project-owned `profiles/` data directory.
  Requirement: `PRS-007`.

## Impact

Only `agent/`, `openspec/`, and the new project-owned `profiles/` directory
change. The resolver reads root configuration as an input and starts the
existing launcher as an external upstream interface; it does not patch, wrap on
disk, or change upstream-owned source. Deterministic tests cover the resolver
and command boundary without starting services, Docker, a database server,
browser, or live model.
