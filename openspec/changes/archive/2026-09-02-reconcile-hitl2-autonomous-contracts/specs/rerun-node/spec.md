> req: REN-001, REN-002, REN-003, REN-004, REN-005, REN-006, REN-007, REN-008

## MODIFIED Requirements

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
