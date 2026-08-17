## Why

The current OpenSpec Change Guidance combines reusable agent-workflow practice with
Deep Research product facts, repository paths, requirement identities, and local
governance bindings. That coupling makes reuse in another DeerFlow-based agent
workflow project depend on copying and then editing source-specific authority, so this
change must establish a portable, product-neutral practice without weakening the
current Deep Research contracts.

## What Changes

- Introduce a product-neutral Change Guidance kernel plus independent opt-in
  `workflow-control`, `node-agent`, and `deerflow-downstream` profiles, with each
  adopting project owning its local composition and authority bindings.
- Extract a pure validator from the current Change Guidance checker while preserving
  `check_change_guidance.py` as the compatible Deep Research CLI and local policy
  wrapper.
- Atomically cut current guidance into `core/`, `profiles/`, and `local/` ownership,
  update every current consumer, and retire the old editable locations without
  compatibility copies.
- Replace the current product navigation entry `product/deep-research.md` with
  `product/README.md`; retain product semantics and the glossary in their existing
  owners, and keep `project-structure.toml` as the sole exact structure authority.
- Define the portable practice as an allowlisted, digest-bound snapshot whose
  neutrality and integrity are proved in this repository.
- Preserve the current Deep Research proposal grammar, policy obligations, checker CLI,
  requirement identities, architecture invariants, and runtime verification behavior.
- Correct the dependency direction so upstream `openspec/` governance may inspect the
  downstream Harness, while no `deep_research_harness/` guide, documentation, Makefile,
  application test, or asset depends on OpenSpec content.
- **BREAKING** for repository navigation only: the current product front-door path and
  Change Guidance document paths cut over atomically; no indefinite aliases or duplicate
  editable policy prose remain.

## Capabilities

### New Capabilities

- `portable-change-guidance`: Defines the product-neutral kernel/profile contracts,
  local binding boundary, export integrity, and real-adoption release criteria.

### Modified Capabilities

- `deep-research-agent-charter`: Rebinds Deep Research authoring, policy selection,
  proposal review, contributor navigation, and local checker obligations to the new
  local composition while preserving their substantive behavior.
- `project-structure`: Records the new exact OpenSpec guidance/governance topology and
  product front door while preserving the structure registry as the single authority.

## Impact

- OpenSpec-only authoring and governance surfaces under `openspec/change-guidance/`,
  `openspec/product/`, `openspec/governance/`, `openspec/config.yaml`, and the bounded
  OpenSpec/Harness entry documents and governance tests that consume them.
- An export manifest, file digests, neutrality checks, and source verification evidence.
- No Deep Research runtime behavior, production code, prompts, glossary body or
  authority, generic architecture schema, package/generator, archive rewrite, or
  `deerflow/` change is introduced.

## Program Focus

- **Program outcome:** Establish one product-neutral, mechanically exportable OpenSpec Change Guidance practice and preserve Deep Research through project-owned local composition.
- **Candidate / obligation budget:** S0-BASELINE, S0-CONSUMERS, S0-ADMISSION, S1-RED-FIXTURES, S1-PURE-KERNEL, S1-COMPAT-WRAPPER, S2-OWNERSHIP-LEDGER, S2-TOPOLOGY, S2-NODE-AUTHORING-GATE, S2-PROFILE-COMPOSITION, S2-LOCAL-CUTOVER, S3-CONSUMERS, S3-FRONT-DOOR, S3-OLD-ENTRY-RETIREMENT, S4-EXPORT
- **Declared workstream order:** baseline-admission, portable-validation, guidance-cutover, product-front-door, release-proof
- **Program decision authority:** The Source Program reviewer approves only this frozen budget, workstream order, plan-level re-scope, and whole-program archive closure; each named workstream owner retains its semantic decisions and no Program role becomes runtime authority, writer, or shared implementation owner.
- **Shared archive invariant:** All declared obligations are complete; old current entries and duplicate editable prose are retired; Deep Research grammar, IDs, guards, runtime verification, glossary authority, and `deerflow` state remain preserved; the fixed portable snapshot passes source verification; no workstream archives independently.
- **Program failure / recovery:** A failed workstream remains active and restores its last passing current entry or forward-repairs within its frozen obligations. A portable-file finding returns to its owning workstream, produces new digests, and re-runs affected proof. If convergence is impossible, the Program decision authority approves rollback or plan-level re-scope.
- **Split / expansion rule:** Work remains in this single Program Change only when necessary to the approved terminal topology and within the declared obligation budget. No sibling-adoption Change, source repair Change, or undeclared workstream is part of this Program.
- **Not in scope:** Deep Research runtime or production code, prompts, `deep_research_harness/CONTEXT.md` glossary migration, genericizing `check_project_architecture.py`, exporting requirement/spec/coverage checkers, `product/instance.yaml`, package/generator/submodule distribution, shared architecture schema, archive rewriting, cross-repository adoption work, or browsing/modifying `deerflow/`.

