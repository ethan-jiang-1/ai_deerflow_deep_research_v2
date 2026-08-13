# Stage 5 Planning - A-004 Post-Loss Diagnostic Authority

> Change: `reconcile-post-loss-diagnostic-authority`
> Date: 2026-08-13
> Status: **PLANNING COMPLETE - APPLY NOT AUTHORIZED**

## Authorization And Boundary

The user authorized progressive work to continue after closing and archiving A-003.
Under the OpenSpec proposal workflow, this authorizes creation and review of planning
artifacts only. It does not authorize application code, tests, typed contracts,
fixtures, storage, deletion behavior, current main specs, `CONTEXT.md`, ADRs,
`openspec/config.yaml`, sync, archive, commit, or any DeerFlow edit/source inspection.

The planning scope is only A-004: reconcile incompatible required behavior for
diagnostics after Bundle loss. Stage 6 terminology synchronization remains a separate
follow-up and must not start from this planning authorization.

## Baseline

| Fact | Observation | Evidence boundary |
| --- | --- | --- |
| Last committed baseline | `177a98c` (`docs(backlog): record A-004 decision state`) | The uncommitted planning artifacts below are not applied current authority. |
| A-004 product decision | Option A: supported lifecycle diagnostics are Bundle-local; after Bundle loss, supported inspection is unavailable. | The decision was confirmed by the product owner on 2026-08-12 in `alignment-audit-60-17-a004a-bundle-local-only.md`, rather than derived from code. |
| Current required-behavior conflict | RER permits an external diagnostic/support-journal fallback; RUS and REJ require Bundle-local diagnostics and prohibit post-loss external inspection. | This compares only owning main-spec text. It does not claim an implementation result. |
| Three questions | Physical residual bytes are not absolutely asserted; no supported external reader exists after loss; no participant receives post-loss external diagnostic presentation. | These are the approved product boundaries, not secure-erasure or storage-forensics claims. |
| Selected OpenSpec scope | RER, RUS, and REJ deltas only. | An active planning change exists at `openspec/changes/reconcile-post-loss-diagnostic-authority/`; it is neither synced nor archived. |
| DeerFlow boundary | Gitlink is out of scope. | This work neither modifies nor source-browses `deerflow/`; an apply-time metadata baseline remains mandatory. |

## Adjustment A-004

- **Status:** proposed required behavior; product decision confirmed; specification
  apply not authorized.
- **Authority owner:** `research-run-experience` owns the participant-visible terminal
  diagnostic location. `research-run-session` owns retained-session readability and
  `run-event-journal` owns the Journal lifetime/inspection boundary. These are three
  adjacent requirement owners, not three lifecycle authorities.
- **Affected paths:** Proposed delta paths only:
  `openspec/changes/reconcile-post-loss-diagnostic-authority/specs/research-run-experience/spec.md`,
  `openspec/changes/reconcile-post-loss-diagnostic-authority/specs/research-run-session/spec.md`,
  and `openspec/changes/reconcile-post-loss-diagnostic-authority/specs/run-event-journal/spec.md`.
  The proposal, design, task list, this record, validation record, and progressive ledger
  are also affected. No current main specification, code, test, or `CONTEXT.md` is in
  scope for planning.
- **Before:** RER permits a diagnostic to outlive Bundle loss, exposes
  `diagnostic_location` values `session_bundle`, `support_journal`, and `unavailable`,
  and requires support-journal fallback when Bundle publication cannot be verified. RUS
  and REJ require diagnostics and Journal inspection to be Bundle-local and unavailable
  after loss, with no external historic fallback. These cannot jointly answer what a
  participant may inspect after loss.
- **After:** The required contract has one answer. A supported diagnostic record,
  reader, and participant presentation are Bundle-local and require an available Bundle.
  `diagnostic_location` is only `session_bundle` or `unavailable`; failed Bundle
  publication does not write, read, or present an external diagnostic. The original
  terminal category, safe opaque reference, recovery facts, redaction, and legal next
  action stay with the typed lifecycle fact. The contract does not assert that storage
  erasure leaves no physical residual bytes. Support Handoff remains planned and, if
  implemented later, operates only while its selected Bundle is available.
