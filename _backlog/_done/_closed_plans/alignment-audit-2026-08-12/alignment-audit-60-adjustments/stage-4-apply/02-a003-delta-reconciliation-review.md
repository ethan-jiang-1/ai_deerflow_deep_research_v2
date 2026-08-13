# Stage 4 Apply - A-003 Delta Reconciliation Review

> Change: `reconcile-evaluation-rubric-authority`
> Date: 2026-08-13
> Status: **REVIEWED - READY FOR NORMAL OPEN SPEC SYNC**

## Reviewed Authority

The selected Option A record, Stage 3 conflict evidence, active CES/EVH/HITL1 deltas,
and their three owning main specifications were re-read together. The active deltas
remain the sole pending owner of this A-003 requirement change.

| Owner | Existing incompatible wording | Pending reconciled behavior | Review result |
| --- | --- | --- | --- |
| CES | A Case-linked Rubric was categorically not an execution input. | Deterministic admission may compare Rubric identity/version and unique criterion IDs; content and cognitive result remain review-only; Runner reports only `completed`/`failed`. | Complete. |
| EVH Wave0/1/2 | Each corpus required generic rubric criteria/data, leaving the execution role ambiguous. | Each names `review_criteria` as unique criterion-ID Case-control-integrity metadata and prohibits content or quality disposition from execution/model input. | Complete and parallel. |
| HITL1 | Its cognitive-program corpus required generic rubric criteria but was outside the EVH owner. | The same criterion-ID metadata and no-quality-input boundary appears in `hitl1-node`, its actual owner. | Complete and parallel. |

No active planning artifact needed correction. The pending delta does not elevate the
loader's `schema_version` format check to required behavior, does not authorize test
or runtime changes, and does not pull `CONTEXT.md` or ADR wording into Stage 4.

## Sync Scope

The next operation syncs exactly the three delta paths returned by
`openspec status --change reconcile-evaluation-rubric-authority --json`:

1. `specs/cognitive-evaluation-suite/spec.md`
2. `specs/evaluation-hardening/spec.md`
3. `specs/hitl1-node/spec.md`

The merge changes only the named existing requirement blocks and adds their new
scenarios. All other requirements, main-spec Purpose sections, implementation files,
tests, terminology surfaces, archives, configuration, and DeerFlow remain out of
scope.
