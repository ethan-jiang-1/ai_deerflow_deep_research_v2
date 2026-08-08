# 04 - Three-Change System Program Decision

> Type: product/architecture decision record | Recorded: 2026-08-02
> Status: Changes 1 and 2 are archived and committed; Change 3's proposal contract
> and all OpenSpec artifacts are complete, ready for review or apply. Current progress is tracked in
> [`../policy-gate-injection-layer.md`](../policy-gate-injection-layer.md).

## Confirmed System Goal

The policy-gate injection layer is one coherent system, delivered through three
dependent OpenSpec changes rather than one oversized change or a V1-only effort:

| Sequence | Change | Responsibility | Authority boundary |
| --- | --- | --- | --- |
| 1 | `add-openspec-control-placement-policy` | External policy, conditional review record, minimal route wording, and deterministic proposal-shape checker | Checks declared structure only; grants no runtime, prompt, or semantic-review authority. |
| 2 | `add-openspec-operation-guidance` | `rules.tasks` obligation plus `operations.apply/archive.guidance` and the local integration probes | Guidance is advisory text; it neither executes commands nor blocks apply/archive. |
| 3 | `add-cross-session-cognitive-guardrails` | Caller-declared, Git-verified committed-range boundary; bounded review evidence; and a non-authoritative closeout record | It does not replace capability specs, deterministic owners, human judgment, or native archive. Concepts beyond this proposal contract require explicit design and evidence. |

The three changes remain ordered because they have different contracts, owners,
rollback points, and proof seams. Change 3's contract was refined by Change 2's
actual `missing-boundary` observation: it cannot infer selected-change coverage from
a shared worktree or claim enforcement from advisory guidance.

## Evidence Gates Are Refinement Gates

Each earlier change produces evidence needed to make the next proposal precise:

~~~text
1. policy + checker
       |  replay, counterexamples, first-use records
       v
2. operation guidance + local OpenSpec probes
       |  delivery, resume, diff-boundary, archive-side-effect evidence
       v
3. cross-session guardrail coordinator
~~~

This sequence is an implementation and acceptance discipline, not a deferral of
the end state. A failed probe must narrow or correct the next change's contract;
it must not be hidden by treating advisory guidance as enforcement or by silently
dropping the system goal.

## Non-Goals That Remain Fixed

- No phase creates runtime graph/state/route authority merely through policy,
  guidance, or review prose.
- No phase makes a model or checklist the automatic authority for cognitive
  quality.
- `openspec/guardrails/` is created only by change 3, with its actual contract
  and runner; it is not pre-created as an empty promise.
- The three changes remain separate OpenSpec units. Phase 1 must not smuggle in
  Phase 2 configuration or Phase 3 coordinator code.

## Confirmed Change 3 Proposal Contract

1. A closeout coverage claim requires an explicit selected-change boundary. Absent
   or invalid inputs yield record-only `missing-boundary`, never semantic clearance,
   task mutation, or archive action.
2. The caller or adapter declares the boundary; Git verifies repository identity,
   commits, ancestry, and the `base..head` diff. The coordinator does not infer
   ownership from a branch name, file list, or shared worktree.
3. Every attestation binds canonical `change_name`, repository identity,
   `base_commit`, and `head_commit`; it is valid only while `HEAD == head` and the
   worktree is clean.
4. Deterministic evidence covers one valid committed range and the missing-field,
   wrong-repository, non-ancestor, HEAD-drift, and dirty-worktree rejections.
5. Change 3 cannot wrap, replace, or block native archive. It may emit an auditable
   `review-required` or `inconclusive` record; actionable findings remain ordinary
   incomplete `tasks.md` work.

No chat decision substitutes for Change 3's proposal, specs, design, tasks, local
evidence, validation, archive, and commit.
