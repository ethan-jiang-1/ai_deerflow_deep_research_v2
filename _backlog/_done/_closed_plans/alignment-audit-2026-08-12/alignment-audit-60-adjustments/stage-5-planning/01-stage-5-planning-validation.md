# Stage 5 Planning Validation - A-004 Post-Loss Diagnostic Authority

> Change: `reconcile-post-loss-diagnostic-authority`
> Date: 2026-08-13
> Status: **PLANNING COMPLETE - APPLY NOT AUTHORIZED**

## Artifacts Reviewed

| Artifact | Result | Review conclusion |
| --- | --- | --- |
| `proposal.md` | complete | States the approved Bundle-local-only decision, valid Focus Card, Workflow Outcome Review, no-code scope, explicit reader/presentation boundary, and three capability owners. |
| RER delta | complete | Removes `support_journal` as a required diagnostic location/fallback, retains terminal fact ownership and legal actions, and makes unverified Bundle publication `unavailable`. |
| RUS delta | complete | Makes retained-session material readable only from an available Bundle, prevents post-loss external diagnostic presentation, and constrains planned Support Handoff to Bundle availability. |
| REJ delta | complete | Makes the Journal's supported persistence, reader, and participant presentation lifetime Bundle-local without claiming physical secure erasure. |
| `design.md` | complete | Separates physical bytes, supported reader, and participant presentation; records rejected external retention and the hard conformance-gap stop. |
| `tasks.md` | complete | Contains 21 unchecked dependency-ordered tasks, separately gates apply/archive authorization, requires a finite external-crossing inspection, and reserves `DEFERRED-CODE-CHANGE` for a code gap. |

## Planning Correction Observed

The first strict validation found six missing scenario titles in modified requirement
blocks. OpenSpec treats `## MODIFIED Requirements` as full replacement blocks, so this
guard prevents an archive from silently dropping unchanged scenarios. The planning
artifacts now retain each original title while changing only its outcome to the selected
Bundle-local-only contract. No main specification, code, or test was edited.

This correction matters because it proves the delta preserves existing retry, redaction,
terminal, and no-recovery scenarios while modifying only the incompatible external
fallback semantics.

## Validation

| Check | Result | Proven scope / limit |
| --- | --- | --- |
| `openspec status --change reconcile-post-loss-diagnostic-authority --json` | passed; 4/4 artifacts complete | Planning artifact graph is complete. It does not authorize or perform apply. |
| `openspec validate reconcile-post-loss-diagnostic-authority --strict` | passed | Delta structure and internal OpenSpec consistency, not runtime/spec conformance. |
| `openspec show reconcile-post-loss-diagnostic-authority --json --deltas-only` | reviewed; 7 modified requirement blocks | RER/RUS/REJ delta parsing exposes the intended required behavior; it does not inspect implementation. |
| `openspec doctor --json` | healthy | Local OpenSpec root health only. |
| `python3 openspec/governance/check_agent_charter.py` | passed | Focus Card and selected-policy governance shape only; it does not assess the product decision. |
| `git diff --check` | passed | No whitespace error in the current planning/audit diff. |
| Manual planning review | passed | All three deltas give the same answer: physical residual bytes are not asserted; supported external reader and post-loss external participant presentation are prohibited; Support Handoff is planned and Bundle-available only. |

No runtime test was run in this planning-only stage. The task list reserves focused
publication/inspection evidence and `UV_OFFLINE=1 make verify` for a separately
authorized apply. A green planning validation does not prove that current typed fields,
storage, code paths, tests, adapters, or live integrations have no `support_journal` or
other external post-loss diagnostic crossing.

## Final Planning Effect And Risk Status

- **Content adjusted:** Only the active OpenSpec planning artifacts, this Stage 5
  evidence, and the progressive checkbox ledger were created or updated. No main spec
  is synchronized.
- **Observed side effects:** None outside planning scope. The active change is
  intentionally visible and unarchived; it must not be interpreted as applied current
  authority.
- **Open risk:** Current local terminal publication or participant projection may still
  retain, write, read, or present `support_journal` or another external diagnostic.
  Support/audit users may also have a legitimate post-deletion retention need that the
  approved Option A deliberately does not solve.
- **Control:** Tasks 2.1 through 2.4 require a finite source-to-consumer inspection,
  an explicit physical-residue proof boundary, focused existing evidence, and
  `DEFERRED-CODE-CHANGE` followed by a stop on any prohibited crossing.
- **Next owner:** A new explicit Stage 5 apply authorization is required. It must be
  followed by the apply workflow and cannot be inferred from planning completion, the
  product decision, or these validation results.
