# evaluation-hardening Specification

> req: EVH-001, EVH-002, EVH-003, EVH-004, EVH-005, EVH-006, EVH-007, EVH-008, EVH-009, EVH-010, EVH-011, EVH-012, EVH-013, EVH-014, EVH-015, EVH-016, EVH-017, EVH-018, EVH-019, EVH-020, EVH-021, EVH-022, EVH-023, EVH-024, EVH-025, EVH-026, EVH-027, EVH-028, EVH-029, EVH-030, EVH-031, EVH-032

## Purpose

Provide deterministic workflow conformance, live behavioral evaluation, full-real release acceptance, and mechanical regression traceability for Deep Research.
## Requirements

### Requirement: Eval corpus framework supports replay-based testing

The eval framework SHALL represent each required research risk as a lane-neutral typed scenario family plus one or more lane-specific cases. The corpus SHALL cover quick factual, claim verification, insufficient evidence, prompt injection, malformed structured output, unavailable tools, budget exhaustion, partial worker success, checkpoint control, and sandbox/filesystem failure. Every family SHALL bind to at least one collected deterministic case that invokes its declared lowest stable production interface and asserts observations projected from checkpoint, validated-ledger, or contained-sandbox authority. Cases that exercise model/tool behavior SHALL use executable typed scripted inputs; lifecycle/store cases SHALL use typed action or fault inputs instead of pretending to be agent loops. A descriptive-only family, string-labeled pseudo-script, synthetic outcome dictionary, or uncollected case SHALL fail asset governance. Deterministic corpus execution SHALL require no model API, external network, or operator credentials.

#### Scenario: One family is reusable across deterministic and live cases
- **WHEN** one risk family has both deterministic and live cases
- **THEN** the cases SHALL share the same risk intent and permitted degradation while each declaring the entrypoint, inputs, bounds, expected outcomes, hard invariants, applicable metrics, seam, and authenticity it can actually prove

#### Scenario: Every first-wave family executes at its responsible seam
- **WHEN** asset governance collects the deterministic corpus
- **THEN** each required family SHALL reference at least one collected case whose evidence claim names the production seam responsible for that case without requiring unrelated graph phases

#### Scenario: Insufficient evidence remains an acceptable bounded outcome
- **WHEN** scripted sources do not support the requested conclusion
- **THEN** the real validator, ledger, and artifact path SHALL record a typed limitation or gap without fabricating an accepted claim or citation

### Requirement: Quality metrics are pure functions

Quality metrics SHALL be pure Python functions with no model calls or I/O. They SHALL consume a validated evaluation outcome projected before metric computation from available accepted ledger records, canonical sources, topic/question coverage, synthesis findings and gaps, final citation maps, and optional labeled replay expectations. The metric set SHALL distinguish structural citation-binding rate, labeled semantic citation precision, final claim-map citation completeness, synthesis finding-support coverage, must-answer coverage, distinct canonical-URL count, distinct normalized-host count, labeled contradiction recall, labeled semantic unsupported-major-claim count, and the separate structural missing-backing-ref count. Canonical-URL and host counts SHALL derive only from validated accepted `SourceRef` values; provider-local `source_id` values SHALL NOT count as cross-record source identity. A metric not selected by the scenario case SHALL return `not_applicable`; a selected metric whose required authoritative input is missing or semantically unlabeled SHALL return `insufficient_authority`. A selected ratio with no authoritative denominator population SHALL also return `insufficient_authority`; an authoritative count metric MAY return measured zero when its required source collection is present, validated, and empty. Otherwise the metric SHALL return `measured`. `not_applicable` and `insufficient_authority` SHALL carry a null value; `measured` SHALL carry a typed numeric value. Every result SHALL include its evidence basis, so an unavailable ratio cannot become a vacuous zero or one and a measured zero count cannot be confused with missing authority. Metric evaluation SHALL remain separate from hard correctness and security invariants, and quality thresholds SHALL require an observed live baseline and separate review.

#### Scenario: Ref-shaped text is not a bound citation
- **WHEN** a final citation string has the expected syntax but does not bind to an accepted ledger record
- **THEN** citation binding rate SHALL treat it as unbound and a required citation-binding hard invariant SHALL fail independently of semantic precision

#### Scenario: Semantic precision requires labels
- **WHEN** cited claim/ref pairs have accepted structural bindings but no labeled support judgment
- **THEN** citation precision and semantic unsupported-claim count SHALL report `insufficient_authority` rather than infer support from ref syntax or existence

#### Scenario: Must-answer coverage uses existing topic authority honestly
- **WHEN** questions bind to planned topics and synthesis findings or typed honest gaps name affected topics
- **THEN** a question SHALL count as covered only when every known topic in its planner-owned binding set is represented by at least one finding or typed honest gap; partially represented questions plus missing or unknown topic ids SHALL be reported separately and SHALL NOT be represented as direct question-to-finding authority

#### Scenario: Empty denominator is not perfect quality
- **WHEN** a selected ratio metric has no authoritative claims, questions, citations, findings, or labeled expectations in its required denominator
- **THEN** it SHALL return `insufficient_authority` with a null value and an evidence-basis reason rather than a vacuous zero or one

#### Scenario: Valid empty collection can measure a zero count
- **WHEN** a selected structural count metric receives its required validated authority collection and that collection is empty
- **THEN** it MAY return `measured` with numeric zero and evidence basis identifying the authoritative empty collection rather than reporting missing authority

#### Scenario: Quality scores are reproducible for a validated outcome
- **WHEN** the same validated evaluation outcome is evaluated twice
- **THEN** all metric statuses, values, and evidence bases SHALL be identical and no model, network, clock, or filesystem input SHALL be consulted

#### Scenario: Hard invariant failure is not averaged into quality
- **WHEN** a scenario has an unauthorized route, forged submission, invalid artifact binding, or incorrect terminal lifecycle outcome
- **THEN** evaluation SHALL fail independently of citation, coverage, diversity, cost, or latency scores

### Requirement: Fault injection covers critical graph points

Fault injection tests SHALL exercise real lifecycle, checkpoint, runtime bridge, store, and graph seams for crash, timeout, cancel, duplicate resume, partial write, stale checkpoint, and conflicting worker-result faults. Each fault SHALL produce verified recovery, an idempotent replay, or an explicit typed terminal outcome without silent partial success.

#### Scenario: Duplicate resume crosses the lifecycle handler seam
- **WHEN** the same consumed HITL response is submitted twice through the resume handler
- **THEN** the second submission SHALL be idempotent and SHALL NOT advance the graph or duplicate artifacts

#### Scenario: Partial publication is recovered through the authoritative store
- **WHEN** a fault is injected at a supported atomic-publication boundary
- **THEN** recovery SHALL expose either the prior committed state or the single durable new state, never a partially authoritative result

### Requirement: Adversarial source tests verify isolation

Adversarial scenarios SHALL pass prompt-injected and authority-forging source content through the real untrusted-data, worker, submission, and gate path. External content SHALL NOT override routing, forge accepted submissions, mutate checkpoint authority, escape attempt-scoped paths, or influence deterministic gate verdicts except through validated evidence fields.

#### Scenario: Route-like source text remains untrusted data
- **WHEN** a scripted tool result contains route, gate, or submission instructions
- **THEN** the real worker and gate path SHALL preserve graph-owned routing and ledger authority

#### Scenario: Adversarial path request is contained
- **WHEN** model output or tool input attempts to read or write outside declared roots
- **THEN** policy SHALL deny the operation and no out-of-scope artifact SHALL be created

### Requirement: Release gate combines deterministic CI with optional LLM canary

The existing five pairwise-disjoint rapid or credentialed evidence selections,
offline/no-implicit-sync rapid deterministic gate, strict selected live/release lanes,
and stable existing workflow/status identity guarantees remain unchanged. Their
canonical rapid deterministic command is
`cd deep_research_harness && UV_OFFLINE=1 make verify`. A sixth,
pairwise-disjoint `periodic` selection SHALL contain maintained deterministic
public-entry scenarios whose clean-copy setup cost is intentionally excluded from the
rapid gate. The periodic selection SHALL be credential-free, offline-capable after its
explicit setup, and represented by a first-class pytest marker and test-evidence
selection; `make test`, `make verify`, and every rapid focused target SHALL exclude it.
Test-asset governance SHALL collect and validate periodic selectors and their central
claims without executing their process bodies as part of the rapid gate.
`tests/scenarios_suspended/` remains distinct: it contains only credentialed release
diagnostics that are not active supported-contract evidence. A dedicated CI workflow
SHALL run the periodic target when a pull request or `master` push changes the declared
entry-environment dependency surface: `deep_research_harness/Makefile`,
`pyproject.toml`, `uv.lock`, `run/**`, `scripts/**`, `src/**`, `src_fake/**`,
`tests/scenarios_periodic/**`, or the periodic workflow definition. It SHALL also run
daily and by manual dispatch; its result SHALL be visible as a distinct CI job, without
claiming repository branch-protection configuration. The periodic target SHALL write a
machine-readable duration report and enforce a declared per-scenario budget or an
explicit owner/reason/expiry waiver. CI path filters, working directories, artifacts,
release-attestation scopes, and protected-path checks for the existing rapid workflow
SHALL continue to use `deep_research_harness/`, while `backend/`, `frontend/`, and
`openspec/` boundary checks remain repository-root checks. A filesystem-root change
SHALL not rename the existing rapid workflow display name, job/status identity, test
lane, or evidence semantic. (`EVH-005`, `EVH-032`)

