> req: DER-005

## MODIFIED Requirements

### Requirement: Fast-lane duration regressions have a bounded CI disposition

The deterministic CI path SHALL retain the canonical verification gate and then run a
project-owned duration-policy check over a JUnit report from the same fast-lane test
invocation, while printing pytest's twenty slowest durations. A fast-lane test taking
more than five seconds SHALL fail the policy unless an exact-selector typed waiver
records its distinct reason, responsible owner, and bounded review/expiry point.

The repository SHALL track and expose the deterministic CI workflow, the manual-only
live-evaluation workflow, the project OpenSpec skill tree, and its declared agent
target. Root ignore rules SHALL NOT classify any of those required delivery artifacts
as local-only. A deterministic delivery guard SHALL fail when a required workflow,
skill, or target is missing, untracked, or hidden by an applicable ignore rule, and
SHALL NOT accept an ignored local copy, an undeclared external installer, or a
host-specific discovery path as evidence of clean-clone availability.

#### Scenario: Unwaived slow test fails CI policy

- **WHEN** the fast-lane JUnit report contains a test whose duration exceeds five
  seconds and no matching valid waiver exists
- **THEN** the duration-policy command fails with that exact selector and duration

#### Scenario: Reviewed waiver is narrow and temporary

- **WHEN** a slow test has a waiver
- **THEN** it applies only to the exact selector, includes a distinct reason and owner,
  and is rejected after its declared review or expiry point

#### Scenario: Required delivery artifacts are discovered from a clean clone

- **WHEN** repository delivery is evaluated without pre-existing local tooling
- **THEN** the tracked deterministic workflow, manual-live workflow, project skill
  tree, and declared target are present and discoverable through their documented
  repository paths

#### Scenario: Deterministic CI remains distinct from the manual-live lane

- **WHEN** the tracked workflow definitions are evaluated
- **THEN** the deterministic route invokes the canonical deterministic verification
  and duration-policy checks, while the credentialed live route remains manual-only
  and is not selected as deterministic CI

#### Scenario: A missing or ignored required delivery artifact fails closed

- **WHEN** a controlled repository fixture removes tracking for, removes, or ignores
  one required delivery artifact
- **THEN** the delivery guard fails before it can claim the CI or OpenSpec lifecycle
  route is available
