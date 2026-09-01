# rerun-node Specification

> req: REN-001, REN-002, REN-003, REN-004, REN-005, REN-006, REN-007, REN-008

## Purpose
Plan bounded generation reruns while preserving accepted evidence authority and resetting only affected projections.
## Requirements
### Requirement: Rerun scope is parsed from the `hitl2_rerun_payload` checkpoint field

The rerun node SHALL read the `hitl2_rerun_payload` field from checkpoint state. When the field is a dict with a valid `scope` key, the node SHALL extract a typed `RerunScope`. Valid scope values SHALL be `full` (redo all topics from planning), `topic` (redo named topics from source intake), and `finding` (redo specific findings — gap re-search or stale source intake). The scope extraction SHALL be a pure input-parsing step that does not depend on generation having been incremented. If `hitl2_rerun_payload` is `None`, absent, or contains an invalid/missing `scope` key, the node SHALL default to `full` scope. The final `RerunPlan` (assembled after generation increment and route determination) SHALL contain the `RerunScope`, the new generation, the parent generation, and the determined route.

When present, `hitl2_rerun_payload` SHALL be treated only as internal graph/control
input to the rerun compiler. It SHALL NOT be advertised as a human HITL2 decision,
reconstructed from a human response, or used as authority for a pending interaction.

#### Scenario: Full rerun from payload with explicit scope
- **WHEN** `hitl2_rerun_payload` is `{"scope": "full", "reason": "rethink methodology"}`
- **THEN** a `RerunScope` is produced with `scope=FULL`, `target_topic_ids=()`, `retain_topic_ids=()`, and `reason="rethink methodology"`

#### Scenario: Topic-scoped rerun from payload with named targets
- **WHEN** `hitl2_rerun_payload` is `{"scope": "topic", "reason": "weak sources", "target_topic_ids": ["methodology", "market-size"]}` and topic registry contains methodology, market-size, and competitors
- **THEN** a `RerunScope` is produced with `scope=TOPIC`, `target_topic_ids=("methodology", "market-size")`, and `retain_topic_ids=("competitors",)`

#### Scenario: Finding-scoped rerun from payload with named findings
- **WHEN** `hitl2_rerun_payload` is `{"scope": "finding", "reason": "verify claims", "target_finding_ids": ["F-003", "F-007"]}`
- **THEN** a `RerunScope` is produced with `scope=FINDING` and `target_finding_ids=("F-003", "F-007")`

#### Scenario: Missing payload defaults to full rerun
- **WHEN** `hitl2_rerun_payload` is `None` or absent from checkpoint state
- **THEN** the rerun node defaults to `scope=FULL` and writes a diagnostic note to `execution_trace`

#### Scenario: Invalid target IDs in payload default to full rerun
- **WHEN** `hitl2_rerun_payload` specifies `target_topic_ids=["nonexistent"]` but "nonexistent" is not in the topic registry
- **THEN** the rerun node defaults to `scope=FULL` and logs a diagnostic warning

### Requirement: Generation increment is monotonic with old ledger preservation

The rerun node SHALL set `generation = parent_generation + 1` in checkpoint state. The reducer SHALL reject any decrease. The old submission ledger and raw evidence artifacts SHALL remain append-only — no accepted `SubmissionRecord` may be deleted or modified. The `parent_generation` field SHALL record the generation being superseded.

#### Scenario: Generation increments monotonically
- **WHEN** the rerun node runs with `generation = 0`
- **THEN** checkpoint state is updated with `generation = 1` and `parent_generation = 0`

#### Scenario: Generation decrease is rejected by reducer
- **WHEN** a node attempts to set `generation` to a value lower than the current `generation`
- **THEN** the reducer raises `ValueError("generation_decrease")`

#### Scenario: Old ledger entries survive rerun
- **WHEN** the rerun node runs after 5 submissions were accepted in generation 0
- **THEN** `accepted_submission_refs` still contains all 5 refs and no submission is removed

### Requirement: Derived projections are invalidated without raw data loss

The rerun node SHALL invalidate derived projections from the old generation by clearing their checkpoint refs: `synthesis_ref` set to `None`, `decision_brief_ref` set to `None`, `report_refs` set to empty, `repair_counts` set to empty dict. The `hitl2_rerun_payload` SHALL be consumed (set to `None`) to prevent re-reading on checkpoint replay. Raw evidence (submission ledger entries, source caches, accepted claims) SHALL NOT be deleted from the sandbox or checkpoint. The rerun node SHALL NOT delete any sandbox files.

#### Scenario: Synthesis ref is cleared on rerun
- **WHEN** the rerun node runs and `synthesis_ref` is set to a valid ContentRef from generation 0
- **THEN** `synthesis_ref` is set to `None` in the new generation's checkpoint state

#### Scenario: Accepted submission refs survive projection invalidation
- **WHEN** the rerun node runs and `accepted_submission_refs` contains 10 refs
- **THEN** all 10 refs remain in `accepted_submission_refs` after rerun

#### Scenario: HITL2 rerun payload is consumed after reading
- **WHEN** the rerun node reads a valid `hitl2_rerun_payload` and produces a `RerunScope`
- **THEN** `hitl2_rerun_payload` is set to `None` so a checkpoint replay does not re-consume the same payload

#### Scenario: Sandbox files are never deleted by rerun
- **WHEN** the rerun node invalidates derived projections
- **THEN** no sandbox file system operation is performed — invalidation is checkpoint-only

### Requirement: Scoped WorkSpecs are materialized via work-unit kernel