OpenSpec governance evidence SHALL NOT be part of the Harness `make verify`
composition. The project SHALL maintain one OpenSpec root governance aggregate that
combines every registered OpenSpec checker — requirements registry, main-spec
structure, project architecture, Change Guidance, requirement evidence coverage, and
Harness dependency direction — as an OpenSpec-side gate run from the repository root.
The aggregate SHALL be orchestration-only: it SHALL invoke each component checker,
preserve its exit code, and aggregate results without owning rule semantics, writing
the requirement registry, or reimplementing delta/registry parsing. The aggregate
SHALL expose a read-only planning phase that delegates active-change admission checks
to the owning components (Change Guidance for the Focus Card, the selected-change
scope of the specification checker for delta headers and titles, the planning scope
of the requirement checker for reservations and collisions, and native strict change
validation for MODIFIED requirement/scenario preservation) and a closeout phase that
requires a zero exit from every component checker before a change SHALL be archived
through repository agent workflows; closeout SHALL NOT add a separate consistency
checker because the component checkers own registry, header, and evidence
consistency. Harness verification SHALL remain independently runnable without the
OpenSpec tree, and no Harness guide, documentation, Makefile, application test, or
asset SHALL read, import, execute, or link OpenSpec content. (`EVH-005`)

#### Scenario: Canonical verification starts from the Harness root
- **WHEN** a developer runs the complete rapid deterministic verification gate
- **THEN** `cd deep_research_harness && UV_OFFLINE=1 make verify` performs the existing
  local aggregate without resolving a former downstream root

#### Scenario: Governance gate runs beside Harness verification
- **WHEN** archive closeout runs for an active change
- **THEN** the OpenSpec root aggregate runs every registered checker from the
  repository root with component exit codes preserved and no duplicate consistency
  check, and `cd deep_research_harness && UV_OFFLINE=1 make verify` completes
  independently without executing or linking OpenSpec content

#### Scenario: A failing closeout stops repository archive workflows
- **WHEN** any component checker exits non-zero at closeout
- **THEN** the aggregate exits non-zero and repository archive agent workflows stop
  with the failing checker identified before native archive runs; a direct native
  `openspec archive` invocation is not blocked

#### Scenario: Planning admission delegates to component owners
- **WHEN** the read-only planning phase checks an active change
- **THEN** Focus Card grammar is evaluated by the Change Guidance checker, delta
  header/title rules by the specification checker's selected-change scope, ID
  reservations and collisions by the requirement checker's planning scope, and
  MODIFIED requirement/scenario preservation by native strict change validation,
  with no parsing reimplemented inside the aggregate

### Requirement: Deterministic test selection references only live markers and passes from a clean checkout

The deterministic verification gate SHALL pass from a clean checkout (no local
`profiles/` state, `.env`, or `config.yaml`). The retired `postgres` marker SHALL be
absent from pytest marker registration, from every deterministic lane expression, and
from every exact-string lane assertion; no lane SHALL exist that fails collection
because it selects a retired marker. Suspended release-acceptance material SHALL remain
pytest-collectable under `tests/scenarios_suspended/` (file name matches `test_*.py`)
while excluded from every deterministic lane by its declared
`requires_llm`/`release_e2e` markers, so suspension is visible to collection tooling
rather than hidden by an uncollectable file name. Deterministic integration tests SHALL
construct the profile state they check themselves and SHALL NOT depend on gitignored
local state under `profiles/`. (`EVH-031`)

#### Scenario: Retired marker has no live reference
- **WHEN** a lane expression, a lane-selection constant, or a contract-test assertion
  references the `postgres` marker
- **THEN** the reference SHALL be absent, and no `test-postgres` target SHALL exist

#### Scenario: Suspended release material stays collectable but excluded
- **WHEN** pytest collects the suspended directory
- **THEN** it SHALL find the release-acceptance file by its `test_*.py` name, and every
  deterministic lane SHALL deselect it through its declared markers

#### Scenario: Deterministic gate passes from a clean checkout
- **WHEN** the repository is checked out cleanly (no local profile, env, or config
  state) and `UV_OFFLINE=1 make verify` runs
- **THEN** the gate SHALL complete successfully, including lint, asset coverage, and
  integration lanes

#### Scenario: Integration tests construct their own profile state
- **WHEN** a deterministic integration test prepares a copied project and checks a
  profile entry
- **THEN** the test SHALL construct the checked profile state itself and SHALL NOT read
  or copy gitignored local `profiles/` content

#### Scenario: Unrelated product change avoids expensive clean-copy setup
- **WHEN** a Harness pull request changes no declared entry-environment dependency path
- **THEN** the rapid deterministic gate runs without executing
  `tests/scenarios_periodic/`, while its required fast, governance, lint, asset,
  integration, and workflow evidence remains unchanged

#### Scenario: Entry-environment change runs maintained process evidence
- **WHEN** a pull request or `master` push changes a declared entry-environment
  dependency path
- **THEN** the dedicated periodic workflow explicitly prepares the project and runs the
  periodic target, including the clean-copy public-entry scenarios

#### Scenario: Periodic evidence is not suspended evidence
- **WHEN** test collection inspects maintained periodic and suspended scenario
  directories
- **THEN** periodic scenarios are collected by their dedicated deterministic target
  without a `release_e2e` marker, while suspended scenarios remain excluded from all
  ordinary and periodic targets by their declared credentialed release markers

#### Scenario: Asset governance retains periodic public-entry claims
- **WHEN** test-asset governance validates the focused selections
- **THEN** it collects the periodic selector and validates its central claims and
  requirement impacts without executing the clean-copy process body as part of
  `make test-assets`

### Requirement: Recorded incidents close at the lowest responsible seam

Every recorded real-mode or later live/release incident SHALL reference at least one central test-evidence claim for a collected deterministic selector at the lowest responsible stable seam when replayable. The incident inventory SHALL retain explicit replaced/duplicate recommendation status and coverage of all-real compilation, context forwarding, model/tool/sandbox readiness, mounted filesystem stores, capability/policy routing, budgets, structured output, gate fatigue, and checkpoint identity. Each claim SHALL declare a stable claim id, exact collected selector, expected focused selection, requirement ids, asset class, one canonical stable seam, optional authenticity, at most one scenario-case id, and any discovery ids; selector globs and prefixes SHALL be rejected. Every registered scenario case SHALL resolve to exactly one claim whose exact collected pytest node id contains the stable case id. Parameterized evidence cases SHALL use stable case ids as pytest ids, and uniform provider-shape selectors SHALL be derived from registered shape case ids. Only selectors referenced by the requirement-evidence policy or a scenario, incident, node, fault, or discovery inventory SHALL require central claims; ordinary collected tests SHALL NOT be duplicated into a second exhaustive catalog. Inventories SHALL reference claim ids instead of independently repeating selector/seam/authenticity declarations. Existing `@impl` annotations SHALL continue to identify owning implementation surfaces; evidence claims SHALL own test-selector proof. Governance SHALL collect and validate deterministic, workflow, live, and release claims in their expected selections, verify referential consistency and evidence policy, and SHALL NOT present static metadata as proof of unobservable internal calls. Provider-dependent behavior that cannot be reproduced honestly SHALL retain a bounded live case and explicit rationale.

#### Scenario: Existing selector cannot overclaim its evidence class
- **WHEN** a selector still exists but its central claim is below an inventory entry's required asset class, seam, or authenticity
- **THEN** asset governance SHALL fail with the inventory id, selector, required evidence, and registered claim

#### Scenario: Incident inventory cannot retain a stale selector
- **WHEN** an incident claim references a selector that is renamed, removed, skipped by its required lane, or no longer collected
- **THEN** asset governance SHALL fail with the incident id, claim id, and stale selector

#### Scenario: Integration failure is diagnosable below E2E
- **WHEN** a recorded replayable interface mismatch is reintroduced
- **THEN** its focused deterministic case SHALL fail before live or release execution and identify the family/case, seam, and typed invariant or error code

#### Scenario: Duplicate mappings cannot disagree silently
- **WHEN** incident, node, fault, or scenario inventories reference one collected selector
- **THEN** they SHALL resolve through the same central claim and governance SHALL reject contradictory local seam or authenticity metadata

#### Scenario: Replayable release discovery has deterministic provenance
- **WHEN** a release discovery concerns a provider payload shape that production parsing or normalization can replay
- **THEN** it SHALL link to either a minimized redacted shape case or an existing focused deterministic regression plus a collected evidence claim before the discovery is considered closed

### Requirement: Scenarios declare stable test seams and authenticity

