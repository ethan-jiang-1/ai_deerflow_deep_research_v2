## Context

The user approved the no-change disposition on 2026-07-30. The real HITL2 handler
accepts only a validated Wave2-pass predecessor and writes the deterministic
`proceed` route; the fake handler consumes its configured fixture route for graph
test control. The retained brief helper reports internal diagnostics but has no
user-decision authority.

The 2026-07-24 archived and synchronized `make-hitl2-decisions-agent-led` change,
the current `hitl2-node` and `agent-led-research-decisions` specs, source, and the
focused tests establish that behavior. In contrast, a shared lifecycle requirement,
the HITL2 spec purpose/full-fake scenario, and the `HIT-002` registry summary still
describe the removed raw-route interrupt. This is specification synchronization debt,
not an alternative runtime contract.

## Goals / Non-Goals

**Goals:**

- Make the accepted specifications and requirement registry describe the approved
  autonomous HITL2 behavior consistently.
- Preserve deterministic fake fixture routes as graph-test control without presenting
  them as human actions.
- Retain focused evidence that both real and fake HITL2 complete without a pending
  human request.

**Non-Goals:**

- No runtime feature or test change; no prompt, interrupt, visible control, model
  integration, typed contract, route, graph, checkpoint, retry, or recovery change.
- No modification to `backend/` or `frontend/`.

## Design

### 1. One accepted no-interaction boundary

`hitl2-node` shall name HITL2 as an autonomous continuation node, not a human decision
node. Its formerly interrupt-oriented requirement will be renamed and restated so the
real path selects validated `proceed` and the fake path consumes its fixture route
without a `PendingResearchInterrupt`. The accepted spec's `Purpose` is updated
directly at apply time because an OpenSpec delta cannot modify capability purpose.

`research-graph-lifecycle` shall state that HITL1 is the graph's current interrupt and
resume surface. It retains the existing HITL1 correlation/replay guarantees, while
stating that HITL2 emits no pending request, raw-route choice, or response requirement.
The generic closed-action requirement remains applicable to its owning nodes; it does
not imply that HITL2 advertises an action.

### 2. Registry is a projection of the accepted requirement

The `HIT-002` registry entry shall summarize the same autonomous no-interrupt
requirement as `hitl2-node`. It is an index, not a source of behavior. Applying this
change updates that projection only after the requirement wording is synchronized.

### 3. Future interaction remains separately admitted

No runtime authority is created by this documentation change. Any future HITL2
interaction needs a separate behavior change that defines the genuine non-inferable
preference or irreversible authorization, trusted producer, visible actions and
material facts, request/response binding, candidate mapping, deterministic graph
owner, recovery boundary, and test seam. Existing route values cannot supply those
facts by themselves.

## Execution And Evidence

The implementation changes only accepted specification text and the requirement
registry. There is no new state, checkpoint, artifact, transition, recovery, or
compatibility path to implement. Source is inspected solely to protect the existing
contract:

- `test_validated_state_routes_proceed_without_a_human_response` proves the real
  autonomous route.
- `test_fake_hitl2_consumes_its_fixture_route_without_an_interrupt` proves fixture
  control is not a pending request.
- `test_happy_path_completes_after_scope_with_autonomous_hitl2` proves full-fake
  graph completion has no HITL2 suspension.
- `test_deferred_activation_dossiers.py` proves the approved no-change precondition
  and successor boundary.

## Risks And Boundaries

- A stale prose claim could be read as permission to restore the raw-route menu.
  Synchronizing node, lifecycle, and registry wording eliminates the conflicting
  claim while retaining the source-audited behavior.
- A fake route can be mistaken for a user option. The specs distinguish deterministic
  fixture selection from a human-input action and require no pending request.
- A later interaction could reuse this change as authority. The proposal and delta
  explicitly require a separate reviewed behavior change before that can happen.
