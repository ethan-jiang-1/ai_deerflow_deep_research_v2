> req: HIN-001, HIN-002, HIN-004, HIN-005, HIN-015

## ADDED Requirements

### Requirement: HITL1 keeps durable interaction facts in the selected Run Bundle

HITL1 SHALL read and persist its accepted profile, pending interaction correlation,
advisory proposal progress, and request-bundle content through the selected Bundle-local
Research State and contained Bundle artifacts. It SHALL not derive a research identity,
choose a path, or use an external checkpoint namespace as a continuation/recovery
authority. The graph-owned interrupt remains the pending-action mechanism, but its
durable lifecycle facts are owned by the Bundle. (`HIN-015`)

#### Scenario: HITL1 follow-up remains in one Bundle after restart
- **WHEN** HITL1 resumes an available suspended Run after restart
- **THEN** it validates the pending interaction from Bundle-local State and writes the follow-up profile artifacts only in that same Bundle

## RENAMED Requirements

- FROM: `### Requirement: HITL1 stores the recorded profile as checkpoint fields and request-bundle content`
- TO: `### Requirement: HITL1 stores recorded profile facts in Bundle-local State and contained content`

## MODIFIED Requirements

### Requirement: HITL1 presents structured brief and profile dimensions through durable interrupts

The real HITL1 node SHALL present a validated structured brief and profile dimensions
through `interrupt(PendingResearchInterrupt(...))` with `mode=TEXT` when a supported
output/interaction language is accepted. When the bounded request-language detector is
`unspecified` and no output language is accepted, HITL1 SHALL issue one correlated
`mode=CHOICE` interrupt advertising exactly `zh` and `en`. That choice SHALL carry no
interaction or action ids, and its selection SHALL be a typed `OPTION` response rather
than a text or action alias. The wire schemas for `PendingResearchInterrupt`,
`HumanInputRequest`, `AcceptedHumanResponse`, and `InternalCancelDecision` SHALL remain
version-compatible with the lifecycle contract.

`HumanInputRequest.context` SHALL be bounded to 2,048 characters and contain compact
JSON with at minimum `context_schema_version: 1`, `brief_summary`,
`proposed_dimensions`, `required_dimensions`, `missing_dimensions`, `valid_options`,
and `instructions`. `request_id` SHALL be derived with
`make_hitl_request_id(bundle_id, phase="hitl1", generation, ordinal)`. The ordinal
comes from the Bundle-local logical HITL1 visit count, so first visit uses ordinal 1 and
each durable follow-up uses the next ordinal. The suspension cursor SHALL reference the
latest consumed message id, falling back to the start message id.

The graph interrupt remains the in-invocation delivery mechanism, but the selected
Bundle-local State is the sole durable pending-interaction authority. HITL1 SHALL retain
exactly one bounded, correlation-valid pending descriptor there and SHALL not create a
second mutable copy in an external checkpoint, session, or adapter. Durable follow-up
facts needed to build the next prompt remain bounded profile-progress data. (`HIN-002`)

#### Scenario: First-visit interrupt with full brief
- **WHEN** HITL1 visits a Bundle for the first time, brief generation succeeds, and a supported output language is accepted
- **THEN** the node calls `interrupt()` with a `PendingResearchInterrupt` containing `phase="hitl1"`, the current generation, `mode=TEXT`, and compact structured context for all required dimensions

#### Scenario: Unsupported language evidence uses the bounded choice
- **WHEN** HITL1 needs an output language but its bounded request-language detector is `unspecified`
- **THEN** it calls `interrupt()` with a current `phase="hitl1"` `mode=CHOICE` request that advertises exactly `zh` and `en`, no interaction, and no action ids

#### Scenario: Follow-up interrupt has a new ordinal
- **WHEN** a prior incomplete response has been consumed and HITL1 loops back to ask only for missing dimensions
- **THEN** the next `request_id` encodes ordinal 2, is distinct from the first visit's `request_id`, and the Bundle-local completed-visit count for `hitl1` is 1 at entry time

#### Scenario: Interrupt context is bounded and parseable
- **WHEN** the interrupt is constructed from a generated brief or follow-up prompt
- **THEN** `HumanInputRequest.context` is valid compact JSON, includes the required keys, advertises stable enum machine values, and does not exceed 2,048 characters