Each reusable scenario family SHALL declare a stable family id, risk intent, owning requirement ids, optional regression ids, and permitted degradation. Each scenario case SHALL declare a stable case id and family id, execution lane, entrypoint, required asset class, canonical stable seam, optional authenticity, bounded preconditions, executable typed inputs or live requirements, expected route/terminal/artifact/support/citation/degradation outcomes, hard invariants, and applicable metrics. The closed asset classes SHALL be code correctness, deterministic workflow conformance, live behavioral evaluation, and release acceptance. The closed canonical stable seams SHALL be domain/engine, node interface, runtime integration, lifecycle/mixed graph, and public entry. When authenticity applies, the closed levels SHALL be `FAKE_GRAPH`, `REAL_NODE_FAKE_CAPABILITIES`, `SCRIPTED_REAL_WORKFLOW`, `LIVE_REAL_DEPENDENCIES`, and `FULL_REAL_PIPELINE`; code-correctness cases MAY omit authenticity. Authenticity SHALL qualify only the claim's already compatible asset class, seam, and scope; it SHALL NOT widen a focused claim or substitute for another asset class or seam. Focused tests SHALL invoke the existing production interface explicitly and project a test-owned observation from observable calls and checkpoint, ledger, and sandbox authorities. A shared assertion interface SHALL reject unknown invariant names and evaluate every expectation applicable to the case.

#### Scenario: Successful execution evaluates every applicable invariant
- **WHEN** a focused case returns a nominal observation
- **THEN** shared assertions SHALL calculate every case hard invariant, validate expected outcomes against the family's permitted-degradation policy, and SHALL NOT mark either successful merely because execution returned without error

#### Scenario: Code correctness is not forced onto the agent authenticity ladder
- **WHEN** a deterministic store, parser, reducer, or real-node-fake-capability case proves its declared risk without an agent loop
- **THEN** its claim SHALL retain the appropriate code-correctness asset class and seam, with no fabricated `SCRIPTED_REAL_WORKFLOW` authenticity

#### Scenario: Unknown evidence vocabulary fails closed
- **WHEN** a family, case, claim, or inventory uses an asset class, stable seam, or authenticity outside the closed canonical vocabulary
- **THEN** governance SHALL reject the value rather than preserve an ad hoc alias or infer a nearby category

#### Scenario: Lower authenticity cannot satisfy a higher claim
- **WHEN** a case claims workflow, live, or full-real evidence without the applicable real lifecycle/graph or agent-loop seams
- **THEN** governance and shared assertions SHALL reject that evidence claim

#### Scenario: Focused real dependencies do not widen coverage
- **WHEN** a live case uses real model or tool dependencies only at a directly seeded focused node
- **THEN** its `LIVE_REAL_DEPENDENCIES` authenticity SHALL NOT satisfy workflow-prefix, predecessor-lifecycle, public-entry, release-acceptance, or `FULL_REAL_PIPELINE` evidence

#### Scenario: Scenario diagnostics carry stable identity
- **WHEN** a case fails in any execution lane
- **THEN** failure output SHALL include family id, case id, lane, applicable authenticity, failed invariant or metric, and only bounded redacted structural diagnostics

### Requirement: Deterministic tests conform real agent workflows

Every available real node SHALL retain at least one deterministic success and one highest-risk failure, repair, degradation, or exhausted case through its stable node interface. Every available real node that uses a model or tool SHALL additionally retain at least one collected deterministic workflow claim through its applicable real runtime bridge-driven agent loop. Governance SHALL discover model/tool-node ownership from loaded `run_agent` attribute calls or method references across production node packages using syntax-aware inspection and compare it with the explicit audited inventory; it SHALL NOT infer ownership from declared node capabilities or present source discovery as execution proof. A deterministic test SHALL carry the `workflow` marker only when it executes at least one temporally ordered production workflow: a real lifecycle/mixed-graph transition sequence, a real runtime-bridge agent loop, or a real worker submit/gate sequence. The marker SHALL identify the workflow-conformance asset class, not automatically grant `SCRIPTED_REAL_WORKFLOW` authenticity. Model/tool workflow claims SHALL construct the applicable real agent or runtime bridge and execute its middleware, execution policy, budget, structured-output parser, validator, submission/gate, checkpoint, and filesystem paths while replacing only external model/tool adapters, deterministic time/randomness, and supported fault points. Scripted adapters SHALL fail when a requested response is exhausted; each evidence-bearing workflow case SHALL assert its declared model/tool call bounds, order, and relevant bound-tool observations without imposing complete-trace semantics on unrelated fixture users. A test that patches the agent, bridge, or assembly factory MAY prove wiring but SHALL NOT claim agent-loop behavior or `SCRIPTED_REAL_WORKFLOW` authenticity. High-risk real prefixes SHALL run as mixed graphs with later unrelated nodes kept fake.

#### Scenario: Scripted worker traverses the complete policy path
- **WHEN** a scripted model issues an allowed web tool call and returns a valid worker result
- **THEN** observable model/tool calls plus checkpoint, ledger, gate, and attempt-artifact outcomes SHALL demonstrate the real resolver, bridge, middleware, policy, budget, validator, and submit path before work is reported accepted or degraded

#### Scenario: Scripted external adapters retain the real loop
- **WHEN** deterministic model turns and tool results drive a model/tool behavior case
- **THEN** the real agent or runtime bridge SHALL consume them, premature exhaustion, unexpected calls, or call order/bounds inconsistent with the case SHALL fail, and the observation SHALL record the relevant tool bindings and calls

#### Scenario: Patched assembly proves wiring only
- **WHEN** `create_agent`, a bridge builder, or another assembly factory is patched to inspect constructor arguments, middleware order, or tool registration
- **THEN** the test MAY claim wiring correctness but SHALL NOT satisfy workflow-conformance, agent-loop, policy-path, or `SCRIPTED_REAL_WORKFLOW` evidence

#### Scenario: Lifecycle sequence can be workflow conformance without a model
- **WHEN** a deterministic case executes ordered real start/resume/cancel or mixed-graph transitions with real checkpoint authority
- **THEN** it MAY enter the workflow selection for the lifecycle/graph seam but SHALL NOT claim `SCRIPTED_REAL_WORKFLOW`, agent-loop, or live-provider authenticity without a real bridge-driven loop

#### Scenario: Malformed output follows bounded repair policy
- **WHEN** scripted model responses remain malformed through configured repair attempts
- **THEN** the real node or worker path SHALL reach its specified typed fallback or exhausted outcome without accepted ledger publication or fabricated artifact success

#### Scenario: Directory placement does not establish workflow authenticity
- **WHEN** a test is placed under `integration`, `graph`, or `eval` without a qualifying ordered production workflow
- **THEN** it SHALL remain code-correctness or real-node coverage and SHALL NOT enter the workflow-conformance selection

#### Scenario: Capability declaration does not discover model use
- **WHEN** a real node calls the shared agent bridge but declares no agent capability or declares a store/controller capability
- **THEN** syntax-aware node ownership discovery SHALL still require its workflow claim, while the collected focused test supplies the behavioral evidence

#### Scenario: Mutable fixture state is isolated and restored
- **WHEN** a deterministic, live, or release fixture changes effective config/home paths, installs a sandbox provider, mutates a cached AppConfig or GraphHost, or creates contained filesystem data and then succeeds or raises
- **THEN** the fixture owner SHALL restore each process-global state it actually changed through its public reset/restore API, and the next case SHALL observe its own explicit configuration and contained filesystem without prior checkpoint, ledger, or artifact state

#### Scenario: Persisted replay requires a concrete escalation
- **WHEN** a case proposes persisted record/replay instead of bounded scripted turns
- **THEN** it SHALL record the caller-sensitive interleaving or stable trace-shape behavior that scripts cannot faithfully represent, include caller identity in matching, normalize only declared volatile fields, fail loudly on a replay miss even when outer middleware handles the model error, and assert stable shape/order without raw provider prose or volatile-value goldens

### Requirement: Test selection and requirement traceability are mechanical

The existing collected-test coverage, invalid-fixture, detector-smoke, registry, and
cross-lane evidence requirements remain unchanged. The production-source ownership scan
SHALL inspect `deep_research_harness/src/**/*.py` as its canonical downstream source
root and shall fail closed for a stale, empty, relocated, or mis-scoped scan. (`EVH-010`)

#### Scenario: Production ownership scan uses the moved source tree
- **WHEN** a detector-smoke fixture places a known invalid `@impl` annotation beneath
  the canonical production source root
- **THEN** the scan discovers and rejects it under `deep_research_harness/src/` rather
  than succeeding against `deerflow_research/src/`

### Requirement: Higher-level failures descend into deterministic assets

Every defect discovered by live evaluation or full-real acceptance SHALL be classified by risk and stable seam. A machine-readable discovery disposition SHALL select exactly one of `uniform_shape`, `existing_regression`, or `provider_only`: uniform shape SHALL name an intended shape-case id that resolves to a collected claim before closure, existing regression SHALL name a collected claim id, and provider-only SHALL name a bounded live case plus non-empty replay-unsuitability rationale; fields belonging to other dispositions SHALL be rejected. Uniform replayable provider payload variations SHOULD be minimized into typed redacted shape cases linked to discovery ids; an existing focused regression MAY remain individual when its setup or responsible seam is not uniform, provided it has the same discovery provenance and central evidence claim. Behavior that depends on nondeterministic provider decisions and cannot be faithfully replayed SHALL remain a bounded live case with captured redacted diagnostics. Neither form SHALL be represented solely by an E2E log.

#### Scenario: Provider-shape case is bounded and attributable
- **WHEN** a provider response variation is added to the shared shape corpus
- **THEN** it SHALL contain only bounded keys, types, aliases, ordering, and synthetic-domain values needed to reproduce the behavior, name its discovery provenance and expected normalized or fail-closed result, pass credential, raw-host-path, external-URL, and size scans, and record human provenance review that free text was minimized rather than copied raw

