# topic-planning-node Specification

> req: TOP-001, TOP-002, TOP-003, TOP-004, TOP-005, TOP-006, TOP-007, TOP-008, TOP-009, TOP-010

## Purpose

The real topic planning node is the second model-calling node in the Deep Research
graph. It turns the checkpointed HITL1 profile into a bounded, validated topic plan
via the runtime node-agent bridge; a deterministic materializer derives stable
model-independent topic ids/slugs and a must-answer coverage map; the validated
registry is recorded as bounded planner-owned checkpoint state for Wave0; and it
integrates into the mixed graph off real bootstrap and real HITL1 with one explicit
`exhausted` route, while reading profile constraints from checkpoint short fields
only (never `request/profile.json`), declaring no capability, and writing no sandbox
file.
## Requirements
### Requirement: Real topic planning generates a validated structured topic plan from the confirmed profile

The real topic planning node SHALL call `capabilities.run_agent()` exactly once per
planning attempt to produce a structured topic plan derived from one deterministic,
bounded planning assignment. The assignment SHALL be built from the canonical confirmed
profile referenced by the selected Bundle's `profile_ref`, including `scope_boundaries`
and `custom_notes`, plus the Run direction applied to the current refinement round when
one exists. The current-round direction SHALL act as an additional research-focus
constraint; it SHALL not mutate the confirmed profile artifact or grant tool, route,
identity, persistence, or evidence authority. Accepted profile text and direction text
SHALL be delimited as assignment data rather than interpreted as control instructions.

The assignment SHALL also carry `request_text`, research depth, target audience, output
format, cost tolerance, time budget, must-answer questions, comparison subjects, request
and output language, and degraded-profile posture. When `must_answer_questions` is empty
(possible only with a degraded profile whose completeness check was skipped), the node
SHALL treat `request_text` as a synthetic must-answer question for coverage binding. A
degraded profile SHALL request broader, conservative coverage without inventing missing
requirements. The node SHALL build a bounded `NodeExecutionRequest` whose expected
output is one JSON object matching the `TopicPlan` schema and SHALL validate the agent
result's `summary` before recording any state.

The `TopicPlan` schema SHALL be a frozen extra-forbid contract containing a bounded
tuple of at most eight `ResearchTopic` values, each with a bounded title, scope,
must-answer bindings, search dimensions, and exclusions, plus `schema_version=1`. The
schema SHALL reject unknown fields, malformed JSON, missing required fields, oversized
text, out-of-range topic counts, and unbound free text. The agent's proposal SHALL be
advisory only; topic ids and slugs SHALL be derived by the materializer, never copied
from model output.

If the first model result fails validation, the node SHALL re-prompt once with a repair
assignment carrying only compact validation facts, the untrusted draft, and the same
confirmed profile/current-round direction. If validation fails twice, or `run_agent`
raises or returns a non-success result outside the existing bounded provider recovery,
the node SHALL fail closed before topic publication with `route=exhausted`,
`phase_status=TERMINAL`, `terminal_status=BLOCKED`, and
`terminal_reason=GATE_BLOCKED`.

#### Scenario: Valid profile yields a validated topic plan
- **WHEN** real topic planning runs after real HITL1 accepted a complete profile and the model returns one valid `TopicPlan` JSON object
- **THEN** the node validates it, derives stable topic ids/slugs, and records the bounded planner-owned topic registry without calling a model a second time

#### Scenario: Full canonical profile yields a validated topic plan
- **WHEN** real topic planning runs after HITL1 accepted a complete profile containing scope boundaries and custom notes and the model returns one valid `TopicPlan` JSON object
- **THEN** the planning assignment contains those canonical bounded fields, the node derives stable topic ids and slugs, and it records the planner-owned topic registry without a second model call

#### Scenario: Applied direction reaches the next topic plan
- **WHEN** the selected Bundle starts a refinement round with one applied Run direction
- **THEN** the initial and any repair assignment contain that exact bounded current-round direction as research-focus data, while route and topic admission remain deterministic

