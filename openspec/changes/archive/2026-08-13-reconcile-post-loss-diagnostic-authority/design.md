## Context

See [proposal.md](proposal.md) for the resolved A-004 product decision. The current
main specifications disagree: `research-run-experience` permits a support-journal
fallback, while `research-run-session` and `run-event-journal` keep retained diagnosis
within an available Bundle and return unavailable after loss.

This is a required-behavior reconciliation. The existing typed diagnostic location,
publisher, retained-session store, and inspection commands are current-behavior
evidence only. They are not authority to reverse the approved product decision.

## Goals / Non-Goals

**Goals:**

- Give RER, RUS, and REJ one answer for the supported diagnostic lifetime, reader,
  and participant-visible outcome after Bundle loss.
- Preserve the original terminal category, bounded safe reference, recovery facts,
  redaction, and one legal lifecycle action when Bundle-local publication is
  unavailable.
- Require an apply-time conformance inspection to distinguish a specification update
  from any current implementation gap.

**Non-Goals:**

- This change does not implement storage deletion, secure erasure, an external
  retention service, or Support Handoff.
- It does not remove every in-memory or physical-storage residual byte, make a claim
  about disk forensics, or define a support/audit retention policy outside the supported
  Deep Research reader.
- It does not modify `CONTEXT.md` or ADR terminology; Stage 6 owns those dependent
  explanatory surfaces after this behavior decision closes.

## Decisions

### 1. Separate storage residue from the supported diagnostic contract

The deltas intentionally answer three different questions:

| Question | Decision | Reason |
| --- | --- | --- |
| May physical storage retain residual bytes after deletion? | Not specified. | This change neither designs nor proves secure erasure. |
| May Deep Research use a supported external diagnostic reader after Bundle loss? | No. | It would contradict Bundle-local diagnostic lifetime and create a second retained observation surface. |
| May a person or AI participant receive external diagnostic presentation after Bundle loss? | No. | Presentation must derive from the same available Bundle-local result as inspection. |

This removes the ambiguity that made “external diagnostics may outlive Bundle loss”
appear compatible with “inspection is unavailable.”

### 2. Preserve lifecycle facts while making diagnostic availability unavailable

When exact diagnostic publication cannot be verified in an available Bundle, the
terminal's existing category, phase, recovery disposition, opaque reference, and legal
next action continue to come from the typed terminal/lifecycle fact. Those bounded
terminal fields are not a read of a retained diagnostic artifact. Only the diagnostic
location and `research_record_created` truth change to `unavailable` / false. A reader,
diagnostic, or Support Handoff never becomes retry, resume, selection, or lifecycle
authority. A later status or inspection of a lost Bundle still follows the existing
unavailable lifecycle result; this decision does not turn a previously returned terminal
projection into a retained post-loss diagnostic reader.

The rejected alternative was an external support journal. It could preserve bounded
diagnostic observations, but it would require a retention writer, reader authorization,
redaction and deletion policy, cross-Bundle correlation boundary, and participant
presentation contract. The product owner rejected that broader lifecycle model for A-004.

### 3. Keep Support Handoff planned and temporally bounded

The deltas name Support Handoff only to prevent a future planned capability from being
mistaken for approved external retention. If later proposed, it must operate while the
selected Bundle exists and must receive a separate capability, product decision, source
of truth, reader authorization, and retention/deletion design. It cannot silently
reintroduce post-loss Journal or diagnostic inspection.

### 4. Apply requires a hard current/required gap stop

The specification can be synchronized only after a separately authorized apply-time
inspection of local terminal publication, diagnostic-location projection, retained
session inspection, and Event Journal inspection. The inspection must look for all
external writes, reads, and participant presentations, not merely for lifecycle
authority crossings.

If any local path writes, reads, or presents a support journal, external diagnostic,
external Journal, or Support Handoff when Bundle-local exact-record publication is
unverified or after Bundle loss, the agent records a `DEFERRED-CODE-CHANGE` including
the path, observed behavior, affected requirement, risk, and separately owned
red-before-green implementation/test candidate. It then stops code-conformance work.
Alignment-only authorization does not permit code or test changes to remove the gap.

### 5. Use the established typed contained-location literal

The accepted RER requirement currently calls a verified contained record
`session_bundle`, while the local `RunFailure` literal and runtime result use
`bundle_journal`. The local runtime assigns `bundle_journal` only when the returned
Bundle observation is available, has the same `bundle_id`, and verifies the exact
terminal diagnostic reference; otherwise it assigns `unavailable`. The focused
publisher and terminal tests use that same condition. `research-run-session` and
`run-event-journal` identify the retained artifact as the Bundle-local Journal.

Therefore `bundle_journal` is the existing machine-visible literal for the selected
Bundle-local behavior and the RER delta adopts it. This is a terminology/contract
correction determined by current typed facts, not a choice about retention, readers, or
participant presentation. Apply must still verify the exact condition and every consumer.
If any inspected condition or consumer differs, record `DEFERRED-CODE-CHANGE` and stop
implementation-conformance work. Stage 6 then propagates the accepted wording to
`CONTEXT.md` and ADR explanatory surfaces; it does not need to choose the literal again.

## Risks / Trade-offs

- **Support/audit visibility after deletion is reduced** -> The product decision accepts
  this. Any future retention need must reopen a separately scoped product decision,
  rather than making a hidden fallback.
- **“No external reader” is misunderstood as secure erasure** -> Every changed
  requirement carries the explicit physical-residue distinction.
- **Accepted RER still encodes `support_journal` while inspected local typed literals do
  not** -> Apply-time inspection must cover unverified Bundle-local publication as well
  as post-loss paths; an external crossing is a `DEFERRED-CODE-CHANGE`, and no
  implementation change is concealed as a spec-only success.
- **A consumer still expects stale `session_bundle`** -> Apply inspects every local
  terminal consumer against the now-required `bundle_journal` literal. Any such
  observable contract difference is a `DEFERRED-CODE-CHANGE`; Stage 6 only synchronizes
  explanatory terminology after the required/current disposition is explicit.
- **Support Handoff is accidentally treated as implemented** -> The deltas label it
  `planned` and prohibit it from becoming a post-loss reader.
- **Three specifications drift again** -> The delta repeats the same supported-lifetime,
  reader, and presentation boundary, and apply re-reads the synced blocks together.

## Migration Plan

1. Obtain a separate explicit apply authorization for this change and record a fresh
   worktree, active-change, and gitlink baseline without opening DeerFlow source.
2. Create an apply-time A-004 Adjustment Record with exact before/after wording,
   risks, possible side effects, controls, and evidence limits.
3. Inspect local typed diagnostic location, terminal publication, retained-session
   inspection, and Event Journal inspection paths. Confirm the exact verified
   contained-publication condition yields `bundle_journal`; on any stale consumer or
   external write/read/presentation, record `DEFERRED-CODE-CHANGE` and do not modify
   code or tests.
4. If the required/current disposition is explicit, apply and sync only the RER/RUS/REJ
   deltas using the normal OpenSpec workflow. Do not directly edit main specs.
5. Run structural and existing deterministic verification appropriate to the observed
   paths; record proof limits, actual side effects, and residual gaps before archive.
6. Obtain separate archive authorization. After archive, re-establish the no-active-
   change baseline and update the progressive alignment ledger.

Before synchronization, the active delta may be revised or abandoned. After sync, a
corrective OpenSpec change is required; archived history is not rewritten.

## Open Questions

None. The product decision, supported reader boundary, participant outcome, and
Support Handoff status are already resolved. Apply-time findings concern current
conformance, not this design's required behavior.
