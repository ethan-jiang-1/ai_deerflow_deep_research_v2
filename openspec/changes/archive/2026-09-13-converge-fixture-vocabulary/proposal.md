## Why

A coding-agent friendliness review found one live vocabulary conflict: the current
composition mode is spelled `fixture` in code (`ImplementationMode.FIXTURE`,
`AdapterKind.FIXTURE`) but `full-fake` in main-spec prose, while a production constant is
still named `MAX_FAKE_RERUN_GENERATIONS`. A reader cannot tell whether `full-fake` names
a second, fake implementation or the current all-fixture composition; the terms are
undefined in the glossary. This change converges the live composition vocabulary and
retires the misleading production symbol without changing behavior.

## What Changes

- Add a `Fixture Composition` glossary term to `deep_research_harness/CONTEXT.md` that
  defines the closed composition set `fixture | mixed | all_real` and lists `full-fake`
  (as a composition alias) under `_Avoid_`; extend the glossary contract test to require
  the new record.
- **Terminology-only spec migration:** replace the undefined `full-fake` prose alias with
  the canonical `fixture` in the affected main-spec requirement statements, scenario
  bodies, and `## Purpose` prose; rename the two requirement titles that embed the alias. Scenario headings are
  preserved because OpenSpec MODIFIED preservation treats a scenario title as a stable
  identity; a residual `Full-fake ...` heading is a label, not normative prose.
- Rebrand the retired no-graph demonstration from `full-fake/no-graph` to `no-graph` so
  the alias no longer denotes two different things.
- Rename the production constant `MAX_FAKE_RERUN_GENERATIONS` to
  `MAX_RERUN_GENERATIONS` and update its references and comments; no value, bound, route,
  or persisted fact changes.
- Update the living human docs and the production `builder.py` rerun-route comments that
  still carry the alias.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

Terminology only; no observable behavior, requirement ID, scenario set, route, or
typed contract changes.

- `bootstrap-node`: `full-fake` composition prose becomes `fixture`.
- `deep-research-agent-charter`: the entry-surface description names the fixture-graph
  demonstration rather than a `full fake` surface.
- `demo-pipeline`: the retired demonstration is named `no-graph`, and `full-fake`
  composition prose becomes `fixture`.
- `final-delivery-node`: `Full-fake` composition prose becomes `fixture`.
- `hitl2-node`: `Full-fake` composition prose becomes `fixture`.
- `readiness-node`: `Full-fake` composition prose becomes `fixture`.
- `rerun-node`: `full-fake` composition prose becomes `fixture`.
- `research-fake-cli-onboarding`: the retired simulation is named `no-graph`.
- `runtime-integration`: `full-fake` composition prose becomes `fixture`.
- `runtime-operations`: `full-fake` composition prose becomes `fixture`; one requirement
  title is renamed.
- `targeted-evidence-loop`: `Full-fake` composition prose becomes `fixture`.
- `topic-planning-node`: `full-fake` composition prose becomes `fixture`.
- `wave0-node`: `full-fake` composition prose becomes `fixture`.
- `wave1-node`: `Full-fake` composition prose becomes `fixture`.
- `wave2-synthesis-node`: `Full-fake` composition prose becomes `fixture`.

## Impact

- `deep_research_harness/CONTEXT.md` and its contract test
  `tests/contract/test_glossary_record_contract.py`.
- `deep_research_harness/docs/testing-and-evaluation.md`, `docs/regression-descent.md`,
  and `deep_research_harness/README.md` where the alias describes composition.
- `deep_research_harness/src/deerflow_deep_research/domain/lifecycle.py`,
  `domain/state.py`, `runtime/bundle_graph.py`, `graph/nodes/rerun/planner.py`,
  `graph/builder.py` (constant rename and comment clarity).
- Fifteen OpenSpec capability delta specs; no new requirement IDs.
- `deerflow/` is neither modified nor source-browsed.

## Program Focus

- **Program outcome:** The Harness has one canonical composition vocabulary — `fixture`,
  `mixed`, `all_real`, defined once in the glossary — with no live `full-fake` prose
  alias in authority surfaces and no `FAKE`-named production composition symbol.
- **Candidate / obligation budget:** FV-C01, FV-C02, FV-C03, FV-C04, FV-C05, FV-C06
- **Declared workstream order:** fixture-composition-language, fixture-rerun-identifier
- **Program decision authority:** The coding-agent-documentation vocabulary owner approves
  only this frozen budget, order, and whole-program archive closure; it owns no runtime
  fact, writer, route, or bound.
- **Shared archive invariant:** No live `full-fake`/`full fake` composition alias remains
  in the migrated authority surfaces except preserved `#### Scenario:` headings and the
  retired machine literal `full_fake`; `CONTEXT.md` defines `Fixture Composition`;
  `MAX_FAKE_RERUN_GENERATIONS` is gone with its numeric bound unchanged; all deterministic
  gates and the full `make verify` selection stay green.
