# DONE-002: A-002 gitlink boundary detector

> 状态: 已完成并归档 | 优先级: 高 | 完成: 2026-08-13
> 上游: Stage 7 final alignment audit | 归档 change: `2026-08-13-establish-gitlink-boundary-detector`

## Why

The current archive protocol records `deerflow/` gitlink and nested-worktree state
manually. `openspec/config.yaml` explicitly says that this is evidence, not automatic
protection. A later change can therefore alter the pointer or nested worktree without a
dedicated deterministic failure.

## 现状对齐

`deerflow/` is an upstream submodule at the repository root. Downstream work must not
modify or source-browse it. The expected detector's job is only to reject an unapproved
gitlink pointer/worktree change according to a declared boundary; it must not inspect
or alter DeerFlow source.

## Delivered

The independently reviewed change is archived at
[`2026-08-13-establish-gitlink-boundary-detector`](../../../openspec/changes/archive/2026-08-13-establish-gitlink-boundary-detector/).
It adds `PRS-018`: full architecture governance fails closed unless the declared
`deerflow` path/full-SHA lock matches the sole root mode-`160000` index entry, nested
`HEAD`, and empty nested porcelain status including untracked paths. The exact
metadata-only check is covered by temporary parent/nested Git fixtures and the live
architecture contract.

The detector does not read, walk, copy, parse, import, modify, reset, checkout, clean,
initialize, or update DeerFlow source. It does not authorize an upstream bump or prove
source, runtime, remote, release, or compatibility status. A future bump remains a
separate reviewed change that updates the declared lock and pointer together.

## Archive Evidence

The archive closeout, preflight, and observed-side-effect record is
[A-002 archive closeout](../_closed_plans/alignment-audit-2026-08-12/alignment-audit-60-adjustments/a002-gitlink-detector-apply/02-a002-archive-closeout-review.md).
The change had no observed adverse side effects within its deterministic verification
boundary. At post-archive baseline there are no active OpenSpec changes; the root index
and nested `HEAD` remain `66b9e7f21212490cf92fafac137542b9deb06615`, nested porcelain
is empty, and there is no gitlink pointer diff.
