# A-002 Apply Admission, Baseline, And Control Review

> Change: `establish-gitlink-boundary-detector`
> Apply authorization: user instruction `APPLY`, 2026-08-13
> Status: **APPLY AUTHORIZED - IN PROGRESS - ARCHIVE/COMMIT NOT AUTHORIZED**

## Authorization And Boundary

The user's explicit `APPLY` instruction authorizes execution of this active change's
checked implementation sequence: the registry/checker/test/evidence/configuration
updates named by the change, normal specification synchronization, verification, and
this A-002 evidence record. It does not authorize archive or commit.

The authorized implementation surface is limited to the active change artifacts,
`openspec/governance/` metadata-only governance surfaces, `openspec/config.yaml`, the
smallest requirement/evidence registrations, focused temporary-Git contract fixtures,
the live architecture contract, the A-002 todo/index, and this progressive record.
It does not authorize Deep Research runtime behavior, public APIs, or changes outside
the named governance/evidence seam.

`deerflow/` remains an upstream gitlink. This work may read its Git metadata only
through the fixed commands defined by the change. It must not open, copy, search,
walk, parse, modify, reset, clean, checkout, initialize, or otherwise inspect
DeerFlow source. The temporary fixtures below are independently created empty Git
repositories, never a copy of the real checkout.

## Fresh Baseline

Captured before A-002 target edits on 2026-08-13:

| Observation | Result | Evidence limit |
| --- | --- | --- |
| Root `HEAD` | `499ae343bb206457dbec16d5a6d4c32028815c40` | Starting commit only. |
| Active OpenSpec changes | `establish-gitlink-boundary-detector` only; `0/21` tasks complete | The active change is pending authority, not applied authority. |
| Root worktree | Modified progressive plan and A-002 todo/index; the active A-002 planning artifacts are untracked | Expected pre-apply planning/ledger material; preserved rather than reset. |
| Root index entry | `160000 66b9e7f21212490cf92fafac137542b9deb06615 0\tdeerflow` | Git metadata only. |
| Nested revision | `git submodule status -- deerflow` reports `66b9e7f21212490cf92fafac137542b9deb06615` | Observed revision only. |
| Nested porcelain | `git -C deerflow status --porcelain=v1 --untracked-files=all` has no output | Cleanliness observation only. |
| Submodule-aware diff | `git diff --submodule=short -- deerflow` has no output | No pointer diff before A-002; no future write barrier is inferred. |

The baseline is admissible: the gitlink has one stage-zero pointer matching the nested
revision, the nested worktree is clean, and no unrelated active OpenSpec change
overlaps this governance boundary. Any later unexpected pointer, dirty nested state,
or overlapping active change is a stop condition, not something this work may repair.

## Apply Review

The apply agent re-read the proposal and its Control Placement Review, `control-placement`,
`control-and-recovery`, the design, the `PRS-018` delta, current main
`project-structure` spec/registry/checker, and focused architecture/import fixtures.

| Review question | Result | Control or task consequence |
| --- | --- | --- |
| Where does the new fact belong? | The full `check_project_architecture.py` path already owns exact registry checks. | Add one independent metadata-only check there; do not place it in Harness runtime, closeout tooling, or source-import traversal. |
| Does existing import checking inspect DeerFlow? | No. `_validate_upstream_does_not_import_downstream` scans only manifest roots `backend` and `frontend`. | Preserve that limited scan. The detector gets no recursive scan or source reader. |
| Is an automatic mutation/recovery legal? | No. A mismatch must fail closed. | No `submodule update`, `checkout`, `reset`, `clean`, staging, or fallback state is permitted. |
| Can a staged intentional bump pass before a parent commit? | Yes, when the stage-zero gitlink pointer and declared lock match, nested `HEAD` matches, and porcelain is clean. | Temporary fixture must prove the matching staged state and paired mismatch. The checker verifies consistency, not bump approval or compatibility. |
| Does current authoring context remain coherent? | Not yet. `openspec/config.yaml` says archive-time observations are “not automatic detection or protection”; after A-002 this must be narrowed to supplementary manual scope/diff evidence. | Extend ordinary task 3.4 and the active proposal/design before production edits; retain the explicit metadata-only and non-compatibility limit. |

No other actionable collision, missing rejection class, or DeerFlow-source-read risk was
found during the admission review. During red-test implementation, a narrower source-read
risk was found: `_validate_single_source_root` uses a root-level `os.walk`, so it would
enumerate `deerflow/` unless explicitly excluded. Task 2.5 now excludes only the declared
gitlink from that existing walk; it changes no downstream scan or upstream source behavior.
The additional `config.yaml` correction is a normal unchecked implementation task, not a
claim that the detector has already been delivered.

## Adjustment Record: A-002

| Field | Apply-time record |
| --- | --- |
| Before | Root gitlink and nested worktree state are recorded as manual archive evidence. A later pointer move or dirty nested checkout can evade deterministic architecture validation. |
| Intended after | Full architecture governance parses one exact path/SHA lock and fails closed on missing, moved, non-gitlink, mismatched, uninspectable, or dirty metadata state, without opening upstream source. |
| Risk | A legitimate future upstream bump or locally generated upstream file is rejected until its state is deliberately reconciled. |
| Possible side effect | Existing minimal manifests may become invalid; checkout verification now depends on local Git metadata availability; manual guidance can become misleading if it still denies the detector. |
| Control / stop condition | Use hermetic empty Git fixtures; keep `--imports-only` Git-free; update every direct manifest fixture; restrict command vectors to the defined read-only metadata queries; stop rather than repair any real gitlink anomaly. |
| Verification boundary | Focused red-to-green fixtures, architecture/requirement/Charter/OpenSpec gates, and the configured offline Harness verification establish metadata integrity only. They do not establish DeerFlow source conformance, runtime behavior, remote state, release status, or compatibility. |
| Current / required gap owner | This active A-002 change owns only the detector described above. A future upstream revision needs a separate reviewed owning change; any runtime compatibility concern stays with its actual Harness contract. |