### Workstream Focus: baseline-admission

- **Primary module / causal owner:** OpenSpec portability baseline and consumer inventory
- **Seam classification:** deterministic-guardrail — the source evidence ledger determines whether every current entry and compatibility promise is known before migration.
- **Question:** Which current consumers, grammar contracts, guards, requirement identities, product links, glossary links, and gitlink facts must the later workstreams preserve or retire?
- **Necessary adjacent/external contracts:** Current Change Guidance checker CLI and fixtures answer the compatibility question; `project-structure.toml` and owning specs answer exact-member and identity questions; git metadata answers only whether the `deerflow` pointer and nested worktree are unchanged.
- **Evidence seam:** A checked-in baseline/consumer ledger plus passing current checker commands, active-change inventory, exact inbound-link inventory, and recorded gitlink/worktree observations.
- **Not in scope:** Moving prose or paths, extracting code, changing current grammar, editing runtime surfaces, or inspecting DeerFlow source.
- **Triggered review policies:** change-admission, local-context
- **Candidate / obligation IDs:** S0-BASELINE, S0-CONSUMERS, S0-ADMISSION
- **Target / retirement:** Produce the frozen migration ledger and admission evidence; retire unknown-current-consumer assumptions before S1 begins, while leaving all current entries active.
- **Surface grade:** Cross-workstream planning and compatibility evidence; it is not runtime or product authority, but every later cutover consumes it.
- **Decision authority:** The baseline owner accepts inventories and checker observations; the Program decision authority admits S1 only when unresolved consumers are either closed or explicitly block migration.
- **Negative path / recovery:** Missing, conflicting, or unenumerable consumers keep the Program active at S0. Correct the ledger or narrow the planned cutover; do not infer absence, widen repository browsing, or begin path retirement.

### Workstream Focus: portable-validation

- **Primary module / causal owner:** Product-neutral Change Guidance grammar validator
- **Seam classification:** deterministic-guardrail — a pure evaluator admits proposal/review grammar from explicit inputs while the local wrapper retains repository policy and filesystem decisions.
- **Question:** Can reusable proposal and conditional-review grammar be evaluated without Deep Research literals, paths, requirement IDs, filesystem traversal, commands, or wrapper globals while preserving current CLI outcomes?
- **Necessary adjacent/external contracts:** `check_change_guidance.py` CLI/path/0-or-1 result answers compatibility; current contract fixtures answer behavioral equivalence; `project-structure.toml` answers registration of the new kernel file.
- **Evidence seam:** Red-before-green neutral/purity/source-ID fixtures, direct pure-API tests, unchanged wrapper CLI fixtures, and a recursive portable-source literal/ID scan with a planted violation.
- **Not in scope:** Moving Change Guidance prose, changing policy names or current exact member sets, generalizing other governance checkers, or weakening proposal grammar.
- **Triggered review policies:** control-placement, authority-and-projections
- **Candidate / obligation IDs:** S1-RED-FIXTURES, S1-PURE-KERNEL, S1-COMPAT-WRAPPER
- **Target / retirement:** Add the pure kernel and delegate from the compatible local wrapper; retire only duplicated grammar evaluation inside the wrapper, not its local bindings or CLI.
- **Surface grade:** Pure kernel API is an exported cross-project contract; wrapper command path, arguments, and result semantics are declared Deep Research project interfaces.
- **Decision authority:** The portable validator owner decides pure grammar API and evaluation semantics; the Deep Research wrapper owner decides local paths, enabled policies, budgets, filesystem checks, and compatibility acceptance.
- **Negative path / recovery:** If current proposal outcomes change, restore wrapper delegation to the last passing local logic, retain the failing neutral/equivalence fixture, and redraw the seam. Never relax grammar or hide a failure to complete extraction.

#### Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Proposal/review grammar evaluation moves behind a pure API | None; grammar admission is deterministic | Explicit grammar input plus pure validator result; portable validator owns evaluation and local wrapper owns repository admission | non-bypassable | Product-neutral evaluation cannot grant local policies; wrapper compatibility can restore the last passing local implementation | One evaluator replaces duplicated portable/local grammar logic without creating a second CLI | Pure API fixtures, wrapper equivalence fixtures, and planted source-literal/ID scan |

### Workstream Focus: guidance-cutover

- **Primary module / causal owner:** Change Guidance core/profile/local composition topology
- **Seam classification:** wiring — the local router composes neutral core and independently enabled profiles while specs and local owners retain all semantic authority.
- **Question:** Can every current guidance paragraph have one editable owner, profiles remain independently opt-in, the full LLM-node cognition-versus-code gate remain prominent regardless of filename, and Deep Research preserve all substantive obligations through an atomic topology cutover?
- **Necessary adjacent/external contracts:** The paragraph ownership ledger answers destination/retirement; the local wrapper/profile registry answers enabled-policy composition; `deep-research-agent-charter` owns local contributor obligations; `project-structure` owns exact paths and members; `portable-change-guidance` owns exportable behavior.
- **Evidence seam:** Ownership/link ledgers, a semantic-parity fixture for the complete LLM-node authoring route and non-model branch, core-only and multi-profile fixtures, disabled-profile and duplicate-owner planted negatives, exact-member checks, current-proposal compatibility fixtures, and strict delta validation.
- **Not in scope:** Product front-door path migration, glossary movement, runtime changes, exporting local Program form or Deep Research information-map budgets as portable requirements, or retaining compatibility prose copies.
- **Triggered review policies:** control-placement, agent-information-map
- **Candidate / obligation IDs:** S2-OWNERSHIP-LEDGER, S2-TOPOLOGY, S2-NODE-AUTHORING-GATE, S2-PROFILE-COMPOSITION, S2-LOCAL-CUTOVER
- **Target / retirement:** Cut guidance to `core/`, `profiles/workflow-control/`, `profiles/node-agent/`, `profiles/deerflow-downstream/`, and `local/`; update all active consumers and delete old current policy files in the same workstream.
- **Surface grade:** Kernel/profile documents and composition contract are exported cross-project surfaces; local routing, policy set, paths, budgets, Program form, and information map remain project-owned contracts.
- **Decision authority:** Portable Change Guidance owner decides kernel/profile semantics and export allowlist eligibility; Deep Research Agent Charter owner decides local composition and contributor obligations; project-structure owner decides exact registered paths.
- **Negative path / recovery:** Duplicate owners, missing policies, disabled-profile leakage, or changed current obligations block cutover. Forward-converge to one owner using the local wrapper adapter, or restore the old current topology as a unit; never keep two editable copies.

#### Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Policy availability, the LLM-node first-read gate, and required review records become profile-composed | The author decides whether the symptom is cognitive-program, deterministic-guardrail, human-decision, or wiring before choosing prompt/context or traditional-code surfaces | Enabled profile registry plus proposal classification and ordered authoring-gate anchors; local wrapper evaluates completeness while owning specs/code retain behavior | non-bypassable | A model-bearing symptom cannot skip cognition because Python is found first; deterministic/human/wiring work cannot fabricate a prompt obligation | One prominent route avoids both code-first and prompt-for-everything failure modes | Semantic-parity fixture for classification, cognitive contract, prompt/context, output/repair, proof/evaluation, deterministic handoff, and explicit non-model branch; plus composition fixtures |

### Workstream Focus: product-front-door

- **Primary module / causal owner:** Deep Research OpenSpec product navigation entry
- **Seam classification:** wiring — one bounded README routes product questions to existing owners without acquiring their facts or exact structure authority.
- **Question:** Can `product/README.md` become the only current product front door while terminology, specs, current facts, governance, and glossary remain in their owning sources?
- **Necessary adjacent/external contracts:** Current non-archive inbound links answer consumer scope; the product member/budget guard answers exact entry shape; `project-structure.toml` owns the path change; `deep_research_harness/CONTEXT.md` remains the glossary authority reached by link only.
- **Evidence seam:** Exact inbound-link inventory, product exact-member/budget/owner-route fixtures, planted stale-link and extra-member failures, and restored-fixture positives.
- **Not in scope:** Moving or rewriting glossary content, adding `product/instance.yaml` or fixed outcome/workflow schemas, copying structure facts, or rewriting archive references.
- **Triggered review policies:** agent-information-map, authority-and-projections
- **Candidate / obligation IDs:** S3-CONSUMERS, S3-FRONT-DOOR, S3-OLD-ENTRY-RETIREMENT
- **Target / retirement:** Atomically create `product/README.md`, update every current consumer and structural registration, and delete `product/deep-research.md` without a compatibility copy.
- **Surface grade:** Repository navigation interface with a clean coordinated cutover; linked terminology/spec/current-fact/governance sources remain separate authoritative surfaces.
- **Decision authority:** The Deep Research product documentation owner decides navigation wording; the glossary/spec/governance owners decide linked facts; project-structure owner approves exact path membership.
- **Negative path / recovery:** If consumers cannot be enumerated, do not cut over. If a missed consumer appears during cutover, forward-fix it in this workstream or restore the old single entry and member guard as a unit; two long-lived front doors are illegal.

### Workstream Focus: release-proof

- **Primary module / causal owner:** Portable practice snapshot and source evidence
- **Seam classification:** deterministic-guardrail — allowlist, digests, neutrality checks, and source verification constrain snapshot identity.
- **Question:** Does one fixed source snapshot contain only product-neutral portable files and retain exact byte identity?
- **Necessary adjacent/external contracts:** The export manifest/digests answer snapshot identity; source governance and Harness verification answer local conformance.
- **Evidence seam:** Allowlist/denylist and digest checks with planted tampering, portable-link checks, source-literal neutrality checks, and complete source verification.
- **Not in scope:** Cross-repository adoption, target runtime semantics, package/generator infrastructure, or claims about future adopters.
- **Triggered review policies:** control-and-recovery, change-admission
- **Candidate / obligation IDs:** S4-EXPORT
- **Target / retirement:** Produce and verify one fixed portable snapshot, then archive this Program when all source obligations pass.
- **Surface grade:** Exported snapshot and digest manifest are reusable cross-project inputs; they promise exact content, not package compatibility or automatic upgrades.
- **Decision authority:** The portable-practice owner accepts the allowlist and snapshot; the Program decision authority approves whole-program archive closure.
- **Negative path / recovery:** A denylisted file, product literal, broken portable link, or digest mismatch returns to the owning workstream, produces corrected bytes and new digests, and re-runs source proof.

Ordinary downstream work neither modifies nor source-browses the `deerflow/` gitlink.
This Program does not own or approve that boundary; closeout records metadata-only
evidence that the pointer and nested worktree remain unchanged.
