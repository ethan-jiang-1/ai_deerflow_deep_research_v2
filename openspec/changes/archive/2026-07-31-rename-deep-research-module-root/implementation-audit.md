# Implementation Audit

Audit date: 2026-07-31

## Repository Consumers

- The tracked module tree contains 516 files.
- `project-structure.toml` contains 159 canonical `deerflow_research/` entries.
- The non-archive, non-backlog exact-path inventory contains 94 files. Each is to be
  classified before editing; generic DeerFlow and `agents/` references are excluded.
- The three Deep Research workflows use the old root for triggers, working directories,
  or artifacts. Their workflow/status identities are not renamed.

## External And Local Consumers

- The origin repository default branch is `master`; its branch-protection endpoint
  reports that the branch is not protected. No README workflow badge was found.
- A local Claude hook contains an absolute old module-root reference. It is ignored
  operator configuration and is not changed by this repository migration.
- The old module root has ignored `.env`, `.venv`, retained-run, and report
  directories. Their contents were not read. The migration command handles only the
  approved retained-state and diagnostic-journal roots; `.env` and `.venv` remain
  operator actions.

## Post-Move Residual Allowlist

- `agent/` in the active change proposal, design, and delta specs is deliberate
  legacy-source documentation. It defines the former root or migration input, never
  an active command or canonical output.
- `agent/` in `deerflow_research/docs/local-operations.md` and
  `test_legacy_state_migration.py` is the exact legacy source accepted by the
  migration command. The implementation reads no other legacy-root material.
- Negative workflow and structural assertions retain old paths only to prove stale
  consumers and compatibility roots fail.
- `backend/`, `frontend/`, `config.example.yaml`, and historical documentation use
  generic DeerFlow agent terminology or their own `.agent` skill paths. They are not
  downstream module-root consumers and remain outside this change boundary.
- Archived OpenSpec changes and `_backlog/` preserve historical checkout evidence.
- No active repository-owned command, guide, current main spec, registry, CI path,
  Docker mount, production scan, source root, test root, or release artifact points
  to `agent/`.
