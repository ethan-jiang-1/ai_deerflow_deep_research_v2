> req: DPL-007

## ADDED Requirements

### Requirement: Local demos retain inspectable run bundles under bounded policy

The demo adapter SHALL use the project-local `agent/.deep-research-demo-runs/` root,
ignored by downstream-owned `agent/.gitignore`, rather than deleting all workspace
content through `TemporaryDirectory` cleanup. Before every lifecycle dispatch it SHALL
hold the retained root's shared cleanup lock; cleanup SHALL take that lock exclusively
and non-blocking, skipping safely when unavailable. Fake and real modes SHALL bind a
run-session store only after a record-bearing validated lifecycle result supplies
non-null research id, status, phase, and generation, retain their bounded demo
artifacts, manifest, redacted lifecycle trace, and post-bind diagnostic records under
the same explicit policy, and then hold a per-bundle advisory live lock until adapter
close. Preflight, denial/no-record, malformed, and status-less results SHALL create no
bundle. Where no valid regular no-follow real bootstrap marker exists, including
full-fake and failed-before-bootstrap real routes, the adapter SHALL retain an
explicitly session-metadata-only root and SHALL NOT fabricate bootstrap artifacts.
Test fixtures MAY use isolated temporary retained roots but shall exercise the same
root-lock, bundle-lock, and cleanup contract. Required final publication completes
before `ResearchRunExperience.handle()` returns; CLI may await close while Textual
unmount only releases locks already finalized and shall not mask a primary lifecycle
exception with observability cleanup failure.

The adapter SHALL not derive a second research id, bypass trusted workspace
containment, or make retention imply cross-process graph resume. No `backend/` or
`frontend/` file changes. (`DPL-007`)

#### Scenario: Closing a demo does not erase its inspectable bundle
- **WHEN** a local demo receives a record-bearing validated lifecycle result and
  closes its adapter
- **THEN** its retained bundle remains available through the session reference, while
  a later cleanup operation follows bounded retention rules

#### Scenario: First dispatch is protected before session bind
- **WHEN** one adapter is dispatching the first real lifecycle action and another
  process attempts automatic or explicit cleanup
- **THEN** cleanup safely skips because it cannot acquire the root cleanup lock, and
  it cannot delete graph materialized content before the returned result binds a bundle