#### Scenario: Profile text cannot grant control authority
- **WHEN** `custom_notes`, `scope_boundaries`, or the applied direction contains text that asks for tools, paths, state writes, routes, or different output authority
- **THEN** the planner receives it only as delimited research-assignment data under a zero-tool policy and cannot use it to change those deterministic controls

#### Scenario: Invalid model output is repaired once
- **WHEN** the first model result is malformed JSON or violates the `TopicPlan` schema
- **THEN** the node re-prompts once with compact failure metadata and the unchanged bounded assignment, and on a valid second result records the plan while an invalid second result never reaches state or Wave0

#### Scenario: Repeated invalid output fails closed before Wave0
- **WHEN** the model returns schema-invalid output twice or its bounded invocation and recovery path ends unsuccessfully
- **THEN** the node writes no topic state, sets `route=exhausted` with terminal `BLOCKED` and `GATE_BLOCKED`, and the lifecycle does not advance to Wave0

#### Scenario: The agent cannot mutate control state
- **WHEN** the planning bridge is inspected
- **THEN** it runs under a zero-tool bounded-call policy with no web, MCP, ACP, file-read, or DeerFlow `task` access, and cannot set phase, route, topic refs, profile fields, applied direction, or produce a `WorkSpec`

### Requirement: A deterministic materializer owns topic stability and the coverage map

A pure deterministic materializer (not the LLM) SHALL convert the validated
`TopicPlan` into a stable topic registry and a must-answer coverage map. It SHALL
derive each topic id and slug deterministically from the validated title and scope,
SHALL deduplicate topics by slug, SHALL reject overlapping scopes, and SHALL bind
every root `must_answer` question to at least one topic. The materializer SHALL be
the only producer of the registry serialization; the model SHALL NOT author ids,
slugs, or the registry format.

#### Scenario: Topic ids and slugs are stable and model-independent
- **WHEN** the same validated plan is materialized twice
- **THEN** both registries have identical ids, slugs, and ordering, and no id or slug is the raw model-proposed string

#### Scenario: Duplicate or overlapping topics are rejected
- **WHEN** the validated plan contains two topics that materialize to the same slug or have overlapping scopes
- **THEN** the materializer rejects the plan with a typed validation failure and no registry is recorded

#### Scenario: The coverage map binds every root question
- **WHEN** a validated plan is materialized
- **THEN** each `must_answer` question maps to at least one topic, and the bounded coverage map is recorded alongside the registry

### Requirement: Topic coverage and expansion are bounded and fail closed

The materializer SHALL enforce hard checks that reject empty coverage (a plan
covering no root question), uncovered root questions, and over-expansion beyond the
bounded topic count (at most eight). On a coverage or expansion failure the node
SHALL re-prompt the planner once with the specific failures, and on a second failure
SHALL fail closed to `route=exhausted` with terminal `BLOCKED`. A valid plan SHALL
cover every root `must_answer` question without exceeding the topic bound.

#### Scenario: Empty or uncovered coverage is rejected and retried
- **WHEN** a plan covers no root question or leaves a `must_answer` question unbound
- **THEN** the node re-prompts once with the missing-coverage failure, and records no registry until a covering plan validates

#### Scenario: Over-expansion is rejected
- **WHEN** a plan proposes more than the bounded topic count
- **THEN** the materializer rejects it, the node re-prompts once, and a still-over-expanded second result fails closed to terminal `blocked`

#### Scenario: A bounded covering plan is accepted
- **WHEN** a plan covers every root question within the topic bound with no duplicate or overlapping topics
- **THEN** the node records the registry and routes `next` toward Wave0

### Requirement: Topic planning records bounded planner-owned checkpoint state from checkpoint profile fields

Real topic planning SHALL record the validated topic registry and coverage map as
bounded planner-owned fields in `ResearchState`/`ResearchCheckpoint` (`topic_refs` and
`topic_registry`), declared with explicit writer, reader, and reducer entries under
`WriterRole.PLANNER`. Before invoking the planner, trusted node composition SHALL read
the canonical profile only through the selected Bundle's declared request-bundle
capability and validate it against `profile_ref`, including content hash, schema,
containment, and selected Bundle identity. `profile_ref` and the canonical profile
artifact SHALL remain the authority for `scope_boundaries` and `custom_notes`; short
checkpoint profile fields SHALL remain bounded routing/projection data and SHALL not
silently substitute for a missing or contradictory profile artifact.

