# Stage 7 Current-Authority Final Matrix

> Date: 2026-08-13
> Baseline: `198cf290146b4308e7a8da432d28abd46aca51d1`
> Scope: current non-archive authority, implementation evidence, and deterministic gates
> Status: **NO NEW UNREGISTERED FINDING**

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
| A-002 | **Open - `DEFERRED-CODE-CHANGE`** | `openspec/config.yaml` requires manual index/submodule/nested-worktree/diff observations and explicitly says they are not automatic protection. No local automatic detector was found. | [A-002 candidate](../../../../todos/todo-a002-gitlink-boundary-detector.md) needs a separately authorized deterministic-governance change. Manual git metadata is not a substitute. |
| A-003 | **Resolved, bounded current conformance** | CES, EVH, HITL1, glossary, and ADR 0025 agree: admission reads only Rubric identity/version and unique criterion IDs as non-model control-integrity metadata; content/judgment stays review-only; the Runner reports only `completed` or `failed`. Stage 4 performed a finite local conformance inspection. | Does not prove every live, future, or uninspected evaluation path. A future observed divergence needs a new code-and-test change. |
| A-004 | **Resolved, bounded current conformance** | RER, RUS, REJ, glossary, and ADR 0006 agree: supported retained diagnostic/Journal reader and participant presentation require an available selected Bundle; after loss they are unavailable; physical residual bytes are not asserted. Stage 5 found no prohibited local crossing. | `A-004-T01` remains a misleading scenario-title tooling residue, not a reopened required-behavior conflict. |
| A-005 | **Resolved within audited scope** | The factual Workspace/Bundle relation, completed-work tense, and stale archived-plan dependency were corrected. C-006 was withdrawn because it was not a verified mismatch. | No current remediation action. |
| A-006 | **Resolved within audited scope** | Over-broad all-node smoke and standalone readable-report claims were removed; only the A-003 boundary remains where it belongs. | No current remediation action. |
| A-007 | **Resolved within audited scope** | Final report remains a Bundle artifact, Support Handoff is `planned`, and the dedicated Primary User TUI route is `dormant`. Stage 6 adds no post-loss fallback. | A future Support Handoff needs independent retention/availability design. |
| A-008 | **Open - N-002 no-code authority residue** | `openspec/agent-charter/README.md` and `openspec/config.yaml` require every actually triggered policy / comma-separated canonical policies, while `openspec/policies/README.md:7` and DRC-001 say `one relevant policy`. | [N-002 candidate](../../../../todos/todo-n002-policy-routing-cardinality.md) requires a small owned main-spec/policy-index correction before this plan can close. |
| A-009 | **Open - `OPTIONAL-HARDENING`** | Requirement coverage validates alive IDs against `@impl` references. Current evidence policy deliberately centralizes richer proof only for selected policy/inventory requirements. | [A-009 candidate](../../../../todos/todo-a009-risk-based-semantic-traceability.md) is optional; it must not create a duplicate exhaustive test catalog. |

## Registered Deferred Work

| Item | Classification | Why it remains open | Owner / candidate |
| --- | --- | --- | --- |
| A-002 | `DEFERRED-CODE-CHANGE` | Manual gitlink checks cannot mechanically protect a future pointer or nested-worktree change. | [gitlink-boundary detector](../../../../todos/todo-a002-gitlink-boundary-detector.md) |
| A-004-T01 | `DEFERRED-TOOLING-CHANGE` | Current RER scenario bodies are correct, but two legacy titles cannot be renamed under current strict OpenSpec delta validation. | [scenario-rename validator](../../../../todos/todo-a004t01-openspec-scenario-rename-validator.md) |
| N-002 | current no-code inconsistency | Singular policy wording conflicts with the canonical multi-policy route and proposal grammar. | [policy-routing cardinality](../../../../todos/todo-n002-policy-routing-cardinality.md) |
| A-009 | `OPTIONAL-HARDENING` | ID-level coverage is intentionally not assertion-semantic traceability. | [risk-based semantic traceability](../../../../todos/todo-a009-risk-based-semantic-traceability.md) |

No new product-behavior or runtime conformance finding was discovered. `N-002` is the
only remaining no-code current-authority mismatch, so it prevents a truthful close of
the alignment plan. The other three items are accurately disclosed independent backlog
work and must not be silently implemented as part of a documentation cleanup.