- **Reason and evidence:** The Stage 3 re-audit documented the named RER/RUS/REJ conflict.
  The selected Option A is a product/lifecycle choice: reducing post-deletion support
  visibility is accepted in exchange for one diagnostic lifetime and no external reader.
  Existing implementation is not used to choose this contract.
- **Main risk:** A real support, audit, or operations need may require retained access
  after deletion, in which case Bundle-local-only is insufficient.
- **Possible side effects:** Support/audit observation ends with Bundle deletion;
  `support_journal` typed locations or tests may expose a required/current gap; a future
  Support Handoff needs a Bundle-available workflow and cannot be treated as an implicit
  retention service; readers could wrongly interpret “no supported reader” as a claim of
  secure erasure.
- **Risk controls / stop condition:** State the physical-bytes, supported-reader, and
  participant-presentation distinctions in all three deltas. Preserve no-recovery,
  no-selection, redaction, and terminal-authority rules. During apply, inspect every
  local external diagnostic write/read/presentation path; on any crossing, record
  `DEFERRED-CODE-CHANGE` and stop code-conformance work without changing code or tests.
  Do not sync, archive, or update terminology without separate authorization.
- **Verification before apply:** Re-read the Option A decision, rejected Option B,
  Stage 3 evidence, proposal/design/tasks, all three owning main-spec blocks, and the
  narrowest local publication/inspection evidence seams. Re-establish a fresh
  HEAD/worktree/active-change/gitlink baseline without opening DeerFlow source.
- **Verification after apply:** Establish, only for inspected local paths, whether an
  unavailable/deleted Bundle can trigger external diagnostic writes, reads, or
  participant presentation. Verify terminal-category/action preservation, run required
  OpenSpec and deterministic gates, and record proof limits. This cannot prove physical
  erasure, all live integrations, or future paths.
- **Observed side effects:** None observed. This is limited to planning artifacts and
  the ledger; no current authority, code, test, storage, or DeerFlow path has changed.
- **Remaining mismatch / follow-up owner:** A-004 remains open until separately
  authorized apply, conformance inspection, sync, and archive finish. Stage 6 owns
  `CONTEXT.md`/ADR terminology synchronization. An implementation path that retains,
  reads, or presents an external post-loss diagnostic becomes a separately authorized
  code/test change after the required `DEFERRED-CODE-CHANGE` record.
- **Authorization and date:** Product decision confirmed 2026-08-12; Stage 5 planning
  authorized 2026-08-13; apply authorization not granted.

## Planning Risk Review

| Potential effect of planning | Why it matters | Control | Current observation |
| --- | --- | --- | --- |
| The delta might deny a reader while silently retaining one through a support fallback. | It would leave the central RER/RUS/REJ conflict unresolved. | Require all three delta owners to prohibit external post-loss write, read, and presentation. | Every delta contains the same Bundle-local-only boundary. |
| “No external reader” might be read as an absolute deletion/security claim. | The product decision is about supported behavior, not storage forensics. | Repeat the physical-residual-bytes exclusion in RER, RUS, REJ, proposal, and design. | No artifact claims secure erasure or that no bytes remain. |
| Existing code or typed fields may still use `support_journal`. | A synchronized spec could otherwise conceal a current/required gap. | Apply tasks require source-to-consumer inspection and `DEFERRED-CODE-CHANGE` for any external write/read/presentation. | Not inspected in this planning stage; no conformance claim is made. |
| A planned Support Handoff may be mistaken for approved retention. | It would expand scope and create a shadow external diagnostic contract. | Label it planned, Bundle-available only, and out of scope; require a later separate capability/change. | No Support Handoff implementation or external retention capability is proposed. |
| Early `CONTEXT.md`/ADR edits could create a second, stale answer. | Terminology would get ahead of the accepted behavior authority. | Leave terminology surfaces untouched until Stage 6. | No `CONTEXT.md` or ADR path is edited. |

## Next Gate

The proposal, RER/RUS/REJ deltas, design, and 22-task execution checklist are created
and strictly validated. See `01-stage-5-planning-validation.md` for validation outcomes,
the OpenSpec completeness correction, and proof boundaries. Only a new, explicit Stage 5
apply authorization may begin `tasks.md`; it cannot be inferred from this planning
record, the confirmed Option A decision, or a passing validation command.
