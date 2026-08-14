## REMOVED Requirements

### Requirement: A canonical local Run Bundle is discovered within trusted scope
**Reason**: Run existence and trusted-scope discovery are already owned by the Bundle
lifecycle; this capability's parallel session owner is obsolete.
**Migration**: `DRH-001` through `DRH-004` and `RDO-001`/`RDO-007` retain the same
Bundle identity, scoped discovery, and no-index behavior.

### Requirement: A bounded Bundle-local Journal records verified lifecycle observations
**Reason**: The Event Journal is the accepted observation owner.
**Migration**: `REJ-001` through `REJ-004` retain bounded, redacted, Bundle-lifetime
observation without lifecycle authority.

### Requirement: Local developer inspection resolves a safe run reference
**Reason**: Inspection is now a scoped Bundle operation, not a session capability.
**Migration**: `RDO-001` through `RDO-004`, `RSV-004`, and `REJ-004` retain selected
Bundle reauthorization and read-only bounded inspection.

### Requirement: Retained session diagnosis is summarized, correlated, and redacted
**Reason**: Retained diagnosis must not remain under a mixed session authority.
**Migration**: `RER-008`, `RER-009`, `RER-013`, `REJ-002`, and `REJ-004` own safe
terminal facts, their participant projection, and contained read-only observation.

### Requirement: Retained Wave0 diagnosis preserves closed worker failure classes
**Reason**: Wave0 worker classification is already owned by its controller capability.
**Migration**: `WFC-001` owns the closed attempt and exhaustion classes; `REJ-002`
retains only their safe process-fact projection.

### Requirement: Retained session diagnostics project classified workflow outcomes
**Reason**: Classified workflow outcomes have current lifecycle and Journal owners.
**Migration**: `RER-008`/`RER-009`/`RER-013`, `WFO-001`, and `REJ-002` retain the
typed terminal fact, bounded recovery history, and redacted observation projection.

### Requirement: Supplied terminal diagnostics are published before retained projections
**Reason**: Publication proof is a current terminal/Journal concern, not a session-store
behavior.
**Migration**: `RER-013`, `REJ-002`, and `REJ-004` retain exact diagnostic-reference
publication truth and deny unavailable external fallback.

### Requirement: Read-only inspection projects only an exact verified terminal diagnostic
**Reason**: The Journal and Run Experience contracts already own verified diagnostic
projection.
**Migration**: `REJ-004` and `RER-013` retain exact-reference, bounded, read-only
inspection without a new control or recovery route.

### Requirement: Retained session material is observation-only after Bundle authority migration
**Reason**: This is a Bundle-loss invariant, not a retained-session authority.
**Migration**: `DRH-006` and `REJ-004` retain unavailable-after-loss behavior and
forbid any external historical reader from recovering a Run.

### Requirement: Retained session inspection exposes truthful event-journal observations
**Reason**: Event Journal inspection is already the current observation contract.
**Migration**: `REJ-002` through `REJ-004` retain bounded correlation, completeness,
redaction, and no-control semantics.
