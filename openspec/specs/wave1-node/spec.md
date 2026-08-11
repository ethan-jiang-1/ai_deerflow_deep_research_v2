# wave1-node Specification

> req: WON-001, WON-002, WON-003, WON-004, WON-005, WON-006, WON-007, WON-008, WON-009, WON-010, WON-011, WON-012

## Purpose
Deep per-topic evidence extraction with new-source floor, structured claims, critic integration, and provenance-aware gate.

## Requirements


### Requirement: Wave1 planner materializes per-topic evidence WorkSpecs

The Wave1 planner SHALL read profile constraints and Wave0 accepted submission
records for the same research generation to materialize one immutable evidence
`WorkSpec` per topic through the existing work-unit controller. Each WorkSpec SHALL
carry search dimensions derived from the topic's must-answer bindings and Wave0
coverage gaps. Before every real Wave1 worker request, the phase SHALL derive its
Wave0 baseline from canonical URLs in those accepted records, not from checkpoint
hashes or an empty replacement set. An empty or absent Wave0 topic registry, an
unavailable required accepted record, or a cross-generation record SHALL fail closed
before worker dispatch.

#### Scenario: One WorkSpec per topic from planner
- **WHEN** real Wave1 runs after real Wave0 produced accepted submissions
- **THEN** the controller allocates one WorkSpec per topic with search dimensions and a derived spec_hash

#### Scenario: Empty Wave0 registry fails closed
- **WHEN** real Wave1 runs but Wave0 produced no accepted submissions
- **THEN** the planner fails before allocating work rather than inventing topics

#### Scenario: Top-level worker receives the accepted Wave0 baseline
- **WHEN** real Wave1 invokes a worker after Wave0 accepted a canonical source URL for the same research generation
- **THEN** the worker receives that URL in its bounded baseline and a duplicate returned URL is not admitted as new coverage

#### Scenario: Baseline cannot be reconstructed from checkpoint hashes
- **WHEN** the checkpoint contains an accepted-record hash but its authoritative Wave0 submission record is unavailable or belongs to another generation
- **THEN** the real phase fails before worker dispatch and does not substitute an empty baseline

### Requirement: Deep evidence worker with new-source floor

For each in-flight WorkSpec, Wave1 SHALL run one bounded web worker agent through
`capabilities.run_agent()` under a real `ExecutionPolicy` with web search tools and
attempt-scoped roots. The initial request SHALL require exactly one web search tool
call, use its multiple returned candidates as the evidence set, and retain later model
turns for a final structured answer. The worker SHALL produce a versioned
`Wave1WorkerOutput` carrying claims (each with `claim_id`, `statement`, `support_refs`,
`counter_refs`), open questions (with resolution states), and per-source
`is_new_vs_wave0` marking. Before writing any source/result artifact, the Wave1-local
semantic validator SHALL require every claim support/counter reference to identify a
source declared by that same worker output, each canonical URL to occur exactly once,
and the assigned-baseline new-source floor to be met. A draft that violates those
conditions SHALL enter the existing bounded structured repair path; a tool/budget stop
or still-inadequate repair SHALL fail closed. All fetched content is untrusted data,
and the worker SHALL NOT write phase, gate, ledger, or another attempt's state.

#### Scenario: Tool window reserves a final answer turn
- **WHEN** the Wave1 worker invokes its initial bounded request
- **THEN** it requires and permits exactly one web search call and retains the existing separate zero-tool structured repair

#### Scenario: Tool-only exhaustion publishes no authority
- **WHEN** the provider returns only tool calls through the bounded request without a successful structured draft
- **THEN** the attempt fails without source/result artifacts or a submission-ledger record

#### Scenario: Worker produces structured claims with provenance
- **WHEN** a Wave1 worker fetches new sources and extracts claims
- **THEN** each claim carries support_refs and counter_refs referencing only sources declared by this worker, and is_new_vs_wave0 distinguishes new from Wave0-duplicate URLs