#### Scenario: One Bundle-local pending authority survives restart
- **WHEN** a lifecycle is suspended at HITL1 and the process later restarts while the Bundle remains available
- **THEN** only the Bundle-local pending descriptor supplies the correlation/lifecycle fact; graph delivery state may be rebuilt from it but no external checkpoint or duplicate descriptor can authorize resume

### Requirement: HITL1 stores recorded profile facts in Bundle-local State and contained content

The real HITL1 node SHALL write the final recorded profile to the selected Bundle's
contained `request/profile.json` through a runtime-owned request-bundle capability and
reference it from Bundle-local State via `profile_ref`. The capability SHALL be attached
only when the selected real factory declares it. It SHALL use the preselected Bundle
reference, perform host-side containment, write atomically, compute the content hash
from canonical JSON bytes, and return a bounded `ContentRef`. Nodes SHALL receive only
the pure protocol, not host paths or raw runtime authority.

Bundle-local State SHALL additionally store the bounded fields needed by topic planning:
`research_depth`, `target_audience`, `output_format`, `cost_tolerance`, `time_budget`,
`must_answer_questions`, and `degraded_profile`, plus bounded transient progress
`pending_profile` and `profile_followup_round`. Those fields SHALL be cleared when
HITL1 accepts or cancels, owned by `WriterRole.CONTROLLER`, listed in the ownership
table, and protected by controller-authorized reducers. Final profile publication SHALL
be atomic from the graph perspective: `accepted` produces the artifact and final fields
together; follow-up writes only transient progress; cancel or brief-generation failure
writes no final profile fields. (`HIN-004`)

#### Scenario: Profile written to contained ContentRef
- **WHEN** a complete valid human response is accepted
- **THEN** HITL1 writes canonical `profile.json` under the selected Bundle's `request/` subtree, receives a bounded `ContentRef`, and sets Bundle-local `profile_ref`

#### Scenario: Partial progress is not final profile state
- **WHEN** the first answer is incomplete
- **THEN** `pending_profile` and `profile_followup_round` are written, but `profile_ref`, final short dimension fields, and `profile.json` are not written until an accepted final profile exists

#### Scenario: Cancel route writes no profile
- **WHEN** the user cancels at HITL1
- **THEN** no final profile fields, `profile_ref`, or `profile.json` are written, and transient profile progress is cleared

### Requirement: HITL1 integrates into the mixed graph with explicit lifecycle and governance updates

The real HITL1 SHALL retain its existing mixed-graph selection, full-fake isolation,
declared `accepted`, `cancel`, `needs_followup`, and `exhausted` routes, bounded
follow-up loop, and no-upstream/UI-change boundary. A real HITL1 factory SHALL receive a
preselected available Bundle context rather than require real Bootstrap to create or
select a root. The normalized topology snapshot and route-contract tests SHALL be
updated for Bundle-local pending/refinement State without adding an undeclared route.
The project-structure registry and generated
`deep_research_harness/AGENTS.md` locator SHALL retain the narrow graph-owned
`langgraph.types.interrupt` exception. (`HIN-005`)

#### Scenario: Mixed graph keeps its declared routes
- **WHEN** the implementation map sets `hitl1=real` with a valid preselected Bundle and every later phase fake
- **THEN** the graph compiles, runs only its declared HITL1 routes, preserves the mixed implementation result, and HITL1 cannot create a second Bundle or external lifecycle authority

#### Scenario: Full-fake graph remains isolated
- **WHEN** the implementation map sets all phases to `fake`
- **THEN** the graph completes the existing deterministic path without a real request-profile writer, external lifecycle recovery, or a production-to-fixture import

### Requirement: HITL1 generates a validated structured brief from the original question

The existing bounded zero-tool brief-generation, schema validation, redaction, and
blocked-route guarantees remain unchanged. Any durable incident or correlation emitted
by real HITL1 SHALL bind only the selected Bundle-local State and opaque `bundle_id`;
it SHALL not write or expose a conversation-derived `research_id`, external checkpoint
identity, or Bundle path. (`HIN-001`)

#### Scenario: Brief failure cannot create legacy Run identity
- **WHEN** real HITL1 records a bounded brief-generation failure for an available Bundle
- **THEN** its State/result correlation uses the selected Bundle fact and does not add a
  research-id or checkpoint-based lifecycle reference
