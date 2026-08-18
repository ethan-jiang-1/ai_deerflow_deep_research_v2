## MODIFIED Requirements

### Requirement: Gate definitions collect all rules and produce deterministic verdicts

The system SHALL define `GateDefinition` as a named collection of `GateRule`
instances registered for a specific phase. `GateRule` SHALL carry a rule name, a
synchronous evaluation function `(ResearchState) -> Failure | None`, and a
`failure_code` (the code this rule is registered to produce; the actual code on a
returned `Failure` MAY differ when the rule discriminates among multiple outcomes).
Rules are pure (no I/O, no model calls), so they are synchronous. `Failure` SHALL
carry the `FailureCode`, its classification (`hard | semantic | repairable |
degradable`), the rule name, a human-readable description, and an optional `ref:
str | None` (a work/attempt id or sandbox path identifying the failing artifact).
`GateResult` SHALL contain the `phase: str` that was evaluated, the typed
`PhaseVerdict`, a stable-ordered list of every `Failure`, an `inspect` summary
string (≤ 512 chars), an `advice` string for the repair agent (≤ 2048 chars),
`failed_refs` (collected from all non-None `Failure.ref` values), a `degraded:
bool` flag, the current `attempt` count for this phase
(`(gate_attempts_by_phase[phase] or 0) + 1` — the post-increment count),
`remaining_budget` (after decrement on REPAIR, or initial default on first
evaluation), `new_generation: int | None` (set to `state["generation"] + 1` on
PASS/BLOCKED, `None` on REPAIR), the failure fingerprint tuple, and a
`consecutive` counter for fatigue tracking. `GateDefinition` SHALL carry a
`route_map: dict[PhaseVerdict, str]` (or a `route_resolver` callable for phases
with multiple repair targets) and a `default_budget: int` for lazy budget
initialization.

