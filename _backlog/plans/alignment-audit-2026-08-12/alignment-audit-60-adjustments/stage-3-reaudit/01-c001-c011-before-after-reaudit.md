# Stage 3 C-001 Through C-011 Re-Audit

> Date: 2026-08-13
> Method: current non-archive authority only; no target edit

## Classification Rule

An item is resolved only when the exact false or stale current claim has disappeared
from its owning current authority. Historical ADR prose and archive material are not
treated as current authority. A retained occurrence is recorded by semantic role, not
by token count.

| C item | Before / intended correction | Current re-audit result | Disposition |
| --- | --- | --- | --- |
| C-001 | Root `backend/` and `frontend/` were described as the DeerFlow upstream mirror. | `openspec/config.yaml`, `deep_research_harness/AGENTS.md`, and the Charter identify `deerflow/` as the upstream gitlink. Remaining `backend`/`frontend` references are dependency paths, host interfaces, or explicit negative guards. | Resolved within the approved Stage 1 scope. |
| C-002 | Closeout prose treated nonexistent root directories as the protected upstream boundary. | `openspec/config.yaml` requires manual gitlink index, submodule, nested-worktree, and submodule-aware diff evidence; it expressly says this is not automatic protection. No automatic gitlink detector was found. | Corrected explanation; A-002 remains `DEFERRED-CODE-CHANGE`. |
| C-003 | README used the obsolete sibling editable-harness path. | The current README names `../deerflow/backend/packages/harness`, matching dependency metadata. | Resolved. |
| C-004 | Evaluation Run Workspace was confused with the host workspace or Run Bundle. | The glossary now states that Runner-owned `workspace/` and sibling `bundle/` directories are created under an execution root. No lifecycle or storage behavior was inferred. | Resolved. |
| C-005.a | Completed evaluation work was written as future work. | The current glossary retains only the present control/run-data boundary and current owner routes. | Resolved. |
| C-005.b | Current glossary authority cited an archived change. | The current route is `local-context`; no archived change slug is used as current authority. | Resolved. |
| C-006 | Broad relocation of all design material from CONTEXT was proposed without a verified mismatch. | No target edit was made, by design. The retained evaluation design headings have not been reclassified as false current behavior by this audit. | Withdrawn, not an open mismatch. |
| C-007 | Current glossary and Charter said a change must choose one policy. | `openspec/CONTEXT.md` and `openspec/agent-charter/README.md` now say one primary owner plus every actually triggered canonical policy. A residual in the policy-library README and Charter main spec is recorded separately in the ledger. | Partially resolved; A-008 is reopened for the residual. |
| C-008 | Every LLM-bearing node was claimed to have a Suite smoke scenario. | Current glossary uses registered current coverage rather than an all-node assertion. | Resolved. |
| C-009 | `limited` and `inconclusive` were said to require a separate readable report. | Current glossary retains the structured Review Record and non-pass semantics without creating an unowned report requirement. | Resolved. |
| C-010.a | A Bundle artifact was conflated with a public Primary User export capability. | `final/report.md` is current as a Bundle artifact; the glossary explicitly says that it does not establish public reopen/copy/export. | Resolved. |
| C-010.b | Support Handoff was described as an existing capability. | It is marked `planned` only, with no producer, schema, reader, or post-loss retention promise. | Resolved; A-004 remains separately unresolved. |
| C-010.c | Dedicated Primary-User TUI and Local-First route were described as current delivery. | Both are `dormant`; the current Dedicated Agent/reflected-tool route remains named. | Resolved. |
| C-011 | Five ADRs presented historical product routes as current without status context. | ADRs 0002, 0003, 0006, 0008, and 0010 retain their historical text and append dated applicability notes. The notes do not resolve A-003 or A-004. | Resolved within the historical-status scope. |

## Retained Topology Terms

The only ambiguous current topology occurrence found is
`openspec/specs/deployment-configuration/spec.md:434`, which says a downstream launch
change must not require changes under upstream `backend/` or `frontend/`. It does not
assert that these are root directories or the upstream mirror, and can be read as the
actual components under `deerflow/`. It is therefore not evidence that A-001 reopened.
It is registered as a low-risk wording candidate in the reduced ledger so a later owner
can decide whether an explicit `deerflow/backend` and `deerflow/frontend` path would be
clearer.

## Scope Result

The Stage 1 and Stage 2 safe cleanup has removed its allowlisted stale claims. The
remaining work is not a reason to modify the completed archive or to expand this
read-only stage. In particular, C-006 remains withdrawn and the A-003/A-004 quarantine
remains intact.