#### Scenario: Existing focused regression remains valid provenance
- **WHEN** a replayable discovery already has a focused deterministic regression whose setup is not suitable for a uniform shape case
- **THEN** the discovery MAY link directly to that selector's evidence claim without duplicating the test solely to populate the corpus

#### Scenario: Discovery has one governable disposition
- **WHEN** a discovery classification is loaded
- **THEN** exactly one disposition-specific reference set SHALL be present, unknown or mixed dispositions SHALL fail, and corpus closure SHALL reject an unresolved intended shape-case id

#### Scenario: E2E integration defect gains a deterministic regression
- **WHEN** full-real acceptance exposes a replayable context, policy, parser, store, graph, or artifact-contract defect
- **THEN** the fixing change SHALL add the smallest deterministic regression at the lowest responsible seam before the defect is considered closed

#### Scenario: Provider-only behavior remains live
- **WHEN** a failure depends on model/tool selection or output distribution that cannot be faithfully represented by a deterministic payload
- **THEN** it SHALL remain a labeled bounded live case with attempts and redacted evidence rather than a tautological scripted test

### Requirement: Evidence layers are smallest-sufficient and distinct-risk

For each requirement changed by a test-evidence change, typed test-owned impact
metadata SHALL identify the owning contract, lowest responsible production seam,
normal edit-loop selector, and the risk each selected layer proves; its selector SHALL
resolve through the claim catalog and collected selection. A requirement normally uses
no more than one pure contract/unit layer, one runtime integration layer, and one
user-path/workflow layer; an additional layer, persisted replay, live dependency, or
full-real proof SHALL name a distinct risk that cannot be proven by the lower selected
seam. The active change `tasks.md` SHALL separately record the next smallest selector
and measured progress without treating prose status as task completion.

#### Scenario: Duplicate proof is rejected without a distinct risk
- **WHEN** a change proposes two evidence layers that assert the same behavior at the
  same responsible seam
- **THEN** the impact map requires one to be removed or records the distinct risk that
  justifies retaining it

#### Scenario: Escalated evidence is honest about its need
- **WHEN** a requirement uses trace replay, live dependencies, or full-real execution
- **THEN** its evidence record identifies the lower-seam gap and the bounded distinct
  risk the escalation proves

#### Scenario: Impact metadata cannot point at stale proof
- **WHEN** a typed requirement-impact entry names a selector not present in the claim
  catalog or its collected selection
- **THEN** deterministic evidence governance rejects the entry before it can claim
  coverage

### Requirement: Real model workflow coverage proves failure-outcome conformance

The deterministic workflow-conformance suite SHALL maintain a syntax-discovered
inventory of every production graph-node package that invokes `run_agent`. In
addition to success-path workflow evidence, each owner SHALL have executable
scripted-real-node cases for every declared applicable non-success outcome and an
assertion at the owning lifecycle or work-controller projection seam. Inventory and
test-asset governance SHALL fail closed on a missing owner, missing declared class,
uncollected selector, stale mapping, or a success-only substitute.

#### Scenario: A missing timeout case is detected for topic planning
- **WHEN** topic planning remains a discovered run-agent owner but its declared
  provider-timeout outcome case is removed or uncollected
- **THEN** deterministic workflow governance fails with the owner and missing
  outcome class before a change can claim complete workflow coverage

#### Scenario: An empty detector cannot pass as enforcement
- **WHEN** the outcome inventory is evaluated against an empty, relocated, or
  mis-scoped production-node root
- **THEN** a focused detector smoke test fails with the known missing owner rather
  than accepting an empty inventory

### Requirement: Evidence-evaluation calibration has independent branch proof

Test-owned evidence SHALL preserve Wave2's existing normal and highest-risk
`REAL_NODE_FAKE_CAPABILITIES` claims and add independent normal and highest-risk
claims for each newly migrated targeted branch: worker, repair, SourceDiagnostic, and
ClaimVerifier. The global capability matrix SHALL therefore expand from twelve to
sixteen rows. Each claim SHALL assert only the direct branch's capability posture and
deterministic candidate admission or non-admission at its owning synthesis,
work-unit, or critic-materializer seam. Separate collected `SCRIPTED_REAL_WORKFLOW`
claims SHALL exercise the real Wave2, targeted-worker, and critic bridge paths for
their applicable tool-call bounds, untrusted-data boundary, and observable admission
or non-admission. No claim SHALL use another branch, an aggregate selector/count,
catalog text, fake-adapter prose, or a scripted transcript as evidence of live model,
source, critic, or research quality. (`EVH-016`)

#### Scenario: Final cohort has direct normal and risk evidence
- **WHEN** evidence-evaluation calibration evidence is collected
- **THEN** every one of the four targeted branches has a distinct normal and
  highest-risk matrix claim at the lowest responsible owning seam, while Wave2 retains
  its existing direct claims and the matrix contains sixteen rows

#### Scenario: Workflow evidence remains separate from branch admission evidence
- **WHEN** a Wave2, targeted worker, or critic calibration case consumes scripted
  model/tool turns through the real runtime bridge
- **THEN** it proves only declared call bounds, untrusted-data handling, and
  deterministic candidate admission or non-admission; a separate direct claim proves
  the branch capability and neither proves research quality or source truth

### Requirement: Planning and initial-intake calibration has independent branch evidence

Test-owned evidence SHALL add independent normal and highest-risk
`REAL_NODE_FAKE_CAPABILITIES` claims for each newly migrated branch: topic planning,
topic-planning repair, Wave1 worker, Wave1 repair, Wave1 SourceDiagnostic, and Wave1
ClaimVerifier. The claims SHALL extend the global capability matrix from eight to
fourteen rows and assert capability posture plus deterministic candidate, review-
artifact, admission, or non-admission behavior at the owning node/work-unit/critic-
materializer seam. Wave0 SHALL retain its existing matrix claims. Separately, the
planner, Wave0 worker, Wave1 worker, and both Wave1 critics SHALL retain collected
`SCRIPTED_REAL_WORKFLOW` claims through their real bridge/runtime path; any revised
selector SHALL assert applicable call bounds, untrusted-data handling, and observable
tool/admission boundary. Neither evidence class SHALL use another branch, an aggregate
selector/count, catalog text, or fake-adapter prose as evidence of live model, source,
critic, or research quality. (`EVH-015`)

#### Scenario: Newly migrated branches have independent normal and risk proof
- **WHEN** planning and initial-intake calibration evidence is collected
- **THEN** the six newly migrated branches extend the capability matrix to fourteen rows with distinct real-node/fake-capabilities claims for normal behavior and their highest-risk posture, repair, or bound-artifact behavior at the declared lowest responsible seam

#### Scenario: Scripted workflow does not replace branch admission evidence
- **WHEN** a planner, Wave0, Wave1 worker, or Wave1 critic calibration case consumes scripted model/tool turns through the real runtime bridge
- **THEN** it proves call bounds, untrusted-data handling, and deterministic candidate or review-artifact admission only, while the separate matrix claim proves the branch capability; neither claim asserts authoritative source truth or high-quality research

### Requirement: Node-agent capability claims use an explicit branch evidence denominator

For an active node-agent capability cohort, test-evidence governance SHALL register a
closed branch-by-behavior-by-authenticity matrix before a branch can claim migration.
Each row SHALL name the direct production branch, capability ID, catalog source,
declaration source, lowest responsible entrypoint, and two distinct central
`TestEvidenceClaim` IDs: one for successful behavior and one for the highest-risk
behavior. The referenced claims SHALL have different collected selectors and retain
their own deterministic authenticity. The evidence checker SHALL reject a missing row,
duplicate branch, unknown capability, missing/identical/unknown claim ID, uncollected
claim, a claimed migrated branch without both behaviors, a claim for a different
branch, or an owner-level/aggregate-count substitution. The matrix SHALL not claim
live model quality from fake or scripted deterministic evidence.
(`EVH-012`)

#### Scenario: Six cohort branches have independent deterministic claims
- **WHEN** the first cohort registers its normal and repair branches
- **THEN** all six rows resolve to their own two collected claim IDs, with success and
  highest-risk coverage appropriate to each branch's tool posture and repair boundary

#### Scenario: Aggregate tests cannot claim capability migration
- **WHEN** a requirement impact names only a broad owner test, pytest total, or a
  selector for a different branch as evidence for a cohort branch
- **THEN** evidence governance rejects the claim before release or archive evidence
  can present that branch as migrated

### Requirement: Profile-brief capability evidence uses independent lifecycle claims

The capability evidence matrix SHALL add one row each for `hitl1/brief` and
`hitl1/brief-repair`, with distinct collected central claims for advisory proposal
success and malformed-output repair/exhaustion. Each claim SHALL exercise the real
HITL1 node seam with fake capabilities, retain deterministic authenticity, and prove
that neither result grants acceptance, route, or checkpoint authority. (`EVH-013`)

#### Scenario: Profile success remains advisory
- **WHEN** a scripted valid brief reaches the real HITL1 first-proposal seam
- **THEN** it yields a proposal only and the matrix records a collected success claim
  distinct from its repair-risk claim

#### Scenario: Exhausted repair cannot publish authority
- **WHEN** malformed brief output and its one repair both fail validation
- **THEN** the matrix's risk claim proves the existing exhausted/non-success path with
  no accepted profile, route, or checkpoint authority

