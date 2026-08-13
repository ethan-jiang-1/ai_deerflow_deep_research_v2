# Stage 4 Planning Validation - A-003 Rubric / Runner Authority

> Change: `reconcile-evaluation-rubric-authority`
> Date: 2026-08-13
> Status: **PLANNING COMPLETE - APPLY NOT AUTHORIZED**

## Artifacts Reviewed

| Artifact | Result | Review conclusion |
| --- | --- | --- |
| `proposal.md` | complete | Defines the selected Option A boundary, a valid Focus Card, Control Placement Review, no-code scope, A-004/N-002 exclusions, and three capability owners. |
| CES delta | complete | Replaces the unqualified "Rubric is not an execution input" statement with the five-part boundary and preserves two Runner statuses plus review-only cognitive verdicts. |
| EVH delta | complete | Applies criterion-ID control-metadata wording to the Wave0, Wave1, and Wave2 cognitive-program families without changing their other closed-corpus limits. |
| HITL1 delta | complete | Applies the same criterion-ID boundary to the existing HITL1 cognitive-program requirement in its actual owner, `hitl1-node`. |
| `design.md` | complete | Defines the one admission evaluator, the handoff inspection requirement, the `DEFERRED-CODE-CHANGE` stop condition, terminology deferral, and excluded conflicts. |
| `tasks.md` | complete | Contains 21 unchecked, dependency-ordered tasks. It separates apply and archive authorization, requires plan/closeout control-placement reviews, and does not authorize code work. |

## Planning Correction Observed

The first planning pass named CES and EVH but did not include the owner of the HITL1
cognitive-program requirement. Review of the current authorities found that
`openspec/specs/hitl1-node/spec.md` owns the HITL1 corpus and its rubric-criteria
requirement, while EVH owns only the Wave0/Wave1/Wave2 requirements.

This was a planning-scope correction, not a behavior or code change. The proposal,
design, task list, and A-003 record now name `hitl1-node`; a complete delta for its
existing requirement was added. This removes a concrete risk of synchronizing three
families while leaving the fourth subject of the same admission evaluator ambiguous.

## Validation

| Check | Result | Proven scope / limit |
| --- | --- | --- |
| `openspec status --change reconcile-evaluation-rubric-authority --json` | passed; 4/4 artifacts complete | The planning artifact graph is complete. This does not authorize or perform apply. |
| `openspec validate reconcile-evaluation-rubric-authority --strict` | passed | Delta structure and internal OpenSpec consistency, not runtime/spec conformance. |
| `openspec doctor --json` | healthy | Local OpenSpec root health only. |
| `python3 openspec/governance/check_agent_charter.py` | passed | Focus Card and selected-policy governance shape only; it does not assess the semantic decision. |
| `git diff --check` | passed | No whitespace error in the current planning/audit diff. |
| Manual planning review | passed | The three deltas use the same five-part boundary; all four cognitive-program families have an owning requirement; apply/archive and A-004/N-002 boundaries remain explicit. |

No runtime test was run in this planning-only stage. The task list reserves focused
admission/Runner evidence and `UV_OFFLINE=1 make verify` for a separately authorized
apply. A green planning validation does not prove that no prohibited Rubric data crosses
the actual Case-to-subject-to-model handoff.

## Final Planning Effect And Risk Status

- **Content adjusted:** Only OpenSpec planning artifacts, this Stage 4 evidence, and
  the progressive checkbox ledger were created or updated. No main spec is synced.
- **Observed side effects:** None observed outside planning scope. The active change is
  intentionally visible and unarchived; it must not be interpreted as applied current
  authority.
- **Open risk:** Current local fixtures may retain criterion IDs through a subject
  boundary, and the planning review has not evaluated whether a consumer exposes those
  IDs or any prohibited Rubric content to a model. This is deliberately unresolved
  conformance work, not a claim that current code satisfies the new requirement.
- **Control:** Task 2.1 requires a finite source-to-consumer handoff table. If the
  actual path gives Rubric content or cognitive quality semantics execution authority,
  task 2.3 requires `DEFERRED-CODE-CHANGE` and prohibits code edits under this change.
- **Next owner:** A new, explicit Stage 4 apply authorization is required. It must be
  followed by the apply workflow; it cannot be inferred from this planning completion,
  the selected product decision, or a passing validation command.
