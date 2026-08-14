## Context

The active charter checker accepts a single `## Change Focus` in every active
proposal and validates selected review records at proposal scope. The convergence
plan's program changes need several independently owned workstreams, but only after
this ordinary bootstrap archives. See `proposal.md` for motivation and the delta for
the admission behavior.

The admission grammar is a declared cross-boundary contributor interface. Existing
ordinary proposals are its compatibility surface. Program proposals introduce no
runtime state, writer, checkpoint, route, or product authority.

## Goals / Non-Goals

**Goals:**

- Keep the ordinary single-`Change Focus` grammar and its policy-review behavior
  fully compatible.
- Add one opt-in program form that mechanically closes its internal workstream and
  Candidate/obligation registration before implementation begins.
- Make each program workstream independently attributable to an owner, target and
  retirement, surface grade, decision authority, negative path/recovery, evidence,
  exclusions, and policy routing.
- Provide deterministic, planted-invalid evidence for every grammar closure rule.

**Non-Goals:**

- Authorizing a program merely because a static checker accepts its grammar.
- Letting a program own runtime facts, code, shared helpers, or another workstream's
  semantic decision.
- Implementing a Candidate, changing DeerFlow, or inferring consumer/data cutover
  from a checker result.

## Decisions

### Two exclusive proposal forms

The checker will classify each active proposal before validating fields:

1. **Ordinary:** exactly one `## Change Focus`, with no Program Focus or Workstream
   Focus heading. Existing Focus Card and top-level conditional review rules stay
   unchanged.
2. **Program:** exactly one `## Program Focus`, no Change Focus, and at least two
   registered Workstream Focus records. Program fields are `Program outcome`,
   `Candidate / obligation budget`, `Declared workstream order`, `Program decision
   authority`, `Shared archive invariant`, `Program failure / recovery`, `Split /
   expansion rule`, and `Not in scope`.

The explicit mode boundary makes an ordinary proposal's established contract
compatible while preventing a program from hiding an extra owner in free text.
Requiring two workstreams and distinct owners prevents the form from becoming a
convenient alternative spelling for a normal single-owner change.

### Program grammar freezes reviewable closure facts

`Declared workstream order` is a comma-separated list of kebab-case stable IDs. A
matching `### Workstream Focus: <stable-id>` must exist for every ID, with no extras.
Each record has the existing Focus Card fields plus `Candidate / obligation IDs`,
`Target / retirement`, `Surface grade`, `Decision authority`, and `Negative path /
recovery`. Candidate/obligation lists are comma-separated opaque identifiers:
the checker verifies non-empty uniqueness and set equality, while reviewers judge
whether the identifiers, owners, retirement, and surface grades are semantically
correct for the named program.

This is deliberately a closure check, not a second plan authority. The remediation
map remains the source for whether a change is allowed to use program form and what
its complete budget is. Apply/archive review compares the actual proposal, tasks,
diff, and evidence to that source; the checker only proves that the proposal does
not contradict itself.

### Workstream-scoped policy records

An ordinary proposal retains the current level-two conditional review headings. In a
program, each Workstream Focus owns its selected policies and any required review
record uses the same table shape under its exact level-four canonical heading (for
example, `#### Control Placement Review`) beneath that workstream. The validator
parses the record inside that workstream rather than accepting one program-wide or
sibling-workstream table. This keeps policy routing and review evidence attributable
to the owner that can answer the decision, without inventing a program-wide semantic
reviewer.

### Checker architecture and errors

The implementation will factor the current focus-card parser into reusable section,
field, list, classification, and selected-policy validators. Ordinary validation will
call the existing shapes. Program validation will parse Program Focus, enumerate the
workstream sections, validate required values, detect duplicate IDs and owners, then
compare workstream order and Candidate/obligation union to the declared lists.

The checker will emit stable `program.*` failures for invalid mode, missing program
or workstream fields, invalid/duplicate IDs or owners, unregistered workstreams, and
budget-union mismatch. It will not evaluate prose, remediation-map semantics,
runtime authority, or implementation diff scope.

The same checker will retain concise program-route anchors in the authoring sources
it already governs: `openspec/config.yaml`, local-context, change-admission, and the
application Focus Gate. Their fixtures will prove that a missing anchor fails, while
the checker continues to avoid judging the semantic truth of program prose.

### Recovery and archive boundary

`Program failure / recovery` records the only program-level control: an evidence or
cutover failure is either repaired within the frozen scope, or the failed workstream
and its dependents are rolled back to the pre-change invariant. If neither closes,
the change remains active and returns to the plan owner for approved re-scope,
whole-program rollback, or one-in/one-out reordering. No workstream can archive on
its own and completed independent workstreams are not rolled back without a stated
dependency.

This is a proposal/closure lifecycle, not automatic runtime recovery. The program
decision authority approves scope, sequencing, and archive admission only; each
workstream retains the decision authority for its own product and compatibility
contract.

## Risks / Trade-offs

- [A permissive parser admits an undeclared scope expansion] -> Compare exact sets
  for stable IDs and Candidate/obligation IDs, and retain a planted fixture for each
  mismatch direction and duplicate.
- [A stricter parser breaks existing ordinary proposals] -> Keep ordinary parsing as
  an explicit branch and run its full existing fixture set unchanged.
- [Program form becomes a parallel architecture owner] -> State the non-authority
  boundary in the policy/config/guides, require per-workstream decision authority,
  and keep semantic scope review outside the checker.
- [A failed workstream is silently deferred or partially archived] -> Require the
  frozen recovery and archive fields in Program Focus; apply/archive review verifies
  the actual tasks, evidence, dependencies, and disposition.
- [Guide text becomes a handbook] -> Add only short routing language and preserve
  the existing information-map line budgets.

## Migration Plan

1. Add tests that demonstrate the current checker accepts an ordinary Focus Card and
   rejects malformed program fixtures before implementation changes the parser.
2. Add the exclusive grammar and program validation, then update config, local
   context, change-admission, and the application Focus Gate with concise routing
   language.
3. Run focused charter tests, repository governance checks, strict validation, and
   the deterministic verification gate.
4. Archive this ordinary bootstrap only after the ordinary compatibility path and
   program positive/negative fixtures pass. Later program changes may then use the
   new form, subject to the remediation map and their own apply/archive review.

Rollback is a normal source reversion of this governance-only change; no persisted
or runtime data migration is involved. A program proposal found invalid before 00
archives remains rejected and does not create an active implementation right.