### Requirement: HITL1 interaction lifecycle acceptance has independent evidence claims

Test-owned evidence SHALL register two distinct collected central claims for the
HITL1 profile-interaction lifecycle: one scripted real-node/fake-capabilities claim
covering confirmation, source-constrained revision, question, and ambiguity; and one
different claim covering exhausted semantic failure fallback. Both claims SHALL assert
the deterministic owner boundary, correlated lifecycle outcome, preserved/updated
proposal state as applicable, and the human-visible control/feedback outcome. They
SHALL NOT claim live model quality, research-result quality, capability migration, or
an aggregate pytest count as lifecycle acceptance evidence. (`EVH-014`)

#### Scenario: Success and fallback journeys have separate collected proof
- **WHEN** lifecycle evidence is collected for this change
- **THEN** two unique central selectors independently prove the accepted interaction
  journey and the exhausted fallback journey at the real HITL1 node seam

#### Scenario: Fake capabilities do not become quality evidence
- **WHEN** either lifecycle claim runs with scripted fake capability results
- **THEN** its recorded authenticity is limited to deterministic real-node/fake-capability
  lifecycle behavior and does not assert live model or research quality

#### Scenario: An empty detector cannot pass as enforcement
- **WHEN** the outcome inventory is evaluated against an empty, relocated, or
  mis-scoped production-node root
- **THEN** a focused detector smoke test fails with the known missing owner rather
  than accepting an empty inventory

### Requirement: Cognitive-program evidence uses explicit proof classification

Every active-branch ledger evidence link SHALL classify its referenced existing or new
central claim as `cognitive-program`, `deterministic-guardrail`, `wiring`, or
`obsolete-duplicate` before consolidation. The ledger SHALL retain exact branch
identity, source seam, and proof role. Every row SHALL retain distinct deterministic
composition, feedback-disposition, and guardrail/admission proof roles plus an
evaluation disposition. Active-branch closing links SHALL use only
`cognitive-program`, `deterministic-guardrail`, or `wiring`; `obsolete-duplicate` SHALL
remain non-closing. (`EVH-017`)

A node-board proof link MAY additionally use `human-decision` only for a conditional
typed human-decision admission/precondition claim. `human-decision` SHALL not close an
active model-branch role or claim that a human interaction exists. An
`obsolete-duplicate` link SHALL remain reviewable but SHALL NOT close a required proof
role, justify test deletion, or be inferred from an aggregate outcome.

#### Scenario: Proof class is constrained by evidence context
- **WHEN** node-board and active-branch proof links are validated
- **THEN** a conditional HITL2 boundary may use `human-decision`, active model branches
  reject that class, and `obsolete-duplicate` closes neither context

### Requirement: Intake and planning calibration has branch-specific judgment evidence

Test-owned calibration evidence SHALL define a dedicated labeled corpus with exactly
one normal and one highest-risk case for each current zero-tool branch: HITL1 profile
brief, profile-brief repair, semantic intake, semantic-intake repair, topic planning,
and topic-plan repair (twelve cases total). It SHALL be separate from both the
canonical `LIVE_CANARIES` collection and the lane-neutral `ScenarioCase` registry.
Every case SHALL name its stable case and branch identity, bounded trusted assignment,
untrusted input boundary when present, expected candidate constraints, explicit
criterion identifiers and quality rubric, nondeterministic boundary, and permitted
degradation. The rubrics SHALL evaluate only whether a candidate is conservative,
faithful to its bounded assignment, and decision-ready; they SHALL not assert source
truth, research quality, human acceptance, topic-registry publication, route
correctness, or a model judgment from deterministic fixtures. A `pass` SHALL mean all
declared criteria were assessable and satisfied; `limited` SHALL mean an assessable
candidate failed one or more declared criteria; `inconclusive` SHALL mean a successful
live run supplied insufficient admissible candidate evidence to assess a declared
criterion. A hard-invariant or execution failure SHALL remain the existing live-run
failure rather than receive a fabricated rubric disposition.

Each branch SHALL retain separate lowest-seam deterministic proof that its rendered
request, zero-tool posture, repair bound, and deterministic non-admission boundary
are intact. Each quality case SHALL execute only through an explicitly selected
`requires_llm` test and SHALL report stable case and branch identity, criterion ids,
a typed `pass`, `limited`, or `inconclusive` rubric disposition, hard-invariant
outcomes, attempts, bounded redacted diagnostics, and available cost/latency fields.
Each case SHALL declare outer attempt, model-call, tool-call, token, and timeout
bounds no wider than its existing zero-tool branch policy. A present typed rubric
result SHALL contain the complete declared criterion ids, a case id equal to the
report scenario id, and a branch id that resolves to that corpus case.
The typed rubric result SHALL be optional on the evidence-v1 live-report contract:
an existing evidence-v1 archive report without it SHALL remain readable as no rubric
result, and a new report with it SHALL validate the typed fields. Missing credentials
in that selected lane SHALL remain a strict preflight failure; the default
deterministic verification selection SHALL not execute or relabel a live calibration
as deterministic evidence. The canonical `LIVE_CANARIES` count, identities, and
deadline budget SHALL remain unchanged.

#### Scenario: Deterministic conformance does not claim judgment quality
- **WHEN** a fake-capability HITL1 or topic-planning case proves request composition,
  repair bounds, and candidate non-admission
- **THEN** its evidence is classified as deterministic conformance and does not pass
  the branch's labeled quality rubric or claim that a model made a useful judgment

#### Scenario: Each selected live calibration reports its bounded result
- **WHEN** an operator explicitly selects an intake or planning calibration case with
  valid live credentials
- **THEN** the case evaluates only its named branch and rubric, records its stable
  case/branch identity, criterion ids, and bounded typed result, and leaves profile
  acceptance, topic publication, and routing under their existing deterministic owners

#### Scenario: Unselected live calibration does not weaken offline verification
- **WHEN** the normal deterministic verification command is run without live-lane
  selection
- **THEN** all twelve calibration cases remain excluded by `requires_llm` while their
  separate deterministic composition and non-admission evidence still runs

#### Scenario: Calibration does not alter canonical live-canary governance
- **WHEN** the canonical live-canary collection and deadline validator are checked
- **THEN** they retain their six fixed cases, identities, and existing deadline budget,
  while the twelve intake/planning calibration cases remain in their separate
  test-only collection

#### Scenario: Rubric disposition is not a hidden test retry
- **WHEN** a selected live calibration completes with all hard invariants but cannot
  satisfy or assess all of its declared criteria
- **THEN** it records `limited` or `inconclusive` under the stated rubric meanings
  without adding a model retry, changing any production lifecycle fact, or claiming
  a `pass`

#### Scenario: A pre-rubric evidence-v1 archive remains readable
- **WHEN** a stored evidence-v1 live report lacks the optional typed rubric result
- **THEN** archive scanning accepts it as an evidence-v1 report with no rubric result
  rather than reclassifying it, fabricating a disposition, or rejecting the archive

### Requirement: Evidence-intake calibration has branch-specific judgment evidence

Test-owned evidence SHALL define a dedicated twelve-case labeled calibration corpus:
one normal and one highest-risk case for each Wave0 source intake and repair, Wave1
evidence extraction and repair, SourceDiagnostic, and ClaimVerifier branch. It SHALL
remain separate from the intake-and-planning corpus, `LIVE_CANARIES`, and the
lane-neutral `ScenarioCase` registry. Every case SHALL declare stable case/branch
identity, trusted assignment, any untrusted boundary, candidate constraints, criterion
ids, rubric, permitted degradation, nondeterministic boundary, and bounded resources.
The rubric SHALL assess only a bounded model candidate and SHALL not assert source
truth, acceptance, artifact publication, gate/route correctness, or research quality.

Each branch SHALL retain deterministic proof at its lowest responsible seam for
request composition, runtime tool posture, repair/review containment, and
non-admission. Wave0 repair evidence SHALL exercise only its parser/typed-structural
seam; Wave1 repair evidence SHALL exercise only its parser or local semantic seam.
Post-candidate `SubmissionValidationFailure` codes and later artifact validation
SHALL remain controller-owned and SHALL not construct a repair request.

Selected tool-bearing workers SHALL use a real model-and-web bridge after strict
model/web preflight; selected zero-tool repairs and critics SHALL use a real
model-only bridge after strict model preflight. Generated tool posture/resources,
successful bridge execution, production parsing, and Wave1 local semantic validation
where applicable SHALL be hard invariants. Failure SHALL be a live-run failure with
no rubric disposition. A typed rubric result SHALL resolve through a closed union of
the two named corpus indexes with globally unique identity and exact case/branch/
criterion matching; older evidence-v1 reports without a rubric remain readable.

#### Scenario: Deterministic conformance does not claim evidence judgment quality
- **WHEN** a fake-capability Wave0 or Wave1 case proves composition and non-admission
- **THEN** it remains deterministic conformance and does not pass a model-quality rubric

#### Scenario: Selected live calibration preflights the branch tool posture strictly
- **WHEN** a selected tool-bearing or zero-tool case lacks its required credentials
- **THEN** preflight fails before invocation and records no quality result

#### Scenario: Each selected live calibration reports its bounded result
- **WHEN** an operator selects a case with valid credentials
- **THEN** it evaluates only the named branch and rubric without lifecycle authority

