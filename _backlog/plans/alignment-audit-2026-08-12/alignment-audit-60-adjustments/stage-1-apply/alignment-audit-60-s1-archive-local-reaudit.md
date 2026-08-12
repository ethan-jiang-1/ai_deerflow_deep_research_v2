# Stage 1 Archive Local Re-Audit

> Change: `retire-v1-topology-residue`
> Archive: `openspec/changes/archive/2026-08-13-retire-v1-topology-residue/`
> Status: **COMPLETE - STAGE 2 NOT AUTHORIZED**
> Date: 2026-08-13

## Scope

This is the required post-archive local re-audit for A-001 and A-002. It reviews only
the Stage 1 topology authority, archive state, and evidence boundaries. It does not
start Stage 2, read DeerFlow source, or create an automatic detector.

## A-001 - Topology Language

- **Before:** `openspec/config.yaml`, `deep_research_harness/AGENTS.md`, and the Agent
  Charter called root `backend/` and `frontend/` the upstream DeerFlow mirrors. README
  named the obsolete sibling `../backend/packages/harness`.
- **After:** The current authorities consistently name `deep_research_harness/` as the
  downstream product and `deerflow/` as the upstream gitlink that ordinary work does
  not modify or source-browse. README names
  `../deerflow/backend/packages/harness`, consistent with unchanged `pyproject.toml`
  and `uv.lock` dependency sources.
- **Re-audit evidence:** A non-archive search found no remaining root-mirror phrase or
  obsolete README path. Remaining `deerflow/backend/...` occurrences are the valid
  editable dependency source or test fixture paths. Retained `backend`/`frontend`
  terms remain classified in the C-001 record as domain, host-interface, or
  legacy-root negative guards.
- **Conclusion:** A-001 cleanup is complete within Stage 1 scope. This does not assert
  that every historic archive uses V2 terminology.

## A-002 - Gitlink Enforcement Gap

- **Before:** Authoring/closeout prose implied that keeping root `backend/` and
  `frontend/` clean protected the active upstream boundary.
- **After:** `openspec/config.yaml` requires explicit manual root status, gitlink index,
  submodule, nested-worktree, and submodule-aware diff evidence. It expressly says that
  these commands are not automatic detection or protection.
- **Re-audit evidence:** At closeout, `deerflow` remains index mode `160000` at
  `66b9e7f21212490cf92fafac137542b9deb06615`; `git submodule status` agrees and nested
  porcelain status is empty. No `deerflow/` diff appears.
- **Conclusion:** A-002 remains `DEFERRED-CODE-CHANGE`. The current manual evidence
  proves only the observed pointer/worktree and scoped diff at review time; it is not a
  gitlink detector and does not provide future automatic protection.

## Archive And Boundary Evidence

- `openspec list --json` reports no active changes after archive.
- The archived change retains `.openspec.yaml`, proposal, design, and fully checked
  tasks; `skip_specs: true` meant there were no delta specs to sync.
- `openspec doctor --json`, Charter governance, and `git diff --check` passed after
  archive.
- No Stage 1 diff exists under `deep_research_harness/src/`, `scripts/`,
  `openspec/governance/`, `openspec/guardrails/`, `openspec/specs/`, or `deerflow/`.
  V-001 remains the single authorized test-file format-only exception.

## Next Authorization Boundary

Stage 1 is complete. Stage 2 (`retire-stale-context-concepts`) remains blocked until a
new, explicit authorization starts its planning work. This record does not authorize
any Stage 2 file, code change, detector work, or modification of archived material.