#### Scenario: Foreign claim source reference is repaired before admission
- **WHEN** a worker output names a support_ref or counter_ref absent from its declared sources
- **THEN** no candidate or source/result artifact is admitted from that draft and the existing zero-tool structured repair receives the bounded malformed draft

#### Scenario: Wave0-duplicate URL does not count as new
- **WHEN** a worker fetches a URL already present in Wave0 accepted submissions
- **THEN** the source is marked is_new_vs_wave0=false and does not count toward the two-source floor

#### Scenario: Open questions have resolution states
- **WHEN** a worker identifies an open question
- **THEN** it is recorded with a state of resolved, targeted-search, deferred, or requires-internal-data

### Requirement: Submit validation enforces new-source floor and invokes critics

Before any source/result artifact or candidate is written, Wave1 SHALL canonicalize
the worker draft's URLs, reject duplicate canonical URLs, derive newness from its
assigned Wave0 baseline, and require both claim provenance and at least two distinct
canonical new URLs. A provenance, uniqueness, or floor violation SHALL enter the
existing bounded structured repair; an inadequate repaired draft emits no source/result
or candidate artifact. Contract-specific submit validation SHALL independently parse
the persisted `Wave1SourceIntakeResult`, reconstruct same-generation accepted Wave0
URLs from its supplied accepted records, verify each persisted `is_new_vs_wave0`
marker against that baseline, and repeat canonical uniqueness, provenance, and the
two-new-URL floor before a `SubmissionRecord` is appended. Its failure SHALL use the
existing typed validation outcome and append no record. After a Wave1 candidate is
accepted, the Wave1 phase SHALL invoke independent local SourceDiagnostic and
ClaimVerifier critics for that accepted work/attempt. Each critic SHALL receive only a
bounded assignment reconstructed from the accepted Wave1 result: SourceDiagnostic
receives ordered new-source observations and ClaimVerifier receives ordered claims
plus assigned new-source identities. Tool results, candidate bodies, artifact paths,
checkpoint fields, and route data SHALL NOT be critic inputs.

Each typed critic result SHALL be materialized only after deterministic validation of
the accepted research/generation/work/attempt identity, record binding, input hash,
and exact source or claim coverage. The immutable review artifacts SHALL be scoped to
the accepted Wave1 work/attempt; they SHALL NOT be submission records, candidate
outputs, checkpoint state, or route authority. A failed, malformed, unbound, or
conflicting critic result SHALL produce no valid artifact. SourceDiagnostic and
ClaimVerifier SHALL use distinct required forbidden-tool capabilities, and the
existing runtime bridge SHALL remain the tool/budget/cancellation enforcer.

#### Scenario: Insufficient new sources reject candidate
- **WHEN** a candidate has fewer than two distinct canonical new-source URLs after deduplication
- **THEN** submit validation fails with a typed code and no SubmissionRecord is appended

#### Scenario: Pre-persistence semantic rejection writes no evidence
- **WHEN** an initial or repaired Wave1 draft has a foreign claim source reference, duplicate canonical URL, or fewer than two distinct new canonical URLs
- **THEN** the bounded structured repair receives the draft before any source/result or candidate artifact is written

#### Scenario: Critics invoked on accepted evidence
- **WHEN** a Wave1 submission is accepted
- **THEN** SourceDiagnostic and ClaimVerifier each receive only its accepted bounded assignment and write independently bound verdict artifacts when their typed result validates

#### Scenario: Invalid critic cannot publish authority
- **WHEN** a Wave1 critic invocation fails, returns malformed data, or references a source or claim outside its accepted assignment
- **THEN** no valid review artifact, submission record, checkpoint update, or route is published by that critic

### Requirement: Wave1 gate with provenance, coverage, and critic verdicts

The real Wave1 gate SHALL evaluate the shared `WorkUnitCompletionRule` before its
Wave1-specific review conditions. When structural work completion is satisfied, it
SHALL evaluate a bounded, validated, non-checkpointed review projection for every
accepted topic. The projection SHALL prove: at least two distinct canonical URLs with
`is_new_vs_wave0=true`; presence of both identity-bound SourceDiagnostic and
ClaimVerifier artifacts; and an open-question disposition in which every question is
`resolved`, `deferred`, or `requires_internal_data`. The projection SHALL contain no
candidate body, source body, artifact location, critic reason, checkpoint field, or
route authority, and gate rules SHALL perform no filesystem or network I/O.

