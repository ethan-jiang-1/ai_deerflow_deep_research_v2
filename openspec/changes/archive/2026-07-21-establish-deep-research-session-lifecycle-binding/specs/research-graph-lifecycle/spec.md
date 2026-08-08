> req: REG-004, REG-014

## MODIFIED Requirements

### Requirement: Lifecycle actions enforce typed and idempotent transitions

Lifecycle actions SHALL retain their current typed, idempotent transition semantics.
Every current action SHALL first verify that a supplied research id, when present,
equals the canonical id derived from its trusted user/thread envelope.  It SHALL reject
a mismatch before checkpoint namespace derivation, graph access, or binding creation,
and SHALL not accept a caller-provided namespace, phase, pending request, or checkpoint
snapshot. (`REG-004`)

#### Scenario: A foreign opaque id cannot select a namespace
- **WHEN** a caller supplies a research id that differs from the id derived from its
  trusted user/thread envelope
- **THEN** lifecycle rejects it without opening a checkpoint, invoking a graph node,
  or revealing whether that id has a binding

### Requirement: Run-session records remain derived lifecycle projections

Run-session manifests, traces, and public binding references SHALL remain derived
lifecycle projections.  The private runtime binding is a trusted lookup input only;
it SHALL never add a `ResearchState` phase, pending request, route, checkpoint
authority, or evidence authority. Any later resumed operation SHALL revalidate the
checkpoint as the control source rather than trusting public session metadata.
(`REG-014`)

#### Scenario: Binding lookup cannot advance a graph
- **WHEN** runtime resolves a bound session for open or status
- **THEN** it may reopen and validate the checkpoint but does not consume a pending
  interrupt, invoke a graph node, mutate a route, or accept evidence
