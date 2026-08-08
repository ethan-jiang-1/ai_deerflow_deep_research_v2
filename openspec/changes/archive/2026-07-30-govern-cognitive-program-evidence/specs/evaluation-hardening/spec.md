> req: EVH-017, EVH-023

## MODIFIED Requirements

### Requirement: Cognitive-program evidence uses explicit proof classification

Every active-branch ledger evidence link SHALL classify its referenced existing or new
central claim as `cognitive-program`, `deterministic-guardrail`, `wiring`, or
`obsolete-duplicate` before consolidation. The ledger SHALL retain exact branch
identity, source seam, and proof role. Every row SHALL retain distinct deterministic
composition, feedback-disposition, and guardrail/admission proof roles plus an
evaluation disposition. Active-branch closing links SHALL use only
`cognitive-program`, `deterministic-guardrail`, or `wiring`; `obsolete-duplicate` SHALL
remain non-closing. (`EVH-017`)

A node-board proof link MAY additionally use `human-decision` only for a conditional
typed human-decision admission/precondition claim. `human-decision` SHALL not close an
active model-branch role or claim that a human interaction exists. An
`obsolete-duplicate` link SHALL remain reviewable but SHALL NOT close a required proof
role, justify test deletion, or be inferred from an aggregate outcome.

#### Scenario: Proof class is constrained by evidence context
- **WHEN** node-board and active-branch proof links are validated
- **THEN** a conditional HITL2 boundary may use `human-decision`, active model branches
  reject that class, and `obsolete-duplicate` closes neither context

## ADDED Requirements

### Requirement: Evidence consolidation preserves named risks without a count target

Any proposed retirement or replacement of a collected test-evidence selector SHALL be
represented by a typed consolidation decision before deletion. The decision SHALL
identify the displaced claim and selector, every affected requirement and named risk,
and the collected retained claim or claims that continue to prove each risk at the
lowest responsible seam. A retained claim at a different seam, authenticity level, or
evidence class SHALL include a bounded rationale for why the original risk remains
proved without overclaiming model judgment or workflow authenticity. (`EVH-023`)

Validation SHALL reject an unknown or uncollected displaced/replacement claim, an
unmapped requirement or risk, self-replacement, a replacement that does not own the
mapped requirement, any seam/evidence-class/authenticity difference without
justification, and any proposal justified only by aggregate test count, directory
placement, marker, or line coverage. An evidence board or consolidation decision SHALL
not itself delete a test or authorize deletion. This change's accepted retirement set
SHALL be empty.

#### Scenario: Unmapped retirement is rejected
- **WHEN** a consolidation candidate removes a selector without mapping every affected
  requirement and named risk to collected retained proof
- **THEN** deterministic evidence governance rejects the decision before any test is
  deleted or any requirement is presented as covered

#### Scenario: Aggregate count cannot justify consolidation
- **WHEN** a consolidation candidate cites only a desired pytest total, marker balance,
  directory placement, line coverage, or an aggregate passing selector
- **THEN** validation rejects it because no displaced risk has been preserved at its
  responsible seam

#### Scenario: Different evidence metadata remains bounded
- **WHEN** retained proof uses a different seam, authenticity level, or evidence class
- **THEN** the decision explains that exact difference and gives a bounded reason the
  replacement preserves the original named risk without claiming a universal strength
  ordering or model quality from deterministic evidence

#### Scenario: Governance rollout deletes no tests
- **WHEN** this evidence-board change is applied
- **THEN** the retirement decision set is empty and every currently collected test
  remains present, regardless of the resulting aggregate count
