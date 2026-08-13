# Stage 5 Apply - A-004 Admission, Baseline, and Adjustment Record

> Change: `reconcile-post-loss-diagnostic-authority`  
> Date: 2026-08-13  
> Status: **APPLIED AND VERIFIED WITH BOUNDED CONFORMANCE; ARCHIVE NOT AUTHORIZED**

## Explicit Authorization and Boundary

The user explicitly sent `APPLY` for
`openspec/changes/reconcile-post-loss-diagnostic-authority` on 2026-08-13. That is
separate from the 2026-08-12 A-004 product decision and the Stage 5 planning
authorization.

Authorized work is limited to the active change's finite local conformance inspection,
the RER/RUS/REJ delta correction and normal OpenSpec sync if inspection permits it,
verification, this Stage 5 evidence, and the progressive ledger. This does **not**
authorize application code, tests, fixtures, typed contracts, storage, deletion
behavior, configuration, governance executables, `CONTEXT.md`, ADRs, archives,
commit, or any DeerFlow edit or source inspection. Any observed current/required code
gap is a `DEFERRED-CODE-CHANGE`, not an apply-time repair. Archive requires a new,
explicit authorization.

## Fresh Baseline

Recorded 2026-08-13 10:49:54 CST, before Stage 5 target edits:

| Observation | Result | Evidence limit |
| --- | --- | --- |
| HEAD | `177a98cea2cf3285cd584f0b8be770b8b02d547b` | Identifies the committed starting point only. |
| Active OpenSpec changes | Only `reconcile-post-loss-diagnostic-authority`, `0/22` tasks complete | The active planning change is expected; it is not applied authority. |
| Root worktree | Modified progressive ledger; untracked Stage 5 planning records and all active-change artifacts | These are expected planning evidence. No application source/test path was named. |
| `deerflow` git index entry | mode `160000`, gitlink `66b9e7f21212490cf92fafac137542b9deb06615` | Gitlink metadata only; it does not protect future edits. |
| `git submodule status -- deerflow` | `66b9e7f21212490cf92fafac137542b9deb06615 deerflow (heads/main-282-g66b9e7f2)` | Observed nested revision only. |
| `git -C deerflow status --porcelain=v1 --untracked-files=all` | no output | A clean nested worktree observation, not an authorization to inspect or modify its source. |
| `git diff --submodule=short` | only the progressive-ledger Stage 5 planning diff; no gitlink diff | Current diff scope only; it is not automatic submodule protection. |

## Required Review Result

The apply agent re-read the proposal, its Workflow Outcome Review, design, all three
delta specs, confirmed A-004 Option A, rejected Option B, and Stage 3 conflict evidence.
The product decision remains unchanged: supported retained diagnostic artifacts,
readers, and participant presentation are Bundle-local; after loss, supported
inspection is `unavailable`; no external Journal, diagnostic, or Support Handoff may
be read, written, or presented as a substitute. The decision does not claim secure
erasure or the absence of physical residual bytes. Safe category, opaque reference,
recovery, and legal-action fields already present in a typed terminal result are not a
retained-artifact read.

One actionable planning finding was added before any target edit:

| Added task | Finding | Required disposition |
| --- | --- | --- |
| 1.5 | Two RER delta scenario titles still use stale language: `Verified bundle record enables session-bundle location` and `Support-journal fallback retains observed origins`. Their bodies already require `bundle_journal` or `unavailable` and prohibit the fallback. | Reconcile the labels before sync. An attempted direct correction was rejected by strict OpenSpec validation because a `MODIFIED` block must preserve every current scenario title. The record must distinguish a permitted validation-compatible correction from a label whose retirement needs a different requirement shape; it changes no code or product decision. |

No other new actionable finding was identified in the review. The Stage 3 conflict is
still the expected one: currently approved RER requires `support_journal`, while RUS
and REJ require Bundle-local diagnostics and unavailable inspection after Bundle loss.

## Adjustment Record: A-004

