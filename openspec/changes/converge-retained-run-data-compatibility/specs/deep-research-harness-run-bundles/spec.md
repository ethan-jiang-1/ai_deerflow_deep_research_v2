> req: DRH-002

## MODIFIED Requirements

### Requirement: Bundle-local Research State is the sole durable lifecycle authority

Each Run Bundle SHALL contain the authoritative Research State for its own lifecycle,
current refinement round, pending interaction, admitted refinement, terminal facts,
evidence references, and legal control outcomes. A non-terminal available State,
including a State awaiting user input, SHALL mean active; a terminal current refinement
round SHALL mean ended. External checkpoints, session records, bindings, indices,
logs, diagnostics, and caches MAY retain observations but SHALL not establish Run
existence, status, authorization, or recovery.

The current Bundle State terminal-reason contract SHALL exclude
`REPAIR_EXHAUSTED`. A current Bundle reader SHALL reject an old Bundle containing that
reason before lifecycle control or terminal projection. It SHALL not map the old reason
to completed, a generic failure, another current terminal reason, a resume, a retry, or
an inferred diagnostic. An explicitly registered old Bundle may use the separate offline
migration route only when its complete terminal State validates and the route can remove
the retired reason without changing its already-authoritative terminal status, Bundle
identity, revision semantics, or typed incident truth. The migration SHALL write one
atomic current Bundle State and leave its source unchanged on failure. The migration
inventory does not grant the runtime reader an old-state compatibility branch; an
unregistered, malformed, stale, partially migrated, or replayed old Bundle is a bounded
unavailable/unsupported outcome with no lifecycle recovery. (`DRH-002`)

#### Scenario: Suspended Bundle remains active
- **WHEN** an available Bundle-local State awaits a user interaction
- **THEN** the Harness reports the Run active and does not start a second active Bundle in that trusted conversation scope

#### Scenario: External observation conflicts with Bundle State
- **WHEN** an external session/checkpoint observation disagrees with an available Bundle-local State
- **THEN** lifecycle control follows the Bundle-local State and the observation cannot change it

#### Scenario: Unregistered retired terminal is denied without a substitute result
- **WHEN** lifecycle control loads a Bundle State containing `REPAIR_EXHAUSTED` that was not migrated through the approved route
- **THEN** it returns a bounded unavailable or unsupported outcome and does not emit a completed, retriable, resumable, or replacement terminal result

#### Scenario: Registered terminal migration preserves terminal identity
- **WHEN** the offline migration route processes a registered valid old blocked Bundle whose retired reason can be removed without changing its terminal facts
- **THEN** the reloaded current Bundle retains its original opaque identity and blocked terminal status without a synthetic current reason

#### Scenario: Failed old-state migration is not a control retry
- **WHEN** a registered Bundle fails terminal validation or atomic migration
- **THEN** its source State remains unchanged and no status, refinement, resume, retry, or control action is admitted from that Bundle