The Wave1-specific rules SHALL make no independent decision while structural
completion is absent. A missing review artifact, insufficient new-source floor, or
`targeted_search` question SHALL produce the existing repairable gate outcome. A
malformed or unreconciled review projection SHALL fail before a business-gate pass,
repair, or route is emitted. Critic prose or verdict value SHALL not select a route.
The route map SHALL remain `{PASS: pass, REPAIR: repair, BLOCKED: exhausted}`.

#### Scenario: Missing critic verdict routes repair
- **WHEN** a topic has accepted submissions but lacks one valid bound SourceDiagnostic or ClaimVerifier artifact
- **THEN** the gate routes repair without admitting a pass

#### Scenario: Two distinct new sources satisfy the floor
- **WHEN** an accepted topic has two distinct canonical sources marked new versus Wave0, both valid review artifacts, and only allowed open-question states
- **THEN** the real Wave1 gate may pass after structural completion

#### Scenario: Unresolved question routes repair
- **WHEN** an accepted Wave1 result contains an open question in `targeted_search`
- **THEN** the gate routes repair without changing a worker or critic tool posture

#### Scenario: Review projection is bounded and validated before gate evaluation
- **WHEN** a review projection omits an accepted topic, exposes a disallowed field, or cannot reconcile with accepted records and their bound review artifacts
- **THEN** the phase fails at the deterministic validation boundary before a pass, repair, or route is emitted

#### Scenario: Repeated floor failure exhausts to blocked
- **WHEN** repair budget is exhausted and new-source floor remains unmet
- **THEN** the gate routes exhausted and the lifecycle terminates

### Requirement: Real Wave1 integrates into mixed graph off full real chain

Real Wave1 SHALL require `bootstrap=real`, `hitl1=real`, `topic_planning=real`,
`wave0=real`, and `targeted_evidence=real`. Selecting `wave1=real` without the full
chain SHALL fail before graph invocation. Topology is unchanged. Full-fake Wave1
remains deterministic and does not construct the node-agent bridge.

#### Scenario: Wave1 requires full real chain
- **WHEN** a recipe selects `wave1=real` without `wave0=real` or `targeted_evidence=real`
- **THEN** recipe construction fails with a typed dependency error

#### Scenario: Full-fake Wave1 remains unchanged
- **WHEN** the full-fake graph reaches Wave1
- **THEN** it runs the fixture work-unit path without constructing the node-agent bridge

### Requirement: Wave1 retains classified invocation causes through work-unit failure

Wave1 SHALL normalize every non-successful worker or repair invocation before it
reaches the existing work-unit controller. It SHALL retain the applicable closed
worker category and safe provider observation when known, and it SHALL leave retry,
aggregation, gate routing, and terminal projection with the existing controller.

#### Scenario: A Wave1 repair invocation fails with a known provider error
- **WHEN** a Wave1 structured-output repair invocation returns a safe non-success
  provider result
- **THEN** the worker emits a classified work-attempt failure preserving that safe
  cause rather than a generic `wave1_worker_repair_failed` error

### Requirement: Wave1 capability expands the assigned baseline exactly once

The real Wave1 initial and structured-repair requests SHALL bind distinct local
capabilities. The initial worker SHALL use its existing required tool policy for
exactly one retrieval call, treat model/tool material as untrusted, and produce
candidates whose source and claim references can be deterministically checked against
the assigned topic and Wave0 baseline. A baseline-duplicate URL SHALL not be admitted
as new coverage. Repair SHALL expose no model-visible tool and SHALL not add a source,
URL, claim, or open question absent from its bounded draft/tool observations. Existing
validator/controller/ledger and failure owners remain the only admission and outcome
authorities. (`WON-007`)

