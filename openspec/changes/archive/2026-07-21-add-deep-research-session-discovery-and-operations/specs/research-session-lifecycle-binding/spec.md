> req: RES-001, RES-004

## MODIFIED Requirements

### Requirement: A private binding ties one session to its authoritative checkpoint scope

The runtime SHALL create an owner-only, versioned session-lifecycle binding only after a
record-bearing validated lifecycle result and authoritative checkpoint identity agree. An
operation-enabled binding SHALL additionally carry a versioned recipe-compatibility
fingerprint and one opaque reference in a private owner-and-profile index derived from the
trusted principal and fixed operation access. Binding metadata SHALL be staged before a
retained bundle is published, and its index entry SHALL activate only after that
publication succeeds. Each owner/profile index SHALL be bounded by retained-session
capacity; only an undiscoverable staged record with no validated manifest reference may
be reaped under the retained-root lease. The fingerprint is a validation value for a
profile-owned fixed recipe; it SHALL NOT select a recipe, node, phase, route, or provider.

Raw user/thread values, provider DSN, host path, checkpoint payload, credential, pending
answer, arbitrary context, or recipe implementation details SHALL NOT appear in public
manifest, trace, CLI/TUI projection, model input, or diagnostic output. Phase-2 bindings
without current owner-index membership or recipe compatibility remain read-only
verification/inspection records; they SHALL NOT be auto-upgraded, backfilled, or made
broker-operable. (`RES-001`)

#### Scenario: Binding rejects a caller-supplied scope
- **WHEN** a caller provides a research id with a user, thread, namespace, or provider
  value that differs from trusted runtime context
- **THEN** the runtime ignores caller authority, fails closed, and creates no binding

#### Scenario: Binding cannot select a different graph recipe
- **WHEN** an operation access has a different recipe-compatibility fingerprint from a
  selected binding
- **THEN** the runtime reports bounded unavailability before provider, path, sandbox, or
  graph access and does not use the stored value to choose a recipe

### Requirement: Binding records are atomic, contained, and safely recoverable

Binding creation, refresh, owner-index update, revocation, and open SHALL use contained
no-follow owner-only primitives and atomic replacement. Per-binding/index coordination
may serialize metadata but SHALL not replace graph/checkpoint mutation serialization, and
a binding metadata lock SHALL NOT be held while entering a provider context, reading a
checkpoint, invoking a graph, or awaiting sandbox work. A crash, corrupt record, lock
contention, or failed retention revocation SHALL yield bounded safe availability facts;
the runtime SHALL never silently rebind a research id to a different user/thread,
enumerate bindings across user scopes, or leave an owner-index entry after confirmed
binding revocation. (`RES-004`)

#### Scenario: Corrupt binding does not become a recovery hint
- **WHEN** a binding record is malformed, linked, broader-mode, or disagrees with the
  reopened checkpoint identity
- **THEN** the runtime reports it unavailable, performs no repair from public metadata,
  and exposes no path or provider detail

#### Scenario: Binding coordination cannot block checkpoint progress
- **WHEN** binding creation or invalidation contends with another local metadata update
- **THEN** it either commits/returns a bounded unavailable result without holding its
  lock across provider or graph work, and it cannot deadlock checkpoint mutation

#### Scenario: Retention revocation is fail closed
- **WHEN** retained-bundle cleanup cannot revoke the validated matching binding/index
  entry
- **THEN** it retains the bundle, reports a bounded cleanup skip, and does not expose an
  operation entry for a partially revoked record
