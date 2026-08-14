## REMOVED Requirements

### Requirement: Retained binding metadata is observation-only
**Reason**: No binding metadata, writer, reader, owner index, or recovery path exists in
the current product; leaving this requirement active falsely names a deleted mechanism
as an owner.
**Migration**: `DRH-006`, `REJ-004`, and project-structure guards retain the
Bundle-loss, read-only-observation, and removed-surface invariants.

### Requirement: Read-only inspection revalidates an available Run Bundle
**Reason**: Inspection no longer uses a binding or provider reopen verifier.
**Migration**: `RDO-001` through `RDO-004`, `RSV-004`, and `REJ-004` require
available-Bundle reauthorization and deny post-loss external fallback.

### Requirement: Binding metadata cannot execute lifecycle operations
**Reason**: The product no longer has a binding operation surface.
**Migration**: `DRH-002`, `DRH-006`, and `REJ-004` retain Bundle-local State as the
only lifecycle authority and prevent observation-derived control.

### Requirement: Binding observations are atomic, contained, and failure-bounded
**Reason**: The described observation-record lifecycle is not implemented and must not
remain a positive compatibility promise.
**Migration**: `REJ-001` through `REJ-004` own the supported Bundle-local Journal
observation and its bounded unavailable outcome.

### Requirement: Retired fixture sessions remain non-operable compatibility records
**Reason**: The retired fixture binding route has no current reader or writer.
**Migration**: `PRS-006` removes the legacy broker/index structural root, and
`RUI-003` keeps trusted scope/checkpoint namespaces from becoming a Run identity,
index, or recovery source; together they reject retired fixture/binding surfaces
before provider, sandbox, or graph work.

### Requirement: Legacy lifecycle bindings cannot resolve or recover a Run Bundle
**Reason**: This negative rule belongs with the current Bundle and Journal owners, not a
deleted binding capability.
**Migration**: `DRH-006` and `REJ-004` retain the no-reopen/no-recovery behavior with
planted removed-module and Journal-control violations.