#### Scenario: One bounded search extends rather than re-fetches Wave0
- **WHEN** a scripted real Wave1 worker performs its initial request against an
  assigned Wave0 baseline
- **THEN** exactly one permitted retrieval occurs, any baseline duplicate is excluded
  from new coverage, and only validator-approved source/claim references can reach
  the existing submission ledger

#### Scenario: Zero-tool repair cannot invent evidence
- **WHEN** the Wave1 parser sends a malformed draft to its structured repair branch
- **THEN** the repair receives no model-visible tool and either returns a
  contract-valid candidate using only retained observations or reaches the existing
  non-admission outcome

### Requirement: Wave1 calibration preserves baseline-aware evidence and review boundaries

The existing Wave1 initial, repair, SourceDiagnostic, and ClaimVerifier policies
SHALL expose model-visible criteria for a bounded evidence candidate. The initial
policy SHALL distinguish the accepted Wave0 baseline from proposed new-source
coverage, retain its existing one-retrieval posture, and request claims whose
support and counter references are limited to the candidate's declared sources.
It SHALL make uncertainty and unresolved questions explicit rather than treating a
source title, URL, tool result, or critic-like conclusion as proof, acceptance, or a
gate result.

The repair policy SHALL be invoked only when the initial Wave1 summary cannot parse
into its typed worker output or fails local pre-persistence provenance, uniqueness, or
new-source-floor validation. It SHALL receive only the same topic and Wave0-baseline
projection rendered by the initial request, bounded invalid draft, retained
observations, and a compact subgraph-generated category; it SHALL not receive a raw
`WorkSpec`, attempt identity, checkpoint, ledger, or accepted record. The assignment
and category SHALL be bounded trusted context; the draft and observations SHALL remain
untrusted data. The category SHALL omit raw exception text, artifact paths,
checkpoint fields, ledger contents, review/gate data, and route data. Assignment and
category SHALL constrain repair only and SHALL not supply candidate evidence: in
particular, a baseline URL is not a permissible new source, claim, reference, or open
question. The repair SHALL use no tool and shall not add a source, URL, claim,
reference, or open question absent from the untrusted draft and retained observations.
A later post-candidate `SubmissionValidationFailure`, its codes, and
artifact-validation detail SHALL not invoke or enter repair. The two critic policies
SHALL receive only their existing accepted bounded assignments and return review
candidates scoped to the assigned source or claim identities. They shall not retrieve,
turn a review verdict into evidence admission, write an artifact, update a ledger,
choose a gate outcome, or select a route. The existing validator, work-unit controller,
review-artifact materializer, and gate remain the only owners of admission, recovery,
evidence publication, and routing.

#### Scenario: New evidence remains visibly distinct from the accepted baseline
- **WHEN** a Wave1 assignment includes accepted Wave0 baseline URLs and one bounded
  retrieval produces source candidates
- **THEN** the evidence candidate treats baseline duplicates as non-new, binds claims
  only to its declared source identities, and represents unsupported or unresolved
  material without claiming accepted coverage or a gate result

#### Scenario: Pre-persistence repair cannot broaden an evidence candidate
- **WHEN** an initial Wave1 evidence draft cannot parse into its typed worker output
  or fails local provenance, uniqueness, or new-source-floor validation before
  persistence
- **THEN** the repair request remains limited to the same assignment, draft,
  observations, and compact validation category; it excludes raw validator errors
  and authority-bearing state, and a still-invalid candidate follows the existing
  deterministic non-admission outcome

#### Scenario: Trusted baseline cannot become repaired evidence
- **WHEN** a Wave1 repair receives a bounded Wave0 baseline plus an untrusted draft
  or observation that asks it to promote a baseline URL into a new candidate
- **THEN** the baseline constrains newness only; the repair introduces no source,
  claim, reference, or open question absent from the untrusted draft and retained
  observations, and does not represent a baseline URL as new evidence

#### Scenario: Downstream submission validation does not invoke repair
- **WHEN** a constructed Wave1 candidate later receives a post-candidate
  `SubmissionValidationFailure`
