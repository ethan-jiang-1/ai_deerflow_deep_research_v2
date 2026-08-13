# Stage 6 Planning - Post-Decision Terminology And Status

> Change: `normalize-post-decision-terminology-status`
> Date: 2026-08-13
> Status: **PLANNING COMPLETE - APPLY NOT AUTHORIZED**

## Authorization And Baseline

The user authorized Stage 6 planning after Stages 1 through 5 were completed and
archived. That authorization creates and validates planning artifacts only. It does
not authorize an apply, sync, archive, commit, application code/test/runtime work,
main or delta specification edit, configuration/governance executable edit, or DeerFlow
source inspection/edit.

| Fact | Planning observation | Boundary |
| --- | --- | --- |
| Committed baseline | `a3c4d63fa5838824d5088b8013d7b163e699497b` (`feat(spec): apply reconcile-post-loss-diagnostic-authority + stage-5 ledger`) | This is a planning reference, not the required future apply baseline. |
| Active change | `normalize-post-decision-terminology-status` is the only active change. | Its `skip_specs: true` disposition is valid because this stage does not alter required behavior. |
| A-003 required/current disposition | Main specs accept deterministic identity/version and unique criterion-ID metadata only; finite local inspection found no observed deferred code gap. | This is bounded local conformance, not a general execution-quality claim. |
| A-004 required/current disposition | Supported diagnostic/Journal reader and participant presentation are Bundle-local; after loss, supported inspection is unavailable. | This does not claim secure erasure, residual-byte absence, live behavior, or every future/uninspected path. |
| A-004-T01 | Two stale RER scenario titles remain validation-compatible identifiers while their bodies have the accepted behavior. | `DEFERRED-TOOLING-CHANGE A-004-T01` remains a separate validator/scenario-rename change. |
| Protected user worktree | `deep_research_harness/AGENTS.md`, `deep_research_harness/CONTEXT.md`, and `openspec/agent-charter/README.md` are modified; `openspec/agent-charter/concepts.md` is untracked. | These concept-map edits are user-owned and outside Stage 6. `CONTEXT.md` may receive only later exact-occurrence edits after a fresh overlap check. |

## Adjustment D-001 - Rubric / Runner Terminology

- **Status:** proposed documentation adjustment; planning complete; apply not authorized.
- **Authority owner:** `cognitive-evaluation-suite` requirement blocks; parallel A-003 wording in `evaluation-hardening` and `hitl1-node`. The glossary and ADR are explanatory projections only.
- **Affected paths:** Later apply may edit the D-001 allowlisted `CONTEXT.md` occurrences and the ADR 0025 current-applicability postscript only; no main spec, delta, code, test, or control artifact.
- **Before:** The Runner/Rubric glossary wording says a Rubric is read only by upper review and is not Runner input. It suppresses the accepted narrow distinction for deterministic Case-control-integrity metadata.
- **After:** State that deterministic admission may read Rubric identity/version and unique criterion IDs only. Criterion prose, weights, thresholds, evaluator guidance, cognitive judgment, model-facing quality input, execution-output quality meaning, and Runner quality verdicts remain excluded. Runner still reports only `completed` or `failed`.
- **Reason and evidence:** `cognitive-evaluation-suite` requires this exact distinction; the Stage 4 post-archive disposition records bounded local conformance and reserves Stage 6 for explanatory propagation.
- **Main risk:** "Metadata" could be read as permission to load or interpret Rubric content during execution.
- **Possible side effects:** The term becomes more precise and longer; historical ADR 0025 wording remains broad by design, so readers must distinguish it from its new current-applicability postscript.
- **Risk controls / stop condition:** Permit only identity/version plus unique IDs; spell out every prohibited content/judgment channel; preserve ADR historical body; stop if a needed sentence cannot map to an accepted main-spec requirement or needs a runtime claim.
- **Verification before apply:** Re-read the CES A-003 blocks and Stage 4 disposition, capture the exact target text and user-worktree hunk, then compare proposed wording against the occurrence allowlist.
- **Verification after apply:** Scoped diff review, strict OpenSpec/governance/docs checks, and record that no code/test/current-conformance claim was introduced.
- **Observed side effects:** None observed in planning-only work. This observation does not cover later documentation apply or reader interpretation.
- **Remaining mismatch / follow-up owner:** Future runtime divergence is a separately authorized code-and-test change. No runtime gap was observed in the bounded Stage 4 inspection.
- **Authorization and date:** Stage 6 planning authorized 2026-08-13; APPLY not authorized.

## Adjustment D-002 - Post-Loss Diagnostic Terminology

- **Status:** proposed documentation adjustment; planning complete; apply not authorized.
- **Authority owner:** `research-run-experience`, `research-run-session`, and `run-event-journal`; their glossary/ADR projections do not own lifecycle behavior.
- **Affected paths:** Later apply may edit the D-002 allowlisted `CONTEXT.md` occurrences and the existing ADR 0006 current-applicability postscript only; no main spec, delta, code, test, storage, or Support Handoff implementation.
- **Before:** External Run Observation says an optional diagnostic/audit/metadata record may outlive the Bundle, without excluding a supported post-loss diagnostic/Journal reader or participant presentation. ADR 0006 says Bundle-loss semantics remain A-004 quarantine.
- **After:** Make clear that an external record is not a supported post-loss retained diagnostic/Journal reader or participant presentation; supported inspection is Bundle-local and unavailable after loss. This does not assert physical erasure or absence of residual bytes. Support Handoff remains planned with no current producer/schema/public entry and cannot become a fallback.
- **Reason and evidence:** The Stage 5 synchronized main specs give one answer for the three separate questions: physical residue is unspecified; supported reader is Bundle-local; participant presentation is unavailable after loss. Stage 5 observed bounded local conformance only.
- **Main risk:** A terse "unavailable" statement could falsely promise secure erasure or accidentally prohibit every non-diagnostic generic external log.
- **Possible side effects:** The glossary gains necessary distinctions; a future Support Handoff proposal must now state its Bundle-available lifetime instead of relying on an implied external fallback.
- **Risk controls / stop condition:** Keep physical bytes, supported reader, and participant presentation as separate statements; preserve typed terminal safe facts as non-artifact projections; retain the planned status; stop if wording requires a support-retention, reader, presentation, or lifecycle decision.
- **Verification before apply:** Re-read the three A-004 main-spec blocks and Stage 5 disposition, capture exact target text plus the protected user hunk, and confirm A-004-T01 is unchanged/out of scope.
- **Verification after apply:** Scoped diff review, strict OpenSpec/governance/docs checks, and a record that no external reader/presentation or secure-erasure claim was created.
- **Observed side effects:** None observed in planning-only work. This does not prove live, physical-storage, third-party, uninspected, or future behavior.
- **Remaining mismatch / follow-up owner:** `DEFERRED-TOOLING-CHANGE A-004-T01` remains separately owned. Any observed external post-loss runtime crossing requires a separate red-before-green code-and-test change.
- **Authorization and date:** Stage 6 planning authorized 2026-08-13; APPLY not authorized.

## Next Gate

The planning artifacts define a closed three-document apply allowlist, separate
Adjustment Records, and explicit risk controls. A new explicit `APPLY` authorization is
required before any `CONTEXT.md` or ADR edit. Planning completion cannot be read as
authorization to apply, archive, or commit.