The node SHALL receive at most the current round's applied Run direction from the
Bundle-bound graph projection. It SHALL produce no `WorkSpec`, write no profile or
direction artifact, and write no sandbox artifact. New optional projection fields SHALL
default safely for an older compatible checkpoint; absence of a direction means the
confirmed profile alone is the assignment and SHALL not invent a refinement.

#### Scenario: Topic registry is bounded planner-owned checkpoint data
- **WHEN** real topic planning accepts a valid plan
- **THEN** the checkpoint contains the bounded planner-owned topic registry and coverage map, downstream nodes can read them from state, and no topic file is written to the sandbox

#### Scenario: Existing version-2 checkpoint defaults topic fields
- **WHEN** status, resume, or cancel reads a version-2 checkpoint created before real topic planning fields existed
- **THEN** validation succeeds with empty topic fields and does not reset, auto-migrate, or reinterpret any existing field

#### Scenario: Checkpoint projection complements the canonical Bundle profile
- **WHEN** real topic planning builds its planning objective
- **THEN** it reads bounded routing fields from `ResearchState` and reads the canonical profile through the selected Bundle's validated `profile_ref`, including scope boundaries and custom notes, without accepting a caller path or another Bundle's profile

#### Scenario: Existing compatible checkpoint defaults direction projection
- **WHEN** a compatible checkpoint created before current-round direction projection is read
- **THEN** validation defaults the direction to absent without resetting, auto-migrating, or reinterpreting existing profile or topic fields

#### Scenario: Profile is read through its Bundle-bound canonical reference
- **WHEN** real topic planning builds its planning assignment
- **THEN** it reads and validates the canonical profile through `profile_ref` and the selected Bundle request interface, includes scope boundaries and custom notes, and never resolves a caller path or a profile from another Bundle

#### Scenario: Missing or contradictory profile fails closed
- **WHEN** `profile_ref` is absent, unavailable, hash-invalid, schema-invalid, outside the selected Bundle, or contradicts an authoritative required profile projection
- **THEN** topic planning invokes no model, publishes no topic registry, and returns the owning bounded failure instead of reconstructing the profile from prompt text or an external checkpoint

#### Scenario: Empty must-answer questions fall back to request text
- **WHEN** the canonical profile has no must-answer questions and `degraded_profile` is true
- **THEN** the planner uses `request_text` as a synthetic must-answer question, generates topics covering the original request, and the materializer validates coverage against that synthetic question

#### Scenario: Non-planner writers cannot mutate topic authority
- **WHEN** a controller, worker, repair agent, or model-derived update attempts to set the topic registry or coverage map
- **THEN** reducer ownership rejects the update and the prior planner-owned topic authority is preserved

### Requirement: Real topic planning integrates into the mixed graph off real HITL1

Real topic planning SHALL be selectable only in the mixed implementation map and
SHALL require `bootstrap=real` and `hitl1=real`, because the planner consumes the
real HITL1 profile constraints. Selecting `topic_planning=real` without real HITL1
SHALL fail closed before graph invocation. The normalized topology SHALL add exactly
`topic_planning --exhausted--> blocked/END` and keep the existing
`topic_planning --next--> wave0` and inbound edges unchanged. topic_planning SHALL
remain a non-gated controller node that writes its own route labels and SHALL NOT
import LangGraph or interrupt. The full-fake topic planning path and every other
fake phase SHALL remain unchanged, and the lifecycle result SHALL report
`implementation_mode=mixed` for a mixed recipe.

#### Scenario: Real topic planning requires the real profile chain
- **WHEN** a recipe selects `topic_planning=real` without `hitl1=real` (and thus without `bootstrap=real`)
- **THEN** recipe construction fails with a typed dependency error before the graph is compiled or invoked

