> req: EVH-015

## MODIFIED Requirements

### Requirement: Planning and initial-intake calibration has independent branch evidence

Test-owned evidence SHALL add independent normal and highest-risk
`REAL_NODE_FAKE_CAPABILITIES` claims for each newly migrated branch: topic planning,
topic-planning repair, Wave1 worker, Wave1 repair, Wave1 SourceDiagnostic, and Wave1
ClaimVerifier. The claims SHALL extend the global capability matrix from eight to
fourteen rows and assert capability posture plus deterministic candidate, review-
artifact, admission, or non-admission behavior at the owning node/work-unit/critic-
materializer seam. Wave0 SHALL retain its existing matrix claims. Separately, the
planner, Wave0 worker, Wave1 worker, and both Wave1 critics SHALL retain collected
`SCRIPTED_REAL_WORKFLOW` claims through their real bridge/runtime path; any revised
selector SHALL assert applicable call bounds, untrusted-data handling, and observable
tool/admission boundary. Neither evidence class SHALL use another branch, an aggregate
selector/count, catalog text, or fake-adapter prose as evidence of live model, source,
critic, or research quality. (`EVH-015`)

#### Scenario: Newly migrated branches have independent normal and risk proof
- **WHEN** planning and initial-intake calibration evidence is collected
- **THEN** the six newly migrated branches extend the capability matrix to fourteen rows with distinct real-node/fake-capabilities claims for normal behavior and their highest-risk posture, repair, or bound-artifact behavior at the declared lowest responsible seam

#### Scenario: Scripted workflow does not replace branch admission evidence
- **WHEN** a planner, Wave0, Wave1 worker, or Wave1 critic calibration case consumes scripted model/tool turns through the real runtime bridge
- **THEN** it proves call bounds, untrusted-data handling, and deterministic candidate or review-artifact admission only, while the separate matrix claim proves the branch capability; neither claim asserts authoritative source truth or high-quality research
