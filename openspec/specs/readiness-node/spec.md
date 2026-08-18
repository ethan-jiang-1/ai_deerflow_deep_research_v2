# readiness-node Specification

> req: REA-001, REA-002, REA-003, REA-004, REA-005, REA-006, REA-007

## Purpose
Determine whether accepted evidence and HITL decisions are structurally and semantically ready for final delivery.

## Requirements
### Requirement: Hard checks verify citation availability, provenance, HITL2 consumption, and admitted-evidence readability

The readiness node SHALL run deterministic hard checks on pre-existing state: accepted
submissions are non-empty (`check_citation_availability`) and all refs are canonical
submission-ledger hashes (`check_provenance`). It SHALL NOT require a consumed HITL2
request: an autonomous HITL2 continuation is neither missing evidence nor missing user
authority. Before building a critic request, the node SHALL also fail closed when an
accepted ledger record cannot be read as bounded synthesis evidence or fails its
integrity check. It SHALL record only a closed structural `HardRuleFailure`, never the
raw store exception, artifact path, or evidence content. Structural evidence or
provenance failures SHALL route to `exhausted` with `BLOCKED` terminal status. (`REA-001`)

#### Scenario: Autonomous continuation is not a readiness failure
- **WHEN** accepted evidence and provenance are valid but no HITL2 request was consumed
- **THEN** readiness does not produce `hitl2_not_consumed` and may continue to its
  critic and normal route determination

#### Scenario: No accepted evidence is a structural failure
- **WHEN** `accepted_submission_refs` is empty
- **THEN** the node produces a `citation_no_accepted_evidence` failure and routes to
  `exhausted` with `terminal_status=BLOCKED`

#### Scenario: Valid evidence passes citation availability
- **WHEN** `accepted_submission_refs` contains at least one canonical `h_` submission-ledger record hash
- **THEN** the citation availability check produces zero failures

#### Scenario: Malformed ref is a provenance failure
- **WHEN** an accepted submission ref is `"bad-format"` rather than a canonical ledger hash
- **THEN** the node produces a `provenance_invalid_ref` failure with the malformed ref

#### Scenario: Accepted evidence read failure is structural
- **WHEN** a canonical accepted ref is missing, unreadable, or fails the ledger reader's
  integrity check
- **THEN** readiness records only its closed hard-rule failure, invokes no critic, and
  routes to `exhausted` with the existing blocked terminal facts

### Requirement: Semantic critic assesses answerability per must-answer question

The real readiness node SHALL declare `NodeCapability.WORK_UNIT_CONTROLLER` and invoke
one bounded zero-tool critic for each readiness visit. Before invocation, trusted code
SHALL derive a bounded read-only evidence projection solely from the checkpointed
must-answer questions, accepted submission references, and ledger-validated synthesis
evidence read through that declared controller. The critic SHALL return exactly one
typed verdict for every supplied question: `ready_substantive`,
`ready_insufficient_judgment`, or `blocked_repair_required`. It SHALL receive no raw
checkpoint, runtime authority, writable path, tool, or route instruction. Full-fake
readiness SHALL remain fixture-controlled. (`REA-002`)

#### Scenario: Complete candidate is admitted
- **WHEN** the zero-tool critic returns one valid verdict for every supplied question
- **THEN** the deterministic readiness boundary accepts the typed candidate for
  report-plan materialization without granting the critic evidence or route authority

#### Scenario: Candidate references cannot exceed the projection
- **WHEN** a candidate names an unknown or duplicate question, or a backing reference
  absent from the accepted evidence projection
- **THEN** readiness rejects that candidate and projects conservative repair-required
  verdicts without admitting the unknown identifier

#### Scenario: Evidence projection is bounded and ledger-derived
- **WHEN** real readiness prepares the critic request
- **THEN** it includes only the approved questions and bounded evidence derived from
  accepted ledger references, and does not expose arbitrary sandbox content

#### Scenario: Full-fake readiness remains fixture-controlled
- **WHEN** the full-fake graph reaches readiness
- **THEN** it does not invoke the critic and retains its declared fixture route

### Requirement: Report plan materializer produces immutable projection

