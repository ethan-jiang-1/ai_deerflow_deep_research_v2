## MODIFIED Requirements

### Requirement: Node determines its own route based on hard-rule results and critic verdicts

The readiness node SHALL write its own `route` field. Route determination SHALL retain
this priority: structural hard-rule failures, including accepted-evidence reader
failures, route to `exhausted` with `BLOCKED`; any admitted or conservatively projected
`blocked_repair_required` verdict routes to `repair_targeted` — **unless the wave2 gate
has already exhausted and degraded, in which case it routes to `pass` instead**;
otherwise it routes to `pass`. A critic candidate SHALL NOT select, write, or bypass a
route. The wave2-degraded condition is read-only from checkpoint state: it holds exactly
when the gate-owned `degraded_decisions` field contains the
`wave2_synthesis:exhaustion_degraded` marker, meaning the wave2 repair budget is spent
and any further `repair_targeted` route would be re-evaluated by the wave2 gate at
exhausted budget with the degradation marker present and therefore terminate the run
`blocked` without a report. In that state the only non-terminal route is `pass`, which
delivers the degraded pass contract: the report plan keeps disclosing the
gate-recorded unresolved searchable gaps as mandatory uncertainties. A non-degraded run
SHALL keep the existing repair loop exactly as before. (`REA-004`)

#### Scenario: Admitted critic result routes through deterministic owner
- **WHEN** hard rules pass and the admitted candidate contains a
  `blocked_repair_required` verdict and the wave2 gate has not degraded
- **THEN** the readiness node writes `repair_targeted` and the critic writes no route

#### Scenario: Insufficient judgment remains an honest pass projection
- **WHEN** hard rules pass and all admitted verdicts are
  `ready_substantive` or `ready_insufficient_judgment`
- **THEN** the node writes `pass` and the report plan records each insufficiency as a
  mandatory uncertainty

#### Scenario: Structural failures still take priority
- **WHEN** a structural hard-rule failure and any critic verdict are present
- **THEN** the node writes `exhausted` with the existing blocked terminal facts,
  even when the wave2 gate has degraded

#### Scenario: Wave2-degraded run never re-opens the spent repair loop
- **WHEN** `degraded_decisions` contains `wave2_synthesis:exhaustion_degraded` and
  hard rules pass but the critic (admitted or conservative fallback) reports
  `blocked_repair_required` for one or more questions
- **THEN** the node writes `pass`, `readiness_blocked_count` still counts the
  blocked questions, and the report plan discloses every unresolved searchable gap
  as a mandatory uncertainty instead of routing `repair_targeted`

#### Scenario: Wave2-degraded run with a failed critic still delivers
- **WHEN** `degraded_decisions` contains `wave2_synthesis:exhaustion_degraded` and
  the bounded critic execution fails (timeout, configuration, provider, or policy)
- **THEN** readiness projects conservative `blocked_repair_required` verdicts as
  before, but routes `pass` (not `repair_targeted`), so the run continues to
  `final_delivery` and the report carries the disclosed gaps
