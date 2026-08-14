## Why

The retained no-graph full-fake path can create a Bundle whose state reads as
`all_real`, and several legacy readers or convenience exports leave the supported
run-input contract ambiguous. The authorized cutover makes zero-credential proof
graph-backed, makes every supported composition explicit, and rejects unregistered
old or external inputs rather than manufacturing stronger provenance or indefinite
compatibility support.

## What Changes

- **BREAKING (operator demo surface):** replace the zero-credential full-fake CLI/TUI
  presentations with the existing fixed fixture-graph proof route. Retire
  `DemoLifecycleTransport.bind_full_fake()`, the `full_fake` implementation mode, and
  their Makefile/README/demo-TUI routes; no separately named no-graph simulator is
  retained.
- **BREAKING (application-internal Python):** remove
  `ResearchGraphRecipe.create()` and `parse_profile_response()`. The root package
  remains fixed to the existing all-real public tool; the named module paths receive
  no third-party compatibility promise or alias.
- Make Bundle-local State require an explicit supported composition mode. Missing,
  `full_fake`, unknown, or otherwise unregistered retained mode input is rejected
  before lifecycle/review projection and is neither written, backfilled, nor upgraded
  to `all_real`.
- Make the source-controlled current profile/proposal schema matrix the only
  supported input scope. Retire duplicate profile helpers and migrate evaluation/test
  consumers to the canonical parse result; unregistered old or external
  profile/proposal/checkpoint input is rejected before it can produce profile,
  proposal, comparison, language, or lifecycle facts.
- Preserve explicit fixture/mixed composition, production all-real construction,
  fixture source isolation, current refinement compatibility, and all existing
  fail-closed negative guards. Emergency rollback may restore an old reader only; it
  must not rewrite a rejected payload. Reintroducing support requires a later change
  with an inventory, notice, migration/retention decision, and removal trigger.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `demo-pipeline`: the supported credential-free demo is fixture-graph execution and
  its retained Bundle mode is truthful; no full-fake presentation remains.
- `research-demo-tui`: the credential-free TUI path becomes graph-backed fixture
  proof rather than a no-graph fake lifecycle.
- `research-fake-cli-onboarding`: the credential-free CLI remains a paste-safe,
  non-product Bundle projection while its only execution route becomes fixture graph.
- `fixture-source-isolation`: fixture composition remains explicit and becomes the
  only credential-free demo composition route without entering production authority.
- `research-graph-lifecycle`: supported Bundle State composition is explicit and
  closed; legacy or unregistered mode inputs fail closed rather than defaulting to
  all-real.
- `hitl1-node`: profile/proposal checkpoint and participant input consumption uses
  the approved current schema matrix and rejects unsupported legacy/external input
  before state mutation or graph continuation.
- `human-interaction-contract`: canonical profile parsing remains a bounded semantic
  candidate path, with no convenience wrapper or old-input inference creating a
  proposal/control/lifecycle fact.

## Impact

- Application code, deterministic tests, Make targets, and current documentation in
  `deep_research_harness/`, including the demo composition boundary, Bundle State
  reader/writer, recipe factories, profile parser, and HITL1 input readers.
- The seven listed OpenSpec capability deltas, requirement/evidence references, and
  focused deterministic evidence; evaluation changes are limited to its existing
  test consumer and do not alter evaluation runtime, review, or quality semantics.
- Existing explicit fixture/mixed recipes and the fixed all-real public tool remain
  supported. There is no new mode selector, supported external Python route, retained
  reader, runtime provider change, root export change, external data migration, or
  DeerFlow modification/source browsing.

## Program Focus

- **Program outcome:** Every admitted run input produces an explicit, truthful, and
  version-defined composition/profile/proposal fact, while unauthorized old or
  external inputs fail before they create, alter, or strengthen a current fact.
- **Candidate / obligation budget:** FM-C01, FM-C02, FM-C04, EC-C06, PC-C01, PC-C02, RC-C03, EV-C06, FM-C03, PC-C05, RC-C05
- **Declared workstream order:** composition-mode, profile-proposal
- **Program decision authority:** The post-migration convergence plan owner approves
  only this frozen budget, order, and whole-program archive closure. It owns no
  runtime fact, State write, profile interpretation, or compatibility decision.
- **Shared archive invariant:** Zero-credential execution reaches the explicit
  fixture graph; all supported State carries `fixture`, `mixed`, or `all_real` from
  its recipe; canonical profile/proposal parsing is the sole supported reader path;
  rejected old/external inputs produce no write, backfill, provenance upgrade, or
  research-completed result.
- **Program failure / recovery:** A workstream failure is forward-repaired only by its
  declared owner, or it and dependent later work is rolled back to the pre-change
  invariant. Emergency rollback may restore a reader but cannot rewrite a payload.
  If neither repair nor rollback closes the frozen scope, the program remains active
  for approved plan-level re-scope or whole-program rollback; no workstream archives
  independently.
