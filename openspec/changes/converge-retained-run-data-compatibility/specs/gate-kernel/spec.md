> req: GAK-004

## MODIFIED Requirements

### Requirement: Bounded repair loop with fatigue escalation

The repair loop SHALL be driven by the graph topology: when the gate returns
`PhaseVerdict.REPAIR`, the `route_map` SHALL produce the repair route label, and
the conditional edge SHALL route to the repair target (which may be the same phase
for self-repair, or a different node). The repair target node on re-entry SHALL
read `latest_gate_feedback` to obtain the structured `inspect` and `advice` for the
repair agent. After the repair agent completes, the gate SHALL evaluate again.

The gate SHALL track the failure fingerprint (stable-ordered tuple of
`(failure_code, rule_name)` for all failures in a single evaluation) and store it
in `GateResult.fingerprint`. `GateResult.consecutive` SHALL count how many
consecutive evaluations of the **same phase** produced the same fingerprint: the
gate SHALL read the previous `GateResult` from `latest_gate_feedback`; if
`previous.phase == current_phase` and the previous fingerprint matches the current
one, `consecutive = previous.consecutive + 1`; otherwise `consecutive = 1`. If
`consecutive >= 3`, the gate SHALL escalate to `PhaseVerdict.BLOCKED` with
`FATIGUE_ESCALATION` regardless of remaining budget. No new state fields are
required -- `latest_gate_feedback` stores the serialized `GateResult` including the
phase, fingerprint, and consecutive count.

The default repair budget SHALL be 3 per phase; `final_delivery` self-repair SHALL
default to 1. Maximum budget SHALL be 10 per phase. The gate kernel SHALL use only
`gate_attempts_by_phase` and `repair_budget_by_phase` as durable repair-attempt and
repair-budget facts. It SHALL neither read, write, reconstruct, nor reset a
`repair_counts` checkpoint field. Checkpoint compatibility disposition occurs before
gate evaluation; the gate SHALL not treat an old field as an alternate budget,
repair-history hint, or admission exception. (`GAK-004`)

#### Scenario: Successful repair after one retry
- **WHEN** the first gate evaluation returns `REPAIR`, the repair agent runs, and the second gate evaluation returns `PASS`
- **THEN** the phase advances with `gate_attempts_by_phase[phase] == 2` and `repair_budget_by_phase[phase]` decremented by 1

#### Scenario: Budget exhaustion blocks the phase
- **WHEN** the gate returns `REPAIR` for the same phase until `remaining_budget` reaches 0
- **THEN** the next evaluation returns `BLOCKED` with `REPAIR_BUDGET_EXHAUSTED` and the phase does not advance

#### Scenario: Fatigue escalation blocks despite remaining budget
- **WHEN** the same failure fingerprint appears for 3 consecutive gate evaluations on the same phase, even with budget remaining
- **THEN** the gate returns `BLOCKED` with `FATIGUE_ESCALATION` and the failure list includes the stable fingerprint

#### Scenario: Different fingerprint resets fatigue counter
- **WHEN** a repair attempt produces a different failure fingerprint from the previous attempt
- **THEN** the fatigue counter resets to 1 for the new fingerprint and budget continues to decrement normally

#### Scenario: First evaluation starts consecutive at 1
- **WHEN** `evaluate_gate` runs for the first time on a phase and `latest_gate_feedback` is `None` or its `phase` field differs from the current phase
- **THEN** `GateResult.consecutive` is 1 regardless of the failure fingerprint

#### Scenario: Different phase feedback does not affect fatigue
- **WHEN** wave0 gate evaluation stores its `GateResult` (phase="wave0") in `latest_gate_feedback`, then wave1 gate evaluates for the first time
- **THEN** wave1 gate sees `previous.phase == "wave0" != "wave1"`, resets `consecutive = 1`, and does not compare fingerprints across phases

#### Scenario: Repair agent receives full gate feedback
- **WHEN** the repair target node re-enters after a `REPAIR` verdict
- **THEN** the repair agent's context includes `GateResult.inspect`, `GateResult.advice`, and `GateResult.failed_refs` from the most recent evaluation

#### Scenario: Retired repair counter cannot reach gate evaluation
- **WHEN** a checkpoint containing `repair_counts` reaches the current graph reader without an approved completed migration
- **THEN** it is rejected before any gate rule, route, feedback, or repair-budget mutation occurs

#### Scenario: Migrated checkpoint uses only current repair facts
- **WHEN** a registered checkpoint is migrated by the approved offline route and then evaluated with the same current gate facts
- **THEN** its verdict, route, and bounded repair budget follow the current gate contract without consulting a replacement counter
