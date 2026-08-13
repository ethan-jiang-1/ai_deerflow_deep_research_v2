# Stage 4 Apply - A-003 Main-Spec Sync

> Change: `reconcile-evaluation-rubric-authority`
> Date: 2026-08-13
> Task: 3.3
> Status: **SYNCED - REQUIRED/CURRENT CONFORMANCE REVIEW REMAINS PENDING**

## Normal OpenSpec Sync

The normal agent-driven OpenSpec sync workflow was used with the three delta paths
reported by `openspec status --change reconcile-evaluation-rubric-authority --json`:

| Owning capability | Delta path | Main-spec path | Sync result |
| --- | --- | --- | --- |
| Cognitive Evaluation Suite | `openspec/changes/reconcile-evaluation-rubric-authority/specs/cognitive-evaluation-suite/spec.md` | `openspec/specs/cognitive-evaluation-suite/spec.md` | Updated the two existing requirements: the five-part Rubric boundary, deterministic identity/unique-ID admission, review-only content, and `completed`/`failed` Runner boundary. |
| Evaluation Hardening | `openspec/changes/reconcile-evaluation-rubric-authority/specs/evaluation-hardening/spec.md` | `openspec/specs/evaluation-hardening/spec.md` | Updated existing Wave0, Wave1, and Wave2 requirements to describe `review_criteria` as unique criterion-ID control metadata and prohibit quality-input use. |
| HITL1 node | `openspec/changes/reconcile-evaluation-rubric-authority/specs/hitl1-node/spec.md` | `openspec/specs/hitl1-node/spec.md` | Updated the existing HITL1 cognitive-program requirement with the same criterion-ID metadata and no-quality-input boundary. |

The current `openspec instructions specs --change reconcile-evaluation-rubric-authority
--json` snapshot supplied the two applicable rules: retain mechanically verifiable
downstream behavior without redefining DeerFlow internals, and retain zero-API
deterministic evidence at the lowest responsible seam. The merged requirements retain
the existing capability requirement IDs and no delta-operation heading was copied into
a main spec.

## Scope And Validation

- `openspec validate --specs`: **49 passed, 0 failed** after sync.
- `git diff --check`: passed at the sync point.
- The Stage 4 main-spec diff names only the three tabled main specs. It contains no
  `deep_research_harness/` code/test edit and no `deerflow` gitlink/worktree change.

These checks establish structural validity, whitespace validity, and bounded changed
path scope. They do not prove runtime conformance or every present/future model handoff.
Task 3.4 separately records the required/current conformance answer.