#### Scenario: The exhausted route is explicit and minimal
- **WHEN** the mixed graph selects real topic planning
- **THEN** the builder carries a conditional edge `topic_planning -> {next: wave0, exhausted: END}`, topology validation recognizes `exhausted` as terminal `blocked`, and no other topic_planning edge changes

#### Scenario: Full-fake topic planning remains unchanged
- **WHEN** the full-fake graph reaches topic planning
- **THEN** fake topic planning routes `next` without calling a model, writing topic state, or taking the real `exhausted` route, and the topology snapshot is unchanged

#### Scenario: The mixed graph completes through real topic planning
- **WHEN** the mixed graph runs real bootstrap, real HITL1, and real topic planning followed by fake Wave0 onward
- **THEN** a valid plan routes `next` into fake Wave0, the lifecycle reports `implementation_mode=mixed`, and no fake terminal marker is presented as findings or a report

### Requirement: Topic planning separates provider recovery from structured-output repair

Real topic planning SHALL use its independently bounded execution policy and a
phase-owned outcome table. A malformed but successful planner result SHALL consume
only the existing one-shot structured-output repair. A safe transient provider timeout
or unavailable result with an eligible safe provider observation SHALL consume at most
one declared provider recovery attempt and record its observed disposition. The bridge
only returns that typed result from one invocation; topic planning alone SHALL decide
whether to make the second planner invocation. Authentication, configuration,
`provider.usage_unavailable`, `budget.exhausted`, `policy.denied`, non-retryable
provider, and unknown failures SHALL fail closed without a fabricated repair or
provider recovery. Any terminal exhaustion SHALL retain the safe terminal incident and
SHALL not write topic authority.

The initial topic-planning request SHALL remain zero-tool and use the explicitly
admitted topic-planning execution policy. A direct transient provider result produced
by that real bridge path SHALL enter the same existing recovery table as an equivalent
typed result from another safe invocation source. The recovery request SHALL be the
identical initial planner request, not a structured-output repair request. A second
eligible transient provider result SHALL produce the existing exhausted recovery
projection; a second non-provider result SHALL retain its actual category with the
existing `retry_followed_by_terminal_failure` disposition. Cancellation during either
invocation or the bounded backoff SHALL propagate and SHALL not record a retry or
terminal incident after cancellation.

#### Scenario: A bridge-produced timeout receives bounded provider recovery
- **WHEN** the first topic-planning model invocation through its explicitly admitted
  zero-tool bridge returns a safe `provider.timeout` with an eligible observation
- **THEN** the node records one bounded provider recovery attempt, calls the planner at
  most once more with the same initial request, and either accepts the recovered
  validated plan or blocks with a topic-planning provider incident

#### Scenario: A second timeout reaches the exhausted provider terminal
- **WHEN** the first and second topic-planning bridge invocations both return eligible
  transient provider failures
- **THEN** the node makes exactly two bridge calls, records one attempt, one scheduled
  retry, a second attempt, and one exhaustion fact, and retains the second category
  with the existing exhausted recovery projection

#### Scenario: A non-provider stop does not gain provider recovery
- **WHEN** the initial topic-planning invocation returns
  `provider.usage_unavailable`, `budget.exhausted`, or `policy.denied`
- **THEN** the node makes no provider retry, writes no topic authority, and retains that
  exact closed category in its terminal incident

#### Scenario: A provider retry followed by a closed stop retains both facts
- **WHEN** an eligible initial provider result causes the one declared retry and that
  second invocation returns `provider.usage_unavailable`, `budget.exhausted`, or
  `policy.denied`
- **THEN** the node makes exactly two invocations, retains the actual second closed
  category with the existing `retry_followed_by_terminal_failure` history, attaches no
  final provider observation to that stop, and makes no third invocation

#### Scenario: Invalid planner JSON does not masquerade as provider recovery
- **WHEN** a successful topic-planning result fails schema or coverage validation
- **THEN** the node issues its one structured-output repair prompt and records no
  provider recovery unless a later invocation independently returns a safe provider
  failure

