## Why

The `converge-fixture-vocabulary` change retired the live `full-fake` composition
alias and defined `Fixture Composition` in the glossary, but nothing prevents the alias
from being reintroduced: `ACTIVE_TERMINOLOGY_RULES` in `check_project_specs.py` catches
`remain fake`/`still fake`/`implementation_mode=full_fake` yet misses the dominant
hyphenated/space form. One live capability also still carries the retired `fake` token in
its own name. This change makes the vocabulary machine-enforced and finishes the rename.

## What Changes

- Add a `compositionAlias` rule to `ACTIVE_TERMINOLOGY_RULES` that flags `full-fake` and
  `full fake` (hyphen or space, case-insensitive) in the existing authority surfaces. It
  does not flag the retired machine literal `full_fake` (underscore) and it is exempted
  on `#### Scenario:` heading lines, whose titles OpenSpec preserves as stable identity.
- Fix the one remaining registry prose occurrence (`DPL-005`).
- Add a deterministic governance test that plants a matching alias and proves both the
  detection and the two exemptions.
- Rename the `research-fake-cli-onboarding` capability to
  `research-fixture-cli-onboarding`, updating the spec directory and title, the
  requirement registry capability ownership, and the two test references. Requirement
  IDs `FCO-001`/`FCO-002` and all behavior are unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This change tightens a project governance checker and renames a capability
directory; no observable behavior or requirement content changes, so `skip_specs: true`
is declared in `.openspec.yaml`.

## Impact

- `openspec/governance/check_project_specs.py` (new rule and scenario-heading exemption).
- `openspec/governance/req-registry.yaml` (capability rename and `DPL-005` prose).
- `openspec/specs/research-fake-cli-onboarding/` → `openspec/specs/research-fixture-cli-onboarding/`.
- `openspec/tests/governance/` (new rule test); `deep_research_harness/tests/assets/requirement_evidence.py`
  and `deep_research_harness/tests/contract/test_main_spec_requirement_sources.py`.
- `deerflow/` is neither modified nor source-browsed.

## Program Focus

- **Program outcome:** The canonical composition vocabulary has a deterministic guard
  with no current violations, and no live capability name carries the retired `fake`
  token.
- **Candidate / obligation budget:** EV-C01, EV-C02, EV-C03, EV-C04
- **Declared workstream order:** composition-terminology-guard, fixture-cli-capability
- **Program decision authority:** The project-governance owner approves only this frozen
  budget, order, and whole-program archive closure; it owns no runtime fact or behavior.
- **Shared archive invariant:** The guard reports zero violations on the current tree
  while flagging a planted alias; the retired `full_fake` literal and preserved
  `#### Scenario:` headings stay unflagged; the renamed capability resolves in the
  registry, spec tree, and tests; all gates stay green.
- **Program failure / recovery:** A failed workstream is repaired inside its declared
  scope or rolled back before archive; the program never partially archives and stays
  active for approved re-scope if both cannot close.
- **Split / expansion rule:** No behavior, requirement ID, runtime path, or DeerFlow
  boundary enters. The bare per-node `fake` shorthand, the `full_fake` literal, and the
  `AuthenticityLevel` taxonomy remain separate concerns.
- **Not in scope:** Tightening to bare `fake` or `full_fake`; scanning `CONTEXT.md` or
  `docs/` (the glossary intentionally lists the alias under `_Avoid_`); any behavior,
  requirement ID, route, or bound; `deerflow/`.

### Workstream Focus: composition-terminology-guard

- **Primary module / causal owner:** `openspec/governance/check_project_specs.py` — it
  owns the deterministic active-terminology guard.
- **Seam classification:** deterministic-guardrail — it enforces a closed vocabulary
  after the cognition-free migration is complete; it fabricates no prompt obligation.
- **Question:** How can the checker reject reintroduction of the undefined `full-fake`
  alias in authority surfaces while leaving the retired `full_fake` machine literal and
  OpenSpec-preserved `#### Scenario:` titles untouched?
- **Necessary adjacent/external contracts:** `openspec/governance/req-registry.yaml`:
  whether all scanned prose is clean; the existing authority-path list: whether the rule
  runs only where the alias is normative.
- **Evidence seam:** A governance test that plants `full-fake` in a scanned line and
  asserts detection, and asserts no violation for a `full_fake` literal or a
  `#### Scenario: Full-fake …` heading; plus the closeout gate returning zero current
  violations.
- **Not in scope:** Bare `fake`, `full_fake`, `CONTEXT.md`/`docs/`, adding a term
  registry, or changing any runtime rule.
- **Triggered review policies:** change-admission,agent-information-map
- **Candidate / obligation IDs:** EV-C01, EV-C02
- **Target / retirement:** Add the `compositionAlias` rule and its exemption; retire the
  residual registry alias prose.
- **Surface grade:** Project governance checker; it constrains documents, not runtime
  behavior.
- **Decision authority:** The governance checker owner decides the rule; authority
  specifications keep owning their own behavior.
- **Negative path / recovery:** A false positive on a legitimate retired literal or a
  scenario heading stops the rule; recovery narrows the rule or restores the prior
  checker before archive. No runtime behavior is changed to make the guard pass.

### Workstream Focus: fixture-cli-capability

- **Primary module / causal owner:** `openspec/specs/research-fixture-cli-onboarding/spec.md` —
  the renamed capability identity.
- **Seam classification:** wiring — a structural capability rename and reference sync;
  no requirement meaning, ID, or behavior changes.
- **Question:** Can the capability that names the credential-free fixture-graph CLI be
  renamed off the retired `fake` token while its requirement IDs and behavior stay
  identical?
- **Necessary adjacent/external contracts:** `openspec/governance/req-registry.yaml`:
  whether `FCO-001`/`FCO-002` ownership follows the new capability; the two harness test
  references: whether they resolve after the rename.
- **Evidence seam:** `check_project_reqs.py` and the root closeout gate, which prove the
  registry, spec tree, and references agree after the rename.
- **Not in scope:** Changing `FCO-001`/`FCO-002` content, any behavior, or any route.
- **Triggered review policies:** change-admission,local-context
- **Candidate / obligation IDs:** EV-C03, EV-C04
- **Target / retirement:** Rename the capability directory and title and sync the
  registry and test references; retire the `fake` token from the capability name.
- **Surface grade:** Project-governance capability identity with no third-party support
  promise; a clean rename is permitted.
- **Decision authority:** The governance owner decides the capability name; the owning
  requirements keep their IDs and meaning.
- **Negative path / recovery:** A missing reference or registry mismatch fails the
  requirement-consistency check; recovery completes the sync or restores the prior name
  before archive.