The rerun node SHALL generate new or revised `WorkSpec` entries for topics and findings within the rerun scope through the existing work-unit controller. Topics outside the rerun scope SHALL retain their accepted evidence and SHALL NOT have new WorkSpecs created. The node SHALL write `pending_work_ids` to checkpoint state for fan-out pickup on the next superstep.

#### Scenario: Full rerun delegates WorkSpec creation to topic planner
- **WHEN** scope is `FULL` and the topic registry contains 3 topics
- **THEN** the rerun node creates no WorkSpecs, clears `pending_work_ids`, and routes to `topic_planning` where the topic planner will regenerate the topic registry and create fresh WorkSpecs

#### Scenario: Topic-scoped rerun creates WorkSpecs only for target topics
- **WHEN** scope is `TOPIC` with `target_topic_ids=("A", "C")` and registry has topics A, B, C
- **THEN** 2 WorkSpecs are created for A and C, `pending_work_ids` contains 2 ids, and topic B's accepted submissions remain in `accepted_submission_refs`

#### Scenario: Retained topic evidence is not re-verified
- **WHEN** topic B is in `retain_topic_ids` with 3 accepted submissions
- **THEN** topic B's submissions are preserved and counted toward coverage without new worker execution

### Requirement: Back edges are a closed set determined by rerun scope

The rerun node SHALL route to a closed set of graph edges determined by scope: `full` scope routes to `topic_planning` (re-plan from scratch); `topic` scope routes to `wave0` (scoped source intake, bypassing the topic planner); `finding` scope routes to `wave0` when target findings have stale sources or `wave1` when only deep evidence is affected. When the generation ceiling is reached, the node SHALL route to `exhausted` with `terminal_status=BLOCKED` and `terminal_reason=RERUN_EXHAUSTED`.

#### Scenario: Full scope routes to topic_planning
- **WHEN** scope is `FULL` and generation is below ceiling
- **THEN** the node routes to `topic_planning` with `phase_status=WAITING`

#### Scenario: Topic scope routes to wave0 bypassing topic planner
- **WHEN** scope is `TOPIC` with `target_topic_ids=("methodology",)` and generation is below ceiling
- **THEN** the node routes to `wave0` with scoped WorkSpecs for the target topic only

#### Scenario: Finding scope with stale sources routes to wave0
- **WHEN** scope is `FINDING` and target findings reference wave0-source-age evidence
- **THEN** the node routes to `wave0`

#### Scenario: Finding scope with deep-evidence-only routes to wave1
- **WHEN** scope is `FINDING` and target findings reference only wave1-extracted evidence with valid wave0 backing
- **THEN** the node routes to `wave1`

#### Scenario: Generation ceiling exhaustion blocks rerun
- **WHEN** `generation` equals `max_rerun_generations`
- **THEN** the node routes to `exhausted` with `terminal_status=BLOCKED` and `terminal_reason=RERUN_EXHAUSTED`

### Requirement: New generation must re-pass affected wave gates and HITL2

The rerun node SHALL reset `gate_attempts_by_phase` and `repair_budget_by_phase` for all phases affected by the rerun scope. Affected wave gates SHALL re-evaluate from scratch against the new generation's evidence. When that flow reaches HITL2, HITL2 SHALL validate the new generation's predecessor and select its graph-owned route autonomously; it SHALL NOT inherit a cached human decision, create a pending input, or re-suspend for a new user choice.

#### Scenario: Gate state is reset for affected phases
- **WHEN** scope is `FULL` and generation 0 had gate attempts `{"wave0": 2, "wave1": 3}`
- **THEN** `gate_attempts_by_phase` for affected phases is cleared and gates re-evaluate from attempt 0

#### Scenario: Unaffected phases retain gate state in topic-scoped rerun
- **WHEN** scope is `TOPIC` with `target_topic_ids=("B",)` and generation 0 had gate attempts `{"wave0": 2, "wave1": 1}` for all topics A, B, C
- **THEN** `gate_attempts_by_phase` for phases affecting topic B is reset; phases unrelated to the rerun scope retain their attempts for diagnostic traceability

#### Scenario: Old HITL2 proceed is not inherited
- **WHEN** a rerun generation re-passes its affected Wave2 path and reaches HITL2
- **THEN** HITL2 validates that generation and follows its graph-owned route without
  reading a cached human decision or creating a new pending request

### Requirement: Mixed-graph integration with unchanged topology

Real rerun SHALL require `hitl2=real` (which transitively requires the full chain through wave0, wave1, wave2_synthesis, and targeted_evidence). Selecting `rerun=real` without `hitl2=real` SHALL fail before graph invocation. The full-fake rerun SHALL remain unchanged, preserving the existing `generation <= MAX_FAKE_RERUN_GENERATIONS` ceiling check and the `{"next": "topic_planning", "exhausted": END}` edge set. Topology SHALL be unchanged — only the allowed route values expand to include `wave0` and `wave1`.

#### Scenario: Real rerun requires real hitl2
- **WHEN** a recipe selects `rerun=real` without `hitl2=real`
- **THEN** recipe construction fails with a typed dependency error

#### Scenario: Full-fake rerun remains unchanged
- **WHEN** the full-fake graph reaches the rerun node at generation 1
- **THEN** it bumps generation to 2 and routes `next` → `topic_planning` with no scope, no invalidation, and no WorkSpec creation

#### Scenario: Real rerun back edges coexist with fake-compat edge keys
- **WHEN** the real rerun node routes to `"topic_planning"`, `"wave0"`, or `"wave1"`
- **THEN** the graph topology accepts the route — the conditional edge map includes the new semantic keys alongside the existing `"next"` key (fake backward compat) and `"exhausted"` key, both of which route to the same targets as before

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
