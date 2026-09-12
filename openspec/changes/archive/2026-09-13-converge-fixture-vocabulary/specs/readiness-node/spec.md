> req: REA-001, REA-002, REA-003, REA-004, REA-005, REA-006, REA-007, REA-008

## MODIFIED Requirements

### Requirement: Semantic critic assesses answerability per must-answer question

The real readiness node SHALL declare `NodeCapability.WORK_UNIT_CONTROLLER` and invoke
one bounded zero-tool critic for each readiness visit. Before invocation, trusted code
SHALL derive a bounded read-only evidence projection solely from the checkpointed
must-answer questions, accepted submission references, and ledger-validated synthesis
evidence read through that declared controller. The critic SHALL return exactly one
typed verdict for every supplied question: `ready_substantive`,
`ready_insufficient_judgment`, or `blocked_repair_required`. It SHALL receive no raw
checkpoint, runtime authority, writable path, tool, or route instruction. Fixture
readiness SHALL remain fixture-controlled. (`REA-002`)

#### Scenario: Complete candidate is admitted
- **WHEN** the zero-tool critic returns one valid verdict for every supplied question
- **THEN** the deterministic readiness boundary accepts the typed candidate for
  report-plan materialization without granting the critic evidence or route authority

#### Scenario: Candidate references cannot exceed the projection
- **WHEN** a candidate names an unknown or duplicate question, or a backing reference
  absent from the accepted evidence projection
- **THEN** readiness rejects that candidate and projects the disclosed conservative
  insufficiency verdicts without admitting the unknown identifier

#### Scenario: Evidence projection is bounded and ledger-derived
- **WHEN** real readiness prepares the critic request
- **THEN** it includes only the approved questions and bounded evidence derived from
  accepted ledger references, and does not expose arbitrary sandbox content

#### Scenario: Full-fake readiness remains fixture-controlled
- **WHEN** the fixture graph reaches readiness
- **THEN** it does not invoke the critic and retains its declared fixture route

### Requirement: Mixed-graph integration with unchanged topology

Real readiness SHALL require `hitl2=real` and the declared work-unit controller.
Selecting `readiness=real` without `hitl2=real` SHALL fail before graph invocation.
The graph wrapper and direct real factory SHALL fail with
`work_unit_capability_missing` before model invocation when the declared controller is
absent. The runtime dependency resolver SHALL construct and select a readiness-specific
zero-tool bridge/policy for readiness rather than supplying an upstream node's bridge.
Fixture readiness SHALL remain unchanged (fixture gate provides route). Topology SHALL
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
- **WHEN** the fixture graph reaches the readiness node
- **THEN** it returns a no-op update with the fixture gate providing the route

#### Scenario: Real readiness coexists with fake final_delivery
- **WHEN** readiness is real while final_delivery is fake
- **THEN** the graph routes `pass` to `final_delivery` and the fake final handles it