A deterministic materializer SHALL produce a `ReadinessReportPlan` from the critic's verdicts and hard-rule results. The plan SHALL contain writable conclusions (from `ready_substantive`), mandatory uncertainties (from `ready_insufficient_judgment`), and prohibited upgrades. It SHALL additionally append one mandatory uncertainty for every gate-recorded unresolved searchable gap: the gap id set comes from the checkpointed `unresolved_gaps` control field, and each gap's description is read from the bundle store's canonical `synthesis/findings.json` artifact through a bounded contained read; a recorded id whose gap body is absent from the artifact SHALL still produce an uncertainty naming the gap id without fabricating a description, and no gap body SHALL enter checkpoint state. The readiness controller SHALL serialize the admitted plan to the canonical `readiness_report_plan` artifact before checkpointing its `ContentRef`; the reference SHALL name the contained path and exact content hash of those immutable bytes. A later reader may consume only a contained, hash-matched plan and no rejected critic output becomes part of it.

#### Scenario: ready_substantive verdicts become writable conclusions
- **WHEN** the critic produces `ready_substantive` for Q1 and Q3
- **THEN** the report plan lists Q1 and Q3 as writable conclusions with backing claim IDs

#### Scenario: ready_insufficient_judgment verdicts become mandatory uncertainties
- **WHEN** the critic produces `ready_insufficient_judgment` for Q2 with limitation "data is contradictory"
- **THEN** the report plan lists Q2 under mandatory uncertainties with that limitation

#### Scenario: blocked_repair_required verdicts produce neither conclusions nor uncertainties
- **WHEN** the critic produces `blocked_repair_required` for Q4
- **THEN** Q4 is absent from both conclusions and uncertainties; `readiness_blocked_count` is incremented

#### Scenario: Unresolved searchable gaps become disclosed uncertainties
- **WHEN** readiness runs with `unresolved_gaps` naming gap `g:x` whose
  `search_required=true` body exists in the canonical synthesis artifact
- **THEN** the report plan lists a mandatory uncertainty carrying that gap's
  description (bounded) and identifying the gap id, and the final report's
  uncertainties section discloses it

#### Scenario: A recorded gap id without a body still discloses honestly
- **WHEN** `unresolved_gaps` names an id whose body is absent from the canonical
  synthesis artifact
- **THEN** the plan still carries a mandatory uncertainty naming that id with an
  explicit no-description limitation rather than dropping or inventing the gap

#### Scenario: No unresolved gaps adds no uncertainties
- **WHEN** readiness runs with empty `unresolved_gaps`
- **THEN** the plan's uncertainties come only from critic verdicts and provenance
  hard-rule failures, exactly as before

#### Scenario: Report plan is persisted and checkpointed
- **WHEN** the materializer produces an admitted report plan
- **THEN** exact serialized bytes are written to the contained canonical plan path and a `ContentRef` with its matching content hash is written to `readiness_report_plan`

#### Scenario: Failed plan persistence cannot mint a reference
- **WHEN** the report-plan artifact cannot be written or verified
- **THEN** readiness does not checkpoint a fabricated plan reference or allow final composition to consume it

### Requirement: Node determines its own route based on hard-rule results and critic verdicts

The readiness node SHALL write its own `route` field. Route determination SHALL retain
this priority: structural hard-rule failures, including accepted-evidence reader
failures, route to `exhausted` with `BLOCKED`; any admitted or conservatively projected
`blocked_repair_required` verdict routes to `repair_targeted`; otherwise it routes to
`pass`. A critic candidate SHALL NOT select, write, or bypass a route. (`REA-004`)

#### Scenario: Admitted critic result routes through deterministic owner
- **WHEN** hard rules pass and the admitted candidate contains a
  `blocked_repair_required` verdict
- **THEN** the readiness node writes `repair_targeted` and the critic writes no route

#### Scenario: Insufficient judgment remains an honest pass projection
- **WHEN** hard rules pass and all admitted verdicts are
  `ready_substantive` or `ready_insufficient_judgment`
- **THEN** the node writes `pass` and the report plan records each insufficiency as a
  mandatory uncertainty

#### Scenario: Structural failures still take priority
- **WHEN** a structural hard-rule failure and any critic verdict are present
- **THEN** the node writes `exhausted` with the existing blocked terminal facts

### Requirement: Node collects all failures before determining route