| Field | Apply-time record |
| --- | --- |
| Before | Current RER permits `session_bundle`, `support_journal`, or `unavailable`, and requires a support-journal fallback when exact contained publication is unverified. Current RUS and REJ instead keep supported diagnosis/Journal inspection inside an available Bundle and return unavailable after loss. |
| After | RER, RUS, and REJ will give one required answer: a supported retained diagnostic artifact, reader, and participant presentation are Bundle-local and require an available selected Bundle. A provider terminal uses `bundle_journal` only after exact contained publication is verified; otherwise it uses `unavailable`. No external diagnostic, Journal, or Support Handoff is written, read, or presented as a post-loss alternative. Typed terminal category/reference/recovery/legal-action fields remain bounded lifecycle facts, not artifact reads. Support Handoff remains planned and Bundle-available only. Physical residual bytes are outside the supported-reader contract. |
| Authority owner | RER owns the participant-visible terminal diagnostic location; RUS owns retained-session readability; REJ owns Journal lifetime and inspection. The current local typed/runtime path is conformance evidence only. |
| Risk | Deletion ends supported support/audit visibility. A real retained-access need would require a separately scoped product, data-retention, reader-authorization, redaction, deletion, implementation, and test decision. |
| Possible side effects | A stale `support_journal` or `session_bundle` consumer could expose a required/current gap. Readers could mistake the no-external-reader rule for secure erasure. A future Support Handoff could be mistakenly treated as already approved external retention. |
| Control / stop condition | Inspect finite local source-to-consumer, session, Journal, and participant paths. Any forbidden external write/read/presentation, stale literal consumer, or failed required condition creates a named `DEFERRED-CODE-CHANGE` with a red-before-green owner; stop conformance work and do not alter code/tests. Keep physical-residue, supported-reader, and participant-presentation questions separate in every synced requirement. |
| Evidence boundary | Local source inspection, existing deterministic tests, OpenSpec/governance checks, and the configured offline verification can establish only bounded current-path observations and structural validity. They cannot prove physical erasure, residual-byte absence, every live/credentialed integration, every future path, or universal semantic compatibility. |
| Current / required gap owner | No `DEFERRED-CODE-CHANGE` arose from the bounded inspection. Any future observed implementation gap belongs to a separately authorized red-before-green code-and-test change. `DEFERRED-TOOLING-CHANGE A-004-T01` belongs to a separate OpenSpec validator change; Stage 6 owns only explanatory `CONTEXT.md`/ADR terminology propagation after this disposition. |
| Applied / verified | Applied by normal sync to the three owning main specs. Bounded local conformance, strict OpenSpec, governance, whitespace, focused evidence, and `UV_OFFLINE=1 make verify` passed. Archive remains outside the current authorization. |

## Scope Check Before Target Edit

The planned immediate work is the finite source-to-consumer inspection and an
OpenSpec-compatible reconciliation of the two stale RER scenario labels named above.
No main spec will be directly edited. Main-spec synchronization will occur only after
inspection permits it and through the normal OpenSpec sync workflow.

## Post-Apply Evidence

| Field | Observed result |
| --- | --- |
| Changed delta paths | `openspec/changes/reconcile-post-loss-diagnostic-authority/specs/research-run-experience/spec.md`, `openspec/changes/reconcile-post-loss-diagnostic-authority/specs/research-run-session/spec.md`, and `openspec/changes/reconcile-post-loss-diagnostic-authority/specs/run-event-journal/spec.md`. |
| Changed main-spec paths | `openspec/specs/research-run-experience/spec.md`, `openspec/specs/research-run-session/spec.md`, and `openspec/specs/run-event-journal/spec.md`. |
| Applied content | The three owners now require available-Bundle-only retained diagnostics and Journal inspection; exact verified publication yields `bundle_journal`, otherwise `unavailable`; there is no external post-loss reader or participant presentation. Detailed sync and common-answer evidence: `02-a004-main-spec-sync.md` and `03-a004-synced-required-current-disposition.md`. |
| No-code confirmation | `git diff HEAD -- deep_research_harness` and its whitespace check were empty; current status contains no `deep_research_harness/` path. `git diff HEAD -- deerflow`, `git diff --submodule=short`, and nested DeerFlow status were empty at the Stage 5 baseline. This is a worktree observation, not a future write barrier. |
| Observed side effects | **None observed within the performed checks.** Four focused tests and the full configured offline deterministic verification passed; finite local inspection found no prohibited external crossing or stale consumer. |
| Evidence bound on no observed side effect | The Gateway stack was unavailable for four skipped integration cases; Pydantic warning output remained non-failing. No live/credentialed run, physical-storage inspection, universal source scan, or future-path proof was performed. |
| Remaining mismatch | No `DEFERRED-CODE-CHANGE` was found in the bounded local path. `DEFERRED-TOOLING-CHANGE A-004-T01` remains: strict OpenSpec retains two legacy RER scenario titles although their bodies now impose the selected Bundle-local-only rule. |
| Deferred code/test gap owner | None for an observed runtime violation. A separately authorized OpenSpec tooling change owns a red validator test and scenario-rename support for A-004-T01; a later RER maintenance change may remove the compatibility labels. Any future runtime violation requires its own red-before-green code-and-test change. |
| Verification evidence | `01-a004-local-conformance-inspection-and-focused-evidence.md`, `02-a004-main-spec-sync.md`, `03-a004-synced-required-current-disposition.md`, `04-a004-structural-governance-verification.md`, and `05-a004-full-deterministic-verification.md`. |
