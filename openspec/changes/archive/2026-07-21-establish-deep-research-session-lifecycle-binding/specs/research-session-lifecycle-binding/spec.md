> req: RES-001, RES-002, RES-003, RES-004

## ADDED Requirements

### Requirement: A private binding ties one session to its authoritative checkpoint scope

The runtime SHALL create an owner-only, versioned session-lifecycle binding only after
a record-bearing validated lifecycle result and authoritative checkpoint identity agree.
It SHALL bind one opaque research id to the injected effective user, injected outer
thread identity, derived checkpoint namespace version, and current provider durability
classification.  Raw user/thread values, provider DSN, host path, checkpoint payload,
credential, pending answer, and arbitrary context SHALL NOT appear in public manifest,
trace, CLI/TUI projection, model input, or diagnostic output.  The initial local-demo
binding store SHALL use a non-enumerated contained subtree that inspection never reads
or renders. (`RES-001`)

#### Scenario: Binding rejects a caller-supplied scope
- **WHEN** a caller provides a research id with a user, thread, namespace, or provider
  value that differs from trusted runtime context
- **THEN** the runtime ignores caller authority, fails closed, and creates no binding

### Requirement: Read-only reopen revalidates the current official provider and checkpoint

The runtime SHALL provide an internal read-only checkpoint reopen verifier only through
the official current checkpointer provider and a validated private binding. It SHALL
verify provider fingerprint and durability, research id, supported checkpoint schema,
and terminal/pending facts from the reopened checkpoint. A missing, stale,
scope-mismatched, provider-mismatched, malformed, or same-process-only-after-restart
binding SHALL yield a bounded unavailable or denied verification result without trying
another namespace or reconstructing state from manifest/trace. (`RES-002`)

#### Scenario: File SQLite reopens a suspended session
- **WHEN** a file-backed SQLite provider is reopened in a fresh process for a bound
  suspended session
- **THEN** the verifier returns bounded checkpoint facts for a later operation surface
  truth without reinvoking a graph node or reading control state from bundle files

### Requirement: Binding metadata cannot execute lifecycle operations

This change SHALL not add or enable user-facing `open`, `status`, `resume`, `cancel`,
or `answer` operations through a binding.  The latest checkpointed pending interrupt
remains the sole authority for any future answer correlation, terminality, and legal
transition; a binding, manifest, trace, or retained artifact SHALL not supply a phase,
cursor, response, route, or evidence decision. (`RES-003`)

#### Scenario: Reopen verification cannot consume a pending request
- **WHEN** the verifier observes a bound checkpoint with a pending interrupt
- **THEN** it returns no response capability, does not invoke a graph node, and leaves
  the pending interrupt and checkpoint unchanged

### Requirement: Binding records are atomic, contained, and safely recoverable

Binding creation, refresh, invalidation, and open SHALL use contained no-follow,
owner-only primitives and atomic replacement.  Per-binding coordination may serialize
binding metadata but SHALL not replace graph/checkpoint mutation serialization, and a
binding lock SHALL NOT be held while entering a provider context, reading a checkpoint,
invoking a graph, or awaiting sandbox work.  A crash, corrupt record, or lock
contention SHALL yield bounded safe availability facts; the runtime SHALL never
silently rebind a research id to a different user/thread or enumerate bindings across
user scopes. (`RES-004`)

#### Scenario: Corrupt binding does not become a recovery hint
- **WHEN** a binding record is malformed, linked, broader-mode, or disagrees with the
  reopened checkpoint identity
- **THEN** the runtime reports it unavailable, performs no repair from public metadata,
  and exposes no path or provider detail

#### Scenario: Binding coordination cannot block checkpoint progress
- **WHEN** binding creation or invalidation contends with another local metadata update
- **THEN** it either commits/returns a bounded unavailable result without holding its
  lock across provider or graph work, and it cannot deadlock checkpoint mutation
