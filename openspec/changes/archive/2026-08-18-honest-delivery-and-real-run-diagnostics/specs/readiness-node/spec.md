## MODIFIED Requirements

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
