## Context

The existing HITL2 real node builds a small deterministic brief but always interrupts
with five internal graph routes. The fake node does the same despite producing no
research findings. This makes a lifecycle implementation detail an unavoidable user
task. The graph already owns the legal routes and the upstream quality gates already
hold the validated state that can justify normal continuation or repair.

## Goals / Non-Goals

Goals:

- Make normal HITL2 continuation an autonomous graph transition that is truthful,
  bounded, deterministic, and validated against its legal upstream boundary.
- Remove the obsolete readiness requirement for a consumed HITL2 confirmation.
- Remove the fake-demo's second interactive prompt while preserving fixture route
  coverage for tests.
- Make first-run commands directly pasteable in zsh.

Non-goals:

- Add an LLM call, provider dependency, free-form route parser, or agent-owned graph
  authority.
- Claim fake lifecycle progress is research output or modify `backend/` or
  `frontend/`.
- Change checkpoint schema, route names, graph topology, or the HITL1 scope and
  preference contract.
- Define a future HITL2 preference/authorization marker or a new human-decision
  prompt contract.

## Decisions

### Put the recommendation in the HITL2 node, not in adapters

Add a pure, bounded continuation-policy helper beside the HITL2 brief builder. Wave2
and readiness already own the quality judgements and repair routes: a HITL2 invocation
is therefore permitted only at the validated Wave2-pass boundary. The helper validates
that bounded predecessor state and
returns the sole ordinary existing route, `proceed`. The node applies that route through
its current `node_update` path. CLI and TUI only render returned progress; neither
reads state nor selects a route.

Putting the logic in `demo.py` or `ResearchRunExperience` was rejected because those
surfaces lack graph authority and would yield divergent behavior between entry points.

### Do not fake a future human-decision capability

This change defines no typed non-inferable preference or irreversible-authorization
marker, so current real and fake HITL2 nodes never interrupt. The existing generic
choice contract remains available for HITL1 and must not be reused simply because a
topology route exists. A future change that introduces a genuine HITL2 decision must
define its own marker, trusted producer, bounded question, recommendation/default,
option effects, response binding, and tests before it can call `interrupt()`.

An unconditional "always ask for confirmation" was rejected because confirmation
without a real decision is friction, not user control. An LLM deciding routes was
rejected because route authority must remain deterministic and provider output is not
an authority source.

### Preserve fixture control coverage without exposing it to a user

Fake HITL2 consumes the fixture plan's next existing route exactly as deterministic
test control. It records that the fixture selected the route in its internal trace but
does not construct a `PendingResearchInterrupt`. The public fake demo therefore
requires the initial scope response only, then reaches its labelled terminal fixture.

Fixture `stop` is a test-control terminal, not a user action. Its terminal projection
must not claim that a user stopped research; fixture coverage either uses a truthful
fixture-specific terminal reason or tests the topology route without publishing a
misleading user-attribution.

### Readiness measures research quality, not confirmation ceremony

`accepted_submission_refs` and provenance remain readiness hard checks. A consumed
HITL2 request is neither evidence nor authorization in the autonomous flow, so
`check_hitl2_consumption` and the corresponding structural failure are removed. This
keeps readiness from blocking a valid real run after the direct HITL2 continuation.

### Make the documentation executable in the documented shell

Replace inline `#` comments in user-copyable command blocks with explanatory prose
outside those blocks. The primary quick-start block is rooted at the repository root;
commands documented for users already inside `agent/` are explicitly labelled as such.

## Risks / Trade-offs

- [A policy could hide a quality problem] -> It can use only the existing validated
  Wave2-pass boundary and existing route; unresolved conditions remain under the
  authoritative quality gates.
- [A future preference is silently defaulted] -> This change has no HITL2 preference
  marker and no HITL2 interrupt path. A future feature must add the marker and its
  authority boundary in a separately reviewed change, rather than treating absence as
  consent.
- [Removing fake HITL2 input weakens topology coverage] -> Test fixture plans still
  exercise every route directly; public demo tests assert that no second prompt occurs.
- [Autonomous wording overstates research progress] -> Fake rendering remains clearly
  labelled as fixture behavior and real rendering uses only returned/validated state.

## Migration Plan

1. Add red lifecycle, policy, readiness, and public-demo tests.
2. Implement the boundary validator, fake auto-route, and removal of the obsolete
   readiness confirmation check.
3. Adapt presentation, documentation, and evidence metadata; run deterministic gates.

No migration or restart is required. Reverting restores the prior prompt behavior;
checkpoint data and retained bundles remain compatible because no schema changes.

## Open Questions

None for the P0 fix. A future product requirement can introduce a typed preference or
authorization marker with its own explicit human-decision schema and policy review.
