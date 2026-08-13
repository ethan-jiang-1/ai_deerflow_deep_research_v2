# Stage 6 Apply Record - D-002 Post-Loss Diagnostic Terminology

> Change: `normalize-post-decision-terminology-status`
> Date: 2026-08-13
> Status: **APPLIED AND VERIFIED - ARCHIVE PENDING**

- **Authority owner:** `research-run-experience`, `research-run-session`, and
  `run-event-journal`. The glossary and ADR 0006 only explain their contract.
- **Affected paths:** Exact Bundle Loss, External Run Observation, Run Event Journal,
  and Support Handoff definitions in `CONTEXT.md`; only ADR 0006's existing
  current-status/applicability postscript.
- **Before:** Bundle Loss limits authoritative State recovery, but does not state the
  retained-diagnostic/Journal reader/presentation disposition. External Run Observation
  says an optional diagnostic/audit/metadata record may outlive a Bundle without
  excluding a supported post-loss diagnostic reader or participant presentation. ADR
  0006 leaves Bundle-loss semantics in A-004 quarantine.
- **After:** Explain separately that supported retained diagnostic/Journal inspection
  and participant presentation require an available selected Bundle and are
  `unavailable` after loss; an external record does not create a supported fallback.
  The wording does not assert secure erasure or absence of residual bytes. Support
  Handoff remains `planned`, has no current producer/schema/public entry, and cannot be
  a current or implicit post-loss fallback. ADR 0006's postscript receives the same
  accepted boundary, preserving historical text and dormant Dedicated-TUI status.
- **Reason and evidence:** The accepted RER/RUS/REJ blocks and Stage 5 disposition
  separately establish physical-residue scope, supported reader, participant
  presentation, typed terminal safe facts, and planned Support Handoff.
- **Main risk:** "Unavailable" may be read as either secure erasure or a prohibition on
  every generic external log.
- **Possible side effects:** The glossary becomes more precise; a later Support Handoff
  proposal must state its retention/availability behavior instead of relying on an
  implied fallback.
- **Risk controls / stop condition:** Keep physical bytes, supported reader, and
  participant presentation distinct; preserve no-authority/no-recovery and typed safe
  terminal facts; retain planned status. Stop if a statement needs storage, reader,
  presentation, lifecycle, or Support Handoff behavior beyond the accepted contract.
- **Verification before apply:** Fresh clean worktree and exact before-text baseline;
  the RER/RUS/REJ blocks and Stage 5 post-archive disposition were reviewed. A-004-T01
  is explicitly out of scope.
- **Verification after apply:** Exact occurrence/diff review against RER/RUS/REJ;
  strict OpenSpec, Charter, Markdown/link, whitespace, and offline deterministic gates;
  record only their stated proof limits.
- **Applied content:** Only the four allowlisted `CONTEXT.md` D-002 definitions now
  separate supported Bundle-local reader/presentation from possible external records
  and physical residue. ADR 0006's existing postscript now names the accepted current
  contract; its title and historical body are unchanged.
- **Observed side effects:** **None observed within the performed documentation,
  governance, and deterministic checks.** The prior broad external-observation wording
  is now narrower without claiming that external records or residual bytes cannot exist.
- **Evidence bound on no observed side effect:** This does not prove secure erasure,
  residual-byte absence, every live/credentialed/third-party presentation, or every
  future/uninspected path. Stage 5's finite local result remains bounded; A-004-T01
  remains open.
- **Remaining mismatch / follow-up owner:** `DEFERRED-TOOLING-CHANGE A-004-T01` stays
  with a separately authorized OpenSpec validator/scenario-rename change. Any observed
  post-loss external runtime crossing needs a separately authorized red-before-green
  code-and-test change.
- **Authorization and date:** User authorized docs-only apply on 2026-08-13; archive
  and commit remain unauthorized.