#### Scenario: Provider recovery does not turn into structured-output repair
- **WHEN** an initial eligible provider timeout is followed by a successful but invalid
  retry result
- **THEN** the node records `retry_followed_by_terminal_failure`, makes no third planner
  invocation, and does not use the structured-output repair path

#### Scenario: Cancellation remains outside the recovery table
- **WHEN** topic planning is cancelled during an initial provider invocation or the
  recovery backoff
- **THEN** cancellation propagates without another bridge call, recovery event, or
  terminal incident

### Requirement: Topic planning capability preserves confirmed-profile planning boundaries

The real topic-planning initial and structured-repair requests SHALL bind distinct
runtime-loaded local capabilities. Their capability Markdown SHALL own the reusable
cognitive method: how to decompose the confirmed profile and current-round direction,
preserve scope boundaries and custom notes, create covering non-overlapping topics,
self-check the candidate, and repair only a rejected draft. Python and typed contracts
SHALL own trusted assignment projection, capability selection, schemas, size and call
bounds, tool enforcement, parser/materializer admission, state writes, routes, and
failure outcomes; reader-only workflow documentation SHALL not be required at runtime.

The initial candidate SHALL be evaluated only against the bounded confirmed assignment,
coverage, expansion, and non-overlap contracts. The repair candidate SHALL receive only
that same assignment, compact validation facts, and the untrusted draft; it SHALL not
introduce external facts, alter profile or direction authority, expose model-visible
tools, or write a topic registry. Existing parser, materializer, node recovery, and
runtime bridge owners remain the only admission and outcome authorities. (`TOP-006`)

#### Scenario: Runtime-loaded Markdown supplies the planning method
- **WHEN** the real planner's final composed request is inspected
- **THEN** it contains the exact activated initial or repair capability body and the deterministic bounded assignment, while reader-only workflow prose is not used as runtime policy

#### Scenario: A valid plan preserves profile coverage without tools
- **WHEN** a scripted real planner produces a valid candidate for a confirmed profile
- **THEN** its request exposes no model-visible tool, the deterministic materializer records only a bounded covering non-overlapping registry, and the candidate itself supplies no route, stable id, or checkpoint authority

#### Scenario: A valid plan preserves the full confirmed assignment without tools
- **WHEN** a scripted real planner produces a valid candidate for a profile with scope boundaries, custom notes, and a current-round direction
- **THEN** its request exposes no model-visible tool, the deterministic materializer records only a bounded covering non-overlapping registry, and the candidate itself supplies no route, stable id, profile mutation, or checkpoint authority

#### Scenario: Repair cannot extend the research assignment
- **WHEN** a malformed planner draft is repaired through the real planner node
- **THEN** the repair uses no tool and either yields a contract-valid plan constrained to the identical canonical profile and applied direction or follows the existing exhausted outcome without topic state

#### Scenario: Missing or mismatched capability fails before model invocation
- **WHEN** the configured topic-planning capability is missing, malformed, has the wrong id, or violates its declared zero-tool posture
- **THEN** trusted composition rejects it before invoking the model and does not fall back to reader documentation or an embedded substitute method

### Requirement: Topic-planning calibration keeps the confirmed profile authoritative

The initial and repair topic-planning policies SHALL expose model-visible criteria for
a decision-ready `TopicPlan`: each topic is scoped to the confirmed profile, every
must-answer question has an explicit binding, topics are distinct rather than
overlapping, and scopes, search dimensions, and exclusions contain no asserted
external research fact. The initial policy SHALL distinguish the required single-topic
profile from a bounded multi-topic profile. A degraded profile SHALL retain the
existing broader, conservative planning posture without inventing missing profile
requirements.

The repair policy SHALL receive only the same confirmed profile, invalid plan draft,
and compact validation facts. It SHALL preserve the profile boundary and shall not
retrieve evidence, add sources or requirements, assign stable identifiers, write
topic state, or select a route. The existing deterministic materializer remains the
sole owner of identifier derivation, duplicate and overlap rejection, complete
coverage validation, topic-registry publication, and exhausted routing.

