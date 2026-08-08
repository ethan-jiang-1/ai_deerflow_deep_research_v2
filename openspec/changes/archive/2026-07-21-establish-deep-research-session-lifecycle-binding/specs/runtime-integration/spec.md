> req: RUI-006

## MODIFIED Requirements

### Requirement: Research lifecycle dispatch preserves runtime and resource boundaries

The reflected Deep Research lifecycle SHALL preserve injected authenticated identity,
runtime-derived scope, and resource ownership when creating a binding and checking a
supplied research id.  It SHALL not add a new public command, expose binding internals
to a tool caller, or initialize a sandbox solely for read-only checkpoint verification.
(`RUI-006`)

#### Scenario: Unauthenticated fallback identity cannot open a bound session
- **WHEN** lifecycle binding resolution lacks an injected authenticated runtime user
- **THEN** it rejects the request without falling back to `default`, opening a provider,
  or revealing whether a research id exists