- **Split / expansion rule:** No new Candidate, simulator, external Python support,
  retained-data migration, provider/lifecycle feature, root export, or DeerFlow
  boundary enters this program. A request to support any rejected input returns to
  the remediation map and requires a separately approved change.
- **Not in scope:** Changes to the all-real public tool, graph topology, node model or
  tool policy, provider/checkpoint storage, current refinement facts, evaluation
  runtime or Review semantics, external retained-data migration, or `deerflow/`.

### Workstream Focus: composition-mode

- **Primary module / causal owner:** `runtime/bundle_control.py` start admission; it
  owns the authoritative initial Bundle State write and therefore cannot infer a
  graph composition that was not supplied by the trusted executor.
- **Seam classification:** deterministic-guardrail because explicit recipe mode and
  State validation preserve lifecycle provenance while demo adapters remain only
  presentation/composition callers.
- **Question:** How can credential-free proof use the existing fixture graph and how
  can Bundle State accept only explicit supported composition without expanding a
  demo/recipe module into a third-party Python contract?
- **Necessary adjacent/external contracts:** `scripts/_demo_core.py` and demo entry
  points answer which zero-credential route binds a trusted executor;
  `runtime/research.py` answers which all-real constructor is retained;
  `domain/state.py` answers State parsing/writing and persisted-mode denial;
  `fixture-source-isolation` answers fixture catalog authority; the root tool answers
  that production composition stays all-real and unselectable.
- **Evidence seam:** Focused demo-transport, recipe/topology, Bundle State round-trip,
  state-reader negative, and root-tool composition tests; planted no-executor,
  missing-mode, old-mode, and unknown-mode inputs prove no completion/write/provenance
  upgrade path.
- **Not in scope:** Inventing a simulator or user-selectable mode, migrating
  private/external retained Bundles, changing graph routes or lifecycle actions,
  exposing `ResearchGraphRecipe` from the root package, or changing fixture source
  package isolation.
- **Triggered review policies:** change-admission, authority-and-projections, participant-outcomes, control-and-recovery, workflow-outcome-review, control-placement
- **Candidate / obligation IDs:** FM-C01, FM-C02, FM-C04, EC-C06, FM-C03, RC-C05
- **Target / retirement:** Fixture `ResearchGraphRecipe` plus `BundleGraphExecutor`
  own zero-credential graph proof; explicit recipe-derived State modes are
  `fixture`/`mixed`/`all_real`; retire `bind_full_fake`, `FULL_FAKE`, missing-mode
  defaulting, and `ResearchGraphRecipe.create()`.
- **Surface grade:** Operator demo command and persisted Bundle State are
  cross-boundary/persisted contracts; the recipe constructor is application-internal
  with authorized clean cutover. Old/external data is explicitly unsupported, not
  inferred absent.
- **Decision authority:** Product Owner owns the fixture-graph cutover; runtime owner
  owns State admission and writer semantics; Python Support Owner owns the clean
  cutover of the constructor. The program authority owns none of these facts.
- **Negative path / recovery:** Absent executor, missing/old/unknown mode, and an old
  constructor import fail without fallback, State write, or completed-research claim.
  Emergency recovery restores the pre-cutover reader as a unit; accepted State is
  never silently rewritten and future support needs a new decision.

#### Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Credential-free run composition | None; an operator cannot select a lifecycle mode | The named demo runtime constructs the fixture recipe/executor; `BundleControl` writes the executor's mode | non-bypassable | A no-graph transport cannot claim all-real/completed research; the legal path is the named fixture-graph command | Reuses fixture catalog/executor; removes no-graph fallback | Demo transport and Bundle State tests with a missing executor |
| Persisted composition provenance | None; a retained payload cannot choose a stronger meaning | `BundleLocalState.from_dict()` validates the explicit enum before lifecycle/review consumers | non-bypassable | Missing, `full_fake`, and unknown modes cause no read projection or write; rollback only restores the reader | Removes defaulting and full-fake enum branch | State decode/reload and no-write negative tests |
| Recipe constructor compatibility | None | `ResearchGraphRecipe.all_real()` is the sole application-internal production constructor | non-bypassable | No alias or third-party fallback remains; legal migration target is `all_real()` | Removes duplicate constructor surface | Signature/import-absence and fixed-public-composition tests |

#### Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Fixture route lacks its required executor/catalog | Demo composition boundary before lifecycle dispatch | Demo runtime has no fallback; repair configuration/source before retry | Bounded startup failure, never completed research | Start the named fixture-graph route with its prepared fixture source | Demo transport/recipe tests prove no `BundleControl` fallback |
| Retained mode is missing, `full_fake`, or unknown | Bundle-local State decoder | Runtime owner may restore the old reader only in an emergency rollback; no payload rewrite | Input rejected before projection or mutation | Start/inspect only a supported explicit-mode Bundle, or obtain a later support change | State decode/reload/no-write tests |
| Retired constructor is imported | Python import/call boundary | No compatibility recovery in this change | Import/attribute failure without alternate constructor | Migrate caller to `all_real()` | Consumer inventory and removed-surface tests |

