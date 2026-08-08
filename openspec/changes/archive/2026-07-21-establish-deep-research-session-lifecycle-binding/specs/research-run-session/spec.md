> req: RUS-001

## MODIFIED Requirements

### Requirement: A canonical local run bundle is a discoverable derived session

The runtime-owned run-session store SHALL retain its existing bounded manifest, trace,
and inspection behavior.  After a validated record-bearing lifecycle result has also
created a private session-lifecycle binding, the manifest MAY expose only an opaque,
versioned binding reference and availability/durability classification.  It SHALL NOT
expose raw user/thread identity, checkpoint namespace, provider DSN, host path,
credential, checkpoint payload, phase cursor, pending input/answer, or control route.

The manifest, trace, binding reference, and locks remain observations: graph nodes,
reducers, lifecycle transition validation, pending-answer correlation, and evidence
acceptance SHALL NOT read them as control authority.  Missing bindings leave existing
retained bundles inspection-only; no binding may be inferred or backfilled from bundle
content. (`RUS-001`)

#### Scenario: Public inspection cannot reveal a private binding target
- **WHEN** a developer inspects a retained session with an available lifecycle binding
- **THEN** output may state bounded binding availability and durability but never emits
  a user id, outer thread id, namespace, provider connection, or host path
