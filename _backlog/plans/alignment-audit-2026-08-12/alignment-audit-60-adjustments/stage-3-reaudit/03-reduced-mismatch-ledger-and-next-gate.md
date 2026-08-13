# Stage 3 Reduced Mismatch Ledger And Next Gate

> Baseline: `09a2e3b7525d65e9c0e56d93c20735727be31e04`
> Date: 2026-08-13
> Scope: current non-archive authority after Stage 1 and Stage 2 cleanup

## A-001 Through A-009

| ID | Stage 3 status | Evidence / owner | Next disposition |
| --- | --- | --- | --- |
| A-001 | Resolved in Stage 1 scope | Current topology authority names `deerflow/` gitlink; no remaining claim calls root `backend/`/`frontend/` the DeerFlow mirror. | Closed; do not rewrite archives. |
| A-002 | Open - `DEFERRED-CODE-CHANGE` | Manual Git metadata evidence is current; `openspec/config.yaml` correctly disclaims automatic protection; no detector exists. | Keep disclosed until a separately authorized detector change. |
| A-003 | Open P1 semantic conflict | CES review-only prohibition conflicts with EVH scenario criteria/admission and current admission implementation. | Stage 4 product-decision change: `reconcile-evaluation-rubric-authority`. |
| A-004 | Open P1 semantic conflict | RER/glossary permit post-loss external observation; RUS/REJ and current implementation require Bundle-local diagnosis. | Stage 5 product-decision change: `reconcile-post-loss-diagnostic-authority`. |
| A-005 | Resolved safe subset | Workspace fact, completed-work tense, and archived-plan dependency were corrected; C-006 was deliberately withdrawn, not hidden. | Closed within the audited mismatch definition. |
| A-006 | Resolved safe subset; A-003 remains isolated | All-node smoke and standalone readable-report claims are gone. Rubric/Runner is tracked only as A-003. | No direct Stage 3 edit. |
| A-007 | Resolved safe subset; A-004 remains isolated | Artifact/export separation, Support Handoff planned status, and dormant TUI route are current. Post-loss retention stays A-004. | No direct Stage 3 edit. |
| A-008 | Reopened partial mismatch | Charter entry surfaces are fixed, but `openspec/policies/README.md:7` and `deep-research-agent-charter/spec.md:13` retain "one relevant policy" while the same main spec requires a comma-separated policy list at line 422. | Register N-002; do not change a main spec or policy README without a separate authorized change. |
| A-009 | Open - `OPTIONAL-HARDENING` | Global `@impl` coverage is green but remains ID-level rather than assertion-semantic. | Keep disclosed; consider a bounded changed/high-risk requirement mapping later. |

## Registered New Findings

| ID | Classification | What was found | Risk and control | Disposition |
| --- | --- | --- | --- | --- |
| N-001 | Reviewed wording candidate, not admitted as mismatch | `deployment-configuration/spec.md:434` says upstream `backend/`/`frontend/` without explicitly qualifying `deerflow/`. In context it is a no-change-under-upstream boundary, not a root-mirror assertion. | Low ambiguity risk. Treating it as an A-001 regression would overread a negative guard. | No scope amendment; revisit only if a future deployment-spec change already owns this line. |
| N-002 | Current policy-cardinality inconsistency | Policy README and DRC-001 say "one relevant policy" while current Charter routing and DRC-009's comma-separated field permit every actually triggered policy. | Moderate authoring-risk: a contributor may under-select triggered reviews. Changing either main spec or policy README requires a bounded OpenSpec change and review. | Not auto-added to Stage 4. Product owner must sequence a small policy-routing correction separately or explicitly bundle it with a compatible future change. |

## Stage 3 Gate Result

- A new-HEAD reduced ledger now separates resolved cleanup from unresolved conflicts.
- A-003 and A-004 have fresh evidence; neither is resolved by test or structural green.
- New findings are registered and no unapproved authority was changed.
- No current code, test, spec, configuration, or DeerFlow edit was made by Stage 3.

## Next Authorized Decision

The next planned move remains a Stage 4 **planning-only** authorization for
`reconcile-evaluation-rubric-authority`, using the already reviewed Option A decision
that criterion IDs are control-integrity metadata while Rubric content remains
non-model-facing and no quality verdict is produced by the Runner. That authorization
must not include apply, code edits, or A-004 work.

Before or alongside that later sequencing decision, the owner should decide whether
N-002 receives its own small policy-routing change. It must not be silently folded into
Stage 4 merely because both affect OpenSpec wording.