#### Scenario: Confirmed constraints remain visible in a bounded plan candidate
- **WHEN** a confirmed profile contains multiple must-answer questions and explicit
  scope constraints
- **THEN** the planning request asks for a bounded, distinct topic candidate whose
  bindings and scope/exclusion fields account for those constraints without asserting
  sources, findings, identifiers, or lifecycle outcomes

#### Scenario: Degraded profile does not create new requirements
- **WHEN** planning receives a degraded confirmed profile
- **THEN** the request asks for broader conservative coverage of the supplied
  must-answer questions and does not use the absence of a dimension to fabricate a
  new profile requirement

#### Scenario: Repair cannot turn validation feedback into planning authority
- **WHEN** a topic plan fails coverage, duplicate, overlap, or structural validation
- **THEN** the one repair request is limited to the same profile and compact failure
  facts, and a still-invalid plan reaches the existing deterministic non-publication
  and exhausted outcome

### Requirement: Topic planning consumes confirmed comparison and language constraints directly

When a confirmed HITL1 profile contains comparison subjects and request/output-language
facts, real topic planning SHALL read those typed facts from checkpoint profile fields
and include them in both its initial and structured-repair assignments. It SHALL use
the accepted output/interaction language for planning communication and shall preserve
the exact two comparison subjects as scope constraints. It SHALL NOT derive, translate,
substitute, or infer a comparison pair or language from `request_text`,
`must_answer_questions`, request-bundle content, or prior model prose.

#### Scenario: Confirmed Chinese comparison reaches planning unchanged
- **WHEN** HITL1 accepts a Chinese profile comparing lithium-ion batteries with
  vanadium redox flow batteries
- **THEN** topic planning receives the exact typed pair and Chinese language preference
  in its bounded checkpoint-derived prompt input

#### Scenario: Planner cannot fill an absent comparison fact
- **WHEN** a checkpoint profile lacks a required comparison pair
- **THEN** topic planning is not reached through the accepted HITL1 route and cannot
  invent a pair from the request text

### Requirement: Topic planning consumes Bundle-local profile and writes Bundle-contained planning facts

Topic planning SHALL consume the confirmed profile, current-round applied direction,
and planning State only through the selected Run Bundle's bound graph and store
interfaces. Its durable topic plan, coverage facts, and artifact references SHALL remain
in that Bundle. It SHALL not recover a profile or direction from an external checkpoint,
conversation memory, session projection, diagnostic, or stale prior-round prompt; derive
a research identity; or select an artifact root. (`TOP-008`)

#### Scenario: Planning refuses a missing selected Bundle
- **WHEN** topic planning is invoked after its selected Bundle becomes unavailable
- **THEN** it does not read a former external checkpoint or publish a plan elsewhere and returns the Bundle-unavailable lifecycle outcome

#### Scenario: Prior-round direction is not reused implicitly
- **WHEN** a later topic-planning invocation has no direction applied to its current round but an earlier round had one
- **THEN** the planner uses the current canonical profile without importing the earlier direction from history, prompt text, or prior topic state

### Requirement: Topic planning records canonical parser and materialization evidence

After an initial or existing one-repair topic-planning model result reaches the planner
parser and deterministic materializer, the node SHALL publish one Journal validation
fact for that stage. A successful parser/materializer result SHALL publish an empty
code collection. A failed result SHALL publish only one or more codes from this closed
set: `topic_plan_empty`, `topic_plan_json_invalid`, `topic_plan_extra_fields`,
`topic_plan_invalid`, `topic_count_profile_mismatch`, `topic_coverage_empty`,
`topic_duplicate_slug`, `topic_overlap`, `topic_coverage_uncovered`, and
`topic_materialization_invalid`. The node SHALL collapse dynamic field paths, coverage
question text, parser messages, and validation exception detail to the applicable
closed code.

The initial and repair facts SHALL remain separately correlated to the same phase and
their order of occurrence. A model/provider invocation that fails before it produces a
candidate reaches no parser/materializer fact and retains its existing invocation or
provider-recovery behavior. This evidence SHALL not add a repair, alter the existing
one-repair bound, change planner-owned checkpoint materialization, or affect its
exhausted route. (`TOP-009`)

