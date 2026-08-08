## MODIFIED Requirements

### Requirement: Test selection and requirement traceability are mechanical

Stable commands and markers SHALL separately select fast correctness, integration
correctness, deterministic workflow conformance, live evaluation, and release
acceptance. The canonical complete deterministic command SHALL include the exact
union of the three zero-API focused selections while excluding credentialed and
deferred-provider tests. Every alive requirement SHALL retain at least one
collected deterministic test-side `@impl` reference.

`openspec/governance/req-registry.yaml` SHALL remain the only append-only
requirement registry. For each active main specification, the pre-heading
`> req:` declaration SHALL list exactly the non-retired registry IDs owned by that
specification capability, and no ID owned by another capability. The registry
checker SHALL provide the same validated alive-requirement ownership projection
consumed by requirement-coverage governance, so a malformed, missing, or misowned
header fails both paths instead of leaving an orphan/coverage disagreement. Main
spec structural governance SHALL separately reject a missing, empty, or
archive-placeholder `## Purpose` and a missing `## Requirements` section.

Governance SHALL additionally scan Python module/class/function docstrings and
comment tokens under the canonical production root `agent/src/**/*.py`, using the
same registry-entry and `[DEPRECATED]` semantics, and reject every production-source
`@impl` ID that is absent from the registry or retired. Source decoding, parsing,
or tokenization failure SHALL fail closed with an actionable repository-relative
location; arbitrary string literals, tests, docs, generated reports, and archived
artifacts SHALL NOT be treated as ownership. Production-source annotations remain
optional implementation ownership and SHALL NOT substitute for collected test
evidence.

Governance SHALL reject focused-selection overlap, an empty workflow selection,
scenario families without deterministic cases, cases without collected claims,
contradictory inventory mappings, unknown or uncovered active requirement IDs, and
cross-lane requirements missing any asset class or authenticity declared by their
evidence policy. Asset classes are independent required evidence, not a single
ordered minimum. Each validator SHALL have direct invalid-fixture coverage for
every rule it owns; a collector, syntax-aware discovery scan, archive scan, or
runtime detector that could succeed on empty or mis-scoped input SHALL retain a
focused detector smoke case. The named `req-registry.yaml.tmp` temporary copy
SHALL be absent as a repository artifact.

Active main specifications, registry descriptions, `agent/AGENTS.md`, and
`agent/README.md` SHALL state current behavior rather than archive chronology.
They SHALL NOT retain numbered-change completion narratives, superseded
fake/real claims, or phase-roadmap wording. `full_fake` is permitted only where
it names the current all-fake recipe, fake-demo behavior, or public reflected-tool
safety boundary; it SHALL NOT label a mixed or all-real recipe. Archived OpenSpec
artifacts are historical context and are excluded from this current-authority scan.

For this requirement, function docstrings include both synchronous and async
functions.

#### Scenario: Missing main-spec header ownership fails closed
- **WHEN** a live registry ID is absent from its capability's main-spec `> req:` header
- **THEN** registry consistency and requirement coverage both fail with the ID and repository-relative spec path

#### Scenario: Foreign header ownership fails closed
- **WHEN** a main-spec header declares an active ID owned by another capability
- **THEN** governance fails before test evidence can treat that ID as alive for the wrong specification

#### Scenario: Placeholder Purpose is rejected
- **WHEN** an active main spec contains an archive-generated `TBD` Purpose placeholder or lacks its Purpose/Requirements section
- **THEN** main-spec structural governance fails with the affected main-spec path

#### Scenario: Unknown or retired production ownership fails closed
- **WHEN** a Python docstring or comment under the canonical production source root contains an `@impl` ID that is unknown to the registry or marked `[DEPRECATED]`
- **THEN** requirement coverage fails with the offending requirement ID and repository-relative source path

#### Scenario: Valid production ownership does not create a coverage mandate
- **WHEN** production source references only active registered IDs and some active requirements intentionally have no production annotation
- **THEN** production ownership validation passes while collected deterministic coverage remains independently required for every active requirement

#### Scenario: Production discovery cannot pass from the wrong root
- **WHEN** a detector smoke fixture places a known invalid annotation under the canonical production source subtree
- **THEN** the syntax-aware source scan discovers and rejects it rather than passing from an empty or mis-scoped input

#### Scenario: Invalid production source cannot bypass ownership validation
- **WHEN** a Python source file under the canonical production root cannot be decoded, parsed, or tokenized
- **THEN** requirement coverage fails closed with an actionable repository-relative diagnostic rather than silently omitting the file

#### Scenario: Temporary registry copy cannot become authority
- **WHEN** requirement governance inspects repository registry surfaces
- **THEN** `req-registry.yaml` is the sole registry and `req-registry.yaml.tmp` is absent

#### Scenario: Cross-lane requirement needs every declared evidence class
- **WHEN** an active requirement is listed in the requirement-evidence policy with required deterministic, workflow, live, or release asset classes and one class is absent
- **THEN** requirement coverage fails with the requirement ID, missing class or authenticity, and observed claims

#### Scenario: Ordinary requirement does not inherit a blanket workflow mandate
- **WHEN** an active requirement is not authenticity-sensitive
- **THEN** an appropriate collected deterministic claim at its responsible seam satisfies coverage without an artificial workflow case

#### Scenario: Focused selections partition deterministic collection
- **WHEN** collection is performed for fast correctness, integration correctness, workflow conformance, and the complete deterministic aggregate
- **THEN** the three focused selector sets are pairwise disjoint and their union equals the aggregate, while live, release, and Postgres selectors remain excluded

#### Scenario: Empty scan cannot masquerade as enforcement
- **WHEN** collection, ownership discovery, archive scanning, or runtime detection is added or materially changed and its input is empty, relocated, or mis-scoped
- **THEN** a focused smoke case proves that a known target violation is detected, while pure validation rules retain direct minimal invalid-fixture tests

#### Scenario: Active historical terminology is rejected
- **WHEN** an active main spec, registry description, module guide, or README contains a numbered-change completion narrative, an obsolete phase-completion claim, or an unapproved `full_fake` use
- **THEN** deterministic governance fails with the active file and matched rule, while the same text in an archived OpenSpec artifact does not affect the result

#### Scenario: Test-evidence authority survives change archival
- **WHEN** this delta is active, synchronized, or archived and a later change needs the current test-evidence contract
- **THEN** pending modifications are discoverable from the active owning delta, approved semantics are discoverable from the `evaluation-hardening` main spec, exact evidence metadata remains in test-owned registries, and archived artifacts are not current authority