#### Scenario: Selected live execution uses the branch-appropriate dependency seam
- **WHEN** an operator selects a worker, repair, or critic case
- **THEN** it uses only the declared real model-and-web or model-only bridge

#### Scenario: Failed branch mechanics do not receive a quality rubric
- **WHEN** a branch violates a hard request, bridge, parser, or local-validator invariant
- **THEN** the run fails without `pass`, `limited`, or `inconclusive`

#### Scenario: Separate calibration collections preserve existing governance
- **WHEN** deterministic selection and canonical live-canary validation run
- **THEN** both calibration corpora remain excluded and canaries retain six cases and their deadline budget

#### Scenario: Rubric disposition is not a hidden retrieval or retry
- **WHEN** a mechanically valid candidate misses declared judgment criteria
- **THEN** it records `limited` or `inconclusive` without a model call, retry, or route claim

#### Scenario: Post-candidate validation is not a repair-calibration input
- **WHEN** a Wave0 or Wave1 candidate receives post-candidate validation failure
- **THEN** no repair prompt receives that failure and the controller retains terminal/retry ownership

### Requirement: Evidence-intake live calibration binds an explicit profile to an admitted Bundle

Each selected case in the existing Wave0/Wave1 evidence-intake live calibration corpus
SHALL resolve exactly one registered explicit demo profile before it constructs the
focused production bridge. It SHALL create a fresh test-owned Run Bundle through the
existing Bundle admission path, establish that Bundle's Event Journal, and bind the
resulting `SelectedBundleContext` through the existing production node dependency seam
before the branch invocation. A missing selected context, unavailable Bundle,
absent/unknown/non-unique profile, or missing branch prerequisite SHALL fail before
provider invocation and produce no rubric result.

The selected calibration SHALL invoke only its named generated branch request through
the real production model/tool bridge, then evaluate its existing production parser and
applicable local semantic validation without submitting a candidate to a ledger, gate,
route, critic, or full-pipeline lifecycle. A selected Wave0/Wave1 worker or repair case
that reaches its candidate parser SHALL classify the final response at that same
boundary and record the correlated closed response shape and canonical validation codes
in the selected Bundle Journal. A selected SourceDiagnostic or ClaimVerifier case SHALL
retain its existing typed parser/rubric boundary and SHALL NOT fabricate a worker-local
response-shape or validation fact. Supported read-only Journal inspection SHALL verify
the profile provenance and any branch-applicable validation facts. A failed hard
invariant or candidate validation SHALL be a live-run failure without a rubric
disposition. The calibration SHALL not retain a raw prompt, model response, tool result,
exception text, provider body, URL, or artifact path in its report or Bundle Journal,
and it SHALL not claim full-pipeline, source-quality, evidence-acceptance, or
profile-quality success. (`EVH-030`)

#### Scenario: A selected worker calibration reaches the production bridge with Bundle authority
- **WHEN** an operator selects one named Wave0 or Wave1 worker calibration with one
  explicit profile and all required live credentials
- **THEN** it creates and binds a fresh selected Bundle before invocation, executes only
  the named branch through the real bridge, and inspects that Bundle's safe Journal
  facts without constructing a work-unit submission or full research run

#### Scenario: Missing Bundle selection fails before a live model call
- **WHEN** a selected evidence-intake calibration cannot establish its selected Bundle
  context before dependency resolution
- **THEN** it fails its hard invariant before provider invocation and records no rubric
  result or inferred candidate outcome

#### Scenario: A real prose result is an attributable live failure
- **WHEN** a selected worker returns final prose or another non-admissible response
  shape after its permitted live tool turn
- **THEN** the calibration fails without a rubric disposition and the selected Bundle
  exposes only the correlated profile, closed response shape, and canonical validation
  facts needed to diagnose it

#### Scenario: Selected critic calibration does not invent a worker boundary
- **WHEN** a selected SourceDiagnostic or ClaimVerifier case reaches its existing typed
  parser and rubric boundary
- **THEN** it remains Bundle- and profile-bound but emits no worker-local response-shape
  or validation fact that the critic branch did not reach

### Requirement: Evidence-judgment calibration has branch-specific judgment evidence

Test-owned evidence SHALL define a third dedicated twelve-case labeled calibration corpus: one
normal and one highest-risk case for each Wave2 synthesis, Wave2 synthesis repair, targeted worker,
targeted worker repair, targeted SourceDiagnostic, and targeted ClaimVerifier branch. It SHALL be
separate from the intake-and-planning and evidence-intake calibration corpora, canonical
`LIVE_CANARIES`, and the lane-neutral `ScenarioCase` registry. Each case SHALL declare stable
identity, bounded assignment, rubric, degradation, nondeterministic boundary, and resource limits.
Rubrics SHALL assess only an assignment-faithful, evidence-grounded, uncertainty-conservative,
provenance- or identity-bound candidate that is decision-ready for its deterministic owner. They
SHALL not assert source truth, research quality, evidence acceptance, publication, gate correctness,
route correctness, or a model judgment from a deterministic fixture.

Each branch SHALL retain lowest-seam deterministic proof. A selected targeted-worker calibration
SHALL preflight model and web credentials and invoke only its generated request through a real
model-and-web bridge. A selected zero-tool branch SHALL preflight model credentials and invoke only
its generated request through a real model-only bridge. Tool posture, resource bounds, real bridge
success, and production parsing SHALL be hard invariants; their failure SHALL receive no rubric
disposition. Typed rubric results SHALL resolve only through the closed three-corpus union with
globally unique case identity and matching branch/criterion tuple. Reports without a rubric result
SHALL remain readable. Default deterministic verification SHALL not execute this live evidence, and
the existing corpus identities and six canonical live canaries SHALL remain unchanged.

#### Scenario: Deterministic conformance does not claim evidence-judgment quality
- **WHEN** a fake-capability Wave2 or targeted-evidence case proves request composition, tool posture,
  repair/review bounds, and deterministic non-admission
- **THEN** its evidence is deterministic conformance and does not claim a useful model judgment

#### Scenario: Selected live calibration preflights branch dependencies strictly
- **WHEN** a selected targeted-worker case lacks model or web credentials, or a selected zero-tool
  case lacks model credentials
- **THEN** preflight fails before invocation without recording a quality result or widening tools

#### Scenario: Each selected live calibration reports only its bounded result
- **WHEN** credentials and all branch hard invariants succeed for a selected case
- **THEN** it records only the named branch and typed rubric result without changing acceptance,
  publication, ledger, gate, or route ownership

#### Scenario: Failed branch mechanics do not receive a quality rubric
- **WHEN** a selected branch violates tool/resource bounds, bridge execution, or production parsing
- **THEN** the selected run fails without a `pass`, `limited`, or `inconclusive` rubric disposition

#### Scenario: Closed calibration collections preserve prior report and canary governance
- **WHEN** deterministic verification, evidence-v1 report validation, and canary validation run
- **THEN** all three calibration corpora remain excluded from deterministic execution, a rubric
  resolves to one unique case, old reports remain readable, and canaries retain six cases

#### Scenario: Rubric disposition is not a hidden retrieval or retry
- **WHEN** a mechanically valid selected candidate cannot satisfy every declared criterion
- **THEN** it records `limited` or `inconclusive` without a model call, retrieval, production retry,
  lifecycle fact, or route claim

### Requirement: Readiness critic activation has distinct conformance and judgment evidence

The active readiness critic branch SHALL retain separate collected evidence for
deterministic request/policy/candidate/route conformance and for bounded answerability
judgment. Scripted zero-API tests SHALL exercise the real readiness request, Node Agent
policy, candidate validation, conservative failure projection, materializer, and route
owner without claiming model quality. A separate bounded labeled evaluation corpus
SHALL assess supported, insufficient, and repair-required answerability judgments;
credentialed live execution is supplemental, explicitly selected, and reports only its
declared judgment disposition.

#### Scenario: Scripted conformance does not claim judgment quality
- **WHEN** a scripted readiness critic completes through the real policy and node path
- **THEN** its evidence claim is deterministic workflow conformance and not a live
  answerability-quality result

#### Scenario: Labeled answerability evaluation remains bounded
- **WHEN** a selected readiness evaluation case is assessed
- **THEN** it declares its question/evidence boundary, expected verdict class,
  criterion, permitted degradation, and whether live execution produced an assessable
  candidate without asserting evidence truth or research quality

#### Scenario: Failure projection has a direct deterministic proof
- **WHEN** model, policy, or structured-output failure is injected at the readiness
  branch seam
- **THEN** a collected deterministic test proves it cannot produce an all-ready result
  or bypass the existing repair/terminal owners

### Requirement: Final composition activation has distinct conformance and judgment evidence

The active final-delivery composer branch SHALL retain separate collected deterministic
evidence for request/policy/candidate/admission/publisher/gate conformance and a
bounded labeled corpus for report-composition judgment. Scripted zero-API tests SHALL
not claim report usefulness. Selected credentialed execution SHALL be supplemental,
explicitly preflighted, and report only its declared composition disposition without
changing publication, lifecycle, or route authority. (`EVH-022`)

#### Scenario: Scripted composition does not claim report quality
- **WHEN** a scripted composer completes through the real policy and final-node path
- **THEN** its evidence claim is deterministic workflow conformance rather than a
  useful-report or research-quality judgment

