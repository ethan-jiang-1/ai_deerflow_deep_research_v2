## Context

The Charter route already says to select every canonical policy whose trigger applies,
and the Focus Card/checker already accepts a comma-separated canonical policy list.
The policy-library index, DRC-001, OpenSpec authoring context, and one Focus Gate
sentence still use singular wording. See [proposal.md](proposal.md) for the motivating
alignment finding.

## Goals / Non-Goals

**Goals:**

- Give every contributor entry point the same trigger-based cardinality rule.
- Preserve one primary causal owner even when more than one review policy applies.
- Preserve the Charter and policy library as guidance-only, never runtime authority.
- Produce focused, reviewable evidence that current singular routing residue is gone.

**Non-Goals:**

- Changing the policy registry, triggers, Focus Card parser, or Agent Charter checker.
- Adding automatic semantic-policy evaluation, application behavior, or DeerFlow
  changes.

## Decisions

### Route every actually triggered canonical policy

The normative phrase will be: select every canonical policy whose route-table trigger
applies to the change. It is narrower and more testable than "all relevant policies":
the Charter route table is the canonical source of triggers, and a contributor does not
read unrelated policies by default.

Alternative considered: say only "select multiple policies when needed." This leaves
the criterion subjective and preserves the possibility of omitting an applicable
policy.

### Keep policy selection separate from causal ownership and runtime authority

The updated DRC-001 requirement and scenario will say both that a change retains one
primary causal owner and that policy selection remains guidance-only. The existing
Focus Card and Charter already establish those boundaries, so no parser, checker, or
runtime change is necessary.

Alternative considered: enforce multi-policy selection in the checker. The checker
cannot determine a change's semantic triggers without creating the prohibited
semantic-policy automation, and the current gap is contradictory authority prose rather
than an observed parser failure.

### Change the four current entry-point occurrences as one bounded set

Apply will align only these current authority surfaces:

1. `openspec/policies/README.md` policy-library introduction;
2. `openspec/config.yaml` local-change authoring route;
3. `deep_research_harness/AGENTS.md` Focus Gate review-record sentence; and
4. DRC-001 through the `deep-research-agent-charter` main-spec delta.

`openspec/agent-charter/README.md` already states the desired route and is evidence,
not an edit target. Archived artifacts retain historical wording and are excluded.

## Risks / Trade-offs

- [An author interprets "every" as "read every policy"] -> Anchor it to policies
  whose route-table trigger applies, and retain the existing default-context boundary.
- [Multiple selected policies are misread as multiple feature owners] -> State the
  distinct one-primary-owner rule in DRC-001 and retain the guidance-only boundary.
- [A broad wording search edits valid historical prose] -> Apply only the four
  enumerated current targets; use a search only as evidence, with archives excluded.
- [A document-only change claims mechanical enforcement] -> Keep the existing checker
  unchanged and record that it validates Focus Card shape, not semantic applicability.

## Migration Plan

1. Re-read the active change, the four target files, and the canonical Charter route
   before any edit; preserve unrelated worktree changes.
2. Make the four bounded documentation/spec edits, then run focused residual-wording
   checks, strict change validation, doctor, and the existing Charter checker.
3. Inspect the delta-to-main-spec result after sync/archive; update the N-002 backlog
   card and Stage 7 ledger only after the approved change is applied, archived, and
   re-audited.
4. Roll back by reverting only this change's bounded prose if verification finds a
   contradiction. No data, runtime migration, or compatibility rollback exists.