### Workstream Focus: profile-proposal

- **Primary module / causal owner:** `domain/profile.py` canonical parsing contract;
  it turns raw semantic input into a bounded profile candidate and does not itself
  write proposal, checkpoint, or lifecycle state.
- **Seam classification:** human-decision because profile/proposal text is a bounded
  human semantic input whose graph/HITL1 owner alone may accept it into current State.
- **Question:** How can profile/proposal/checkpoint readers use one current,
  source-controlled schema matrix and canonical parse result while rejecting
  unsupported external/legacy inputs without inventing a profile, proposal,
  comparison, language, or graph continuation?
- **Necessary adjacent/external contracts:** HITL1 node/state writers answer when a
  parsed candidate becomes a checkpointed proposal; the human-interaction contract
  answers visible recovery/control preservation; evaluation tests answer their
  convenience-consumer migration only; Bundle State/checkpoint readers answer the
  approved input matrix and no-write rejection path; Python Support Owner's decision
  answers removal of the exported wrapper.
- **Evidence seam:** Direct parser/result tests plus HITL1/checkpoint read-write-reload
  tests prove current input round-trips, while planted absent-schema, legacy-version,
  alias, malformed, and external-shaped payloads fail before profile/proposal write,
  visible control, or graph continuation.
- **Not in scope:** Changing profile vocabulary, human controls, graph routes,
  semantic-provider quality, external producer migration, evaluation runtime/review
  semantics, a compatibility reader, or a new Python facade.
- **Triggered review policies:** change-admission, authority-and-projections, human-interaction-integrity, control-and-recovery, workflow-outcome-review, control-placement
- **Candidate / obligation IDs:** PC-C01, PC-C02, RC-C03, EV-C06, PC-C05
- **Target / retirement:** `parse_profile_input()` and `ProfileParseResult` are the
  canonical parser/result; HITL1's current versioned profile/proposal paths are the
  only supported producers/readers; retire duplicate profile helpers and
  `parse_profile_response()`.
- **Surface grade:** Domain module exports are application-internal with authorized
  clean cutover; profile/proposal/checkpoint payloads are persisted/cross-boundary
  and reject every unregistered external or old shape rather than receiving inferred
  support.
- **Decision authority:** Product + Data Owners own the approved current input scope
  and rejection of unregistered inputs; HITL1 owns acceptance and State mutation;
  domain profile owns candidate parsing; Python Support Owner owns wrapper removal.
- **Negative path / recovery:** Unsupported schema/version/alias/extra shape fails
  before a candidate becomes a proposal or control. Emergency rollback may restore an
  old reader only; no reader maps old input to a stronger current fact, and future
  support needs its own inventory/cutover change.

#### Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Profile text becomes a candidate | Human semantic input may propose a bounded profile | `parse_profile_input()` yields `ProfileParseResult`; HITL1 validates/accepts any State write | human-decision | Parsing cannot create a control, proposal, route, or checkpoint fact | Reuses canonical result rather than a wrapper | Parser and HITL1 accepted/rejected transcript tests |
| Profile/proposal/checkpoint input version | None; a payload cannot choose its schema semantics | Current schema matrix readers validate before HITL1/State consumers | non-bypassable | Unsupported inputs create no profile/proposal/continuation or provenance upgrade | Removes scattered defaults/aliases and indefinite readers | Reader-to-HITL1 no-write/reload negative tests |
| Evaluation parser convenience dependency | None | Evaluation test consumes `ProfileParseResult.partial`; domain parser remains fact owner | non-bypassable | Test migration cannot alter evaluation runtime or quality claims | Removes wrapper-only surface | Focused domain/live-evaluation parser tests |

#### Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Malformed or unsupported profile/proposal/checkpoint input | Canonical reader before candidate/State admission | No automatic fallback/migration; emergency rollback only restores reader | Rejected input with no State/proposal/control mutation | Supply current schema input or obtain a later approved support change | Parser and checkpoint-to-HITL1 no-write tests |
| Retired parser wrapper import | Domain module import/call boundary | No compatibility recovery in this change | Import/attribute failure without a result projection | Migrate consumer to `parse_profile_input().partial` or the full result | Focused domain and evaluation-consumer tests |
| Semantic candidate is valid but not accepted | HITL1 current proposal/visible-control owner | Existing bounded interaction/recovery rules remain unchanged | Existing pending proposal/control, not a final profile | Use the advertised current control or ordinary semantic reply | Existing human-interaction and HITL1 transcript tests |
