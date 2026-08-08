## 1. Reconfirm Migration Inputs

- [x] 1.1 Re-run the tracked-path, active-spec, CI, Docker, and ignored-state inventory at the implementation commit; classify each residual `agent/` match as generic terminology, historical evidence, external/operator configuration, or a stale active consumer.
- [x] 1.2 Inspect GitHub branch protection, badges, workflow consumers, local hooks, shell aliases, IDE tasks, and local compose wrappers for old absolute/status identities; record external findings without committing user-specific paths or secrets.
- [x] 1.3 Extend the existing PRS-001, EVH-005, and RUS-001 deterministic evidence mappings for canonical-root, workflow-path, and local-data-migration coverage before implementation evidence is collected.

## 2. Add Focused Failing Evidence

- [x] 2.1 Add structural-governance and charter-checker fixtures proving `deerflow_research/` is required and a tracked `agent/` compatibility root or stale generated locator is rejected.
- [x] 2.2 Add focused contract tests for renamed scripts, Make commands, active documentation/spec references, CI trigger/cwd/artifact paths, release-attestation scopes, and production annotation scanning while preserving workflow status identity.
- [x] 2.3 Add Docker contract coverage that renders the base-first Compose configuration and asserts the host mount, `/app/deerflow_research/src`, and Gateway-only `PYTHONPATH` together.
- [x] 2.4 Add retained-data and diagnostic-journal migration tests for explicit confirmation, quiesced-source preflight, absent legacy roots, byte-equivalent idempotency, conflicts, symlink rejection, excluded reports/secrets/environments, partial two-root outcomes, and no-delete rollback behavior.

## 3. Migrate The Tracked Module Contract

- [x] 3.1 Update `openspec/governance/project-structure.toml`, architecture/charter checkers, fixtures, current structural specs, and the checker-rendered module guide to define `deerflow_research/` as the sole downstream root.
- [x] 3.2 Use `git mv agent deerflow_research` in the same atomic tracked change; preserve `deerflow-deep-research`, `deerflow_deep_research`, and `deep_research` identities, and do not create an alias, symlink, or second source root.
- [x] 3.3 Update all repository-owned active path consumers: root/module guides, README and current docs, Make/scripts, profiles and ignore rules, active OpenSpec specs/config/governance, tests/fixtures, and generated evidence via their owning generators. Preserve archives unless an old reference remains an active navigator, command, or validator.
- [x] 3.4 Update CI workflow path filters, working directories, artifacts, release attestation fixtures, and root-relative protected-path checks while retaining file names, display names, job/status identifiers, and concurrency identity unless the external audit explicitly authorizes another change.
- [x] 3.5 Update local/Docker preparation and Compose contracts to mount `deerflow_research/src` at `/app/deerflow_research/src` and export only that target as the Gateway `PYTHONPATH`.

## 4. Implement Retained-State Migration

- [x] 4.1 Implement a project-owned, operator-confirmed migration that preflights quiesced old retained-state and diagnostic-journal roots, copies only their contained regular files through staging, and reports bounded per-root outcomes.
- [x] 4.2 Refuse conflicting or unsafe roots without overwrite or deletion; recognize only byte-equivalent destinations as already migrated, report partial two-root publication honestly, and keep retries deterministic.
- [x] 4.3 Update default session/diagnostic root resolution and operator documentation for the new roots, secure `.env` copy/recreation, `.venv` rebuild, post-copy inspection, and tracked-only rollback.

## 5. Verify And Gate Merge

- [x] 5.1 Run focused structural, path-contract, Docker-rendering, and retained-data migration tests; render generated structural evidence through its owning checker rather than editing it manually.
- [x] 5.2 Run `python3 openspec/governance/check_project_architecture.py`, `uv lock --check`, `docker compose config` for the relevant override, and `cd deerflow_research && UV_OFFLINE=1 make verify`.
- [x] 5.3 Run `openspec validate rename-deep-research-module-root --strict`, `git diff HEAD --check`, and `git status --porcelain=v1 --untracked-files=all`; confirm `backend/` and `frontend/` remain clean.
- [x] 5.4 Perform and record a strict post-move residual `agent/` allowlist review; every remaining active path reference must be fixed, while generic terminology, deliberately historical archives, and external/operator items must have an explicit rationale.