A phase node SHALL be permitted to hand a budget-class execution failure to its gate
instead of writing a terminal state: the node records a bounded state signal owned
by that node's writer role, returns a non-terminal update, and a registered gate
rule projects the signal as a `Failure` (classification `repairable` unless the
phase's degradation policy says otherwise). Such a projected failure SHALL enter the
existing verdict, budget, fatigue, and exhaustion-degradation machinery unchanged —
no new verdict, route, or degradation path is added by this hand-back, and the
gate's `degraded_decisions` marker remains the sole bound on degradation.

The evaluate function SHALL run every registered rule, collect all failures in
registration order, and derive the verdict as: `blocked` if any hard failure exists
or the budget is exhausted for repairable failures; `repair` if only
repairable/semantic failures exist and budget remains; `pass` otherwise (including
when only degradable failures exist, which SHALL set `degraded=True` on the
`GateResult`). `PhaseVerdict.NEEDS_HUMAN` is reserved for future use — no
`FailureCode` classification produces it in this change, and no fixture rule
triggers it. The `route_map` (or `route_resolver`) SHALL translate the verdict to
the route string written to `state["route"]`; a `degraded_pass` SHALL map to the
same route label as `pass`.

`GateDefinition` SHALL additionally carry an opt-in
`degraded_pass_on_exhaustion: bool` (default `false`). For a gate that declares it,
budget exhaustion with no hard failure SHALL produce `pass` with `degraded=True`
(riding the same route label as `pass`, and NOT appending
`REPAIR_BUDGET_EXHAUSTED` or writing any terminal transition) instead of `blocked`,
provided this phase has not already produced an exhaustion-degraded pass since its
repair budget was last seeded. The kernel SHALL bound degradation through the
gate-owned `degraded_decisions` state field: the state update for an
exhaustion-degraded pass appends one stable marker (`<phase>:exhaustion_degraded`)
and a later exhaustion evaluation of the same phase with the marker present
escalates to `blocked` exactly as for a gate without the policy. Any hard failure
SHALL still block regardless of the policy. The rerun planner's gate-state reset
SHALL clear the phase's marker together with the budgets it already resets, so a
fresh research round can degrade at most once again.

#### Scenario: All rules pass produces pass verdict
- **WHEN** `evaluate_gate` runs all rules and none returns a Failure
- **THEN** `GateResult.verdict` is `PhaseVerdict.PASS`, `failures` is empty, and `inspect` summarizes no issues

#### Scenario: Single repairable failure with budget produces repair verdict
- **WHEN** one rule returns a repairable `Failure` and `remaining_budget` is at least 1
- **THEN** `GateResult.verdict` is `PhaseVerdict.REPAIR`, `failures` contains that one failure, and `advice` describes the failure for the repair agent

#### Scenario: Hard failure produces blocked verdict regardless of budget
- **WHEN** one rule returns a hard `Failure` even when budget remains
- **THEN** `GateResult.verdict` is `PhaseVerdict.BLOCKED`, no repair is attempted, and `advice` states the hard failure cannot be repaired

#### Scenario: A projected node budget failure rides the existing machinery
- **WHEN** a phase node hands back a budget-class failure signal and the phase gate
  projects it as a repairable rule failure
- **THEN** the verdict, budget decrement, fatigue fingerprint, and any
  exhaustion-degradation follow the existing kernel branches with no new route or
  verdict kind, and only the gate may append the degradation marker

#### Scenario: Budget exhaustion with repairable failures escalates to blocked
- **WHEN** repairable failures exist but `remaining_budget` is 0
- **THEN** `GateResult.verdict` is `PhaseVerdict.BLOCKED` with `REPAIR_BUDGET_EXHAUSTED` in the failure list

#### Scenario: Declared exhaustion policy degrades to a bounded honest pass
- **WHEN** a gate with `degraded_pass_on_exhaustion=true` exhausts its budget with
  only semantic/repairable failures remaining, no hard failure, and no prior
  exhaustion-degraded marker for the phase
- **THEN** `GateResult.verdict` is `PhaseVerdict.PASS` with `degraded=True`, the
  route label equals `route_map[PASS]`, no `REPAIR_BUDGET_EXHAUSTED` failure or
  terminal transition is produced, and the state update appends the phase's
  `exhaustion_degraded` marker to `degraded_decisions`

#### Scenario: Degradation happens at most once per budget seeding
- **WHEN** the same phase evaluates at exhausted budget again after it already
  produced an exhaustion-degraded pass (marker present)
- **THEN** the verdict is `PhaseVerdict.BLOCKED` with `REPAIR_BUDGET_EXHAUSTED`
  exactly as for a gate without the policy

#### Scenario: Hard failure still blocks under the declared policy
- **WHEN** a gate with `degraded_pass_on_exhaustion=true` collects any hard failure
- **THEN** the verdict is `PhaseVerdict.BLOCKED` regardless of budget, marker, or policy

#### Scenario: Rerun reset restores one degradation opportunity
- **WHEN** the rerun planner's gate-state reset runs after a phase degraded
- **THEN** the phase's `exhaustion_degraded` marker is cleared together with its
  gate attempts and repair budget, and a later exhaustion may degrade at most once
  more

#### Scenario: Undeclared gates keep today's exhaustion semantics
- **WHEN** a gate without `degraded_pass_on_exhaustion` exhausts its budget with
  semantic failures remaining
- **THEN** the verdict is `PhaseVerdict.BLOCKED` and no marker is written

#### Scenario: Degradable-only failures produce degraded pass
- **WHEN** all failures are classified `degradable` and no hard, semantic, or repairable failures exist
- **THEN** `GateResult.verdict` is `PhaseVerdict.PASS` with `degraded=True`, and routing uses the same route label as a clean pass

#### Scenario: Multiple repairable failures produce repair with combined fingerprint
- **WHEN** rule A and rule B both return repairable `Failure` values with different codes
- **THEN** `GateResult.verdict` is `PhaseVerdict.REPAIR`, `failures` lists both in registration order, `failed_refs` collects refs from both, and the fingerprint is `((code_A, rule_A), (code_B, rule_B))`

#### Scenario: Collect-all runs every rule even after a hard failure
- **WHEN** rule 1 returns a hard failure and rule 2 returns a repairable failure
- **THEN** both failures appear in `GateResult.failures` in registration order, and the verdict is `PhaseVerdict.BLOCKED`

#### Scenario: Route map translates verdict to topology edge label
- **WHEN** the gate produces `PhaseVerdict.BLOCKED` for wave0 with `route_map[BLOCKED] = "exhausted"`
- **THEN** the state update writes `route = "exhausted"`, matching the topology edge `TopologyEdge("wave0", "exhausted", "blocked")`

#### Scenario: Route map key missing for reachable verdict fails construction
- **WHEN** a `GateDefinition` is constructed with a `route_map` that is missing a key for a reachable verdict (one that the registered rules could produce)
- **THEN** construction fails with a typed error before any gate evaluation

#### Scenario: Route map value not in topology edge labels fails construction
- **WHEN** a `GateDefinition` is constructed with a `route_map` whose value is not a known topology route label (e.g. `"unknown_edge"`)
- **THEN** construction fails with a typed error before any gate evaluation

#### Scenario: Needs-human verdict is reserved
- **WHEN** the `PhaseVerdict` enum is inspected
- **THEN** `NEEDS_HUMAN` is defined but no `FailureCode` classification produces it; it is reserved for quality/critic use
