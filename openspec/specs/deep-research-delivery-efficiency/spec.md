# deep-research-delivery-efficiency Specification

> req: DER-001, DER-002, DER-003, DER-004, DER-005, DER-006

## Purpose

Keep Deep Research deterministic delivery verification fast, reproducible, and
truthful without weakening selection, architecture, ledger, or release evidence.
## Requirements
### Requirement: Deterministic collection is shared without changing selection truth

The Deep Research test-governance collector SHALL be the only collection interface
used by lane selection, replay registry, regression descent, workflow inventory, and
asset governance. For the project test root, it SHALL collect one validated catalog of
node ids and inherited marker names, then derive each existing path/marker query in
memory. It SHALL preserve existing selected-selector results and SHALL not cache a
failed, empty, or malformed catalog as success; temporary roots and injected commands
retain an isolated direct-collection path.

#### Scenario: Identical lane queries share one collection
- **WHEN** multiple deterministic governance checks request different lane selections
- **THEN** they derive their selector sets from one validated catalog without changing
  partition, overlap, workflow-inventory, or evidence assertions

#### Scenario: Changed collector inputs fail independently
- **WHEN** a caller supplies a different root, expression, paths, command, or a
  failing collector response
- **THEN** it does not receive an unrelated cached result and preserves the existing
  fail-closed error behavior

#### Scenario: Nested environment launch does not fragment the default cache
- **WHEN** the asset checker runs inside its prepared agent Python environment
- **THEN** its default collector invokes that current Python interpreter rather than
  spawning a nested environment launcher, while explicit injected commands and
  temporary roots remain isolated direct-collection paths

### Requirement: Architecture checker has one reusable implementation authority

The project architecture checker SHALL expose one in-process repository-check seam
used by its command-line adapter and suitable live contract tests. Its CLI arguments,
exit status, and diagnostic behavior SHALL remain verified separately where they are
the behavior under test.

#### Scenario: Live repository contract avoids redundant process spawn
- **WHEN** a test only needs to verify the checked-in repository satisfies the
  architecture contract
- **THEN** it invokes the reusable checker seam and reports the same validation result
  without a child Python process

#### Scenario: Command-line failure remains observable
- **WHEN** the checker is invoked with invalid repository input through its CLI
- **THEN** its nonzero exit and diagnostic remain testable and are not replaced by an
  in-process-only assertion

### Requirement: Ledger boundary evidence distinguishes exact limits from round-trip behavior

Ledger tests SHALL retain the exact production record and byte limits and reject
`MAX_SUBMISSION_LEDGER_RECORDS + 1` before parsing. Their normal edit-loop round-trip
proof SHALL use a bounded representative hash chain while still exercising canonical
encoding, parsing, and linkage; any full-limit success proof SHALL be explicitly
classified and justified as slow evidence.

#### Scenario: Representative round trip remains linked and canonical
- **WHEN** the normal deterministic suite constructs its bounded ledger chain
- **THEN** parsed records preserve their ordered hash links and the encoded ledger
  remains within the production byte limit

#### Scenario: Overflow remains fail-closed at the exact production boundary
- **WHEN** ledger input contains more than the configured maximum record count
- **THEN** validation rejects it before record parsing regardless of the bounded
  representative round-trip size

### Requirement: Focused verification targets expose purpose and elapsed time

The agent Make surface SHALL provide reviewed focused targets for intake, retained
observation, work-unit, and strict-checkpoint work. Each SHALL run its exact selector,
print one stable purpose and elapsed time, and remain explicitly supplemental to the
unchanged complete deterministic verification target.

#### Scenario: Developer chooses the smallest reviewed target
- **WHEN** a change affects one named focus area
- **THEN** its documented target executes only that area’s reviewed deterministic
  selector and reports elapsed time without running live or release dependencies

#### Scenario: Focused target cannot replace complete verification
- **WHEN** final verification or archive evidence is recorded
- **THEN** it still uses the canonical complete deterministic gate rather than
  presenting a focused target as release evidence

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

### Requirement: Aggregate fast-lane acceptance is measured with phase attribution

The change SHALL retain a validated reference-benchmark report with the exact command,
timestamp, Python/platform identity, selected-test count, collection duration,
setup duration, call duration, and total wall time. Under the recorded baseline
conditions, final evidence SHALL show `make test-fast` completes in at most 35
seconds; this reference acceptance SHALL remain distinct from the portable per-test CI
duration policy.

#### Scenario: Benchmark separates expensive work categories
- **WHEN** the reference fast-lane benchmark completes
- **THEN** its validated report separately identifies collection, setup, and call
  timing alongside its total and selected-test count

#### Scenario: Aggregate result cannot be substituted by a CI waiver
- **WHEN** a fast-lane test has a valid individual CI duration waiver
- **THEN** that waiver does not satisfy the reference 35-second aggregate acceptance
  unless the recorded benchmark itself is within the budget