- **THEN** its validation codes and artifact-validation detail do not enter a repair
  request, no `SubmissionRecord` is appended, and the existing controller terminal,
  retry, and gate path remains the only recovery owner

#### Scenario: Critics remain review-only and assignment-bound
- **WHEN** SourceDiagnostic or ClaimVerifier receives an accepted bounded assignment
- **THEN** its candidate classifies only the assigned identities and uncertainty,
  while invalid, incomplete, or out-of-assignment output cannot publish a review
  artifact, evidence record, gate result, checkpoint update, or route

### Requirement: Wave1 evidence work remains bound to its selected Run Bundle

Wave1 planning, worker evidence, WorkSpecs, submissions, and contained artifacts SHALL
use the selected runtime-bound Run Bundle context. They SHALL not accept or infer a
legacy research identity/path or use retained session/checkpoint data to select a work
root. Bundle loss SHALL prevent further evidence publication for that Run. (`WON-009`)

#### Scenario: Lost Bundle blocks later Wave1 evidence publication
- **WHEN** Wave1 has an accepted worker result but its selected Bundle is unavailable before publication
- **THEN** it publishes no artifact or replacement State and reports the typed unavailable outcome

### Requirement: Wave1 runtime capabilities own bounded baseline-aware extraction cognition

The real Wave1 worker SHALL bind distinct runtime-loaded local capability resources
for initial evidence extraction and one pre-persistence structural repair. Each
activated resource SHALL contain the reusable method for its bounded task: assignment
interpretation, one permitted retrieval or zero-tool posture, baseline-newness and
candidate-reference judgment, untrusted-data handling, uncertainty/open-question
handling, self-check, and completion condition. The final rendered context SHALL
contain the exact activated body; a duplicate method outside the resource SHALL not be
required to determine the worker procedure.

Outside the resource, Wave1 SHALL pass only the bounded topic/Wave0-baseline
assignment, closed output contract, repair category, and delimited untrusted draft or
retrieval observations. Runtime policy retains tool, root, call-budget, and
cancellation authority. Parser, local semantic validation, artifact writer, submit
validator, ledger, controller, critics, gate, retry, and routes remain deterministic
owners. A baseline URL SHALL not become new evidence; a capability SHALL not admit
evidence, write an artifact or ledger, invoke a critic, select a recovery, gate, route,
or State outcome.

#### Scenario: Production rendering supplies one exact extraction or repair method
- **WHEN** real Wave1 prepares an initial extraction or structural-repair invocation
- **THEN** its final rendered context contains the exact corresponding capability body
  and declared posture while assignment, contract, category, and untrusted data remain
  bounded projections

#### Scenario: Baseline and retrieval material remain constrained data
- **WHEN** assignment or retrieved text asks Wave1 to promote a baseline URL, widen a
  tool/path, admit evidence, or select a lifecycle outcome
- **THEN** the worker can return only a bounded candidate or limitation and existing
  deterministic owners retain newness, tool, artifact, ledger, critic, gate, and route
  authority

#### Scenario: Repair is bounded before persistence
- **WHEN** an initial candidate fails parser or local semantic validation
- **THEN** Wave1 invokes at most its existing one zero-tool repair with the same bounded
  assignment and retained untrusted observations, then rechecks the candidate through
  the existing deterministic path

#### Scenario: Post-candidate validation does not re-enter repair
- **WHEN** a parsed candidate later fails deterministic submission validation
- **THEN** Wave1 follows only the existing controller recovery and does not pass
  validation detail to the structural-repair capability

### Requirement: Wave1 worker programs expose one compact final output envelope

The real Wave1 initial evidence-extraction program and its existing one zero-tool
structural-repair program SHALL each make the same compact final completion envelope
visible to the model. The initial program SHALL state that it first completes exactly
its existing permitted retrieval work and then returns exactly one final JSON object,
with no markdown, prose, code fence, explanatory prefix, or trailing text. The repair
program SHALL state the same final JSON-only completion rule while retaining its
existing zero-tool posture.

