# research-session-lifecycle-binding Specification

> req: RES-001, RES-002, RES-003, RES-004, RES-005, RES-006

## Purpose

Bind a retained research session to its checkpoint scope for private, read-only restart
verification without creating a public lifecycle operation surface.
## Requirements

### Requirement: Retained binding metadata is observation-only

Any retained lifecycle-binding or owner-index metadata SHALL be an optional,
observation-only compatibility record. It SHALL not select a Run, publish a Bundle,
authorize status/control/resume/cancel/refine, supply a trusted scope, choose a recipe or
provider, or survive as a recovery authority after Bundle loss. Raw user/thread values,
provider DSN, host path, checkpoint payload, credential, pending answer, arbitrary
context, or recipe implementation details SHALL not appear in public projection, model
input, or diagnostic output. (`RES-001`)

#### Scenario: Binding rejects a caller-supplied scope
- **WHEN** a caller provides a Bundle id with a user, thread, namespace, or provider value that differs from trusted runtime context
- **THEN** the runtime ignores caller authority, fails closed, and creates or activates no binding

### Requirement: Read-only inspection revalidates an available Run Bundle

The runtime SHALL provide read-only inspection of a Deep Research Run only through the
available selected Bundle and its validated Bundle-local State. A retained binding or
external provider/checkpoint may supply a bounded historical observation, but SHALL not
be opened to validate, select, recover, or reconstruct a Run. A missing, stale,
scope-mismatched, malformed, unreadable, or deleted Bundle SHALL yield a bounded
unavailable/denied result without trying another namespace or reconstructing State from
manifest/trace. (`RES-002`)

#### Scenario: External provider cannot reopen a deleted Bundle
- **WHEN** a generic provider still contains a snapshot for a binding whose Bundle has been deleted
- **THEN** inspection returns unavailable without reading that snapshot as lifecycle State

### Requirement: Binding metadata cannot execute lifecycle operations

This capability SHALL not add or enable user-facing `open`, `status`, `resume`,
`cancel`, `refine`, or answer operations through a binding. Bundle-local State and its
current pending interaction remain the sole authority for response correlation,
terminality, and legal transition; a binding, manifest, trace, or retained artifact
SHALL not supply a phase, cursor, response, route, or evidence decision. (`RES-003`)

#### Scenario: Retained observation cannot consume a pending request
- **WHEN** a diagnostic record refers to a Bundle with a pending interaction
- **THEN** it returns no response capability, does not invoke a graph node, and cannot change Bundle-local State

### Requirement: Binding observations are atomic, contained, and failure-bounded

If compatibility observation records remain, their creation, refresh, revocation, and
read SHALL use contained no-follow owner-only primitives and atomic replacement.
Metadata coordination may serialize that observation work but SHALL not replace Bundle
State mutation serialization or be held while entering a provider context, reading
Bundle State, invoking a graph, or awaiting sandbox work. A crash, corrupt record, lock
contention, or failed cleanup SHALL yield bounded observation availability facts; the
runtime SHALL never silently rebind a Bundle id, enumerate records across scopes, or
make an observation record a lifecycle recovery hint. (`RES-004`)

#### Scenario: Corrupt binding does not become a recovery hint
- **WHEN** a retained binding record is malformed, linked, broader-mode, or disagrees with the available Bundle identity
- **THEN** the runtime reports it as an unavailable observation, performs no repair from public metadata, and exposes no path or provider detail

### Requirement: Retired fixture sessions remain non-operable compatibility records

A binding or retained record associated with the retired full-fixture public recipe SHALL
remain validation and inspection data only. It SHALL not select a fixture adapter, cause a
fixture package import, or authorize a real recipe to resume, cancel, or reinterpret that
checkpoint. A current public real operation access SHALL reject a retired fixture binding
before provider, sandbox, or graph access; retained inspection MAY expose only existing
bounded legacy facts and the documented next action.

#### Scenario: Recipe mismatch cannot revive a fixture adapter
- **WHEN** a current real operation access encounters a binding for the retired fixture
  recipe revision
- **THEN** it returns bounded non-operability before provider or graph access and does not
  use the stored fingerprint to choose a recipe

#### Scenario: Legacy inspection remains read-only
- **WHEN** an owner inspects a retained fixture session through an existing inspection path
- **THEN** the path returns only validated bounded retained facts and cannot resume, cancel,
  migrate, or create a new public lifecycle

### Requirement: Legacy lifecycle bindings cannot resolve or recover a Run Bundle

Lifecycle-binding records, owner indexes, and checkpoint compatibility metadata SHALL
not select, authorize, reopen, resume, cancel, or recover a Deep Research Run. If
retained for diagnostic compatibility, they SHALL be read-only observations and SHALL
not disclose raw scope/provider/path details. A missing or unavailable Bundle SHALL
remain unavailable regardless of a valid-looking binding. (`RES-006`)

#### Scenario: Valid binding has no control effect after Bundle loss
- **WHEN** a legacy binding validates syntactically but its referenced Bundle is unavailable
- **THEN** a lifecycle request returns unavailable without opening a provider, rebuilding context, or mutating a binding
