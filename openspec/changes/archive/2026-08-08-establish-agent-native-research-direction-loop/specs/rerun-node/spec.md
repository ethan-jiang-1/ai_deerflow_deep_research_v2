> req: REN-008

## ADDED Requirements

### Requirement: An applied Run direction enters one full-scope rerun

When the Bundle lifecycle commits a pending Run direction to a new refinement round,
the rerun capability SHALL treat that applied direction as a distinct trusted rerun
source and select the existing `full` scope. It SHALL not reinterpret the direction as
a HITL2 decision or require a synthetic `hitl2_rerun_payload`. The resulting rerun plan
SHALL advance the existing generation authority once, retain the applied direction as
the bounded current-round assignment, invalidate only the derived projections already
owned by a full rerun, and route to `topic_planning`.

The applied direction SHALL not choose a graph edge, topic id, artifact path, or
checkpoint identity. The existing deterministic rerun planner, generation ceiling,
projection invalidation, retained-evidence rules, and route map SHALL remain the only
owners of those effects. Replaying the same committed round SHALL not create a second
rerun plan or generation.

The rerun capability SHALL expose its existing full-rerun generation ceiling through
one internal pure capacity predicate. Bundle lifecycle admission and its bounded private
replay-receipt validation SHALL consume that predicate rather than copy a generation
limit or select a rerun route.

The capacity bound SHALL be selected only by trusted runtime composition and supplied as
the same immutable policy to lifecycle admission/receipt validation, the Bundle-bound
compiler, and the rerun node's dependencies. It SHALL NOT be accepted from a public
tool, Agent, model, Bundle State, or direction. The production composition for this
change remains pinned to its current bound. An alternate test composition at or below
every existing public generation maximum MAY exercise the lifecycle or graph boundary
only when it supplies that exact same policy to every participating component. An
alternate bound above those existing public/runtime generation contracts MAY exercise
only the pure compiler/direct-node seam and SHALL NOT construct a public result, work
unit, Bundle State/checkpoint, lifecycle transition, or full graph continuation.
Changing or exposing the production bound requires a later compatible change that widens
every affected contract together.

The implementation SHALL express the full-rerun update through one pure typed compiler
shared by the rerun node and Bundle-bound checkpoint preparation. The compiler SHALL
receive the trusted `run_refinement` source only as assignment data, produce the same
full-scope generation/invalidation/route update as the rerun node, and have no
checkpoint, Bundle-State, model, tool, provider, or artifact side effect. The graph
preparation path SHALL submit that exact output through the production graph's rerun
writer/edge; it SHALL not construct a second hand-built rerun update or execute a node
before the Bundle-State refinement commit.

#### Scenario: Applied direction selects the existing full rerun
- **WHEN** a Bundle commits one pending direction as the assignment for its next refinement round below the generation ceiling
- **THEN** the rerun capability creates one full-scope rerun plan, advances the generation once, and routes to `topic_planning` in the same Bundle

#### Scenario: Direction source remains distinct from HITL2
- **WHEN** the rerun capability receives a lifecycle-applied Run direction without a HITL2 rerun payload
- **THEN** it selects full scope from the typed direction source and does not fabricate, read, or persist a human HITL2 rerun decision

#### Scenario: Full rerun retains evidence and clears only derived projections
- **WHEN** a direction-triggered full rerun is committed after prior evidence and reports exist
- **THEN** accepted submissions, raw evidence, and prior artifacts remain inspectable while topic, synthesis, decision, report, repair, and gate projections owned by the new generation are reset according to the existing full-rerun contract

#### Scenario: Replayed applied round does not rerun twice
- **WHEN** checkpoint replay revisits a direction round whose rerun generation and plan were already committed
- **THEN** the rerun capability observes the committed generation and does not increment, invalidate, or route a second time

#### Scenario: Generation ceiling prevents false application
- **WHEN** an admitted direction requests a next round but the existing rerun generation ceiling permits no further full rerun
- **THEN** the deterministic rerun owner returns the existing bounded exhausted outcome and no consumer may claim that topic planning applied the direction

#### Scenario: Higher alternate capacity remains a pure test seam
- **WHEN** a trusted test composition selects a capacity above the current public generation maximum
- **THEN** it may compare pure compiler/direct-node output only and does not create a public lifecycle result, work unit, Bundle State/checkpoint, or full graph continuation
