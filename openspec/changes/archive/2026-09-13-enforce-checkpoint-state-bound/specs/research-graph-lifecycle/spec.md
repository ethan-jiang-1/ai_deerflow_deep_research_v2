> req: REG-008

## MODIFIED Requirements

### Requirement: Large research content stays out of the checkpoint as bounded content refs

`ResearchState` SHALL NOT store web page bodies, PDFs, full evidence summaries, full
reports, screenshots, large tool output, or full HITL1 profile JSON bodies. Such content
SHALL live only as sandbox artifact files, and `ResearchState` SHALL reference it by at
most a sandbox path, a content hash, a schema version, and a short summary. A hard
checkpoint-size bound SHALL reject any state update whose serialized form exceeds the
bound; semantic content SHALL fail validation rather than be silently truncated. Raw
runtime authority - `TrustedRuntimeEnvelope` fields, AppConfig, model and tool handles,
sandbox handles, file handles, host paths, and credentials - SHALL NOT enter the
checkpoint.

The bound SHALL be enforced on the live path at the persisted graph-checkpoint write
boundary, not only in offline validation: the write of an over-bound checkpoint or
single write value SHALL fail before any bytes reach the Bundle-contained graph store,
so the checkpoint is not mutated. The same bound and the same canonical serialization
SHALL also gate reading or resuming a retained checkpoint before graph compilation and
SHALL gate offline migration output, so write, read, and migration share one definition.
An over-bound state update SHALL terminate the run as a blocked Bundle with the
deterministic cause `checkpoint.inconsistent` (`RunFailureCode.CHECKPOINT_INCONSISTENT`)
and terminal reason `INTERNAL_BLOCKED`, recorded as a compact status-visible incident
with `FailureCertainty.DIRECT`; it SHALL NOT be repaired, retried, or silently truncated.

The per-block work-unit bound SHALL remain strictly below the whole-state bound. The
whole-state bound is the sole arbiter: keeping every individually bounded sub-block
within its own limit SHALL NOT admit an aggregate whose serialized form exceeds the
whole-state bound.

The HITL1 final `ResearchProfile` SHALL be serialized as canonical JSON in
`request/profile.json`; the checkpoint SHALL store only `profile_ref`, short enum/string
fields, bounded `must_answer_questions`, `degraded_profile`, and bounded transient
progress needed to ask follow-ups.

#### Scenario: Oversized content is rejected
- **WHEN** a node returns a state update whose serialized size exceeds the hard checkpoint-size bound
- **THEN** the update is rejected with a typed failure and the checkpoint is not mutated

#### Scenario: Content is referenced, not embedded
- **WHEN** a state update carries large content
- **THEN** the reducer stores only a `ContentRef` (sandbox path, content hash, schema version, short summary) and excludes the raw body from the checkpoint

#### Scenario: Raw runtime authority is rejected
- **WHEN** a state update includes a `TrustedRuntimeEnvelope`, AppConfig, model/tool handle, sandbox handle, or credential field
- **THEN** the reducer rejects the unknown field and the checkpoint is not mutated

#### Scenario: HITL1 profile body is referenced, not embedded
- **WHEN** a complete HITL1 profile includes scope boundaries or custom notes
- **THEN** those full profile values live in `request/profile.json`, while the checkpoint contains only the bounded `ContentRef` and short planning fields

#### Scenario: Runtime authority is rejected from profile state
- **WHEN** a state update tries to carry a request-bundle writer, host path, file handle, AppConfig, model handle, or sandbox handle
- **THEN** checkpoint validation rejects the update and no profile state is mutated

#### Scenario: An over-bound write is rejected before the checkpoint is mutated
- **WHEN** a graph write or checkpoint whose serialized form exceeds the hard bound is
  about to be persisted to the Bundle-contained graph store
- **THEN** persistence fails with the typed bound error before any bytes are written, and
  the store's prior bytes remain unchanged

#### Scenario: An over-bound node update terminates as a blocked run
- **WHEN** a node returns a state update that crosses the hard bound
- **THEN** the run records terminal `BLOCKED` with incident `checkpoint.inconsistent`,
  terminal reason `INTERNAL_BLOCKED`, and `FailureCertainty.DIRECT`, without a repair
  route, an automatic restart, or a persisted over-bound state

#### Scenario: A retained over-bound checkpoint is rejected before graph compilation
- **WHEN** a retained Bundle graph checkpoint exceeds the hard bound
- **THEN** reading or resuming that Bundle rejects it with the typed
  inconsistent-checkpoint outcome before any graph node executes, and it is not
  auto-migrated, reset, or truncated

#### Scenario: A legal sub-block cannot bypass the whole-state bound
- **WHEN** a state update keeps every individually bounded sub-block within its own
  limit but its aggregate serialized form exceeds the whole-state bound
- **THEN** the whole-state bound rejects the update, so an individual sub-block limit
  never creates a legal path past the whole-state bound
