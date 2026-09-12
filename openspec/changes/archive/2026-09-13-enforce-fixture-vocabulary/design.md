## Context

See proposal.md — Why. `converge-fixture-vocabulary` migrated the live alias and defined
`Fixture Composition`; this change adds the guard that keeps it migrated. The current
guard is `ACTIVE_TERMINOLOGY_RULES` in `openspec/governance/check_project_specs.py`,
applied line by line over the main specs, `req-registry.yaml`, `AGENTS.md`, `README.md`,
the public controller `SKILL.md`, and the agent `SOUL.md`.

Two properties constrain the design: the retired machine literal `full_fake` (underscore)
is a closed rejected input that must stay; and OpenSpec archive preservation keeps every
`#### Scenario:` title verbatim, so a few `Full-fake …` headings remain as stable labels.

## Goals / Non-Goals

**Goals:**

- Detect reintroduction of the `full-fake`/`full fake` composition alias in the authority
  surfaces with zero false positives on `full_fake` and preserved scenario headings.

**Non-Goals:**

- Policing bare `fake`, `all-fake`, the `full_fake` literal, or the evaluation
  `AuthenticityLevel` taxonomy.
- Scanning `CONTEXT.md` or `docs/`, where the glossary intentionally names the alias.

## Decisions

1. **Rule is `\bfull[- ]fake\b`, case-insensitive.** The hyphen/space forms are the prose
   alias; the underscore form is the machine literal, so it is not matched. Alternative:
   `full[_- ]fake` — rejected because it would flag the retained rejected value.
2. **Scenario-heading lines are exempt from this rule.** OpenSpec treats a scenario title
   as a stable identity, so preserved `#### Scenario: Full-fake …` headings are labels,
   not normative prose. The exemption is scoped to the `compositionAlias` rule so the
   existing rules keep their reach.
3. **Authority paths are unchanged.** `CONTEXT.md` deliberately lists `full-fake` under
   `_Avoid_`; adding it (or `docs/`) would create a false positive. The glossary remains
   the definition owner, not a guarded surface.
4. **The capability rename is structural.** `research-fake-cli-onboarding` →
   `research-fixture-cli-onboarding` changes a directory and its title plus registry and
   test references; requirement IDs and behavior are untouched, so `skip_specs: true`
   applies.

## Risks / Trade-offs

- The scenario-heading exemption leaves preserved `Full-fake …` titles unguarded. This is
  an accepted OpenSpec identity constraint, not a loophole for new prose in a statement.
- The guard is document-scoped; a reviewer could see it as narrow. It is intentionally
  scoped to the surfaces where the alias was normative.
