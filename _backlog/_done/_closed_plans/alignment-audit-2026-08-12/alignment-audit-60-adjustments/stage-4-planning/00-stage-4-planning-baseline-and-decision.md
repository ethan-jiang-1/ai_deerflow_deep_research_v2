# Stage 4 Planning - A-003 Rubric / Runner Authority

> Change: `reconcile-evaluation-rubric-authority`
> Date: 2026-08-13
> Status: **PLANNING COMPLETE - APPLY NOT AUTHORIZED**

## Authorization And Boundary

The user authorized the progressive plan to move forward after the Stage 3 re-audit.
Under the OpenSpec proposal workflow, that authorizes creation and review of planning
artifacts only. It does not authorize application code, tests, typed contracts,
fixtures, prompts, current main specs, `CONTEXT.md`, ADRs, `openspec/config.yaml`,
sync, archive, commit, or any DeerFlow edit/source inspection.

The planning scope is only A-003: reconcile the mutually incompatible CES, EVH, and
HITL1 required behavior for Rubric data at cognitive-program admission. A-004 and
N-002 remain separate, registered follow-ups.

## Baseline

| Fact | Observation | Evidence boundary |
| --- | --- | --- |
| Last committed Stage 2 state | `09a2e3b7525d65e9c0e56d93c20735727be31e04` (`docs: retire stale context concepts`) | The Stage 3 record is the fresh post-cleanup baseline; it is currently uncommitted audit evidence, not a change to current authority. |
| Stage 3 conclusion | A-003 remains a P1 conflict between CES's unqualified non-execution-input language and EVH/current admission's required Rubric criterion validation. | The conclusion is cited from `stage-3-reaudit/02-current-authority-conflicts-and-evidence.md`; this planning record does not make a new runtime claim. |
| User product decision | Option A: Rubric identity and criterion IDs are deterministic case-control-integrity metadata; content and quality judgment stay review-only. | The decision predates this plan and is recorded in `alignment-audit-60-15-a003a-criterion-ids-metadata.md`. |
| Selected OpenSpec scope | CES, EVH, and HITL1 deltas only. | An active planning change now exists at `openspec/changes/reconcile-evaluation-rubric-authority/`; it is not applied or archived. |
| DeerFlow boundary | Gitlink is still observed only through Git metadata; its source is out of scope. | This planning work neither modifies nor source-browses `deerflow/`. A fresh apply-time gitlink/worktree check remains mandatory. |

## Adjustment A-003

- **Status:** proposed; product decision confirmed; specification apply not authorized.
- **Authority owner:** `cognitive-evaluation-suite` owns the execution-input and Runner
  contract. `evaluation-hardening` owns Wave0/Wave1/Wave2 scenario metadata and
  `hitl1-node` owns the equivalent HITL1 requirement. The deterministic admission
  mechanism is conformance evidence, not an authority that can choose the requirement.
- **Affected paths:** Proposed delta paths only:
  `openspec/changes/reconcile-evaluation-rubric-authority/specs/cognitive-evaluation-suite/spec.md`,
  `openspec/changes/reconcile-evaluation-rubric-authority/specs/evaluation-hardening/spec.md`,
  and `openspec/changes/reconcile-evaluation-rubric-authority/specs/hitl1-node/spec.md`.
  Planning artifacts are also affected. No current authority or frozen path is in scope.
- **Before:** CES says a Case-linked Rubric SHALL NOT be an execution input. EVH calls
  for cognitive-program rubric criteria and admission rejection for invalid Rubric data;
  current local admission parses the Rubric JSON and compares criterion IDs. The
  unqualified CES sentence and that deterministic admission requirement cannot both be
  the current required contract.
- **After:** Required behavior distinguishes five facts. Admission may compare the
  selected Case's declared Rubric identity/version and unique criterion-ID set before
  subject construction. Rubric prose, weights, thresholds, evaluator guidance, and all
  quality dispositions remain absent from subject/model-facing execution input,
  execution output, and Runner completion status. Review remains the only cognitive
  quality authority.
- **Reason and evidence:** The Stage 3 conflict record identifies the mutually
  incompatible main-spec wording and `runtime/evaluation/controls.py:80-113` behavior.
  The selected Option A is an independent product decision, not a code-derived one.
- **Main risk:** The word "metadata" might later be used as an unconstrained exception
  that lets quality semantics enter evaluation execution.
- **Possible side effects:** Readers and future implementers must maintain a more
  precise five-way distinction; a real subject/model handoff may expose existing
  Rubric content crossing that no-code alignment cannot repair; already-written
  glossary/ADR wording can remain temporarily out of sync until Stage 6.
- **Risk controls / stop condition:** Enumerate the allowed admission facts and
  prohibited content/judgment facts in all three deltas; preserve the Runner's two-status
  contract; inspect the actual admission-to-subject/model handoff at apply; stop and
  record `DEFERRED-CODE-CHANGE` instead of editing frozen paths if the handoff crosses
  the boundary. Do not sync, archive, or propagate terminology without separate
  authorization.
- **Verification before apply:** Re-read the accepted Option A record, Stage 3 evidence,
  proposal/design/tasks, both owning main specs, the local admission seam, and the
  narrowest tests. Re-establish a fresh HEAD/worktree/active-change/gitlink baseline.
- **Verification after apply:** Prove malformed identity/criterion-ID admission is
  rejected before subject construction; inspect the real handoff for absence of
  prohibited Rubric content and Runner quality semantics; run required OpenSpec and
  deterministic gates, with their proof limits recorded.
- **Observed side effects:** None observed. This statement is limited to planning
  artifacts and Stage 3 evidence: no current authority, code, test, case, prompt, or
  DeerFlow path has been changed by Stage 4 planning.
- **Remaining mismatch / follow-up owner:** A-003 stays open until separately
  authorized apply, conformance inspection, sync, and archive complete. Stage 6 owns
  subsequent `CONTEXT.md`/ADR terminology synchronization. Any found handoff violation
  is a separately authorized code-change candidate, not work for this alignment change.
- **Authorization and date:** Product decision confirmed 2026-08-12; Stage 4 planning
  authorized 2026-08-13; apply authorization not granted.

## Planning Risk Review

| Potential effect of planning | Why it matters | Control | Current observation |
| --- | --- | --- | --- |
| The delta could quietly declare more than Option A permits. | It would make a quality Rubric an execution authority. | Compare every delta clause with the five-part boundary and the rejected Option B record. | Proposal and deltas list only identity/version and unique IDs as admission facts. |
| Current code could be treated as proof that no model sees Rubric content. | The existing parser test does not necessarily observe the whole subject/model handoff. | Require direct handoff inspection at apply and a defer stop condition. | Not yet inspected for apply conformance; no claim is made. |
| Stage 4 could prematurely rewrite terminology surfaces. | That would create duplicate behavior authority while A-004 remains unresolved. | Keep CONTEXT/ADR work out of the delta and reserve it for Stage 6. | No terminology surface is edited. |
| The active planning change could be mistaken for an applied specification. | That would hide the still-open A-003 mismatch. | Keep all execution tasks unchecked and state planning-only status in the progressive ledger. | Change is active, unarchived, and not synced. |

## Next Gate

The proposal, CES/EVH/HITL1 deltas, design, and 21-task execution checklist have been
created and validated. See
`01-stage-4-planning-validation.md` for the validation results, their proof boundaries,
and the planning correction that admitted the HITL1 owner. Only a new, explicit Stage 4
apply authorization may begin `tasks.md`; it must not be inferred from this planning
record or from the prior product decision.