#### Scenario: Labeled composition evaluation remains bounded
- **WHEN** an operator selects a final-composition evaluation case
- **THEN** it declares its plan/evidence boundary, exact plan-text/citation-binding
  preservation criterion,
  permitted degradation, and assessable-candidate disposition without asserting source truth

#### Scenario: Candidate failure has direct deterministic proof
- **WHEN** a composer model, policy, parser, or bounds failure is injected
- **THEN** a collected deterministic test proves it cannot publish an artifact or
  bypass the existing final gate and publisher owners

### Requirement: Evidence consolidation preserves named risks without a count target

Any proposed retirement or replacement of a collected test-evidence selector SHALL be
represented by a typed consolidation decision before deletion. The decision SHALL
identify the displaced claim and selector, every affected requirement and named risk,
and the collected retained claim or claims that continue to prove each risk at the
lowest responsible seam. A retained claim at a different seam, authenticity level, or
evidence class SHALL include a bounded rationale for why the original risk remains
proved without overclaiming model judgment or workflow authenticity. A retention-only
suspension that keeps the original source but removes it from active collection and
evidence is not a consolidation replacement: it SHALL be governed by an owning
requirement, SHALL not map its full-real risk to a lower-authenticity claim, and SHALL
not represent the suspended selector as current coverage. (`EVH-023`)

Validation SHALL reject an unknown or uncollected displaced/replacement claim, an
unmapped requirement or risk, self-replacement, a replacement that does not own the
mapped requirement, any seam/evidence-class/authenticity difference without
justification, and any proposal justified only by aggregate test count, directory
placement, marker, or line coverage. An evidence board or consolidation decision SHALL
not itself delete a test or authorize deletion. This change's accepted retirement set
SHALL be empty.

#### Scenario: Unmapped deletion or replacement is rejected
- **WHEN** a consolidation candidate deletes or replaces a selector without mapping
  every affected requirement and named risk to collected retained proof
- **THEN** deterministic evidence governance rejects the decision before any test is
  deleted or any requirement is presented as covered

#### Scenario: Retained suspension cannot impersonate a replacement
- **WHEN** a tracked selector is suspended from every active execution and evidence
  surface without being deleted or replaced
- **THEN** the owning suspension requirement retains the source and its diagnostic
  boundary without asserting that lower-authenticity or historical material proves the
  suspended selector's current full-real risk

#### Scenario: Aggregate count cannot justify consolidation
- **WHEN** a consolidation candidate cites only a desired pytest total, marker balance,
  directory placement, line coverage, or an aggregate passing selector
- **THEN** validation rejects it because no displaced risk has been preserved at its
  responsible seam

#### Scenario: Different evidence metadata remains bounded
- **WHEN** retained proof uses a different seam, authenticity level, or evidence class
- **THEN** the decision explains that exact difference and gives a bounded reason the
  replacement preserves the original named risk without claiming a universal strength
  ordering or model quality from deterministic evidence

#### Scenario: Governance rollout deletes no tests
- **WHEN** this evidence-board change is applied
- **THEN** the retirement decision set is empty and every currently collected test
  remains present, regardless of the resulting aggregate count

### Requirement: Suspended credentialed selectors remain retained but inactive

A credentialed `FULL_REAL_PIPELINE` selector that is presently unsuitable for an
ordinary automation loop SHALL remain tracked under
`deep_research_harness/tests/scenarios_suspended/` rather than be deleted or
represented as passing evidence. Its non-test filename SHALL exclude it from ordinary
pytest discovery, and its retained `release_e2e` marker SHALL remain excluded from
every active test lane. Active Make targets, GitHub workflows, focused lane selection,
and active evidence registries SHALL not invoke, select, or claim the suspended
selector as current release evidence.

The local suspended-scenarios record SHALL link to the single diagnostic issue that
owns its repair and state the reactivation precondition. Reactivation SHALL require a
new approved OpenSpec change and a deterministic diagnostic loop that completes in
less than ten seconds before another credentialed execution is authorized. (`EVH-024`)

While the selector is suspended, the active requirement-evidence policy SHALL not
require a current full-real release claim. The retained source and any versioned
redacted attestation are historical diagnostic material; neither SHALL be treated as a
collected replacement claim or as evidence of a current successful release.

#### Scenario: Ordinary automation excludes a retained selector
- **WHEN** a contributor runs ordinary pytest collection or an active Make or GitHub
  workflow test lane
- **THEN** the retained suspended selector is neither collected nor selected, while its
  active deterministic control-plane evidence remains collected

#### Scenario: A later release reactivation is proposed
- **WHEN** a contributor wants to run the retained credentialed selector again
- **THEN** a new approved OpenSpec change first supplies the linked issue's
  less-than-ten-second deterministic diagnostic loop and then defines any authorized
  credentialed execution

### Requirement: The singular release acceptance proves a model-led first-party smoke path

The retained `release-full-real-acceptance` scenario SHALL remain the sole
`FULL_REAL_PIPELINE` release-acceptance definition. It SHALL begin with the fixed
Chinese request to prepare a Python 3.12 upgrade checklist using Python official
documentation, wait for the model-led HITL1 proposal, and submit a natural-language
confirmation before using the existing remaining lifecycle path. It SHALL not inject a
hand-authored profile payload or create another release runner.

For this scenario only, the test-owned live web adapter and release assertion SHALL
admit only the declared canonical Python 3.12 source set. A successful release outcome
SHALL retain the confirmation handoff and verify a non-empty Chinese final report with
at least three cited claim bindings from at least two distinct URLs in that source set.
The selector is retained in the suspended-scenarios surface and has no active
credentialed release lane, Make target, GitHub workflow, focused release-evidence
category, or `FULL_REAL_PIPELINE` evidence claim. It SHALL not be presented as a
current successful release acceptance. The network-free tests cover the fixed
interaction and source-set admission seams without claiming that a live run proves
general research quality. The current Harness structural/lifecycle change closes its
deterministic Bundle-authority migration with those tests; a successful credentialed
execution remains a separately tracked diagnostic issue and is not this change's
archive prerequisite.

The runner SHALL call the same trusted public Deep Research entry as a user-facing
execution and obtain lifecycle, report, citation, containment, and terminal facts only
from the selected available Run Bundle and its Bundle-local State. It SHALL not pass or
derive a `research_id`, compile or inspect a Deep Research GraphHost snapshot, select
an external checkpoint, or infer an outcome from a workspace-derived report path. A
missing or unreadable selected Bundle SHALL fail a future authorized release attempt
rather than cause legacy recovery or result inference. (`EVH-024`)

#### Scenario: A reactivated release proof remains Bundle-authoritative
- **WHEN** a later approved change explicitly reactivates the credentialed full-real
  release selector
- **THEN** its one public-entry execution carries only the selected opaque `bundle_id`
  through trusted control context, and its report/citation assertions observe the
  selected Bundle without a session, checkpoint, GraphHost, or workspace fallback

### Requirement: Deterministic evidence proves Run Bundle lifecycle authority and loss boundaries

The deterministic evidence corpus SHALL retain collected zero-API cases at the lowest
responsible lifecycle/store/adapter seams for fresh opaque Bundle publication,
one-active admission, Current Bundle Handle continuation, absent-handle scoped
discovery, safe refinement ordering, ended-Bundle reactivation, Bundle loss,
no-external-recovery, cross-conversation isolation, and Cognitive Evaluation separation.
Each case SHALL invoke a real focused production interface with typed inputs and assert
the Bundle-local State/content or typed lifecycle outcome it owns. Static path scans,
mocked presentation dictionaries, test counts, and live-provider success SHALL not
substitute for this evidence. (`EVH-025`)

#### Scenario: Deleted Bundle case proves no external recovery
- **WHEN** a deterministic lifecycle case deletes a selected Bundle while a legacy checkpoint/session/binding observation remains available
- **THEN** it observes a typed unavailable result, no replacement State/directory, and no use of the external observation as lifecycle authority

### Requirement: Verification and evidence paths use the canonical Harness root

The complete deterministic verification command, requirement/evidence registries,
source ownership scans, architecture checks, Docker/profile contract tests, and release
path protections SHALL use `deep_research_harness/` as the sole downstream physical
root. They SHALL preserve the existing distinct fast, integration, workflow, live, and
release evidence classes and SHALL reject stale protected-path or source-root references
that could omit the moved downstream surface. (`EVH-026`)

#### Scenario: Root-sensitive governance cannot pass from the former path
- **WHEN** a test/evidence/architecture rule is pointed at `deerflow_research/` after the move
- **THEN** its focused detector test fails rather than silently collecting an empty or mis-scoped surface

### Requirement: Wave0 cognitive-program evidence is closed, deterministic, and non-live

The evaluation harness SHALL accept one closed `wave0_cognitive_program` case family
for versioned Wave0 source-intake cognitive evidence. Its fixture SHALL contain exactly
normal bounded retrieval handoff, adversarial retrieved instruction, retrieval
shortfall, malformed initial candidate with one repair, and post-candidate validation
rejection. Every scenario SHALL declare expected Wave0 capability ids, bounded
assignment fragments, forbidden control effects, and a non-empty unique set of
criterion IDs. Those IDs are Case-control-integrity metadata: deterministic registry
admission validates the selected Rubric's declared identity/version and the scenarios'
unique criterion-ID set before subject construction. They SHALL NOT carry criterion
prose, weights, thresholds, evaluator guidance, or a quality disposition into the Wave0
execution subject or model-facing input. The evaluator SHALL reject missing or duplicate scenario, capability,
runtime-control, or criterion-ID metadata, and SHALL bind the two Wave0 capability
resources and existing worker schema sources by project-relative sha256 controls.

