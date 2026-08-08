> req: EVH-016

## ADDED Requirements

### Requirement: Evidence-evaluation calibration has independent branch proof

Test-owned evidence SHALL preserve Wave2's existing normal and highest-risk
`REAL_NODE_FAKE_CAPABILITIES` claims and add independent normal and highest-risk
claims for each newly migrated targeted branch: worker, repair, SourceDiagnostic, and
ClaimVerifier. The global capability matrix SHALL therefore expand from twelve to
sixteen rows. Each claim SHALL assert only the direct branch's capability posture and
deterministic candidate admission or non-admission at its owning synthesis,
work-unit, or critic-materializer seam. Separate collected `SCRIPTED_REAL_WORKFLOW`
claims SHALL exercise the real Wave2, targeted-worker, and critic bridge paths for
their applicable tool-call bounds, untrusted-data boundary, and observable admission
or non-admission. No claim SHALL use another branch, an aggregate selector/count,
catalog text, fake-adapter prose, or a scripted transcript as evidence of live model,
source, critic, or research quality. (`EVH-016`)

#### Scenario: Final cohort has direct normal and risk evidence
- **WHEN** evidence-evaluation calibration evidence is collected
- **THEN** every one of the four targeted branches has a distinct normal and
  highest-risk matrix claim at the lowest responsible owning seam, while Wave2 retains
  its existing direct claims and the matrix contains sixteen rows

#### Scenario: Workflow evidence remains separate from branch admission evidence
- **WHEN** a Wave2, targeted worker, or critic calibration case consumes scripted
  model/tool turns through the real runtime bridge
- **THEN** it proves only declared call bounds, untrusted-data handling, and
  deterministic candidate admission or non-admission; a separate direct claim proves
  the branch capability and neither proves research quality or source truth