The readiness node SHALL collect all hard-rule failures and critic verdicts before determining the route. No single failure SHALL short-circuit the collection. All failures SHALL be written to `readiness_hard_failures` for diagnostic traceability.

#### Scenario: All failures appear in checkpoint state
- **WHEN** hard rules detect one citation failure and one provenance failure
- **THEN** both failures appear in `readiness_hard_failures` written to checkpoint state

### Requirement: Critic runs under bounded read-only policy

The real readiness critic SHALL run through the existing bounded Node Agent path with
one invocation, zero allowed tools, no writable roots, a finite model/token/wall-time
budget, and a closed `ReadinessCriticOutput` candidate. Missing, malformed, duplicate,
out-of-scope, incomplete, or failed execution output SHALL be deterministically
projected to conservative `blocked_repair_required` verdicts for the affected supplied
questions; it SHALL NOT silently use the all-ready fallback. (`REA-006`)

The checkpointed critic summary SHALL contain only the admitted, bounded typed
per-question projection consumed by the materializer. Raw provider output, prompt
text, sandbox paths, rejected candidate content, and unused critic-only fields SHALL
NOT be checkpointed. The critic contract SHALL bound retained field/cardinality values;
the existing policy's structured-result byte budget remains a separate hard cap on raw
bridge success output.

#### Scenario: Invalid output fails closed to existing repair
- **WHEN** the critic result is malformed or does not provide one valid verdict for
  every supplied question
- **THEN** readiness projects repair-required verdicts and follows the existing
  `repair_targeted` route calculation

#### Scenario: Execution failure cannot claim readiness
- **WHEN** the bounded Node Agent reports timeout, configuration, provider, or policy
  failure
- **THEN** no question is projected as `ready_substantive` solely from that failure
  and the existing repair path is the only legal next action

#### Scenario: Tool posture is enforced
- **WHEN** the readiness critic request and effective runtime policy are inspected
- **THEN** they permit no web, sandbox, or other tool calls and no writable root

#### Scenario: Rejected output is not retained as checkpoint authority
- **WHEN** critic output fails admission
- **THEN** checkpoint state records only the conservative projected verdicts and no
  raw rejected output, provider diagnostic, or prompt text

#### Scenario: Unused parseable critic fields are not retained
- **WHEN** an otherwise admitted candidate includes critic-only limitations, synthesis
  flaws, or contradiction identifiers that the report-plan materializer does not read
- **THEN** `readiness_critic_summary` contains only the bounded admitted per-question
  projection and none of those extra fields

### Requirement: Mixed-graph integration with unchanged topology

Real readiness SHALL require `hitl2=real` and the declared work-unit controller.
Selecting `readiness=real` without `hitl2=real` SHALL fail before graph invocation.
The graph wrapper and direct real factory SHALL fail with
`work_unit_capability_missing` before model invocation when the declared controller is
absent. The runtime dependency resolver SHALL construct and select a readiness-specific
zero-tool bridge/policy for readiness rather than supplying an upstream node's bridge.
Full-fake readiness SHALL remain unchanged (fixture gate provides route). Topology SHALL
be unchanged. (`REA-007`)

#### Scenario: Real readiness requires real hitl2
- **WHEN** a recipe selects `readiness=real` without `hitl2=real`
- **THEN** recipe construction fails with a typed dependency error

#### Scenario: Missing declared controller fails before model invocation
- **WHEN** real readiness is built or graph-invoked without the declared work-unit
  controller
- **THEN** it fails with `work_unit_capability_missing` before a readiness request,
  model call, candidate, or route is created

#### Scenario: Real readiness receives its own bridge policy
- **WHEN** a runnable real-readiness recipe resolves the readiness dependencies
- **THEN** the resolved bridge has the readiness-specific zero-tool policy and is not
  the HITL1, topic-planning, or Wave2 synthesis bridge

#### Scenario: Full-fake readiness unchanged
- **WHEN** the full-fake graph reaches the readiness node
- **THEN** it returns a no-op update with the fixture gate providing the route

#### Scenario: Real readiness coexists with fake final_delivery
- **WHEN** readiness is real while final_delivery is fake
- **THEN** the graph routes `pass` to `final_delivery` and the fake final handles it