The registered deterministic subject SHALL construct each declared scenario through
the production Wave0 node/controller boundary with fresh scenario-local dependencies,
the real runtime bridge, and scripted external model/tool adapters. It SHALL establish
only exact resource loading, runtime tool/candidate handoff, pre-candidate repair
placement, and deterministic source-admission non-bypassability. The family SHALL not be admitted to
the selected-live entrypoint. A selected-live request for it SHALL fail before creating
a run, manifest, review, provider call, or credentialed-live quality layer; neither
the deterministic family nor its review is a source-quality, release, lifecycle, or
route claim.

#### Scenario: Closed Wave0 corpus rejects incomplete controls
- **WHEN** a Wave0 cognitive-program case omits a required scenario or contains
  duplicate capability, runtime-control, or criterion-ID metadata
- **THEN** evaluation admission rejects the case before subject construction or any
  model, tool, artifact, ledger, or review activity

#### Scenario: Wave0 criterion IDs cannot become quality input
- **WHEN** a Wave0 case is admitted after its criterion IDs match the selected Rubric control
- **THEN** any retained criterion IDs are non-model control metadata and are not
  interpreted as scoring, quality instruction, or a verdict; the subject receives no
  criterion prose, weights, thresholds, evaluator guidance, or quality disposition
  from that Rubric

#### Scenario: Deterministic scenarios retain Wave0 admission boundaries
- **WHEN** the registered Wave0 cognitive-program subject executes every declared
  scenario with scripted external observations
- **THEN** each uses fresh production node/controller dependencies and the real runtime
  bridge with scripted external adapters, and establishes only its declared resource,
  tool/candidate, repair, or validation-isolation handoff without fabricated accepted
  coverage, source truth, retry, gate, route, or State authority

#### Scenario: Deterministic corpus cannot enter selected live evidence
- **WHEN** a caller selects the Wave0 cognitive-program case through the selected-live
  entrypoint
- **THEN** admission fails before a runs root, manifest, review, provider call, or
  credentialed-live evidence layer is created

### Requirement: Wave1 cognitive-program evidence is closed, deterministic, and non-live

The evaluation harness SHALL accept one closed `wave1_cognitive_program` case family
for versioned Wave1 extraction/repair cognitive evidence. Its fixture SHALL contain
exactly normal bounded retrieval handoff, adversarial retrieved instruction, accepted
Wave0-baseline duplicate containment, malformed initial candidate with one parser
repair, local-semantic candidate rejection with one repair, and post-candidate
submission-validation rejection. Each scenario SHALL bind only the Wave1 extraction or
repair capability ids needed by its branch, closed trusted assignment/baseline data,
bounded untrusted observations or draft, forbidden effects, and a non-empty unique set
of criterion IDs. Those IDs are Case-control-integrity metadata: deterministic registry
admission validates the selected Rubric's declared identity/version and the scenarios'
unique criterion-ID set before subject construction. They SHALL NOT carry criterion
prose, weights, thresholds, evaluator guidance, or a quality disposition into the
Wave1 execution subject or model-facing input.

The case execution plan SHALL bind the two capability digests and Wave1 worker-schema
digest. Every scenario SHALL invoke fresh production Wave1 node/controller dependencies
and the real runtime bridge with scripted external adapters. The fixture and adapter
SHALL establish only declared deterministic handoff, method, tool-posture, and
authority-boundary evidence. They SHALL NOT claim source quality, provider behavior,
selected-live eligibility, release status, source/claim admission, critic outcome,
controller retry, gate, route, or State authority.

The `wave1_cognitive_program` case SHALL remain absent from selected-live admission.
A selected-live request for it SHALL fail before creating a runs root, manifest, review,
subject, provider invocation, or credentialed-live evidence layer.

#### Scenario: Closed Wave1 corpus rejects incomplete or over-broad controls
- **WHEN** a Wave1 cognitive-program case omits a required scenario, duplicates a
  capability/runtime-control/criterion-ID identity, or declares a SourceDiagnostic,
  ClaimVerifier, provider, or web dependency
- **THEN** evaluation admission rejects the case before subject construction or any
  model, tool, artifact, ledger, review, or live-evidence activity

#### Scenario: Wave1 criterion IDs cannot become quality input
- **WHEN** a Wave1 case is admitted after its criterion IDs match the selected Rubric control
- **THEN** any retained criterion IDs are non-model control metadata and are not
  interpreted as scoring, quality instruction, or a verdict; the subject receives no
  criterion prose, weights, thresholds, evaluator guidance, or quality disposition
  from that Rubric

#### Scenario: Deterministic Wave1 scenarios preserve the extraction boundary
- **WHEN** the registered Wave1 cognitive-program subject executes every declared
  scenario with scripted external observations
- **THEN** each uses fresh production node/controller dependencies and the real runtime
  bridge with scripted adapters, and establishes only its declared exact-resource,
  bounded-prompt, baseline/repair, and post-validation-isolation facts

#### Scenario: Wave1 deterministic corpus cannot enter selected live evidence
- **WHEN** a caller selects the Wave1 cognitive-program case through the selected-live
  entrypoint
- **THEN** admission fails before a runs root, manifest, review, provider call, or
  credentialed-live evidence layer is created

### Requirement: Wave2 cognitive-program evidence is closed, deterministic, and non-live

The evaluation harness SHALL accept one closed `wave2_cognitive_program` case family
for versioned Wave2 initial-synthesis and structured-repair evidence. Its fixture
SHALL contain exactly normal accepted-evidence synthesis, unsupported or
instruction-like evidence containment, honest-gap/uncertainty judgment paired with a
backed finding, malformed initial candidate with one repair, and invalid repaired
candidate non-publication. Each scenario SHALL bind only the needed Wave2 capability
id, closed trusted assignment/evidence data, bounded untrusted draft or evidence,
forbidden effects, and a non-empty unique set of criterion IDs. Those IDs are
Case-control-integrity metadata: deterministic registry admission validates the
selected Rubric's declared identity/version and the scenarios' unique criterion-ID set
before subject construction. They SHALL NOT carry criterion prose, weights, thresholds,
evaluator guidance, or a quality disposition into the Wave2 execution subject or
model-facing input.

The case execution plan SHALL bind both Wave2 capability digests and the
`SynthesisResult` schema digest. Every scenario SHALL use fresh production Wave2
node dependencies and the real zero-tool runtime bridge with scripted adapters. The
fixture and adapters SHALL establish only exact-resource, bounded-prompt,
accepted-evidence, repair, and deterministic-admission evidence. They SHALL NOT
claim provider quality, selected-live eligibility, artifact admission, gap routing,
gate outcome, lifecycle, or State authority.

Where a valid scripted candidate passes the real node's existing internal
materializer/preview path, its scenario adapter SHALL use a fresh contained Bundle
dependency and SHALL NOT record that write, preview, or any later gate result as a
corpus proof claim. An invalid repaired candidate MAY establish its required
non-publication fact by observing the absence of that write. This distinction does
not alter the production materializer, preview, gate, or lifecycle owner.

The `wave2_cognitive_program` family SHALL remain absent from selected-live
admission. A selected-live request for it SHALL fail before creating a runs root,
manifest, review, subject, provider invocation, or credentialed-live evidence layer.
(`EVH-029`)

#### Scenario: Closed Wave2 corpus rejects incomplete or over-broad controls
- **WHEN** a Wave2 cognitive-program case omits a required scenario, duplicates a
  capability/runtime-control/criterion-ID identity, or declares a provider, web, targeted
  evidence, readiness, gate, or route dependency
- **THEN** evaluation admission rejects the case before subject construction or any
  model, tool, artifact, preview, gate, review, or live-evidence activity

#### Scenario: Wave2 criterion IDs cannot become quality input
- **WHEN** a Wave2 case is admitted after its criterion IDs match the selected Rubric control
- **THEN** any retained criterion IDs are non-model control metadata and are not
  interpreted as scoring, quality instruction, or a verdict; the subject receives no
  criterion prose, weights, thresholds, evaluator guidance, or quality disposition
  from that Rubric

#### Scenario: Deterministic Wave2 scenarios preserve the cognitive boundary
- **WHEN** the registered Wave2 cognitive-program subject executes every declared
  scenario with scripted accepted evidence and model output
- **THEN** each uses fresh production node dependencies and the real zero-tool bridge,
  and establishes only its declared resource, prompt, grounding, repair, deterministic
  admission, and invalid-candidate non-publication facts; a successful internal write,
  preview, or gate result is not a corpus claim

#### Scenario: Honest uncertainty remains distinct from a gaps-only rejection
- **WHEN** the closed Wave2 corpus supplies accepted evidence to its honest-gap scenario
- **THEN** that candidate contains at least one finding backed by the assigned evidence
  together with the bounded gap, while a gaps-only candidate follows the existing
  repair or invalid-repair path and cannot substitute for the uncertainty scenario

#### Scenario: Wave2 deterministic corpus cannot enter selected live evidence
- **WHEN** a caller selects the Wave2 cognitive-program case through the selected-live
  entrypoint
- **THEN** admission fails before a runs root, manifest, review, provider call, or
  credentialed-live evidence layer is created
