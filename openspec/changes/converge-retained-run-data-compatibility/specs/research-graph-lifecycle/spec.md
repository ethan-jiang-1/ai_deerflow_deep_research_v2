> req: REG-011

## MODIFIED Requirements

### Requirement: A versioned ResearchState schema fails closed on incompatible versions

The Bundle-local State reader and writer SHALL validate a closed supported
`ResearchState.schema_version` before reading, reducing, or projecting State. An
unsupported, malformed, incomplete, or incompatible State SHALL return a bounded
unavailable/schema outcome and SHALL not be silently reset, auto-migrated, or replaced.
Compatible migration mechanics, when separately approved, SHALL occur wholly inside the
available Bundle and preserve State version/atomicity/containment guarantees. (`REG-011`)

The current graph checkpoint schema SHALL omit `repair_counts`. Before graph
construction, node invocation, reducer application, or lifecycle projection, the graph
checkpoint reader SHALL accept only a current schema record or reject the record with
its existing bounded unsupported-schema/checkpoint outcome. It SHALL not silently
upgrade, reset, rewrite, or derive repair facts from an old checkpoint. Only an
explicitly registered old checkpoint may enter the separately invoked offline migration
route. That route SHALL decode and validate the complete old record, prove that removing
`repair_counts` leaves the current gate-owned attempt/budget facts intact, and atomically
write a current-schema record. Its source-controlled migration inventory is an operator
input and evidence record, not a runtime reader, lifecycle authority, or graph entry
selector. An old checkpoint absent from that inventory, malformed, partially migrated,
stale, or replayed across an incompatible identity SHALL be rejected without graph
mutation.

#### Scenario: Incompatible Bundle State is not replaced
- **WHEN** an available Bundle contains an unsupported State version
- **THEN** status, control, and inspection fail closed before graph work and no replacement State is written

#### Scenario: Unregistered legacy checkpoint fails before graph work
- **WHEN** the current graph reader receives a checkpoint with `repair_counts` that is not an approved completed migration output
- **THEN** it returns the bounded checkpoint/schema denial before graph compilation, node invocation, State reduction, or Bundle lifecycle action

#### Scenario: Registered checkpoint migration preserves current control facts
- **WHEN** the offline migration route processes a registered valid checkpoint with `repair_counts`
- **THEN** it validates the whole input, writes one current record without that field, and a reload/replay preserves the existing generation, terminal monotonicity, and gate attempt/budget facts

#### Scenario: Failed migration does not become a graph recovery path
- **WHEN** decoding, validation, identity matching, or atomic output of a registered checkpoint migration fails
- **THEN** no current checkpoint is written, the source record is unchanged, and the next legal runtime action is the same bounded rejection rather than resume or retry
