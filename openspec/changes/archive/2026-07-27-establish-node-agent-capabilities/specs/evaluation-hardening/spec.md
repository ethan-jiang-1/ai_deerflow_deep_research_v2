> req: EVH-012

## ADDED Requirements

### Requirement: Node-agent capability claims use an explicit branch evidence denominator

For an active node-agent capability cohort, test-evidence governance SHALL register a
closed branch-by-behavior-by-authenticity matrix before a branch can claim migration.
Each row SHALL name the direct production branch, capability ID, catalog source,
declaration source, lowest responsible entrypoint, and two distinct central
`TestEvidenceClaim` IDs: one for successful behavior and one for the highest-risk
behavior. The referenced claims SHALL have different collected selectors and retain
their own deterministic authenticity. The evidence checker SHALL reject a missing row,
duplicate branch, unknown capability, missing/identical/unknown claim ID, uncollected
claim, a claimed migrated branch without both behaviors, a claim for a different
branch, or an owner-level/aggregate-count substitution. The matrix SHALL not claim
live model quality from fake or scripted deterministic evidence.
(`EVH-012`)

#### Scenario: Six cohort branches have independent deterministic claims
- **WHEN** the first cohort registers its normal and repair branches
- **THEN** all six rows resolve to their own two collected claim IDs, with success and
  highest-risk coverage appropriate to each branch's tool posture and repair boundary

#### Scenario: Aggregate tests cannot claim capability migration
- **WHEN** a requirement impact names only a broad owner test, pytest total, or a
  selector for a different branch as evidence for a cohort branch
- **THEN** evidence governance rejects the claim before release or archive evidence
  can present that branch as migrated