#### Scenario: Initial malformed topic plan is repaired with two validation facts
- **WHEN** an initial planner result reaches parsing or materialization with an invalid
  candidate and the existing repair result reaches validation
- **THEN** the Journal records an `initial` fact with only the applicable closed code
  and a distinct `repair` fact with its own empty or closed code collection

#### Scenario: Valid initial plan records a successful validation fact
- **WHEN** an initial planner candidate parses and materializes into the existing
  accepted bounded topic registry
- **THEN** the Journal records one `initial` validation fact with an empty code
  collection and does not invoke repair

#### Scenario: Dynamic validation detail cannot escape into the Journal
- **WHEN** a planner materialization failure includes a question, field path, or
  exception-rendered detail
- **THEN** the Journal retains only the corresponding closed canonical code and the
  existing planner/controller behavior is unchanged

### Requirement: Topic planning has a compact output envelope aligned with its admitted execution budget

The real topic-planning node SHALL present both its initial and one-shot repair
requests as one compact JSON TopicPlan candidate: no prose, markdown, code fences, or
restatement of the assignment; title text at most 80 characters; scope text at most
240 characters; and no more than four search dimensions or four exclusions per topic,
each at most 80 characters. The existing TopicPlan parser and materializer SHALL keep
their current authoritative validity bounds and admission ownership; the compact
envelope is the bounded model-visible target, not a new route, state writer, or
model-authorized control.

The real topic-planning policy SHALL remain zero-tool and one-model-call, with a local
total-token budget of 12288 and its existing wall-time budget of 60 seconds. When a
rendered request's deterministic byte upper bound plus the output ceiling fits that
total budget, it SHALL admit one response of up to 4096 output tokens and retain a
structured candidate of up to 16384 bytes before existing parser/materializer
validation. It SHALL not change the provider-recovery table, one-shot structured-output
repair, checkpoint writer, `next`/`exhausted` routes, blocked terminal disposition, or
legal lifecycle action.

#### Scenario: The fixed scripted-demo planner request is admitted before provider invocation
- **WHEN** the observed fixed scripted-demo profile is projected through the real
  initial topic-planning prompt renderer under the local 4096-output-token and
  12288-total-token policy
- **THEN** its rendered-request upper bound plus the reserved output ceiling is at most
  the total budget, so the existing runtime may invoke the provider rather than stop
  at `token_admission`

#### Scenario: An oversized rendered request retains the existing closed admission stop
- **WHEN** a topic-planning request's rendered byte upper bound plus its 4096-token
  output ceiling exceeds the local 12288-token budget
- **THEN** the runtime stops before provider invocation with the existing
  `token_admission` reason, topic planning publishes no topic state, and it adds no
  repair or provider-recovery attempt before the existing exhausted path

#### Scenario: Compact initial and repair candidates are preserved for validation
- **WHEN** the topic planner receives either the initial assignment or its one allowed
  repair assignment and returns one JSON candidate within the compact envelope and
  within 4096 output tokens and 16384 bytes
- **THEN** the runtime passes the untruncated candidate to the existing parser and
  materializer, and a candidate accepted by the existing subsequent validation follows
  the existing planner-owned `next` path

#### Scenario: Existing parser authority is not narrowed after runtime retention
- **WHEN** the runtime has retained a topic-plan candidate and it remains valid under
  the existing authoritative TopicPlan parser and materializer bounds
- **THEN** the deterministic parser and materializer retain their existing admission
  decision and no prompt or budget setting grants the model a route, identifier,
  checkpoint, or lifecycle authority

#### Scenario: Calibrated policy retains the existing closed stop above its envelope
- **WHEN** the real topic-planning model response exceeds 4096 output tokens or its
  retained structured candidate exceeds 16384 bytes
- **THEN** the existing bounded runtime failure handling applies with no added retry,
  no topic-state publication, and the existing exhausted terminal path