- **Program failure / recovery:** A failed workstream is forward-repaired inside its
  declared writer scope, or that workstream is rolled back to its pre-change invariant
  before any archive. Neither workstream partially archives; if both cannot close, the
  program stays active for approved re-scope.
- **Split / expansion rule:** No new capability, code path, behavior, route, bound, or
  DeerFlow boundary enters this program. The deferred capability rename and the
  `AuthenticityLevel` taxonomy are separate follow-ups.
- **Not in scope:** Renaming the `research-fake-cli-onboarding` capability directory
  (deferred to the follow-up vocabulary-enforcement change); the retired machine literal
  `full_fake`; preserved `#### Scenario:` headings; the bare per-node `fake` mode shorthand;
  `AuthenticityLevel.FAKE_GRAPH`/`REAL_NODE_FAKE_CAPABILITIES`; test-double identifiers
  (`fake_models.py`, `fake_make`, the `fake.py` guard); any behavior, requirement ID,
  registry entry, or `deerflow/` change.

### Workstream Focus: fixture-composition-language

- **Primary module / causal owner:** `deep_research_harness/CONTEXT.md` — it owns the
  current product-term definitions and `_Avoid_` distinctions, not runtime behavior.
- **Seam classification:** wiring — it repairs the route from the canonical composition
  term to its existing code and spec owners; it creates no cognitive role, human decision,
  guardrail, or behavior.
- **Question:** How can the Harness present one canonical composition vocabulary while
  the spec prose, living docs, and glossary stop treating `full-fake` as an undefined
  second term?
- **Necessary adjacent/external contracts:** `domain/lifecycle.py` `ImplementationMode`
  and `graph/implementation_map.py` `AdapterKind`: they are the authoritative closed set
  the glossary must name; the migrated capability specs: whether each reword preserves
  the requirement's meaning and scenario set; `tests/contract/test_glossary_record_contract.py`:
  whether the new glossary record and `_Avoid_` boundary are mechanically covered.
- **Evidence seam:** The existing glossary contract test plus deterministic scans showing
  the canonical term is present and the live alias is absent from the migrated authority
  surfaces; the full `make verify` selection proves no behavior moved. No model or live
  claim is created.
- **Not in scope:** Any behavior, route, state, requirement ID, or scenario-set change;
  preserving literal `full_fake`; the `research-fake-cli-onboarding` capability rename.
- **Triggered review policies:** change-admission,agent-information-map,authority-and-projections
- **Candidate / obligation IDs:** FV-C01, FV-C02, FV-C03, FV-C04
- **Target / retirement:** Add the `Fixture Composition` glossary term; retire the live
  `full-fake`/`full fake` composition alias from the migrated requirement statements,
  scenario bodies, and living docs.
- **Surface grade:** Current human and AI-facing documentation vocabulary; glossary terms
  are current explanatory terms, while main-spec deltas converge pending wording.
- **Decision authority:** The product-record owner maintains glossary scope; each
  capability spec remains authoritative for its own requirement meaning.
- **Negative path / recovery:** A missing canonical term, a changed scenario set, or a
  reword that alters meaning stops the migration. Recovery restores the affected artifact
  or supplies the missing definition inside this workstream before archive; no behavior
  is changed to make the reword appear safe.

### Workstream Focus: fixture-rerun-identifier

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/domain/lifecycle.py` —
  it owns `MAX_FAKE_RERUN_GENERATIONS`, the production composition bound name.
- **Seam classification:** wiring — a pure identifier rename and reference sync; the
  numeric bound, its enforcement, and every route remain unchanged.
- **Question:** Can the production constant that bounds rerun generations be renamed so
  it no longer implies a fake implementation, while its value and enforcement stay
  identical?
- **Necessary adjacent/external contracts:** `domain/state.py`, `runtime/bundle_graph.py`,
  `graph/nodes/rerun/planner.py`: whether each import and check keeps the exact same
  bound; `openspec/specs/rerun-node/spec.md`: whether the normative reference to the
  constant is updated with the same meaning.
- **Evidence seam:** The existing state, rerun, and bundle-graph unit tests plus the
  deterministic `make verify` selection, which prove the same bound and routes after the
  rename.
- **Not in scope:** Changing the bound value, the rerun route set, refinement capacity,
  persisted generation fields, or any behavior.
- **Triggered review policies:** change-admission,local-context
- **Candidate / obligation IDs:** FV-C05, FV-C06
- **Target / retirement:** Rename the constant and every reference; retire the misleading
  `FAKE` token from the symbol name.
- **Surface grade:** Application-internal Python identifier with no third-party support
  promise; a clean rename is permitted.
- **Decision authority:** The domain lifecycle owner decides the identifier; the rerun
  planner and runtime graph retain their existing bounds and routes.
- **Negative path / recovery:** A missed reference fails import or the nearest deterministic
  test; recovery completes the reference sync or restores the prior symbol name before
  archive. No fallback alias is retained.
