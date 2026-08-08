> req: TOP-001, TOP-004, TOP-006, TOP-008

## MODIFIED Requirements

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

#### Scenario: Profile is read from checkpoint, not the bundle
- **WHEN** real topic planning builds its planning objective
- **THEN** it reads `request_text`, depth/audience/format/cost/time enums, `must_answer_questions`, and `degraded_profile` from `ResearchState`, declares no request-bundle capability, and never opens `request/profile.json`

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
