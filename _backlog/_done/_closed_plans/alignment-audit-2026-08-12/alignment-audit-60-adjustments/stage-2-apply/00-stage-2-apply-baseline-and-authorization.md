# Stage 2 Apply Baseline And Authorization

> Change: `retire-stale-context-concepts`
> Apply date: 2026-08-13
> Status: **APPLY AUTHORIZED - IN PROGRESS**

## Authorization

The user explicitly authorized `apply` for this active Stage 2 OpenSpec change on
2026-08-13. The authorization covers only the allowlisted documentation targets in the
approved proposal and the required Stage 2 evidence records. It does not authorize an
archive, code, tests, main specs, registries, governance executables,
`openspec/config.yaml`, archive contents, or any `deerflow/` content.

## Fresh Baseline

- HEAD: `03fefd424fec3f622e7d5844d504d02fb37633ab`
  (`docs: retire v1 topology residue`).
- Active OpenSpec changes: only `retire-stale-context-concepts`, with 0 of 21 tasks
  complete before this record.
- Root worktree already contained:
  - modified `_backlog/plans/alignment-audit-2026-08-12/alignment-audit-60-progressive-execution-plan.md`;
  - untracked `stage-2-planning/` evidence; and
  - untracked `openspec/changes/retire-stale-context-concepts/` planning artifacts.
  These are pre-existing Stage 2 work and are not overwritten by this apply.
- `git ls-files --stage deerflow`: mode `160000`, pointer
  `66b9e7f21212490cf92fafac137542b9deb06615`.
- `git submodule status -- deerflow`: the same
  `66b9e7f21212490cf92fafac137542b9deb06615` pointer.
- `git -C deerflow status --porcelain=v1 --untracked-files=all`: empty.

## Proof Boundary

This baseline records Git metadata and the nested worktree status only. It neither
source-browses DeerFlow nor provides automatic protection for the gitlink. The apply
uses only the approved documentation allowlist and stops if any frozen path is needed.
