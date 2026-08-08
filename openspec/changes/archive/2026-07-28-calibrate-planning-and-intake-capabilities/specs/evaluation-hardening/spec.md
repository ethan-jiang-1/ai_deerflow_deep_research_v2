> req: EVH-015

## ADDED Requirements

### Requirement: Planning and initial-intake calibration has independent branch evidence

Test-owned evidence SHALL add independent normal and highest-risk
`REAL_NODE_FAKE_CAPABILITIES` claims for each newly migrated branch: topic planning,
topic-planning repair, Wave1 worker, and Wave1 repair. The claims SHALL extend the
global capability matrix from eight to twelve rows and assert capability posture plus
deterministic candidate admission or non-admission at the owning node/work-unit seam.
Wave0 SHALL retain its existing matrix claims. Separately, the planner, Wave0 worker,
and Wave1 worker SHALL retain collected `SCRIPTED_REAL_WORKFLOW` claims through their
real bridge/runtime path; any revised selector SHALL assert the applicable call bounds,
order, and observable tool/admission boundary. Neither evidence class SHALL use
another branch, an aggregate selector/count, catalog text, or fake-adapter prose as
evidence of live model, source, or research quality. (`EVH-015`)

#### Scenario: Newly migrated branches have independent normal and risk proof
- **WHEN** planning and initial-intake calibration evidence is collected
- **THEN** the four newly migrated branches extend the capability matrix to twelve
  rows with distinct real-node/fake-capabilities claims for normal behavior and their
  highest-risk posture or repair behavior at the declared lowest responsible seam

#### Scenario: Scripted workflow does not replace branch admission evidence
- **WHEN** a planner, Wave0, or Wave1 calibration case consumes scripted model/tool
  turns through the real runtime bridge
- **THEN** it proves call bounds, untrusted-data handling, and deterministic candidate
  admission only, while the separate matrix claim proves the branch capability; neither
  claim asserts authoritative source truth or high-quality research
