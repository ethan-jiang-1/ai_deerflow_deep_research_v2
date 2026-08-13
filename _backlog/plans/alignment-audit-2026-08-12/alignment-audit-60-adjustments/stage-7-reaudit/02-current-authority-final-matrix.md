# Stage 7 Current-Authority Final Matrix

> Date: 2026-08-13
> Baseline: `198cf290146b4308e7a8da432d28abd46aca51d1`
> Scope: current non-archive authority, implementation evidence, and deterministic gates
> Initial status: **NO NEW UNREGISTERED FINDING**
> Final closeout: N-002 was resolved by the archived
> `2026-08-13-reconcile-policy-routing-cardinality` change; see
> [post-archive closeout](03-n002-post-archive-closeout.md).

## Classification Rule

An original finding is closed only when its false or mutually incompatible current
authority has been removed or reconciled. A deterministic green result proves only the
command's stated boundary. A deliberately deferred implementation/tooling gap remains
open even when its documentation has become accurate. Archived change artifacts preserve
history and are never used as a reason to reopen or rewrite current authority.

## A-001 Through A-009

| ID | Final current classification | Current evidence and owner | Remaining boundary / next action |
| --- | --- | --- | --- |
| A-001 | **Resolved** | `deep_research_harness/AGENTS.md`, `openspec/config.yaml`, and current topology guidance identify `deerflow/` as the upstream gitlink. Current `backend`/`frontend` occurrences are dependency paths or negative guards, not a claim that root directories mirror upstream. | Do not bulk-replace valid negative guards; revisit N-001 only when a deployment-spec change already owns its wording. |
| A-002 | **Resolved** | The archived `2026-08-13-establish-gitlink-boundary-detector` change added `PRS-018`: the architecture gate now fail-closes on declared lock, root index gitlink, nested `HEAD`, and nested porcelain disagreement without reading upstream source. | [A-002 closeout](../a002-gitlink-detector-apply/02-a002-archive-closeout-review.md); the completed todo is [DONE-002](../../../../_done/_done_todos/todo-a002-gitlink-boundary-detector.md). |
| A-003 | **Resolved, bounded current conformance** | CES, EVH, HITL1, glossary, and ADR 0025 agree: admission reads only Rubric identity/version and unique criterion IDs as non-model control-integrity metadata; content/judgment stays review-only; the Runner reports only `completed` or `failed`. Stage 4 performed a finite local conformance inspection. | Does not prove every live, future, or uninspected evaluation path. A future observed divergence needs a new code-and-test change. |
| A-004 | **Resolved, bounded current conformance** | RER, RUS, REJ, glossary, and ADR 0006 agree: supported retained diagnostic/Journal reader and participant presentation require an available selected Bundle; after loss they are unavailable; physical residual bytes are not asserted. Stage 5 found no prohibited local crossing. | `A-004-T01` is a misleading scenario-title tooling residue, not a reopened required-behavior conflict; its owner investigation places it in external OpenSpec tooling suspension. |
| A-005 | **Resolved within audited scope** | The factual Workspace/Bundle relation, completed-work tense, and stale archived-plan dependency were corrected. C-006 was withdrawn because it was not a verified mismatch. | No current remediation action. |
| A-006 | **Resolved within audited scope** | Over-broad all-node smoke and standalone readable-report claims were removed; only the A-003 boundary remains where it belongs. | No current remediation action. |
| A-007 | **Resolved within audited scope** | Final report remains a Bundle artifact, Support Handoff is `planned`, and the dedicated Primary User TUI route is `dormant`. Stage 6 adds no post-loss fallback. | A future Support Handoff needs independent retention/availability design. |
| A-008 | **Resolved post-audit** | The archived N-002 change aligned the policy-library index, authoring context, Harness Focus Gate, and DRC-001: every route-table trigger selects its canonical policy, while one primary causal owner remains and policy is guidance-only. | [N-002 closeout](03-n002-post-archive-closeout.md). |
| A-009 | **Open - `OPTIONAL-HARDENING`** | Requirement coverage validates alive IDs against `@impl` references. Current evidence policy deliberately centralizes richer proof only for selected policy/inventory requirements. | [A-009 candidate](../../../../todos/todo-a009-risk-based-semantic-traceability.md) is optional; it must not create a duplicate exhaustive test catalog. |

## Registered Deferred Work

| Item | Classification | Why it remains open | Owner / candidate |
| --- | --- | --- | --- |
| A-004-T01 | `DEFERRED-EXTERNAL-TOOLING` | Current RER scenario bodies are correct, but two legacy titles cannot be renamed under the installed OpenSpec CLI's shared strict-validation/archive guard. | [suspended scenario-rename validator](../../../../_done/_suspended_plans/todo-a004t01-openspec-scenario-rename-validator.md) and [owner research](../a004t01-scenario-rename-owner-research/a004t01-scenario-rename-owner-research.md) |
| A-009 | `OPTIONAL-HARDENING` | ID-level coverage is intentionally not assertion-semantic traceability. | [risk-based semantic traceability](../../../../todos/todo-a009-risk-based-semantic-traceability.md) |

No new product-behavior or runtime conformance finding was discovered. The initial
N-002 authority mismatch has since been resolved and archived; the other three items
remain accurately disclosed independent backlog work and must not be silently
implemented as part of a documentation cleanup.