For either program, the completion envelope SHALL specify a final object containing
exactly `schema_version`, `sources`, `claims`, and `open_questions`.
`schema_version` SHALL be `1`; `sources` SHALL contain at least two distinct URLs that
are new relative to the assigned Wave0 baseline, and each source item SHALL contain
exactly `source_id`, `canonical_url`, and `title`. Claims and open questions SHALL
retain their existing closed item shapes and reference constraints. Before returning
the final response, the program SHALL instruct a self-check of the closed key sets,
minimum new-source shape, baseline-newness constraint, and absence of placeholders,
prose, fences, authority claims, or prompt-description fields.

This completion envelope SHALL not alter the existing result schema, parser, local
semantic validation, provenance or new-source floors, submission validation, tool
window, budget, repair bound, controller retry, ledger, critics, gate, route, Bundle
lifecycle, or terminal outcome. (`WON-011`)

#### Scenario: Tool-bearing Wave1 worker completes in the closed envelope
- **WHEN** the initial Wave1 worker has completed its existing permitted retrieval
- **THEN** its completion instruction requires one standalone JSON object with only the
  closed Wave1 keys, while the existing parser, local semantic validator, and
  deterministic admission path remain the only way a returned candidate can affect
  evidence coverage

#### Scenario: Wave1 repair has the same closed final envelope without a tool
- **WHEN** the existing Wave1 parser or local semantic validator sends an initial draft
  to its one zero-tool repair
- **THEN** the repair receives no added tool or recovery authority and is instructed to
  return only the closed Wave1 JSON envelope before the existing parser, local
  validator, and non-admission path run

#### Scenario: Prohibited output forms remain explicit without adding a validator
- **WHEN** either Wave1 initial or repair completion envelope is rendered
- **THEN** it explicitly prohibits prose, fences, embedded objects, unlisted keys,
  literal placeholders, and baseline URLs represented as new evidence without changing
  which fields the existing parser and deterministic validators accept or reject

#### Scenario: Non-standalone or baseline-duplicate output remains non-admissible
- **WHEN** either Wave1 program returns prose, a code fence, an embedded object, or a
  candidate whose claimed new-source floor is supplied by an assigned baseline URL
- **THEN** the unchanged parser or local semantic validator rejects it through the
  current bounded path without accepting evidence or widening a retry

### Requirement: Wave1 retains closed response-shape and post-candidate validation evidence

For every Wave1 initial or repair result that reaches the existing parser or local
pre-persistence validation boundary, Wave1 SHALL classify the final response as exactly
one of `empty`, `prose`, `fenced`, `embedded_json`, or `json_object` and retain that
closed classification on its correlated Bundle-local Journal validation fact. `empty`
means no non-whitespace response; `fenced` means a response containing a Markdown code
fence; `json_object` means the complete trimmed response is a JSON object;
`embedded_json` means a non-standalone response contains a JSON object; and `prose`
covers every other non-empty response. The classification SHALL be a structural
observation only and SHALL not cause parsing, semantic validation, admission, repair,
or routing behavior to differ.

When a parser- and locally-valid Wave1 candidate later fails an existing deterministic
post-candidate submission or artifact validation boundary, Wave1 SHALL retain one
correlated `post_candidate` Journal validation fact containing only that boundary's
existing canonical code collection. It SHALL retain no raw response, draft, prompt,
tool observation, URL, artifact path, validation message, or exception text. A
post-candidate fact SHALL not enter the structural repair request or change the existing
controller retry, ledger, critic, gate, route, terminal, or lifecycle owner. (`WON-012`)

#### Scenario: A final prose response is distinguishable without being retained
- **WHEN** a Wave1 initial or repair result contains final prose after its model turn
- **THEN** the correlated Journal validation fact records `prose` and the existing
  canonical parser code without retaining the response body

#### Scenario: A parser-accepted candidate records a later validation failure safely
- **WHEN** a Wave1 candidate passes parsing and local semantic validation but fails
  deterministic submission or artifact validation
- **THEN** the Journal retains one correlated `post_candidate` fact with the existing
  canonical code collection, no repair request receives that code, and no submission is
  published
