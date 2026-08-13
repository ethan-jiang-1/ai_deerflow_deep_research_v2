# Stage 6 Apply Admission Baseline

> Change: `normalize-post-decision-terminology-status`
> Date: 2026-08-13
> Status: **APPLY AUTHORIZED - DOCS-ONLY - ARCHIVE/COMMIT NOT AUTHORIZED**

## Authorization And Boundary

The user's instruction `我们继续 APPLY` explicitly authorizes application of
`normalize-post-decision-terminology-status`. It authorizes only the planned,
documentation-only D-001 and D-002 terminology/status work, its task/evidence records,
and the progressive ledger. It does not authorize archive, commit, main or delta specs,
application code, tests, typed contracts, configuration, governance executables,
archives, `A-004-T01`, or DeerFlow source inspection/edit.

The target-authority allowlist remains closed:

1. Exact D-001/D-002 glossary occurrences and the short Rubric explanatory section in
   `deep_research_harness/CONTEXT.md`.
2. Only the existing current-status/applicability postscript in
   `deep_research_harness/docs/adr/0006-layered-support-disclosure.md`.
3. Only a new dated current-status/applicability postscript in
   `deep_research_harness/docs/adr/0025-rubrics-are-case-specific-review-authorities.md`.

## Fresh Apply Baseline

| Check | Observation | Evidence limit |
| --- | --- | --- |
| HEAD | `b54eaea890478b93d1d3dd290a06cd0918a8ea66` (`docs(charter): add one-page concept map routing terms to first edit`) | Identifies the apply baseline only. |
| Worktree | `git status --porcelain=v1 --untracked-files=all` had no output. | A clean observation is not a future write barrier. |
| Active change | `normalize-post-decision-terminology-status` is the only active change; CLI reports `0/20` tasks before this apply record. | Planning status does not itself prove application correctness. |
| Target documents | Focused `git diff` for `CONTEXT.md`, ADR 0006, and ADR 0025 had no output. | Exact target text was captured separately in D-001/D-002 records. |
| DeerFlow gitlink index | `160000 66b9e7f21212490cf92fafac137542b9deb06615 0 deerflow`. | Git metadata only; DeerFlow source was not opened. |
| Submodule status | `66b9e7f21212490cf92fafac137542b9deb06615 deerflow (heads/main-282-g66b9e7f2)`. | Observed reference state, not automatic protection. |
| Nested DeerFlow worktree / submodule diff | Both commands had no output. | Does not establish framework behavior. |

## Concept-Map Re-baseline

The Stage 6 planning snapshot saw concept-map work in the shared worktree. At apply
admission, it is no longer uncommitted or overlapping: commit `b54eaea` contains the
concept map and its links in `deep_research_harness/AGENTS.md`,
`openspec/agent-charter/README.md`, and `openspec/agent-charter/concepts.md`. Its
three-file diff contains no Stage 6 target document. `CONTEXT.md` has no outstanding
concept-map hunk or any other worktree diff. Therefore the fresh baseline separates
that completed external work from this Stage's exact glossary occurrences.

If new user work appears in a target document before a later edit, the agent must stop
and re-baseline rather than overwrite, stage, revert, or absorb it.

## Apply Review Result

The apply agent re-read the proposal/design/tasks, the six owning main-spec blocks, the
Stage 4/5 post-archive dispositions, the target before text, and the A-004-T01 deferral.
No new behavioral finding requires a new product decision. The following bookkeeping
finding is non-behavioral and is separately tracked before target wording changes:

| Added task | Finding | Required disposition |
| --- | --- | --- |
| 1.4a | Stage 6 planning validation says `tasks.md` has 19 unchecked tasks, while the actual planning-time task file and OpenSpec CLI have 20. | Correct the historical planning count to 20; the added apply bookkeeping task increases the live task count to 21, without changing scope, task semantics, or the target-authority allowlist. |

`DEFERRED-TOOLING-CHANGE A-004-T01` remains outside Stage 6: its two RER scenario
titles stay unchanged even though their bodies already require `bundle_journal` or
`unavailable`.
