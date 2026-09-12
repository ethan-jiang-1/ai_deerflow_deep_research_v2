## Context

See proposal.md — Why. The current composition vocabulary is split across three owners:

- `domain/lifecycle.py` `ImplementationMode` and `graph/implementation_map.py`
  `AdapterKind` define the closed runtime set `fixture | mixed | all_real`.
- Main-spec prose uses the undefined `full-fake` alias for the same all-fixture mode.
- `domain/lifecycle.py` names its rerun bound `MAX_FAKE_RERUN_GENERATIONS` even though it
  bounds real `refinement_round`/`generation` values.

`deep_research_harness/CONTEXT.md` defines neither `fixture` nor `full-fake`, so the
alias has no glossary owner. The project glossary is a domain-modeling artifact: it owns
definitions and `_Avoid_` distinctions, not runtime behavior.

## Goals / Non-Goals

**Goals:**

- Give the composition vocabulary one definition owner and one canonical spelling.
- Remove the live alias from normative requirement prose and the misleading token from
  the production symbol, provably without moving behavior.

**Non-Goals:**

- Renaming the `research-fake-cli-onboarding` capability (deferred; see Decision 3).
- Rewriting non-normative scenario labels or the retired machine literal `full_fake`.
- Migrating the bare per-node `fake` mode shorthand or the evaluation `AuthenticityLevel`
  taxonomy.

## Decisions

1. **Canonical term is `Fixture Composition`, defined in CONTEXT.md.** It names the
   closed set `fixture | mixed | all_real` and lists the composition alias under
   `_Avoid_`. Alternative: define the term only in a spec — rejected because `CONTEXT.md`
   is the existing vocabulary owner and the alias is currently ownerless.

2. **Spec migration is terminology-only and preserves scenario identity.** OpenSpec's
   archive step compares every current `#### Scenario:` name against the MODIFIED block
   and aborts if any is missing, so a scenario title is a stable identity, not prose.
   The migration therefore rewrites requirement statements and scenario bodies and
   renames requirement titles through `## RENAMED Requirements`, while leaving scenario
   headings unchanged. Alternative: REMOVED+ADDED to rename scenarios — rejected because
   OpenSpec rejects a requirement present in both sections. Consequence: a residual
   `Full-fake ...` appears only in preserved scenario headings; the follow-up enforcement
   change scopes its rule to non-`#### Scenario:` lines for this reason.

3. **The capability rename is deferred.** A same-change capability rename would require
   the delta capability to resolve to the renamed main-spec directory during apply while
   the plan-time requirement-ownership check compares delta capabilities against the
   registry's current capability name. Keeping the rename out of this program avoids that
   ordering conflict; the follow-up enforcement change performs it as a structural rename
   after the wording is already clean.

4. **`full_fake` (underscore) is retained as a machine literal.** It is the rejected
   legacy composition value exercised by validation, not a prose alias; renaming it would
   change a closed input the runtime deliberately refuses.

## Risks / Trade-offs

- A wording edit could be mistaken for a behavior change. Mitigation: no requirement ID,
  scenario set, route, bound, or typed contract changes; the full deterministic gate and
  the spec's own scenarios remain unchanged.
- Preserved `Full-fake ...` scenario headings leave a visible residue. This is an
  accepted OpenSpec identity constraint, documented in Decision 2, and excluded from the
  follow-up guard.
- The reworded `deep-research-agent-charter` entry-surface clause is the one place a
  wording decision approaches product content; it is limited to renaming the surface and
  does not add, remove, or reorder a required surface.
