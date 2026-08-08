# Local Profiles

Local profiles keep normal, development, test, and demo configurations separate
without modifying DeerFlow's original root files.

From `deep_research_harness/`, prepare once and then create, check, and start a local scenario:

```bash
make profile-setup
make profile-init PROFILE=demo
make profile-check PROFILE=demo
make profile-dev PROFILE=demo
```

`profile-setup` runs the normal DeerFlow installation and prepares the local
profile command environment. Profile files and their DeerFlow home live together
under `profiles/<name>/` and are intentionally not committed.

Keep API keys and other literal secrets in the root `.env`. Do not put
`DEER_FLOW_CONFIG_PATH`, `DEER_FLOW_EXTENSIONS_CONFIG_PATH`, `DEER_FLOW_HOME`,
`DEER_FLOW_PROJECT_ROOT`, or `DEER_FLOW_SKILLS_PATH` there when using profiles.

Each profile begins as an independent copy of root `config.yaml` and optional
`extensions_config.json`. Its SQLite database is isolated under that profile's
`.deer-flow/data/`. A test or demo profile can instead set
`database.backend: memory`; its database/checkpoint state then disappears when
the process ends.

Profiles share the repository skills directory unless their own `config.yaml`
explicitly sets `skills.path`. Sandbox mounts, Docker behavior, ports, and
launcher logs are not isolated by local profiles: they remain in the upstream
root `logs/` area and compatibility directories such as `backend/.deer-flow/`.
Use the normal root `make stop` to stop local DeerFlow services; it is not tied
to a particular profile. Startup-only configuration changes require a restart.
