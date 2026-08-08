## Why

HITL2 currently validates a completed Wave2 path and continues autonomously with
`proceed`. The user approved the no-change disposition on 2026-07-30: no genuine
non-inferable preference or irreversible authorization is currently admitted at that
boundary, so introducing an interaction would turn internal graph control into a false
product decision.

The 2026-07-24 archived and synchronized `make-hitl2-decisions-agent-led` change,
the current `hitl2-node` and `agent-led-research-decisions` specs, and the current
source/test seams all establish autonomous continuation as the current HITL2 contract.
The contradictory HITL2 clause retained in the shared `research-graph-lifecycle`
spec, the stale `hitl2-node` interrupt metadata and fake-path scenario, and the stale
`HIT-002` requirement-registry summary are synchronization debt: they predate that
node-owned change and still describe the rejected raw-route menu. This no-change
change owns their scoped reconciliation; they do not restore a current interaction.

## What Changes

- Record the approved no-change disposition and retain autonomous continuation.
- Reconcile `hitl2-node` and `research-graph-lifecycle` requirements so they no
  longer describe a current HITL2 interrupt, raw-route choice, or fake interrupt path.
- Synchronize the `HIT-002` requirement-registry summary with the accepted
  autonomous HITL2 contract.
- Preserve the existing runtime code, prompts, typed contracts, checkpoint behavior,
  routes, lifecycle, and public APIs. A future interaction remains a separately
  reviewed behavior change with its own typed product-decision contract.

## Product Disposition

- **Status:** Approved no-change on 2026-07-30; no runtime behavior is admitted.
- **Current evidence:** the HITL2 activation dossier requires user approval of a
  genuine non-inferable preference or irreversible authorization and its visible
  outcome; the real node currently follows the autonomous `proceed` path;
  `hitl2-node` and `agent-led-research-decisions` specify that same path; the legacy
  shared lifecycle clause is not current node behavior.
- **Approved outcome:** retain autonomous `proceed`; do not create an interrupt,
  prompt, model call, human-input contract, or raw-route UX.
- **Synchronization consequence:** this change reconciles
  `research-graph-lifecycle`, the stale `hitl2-node` interrupt metadata/scenario,
  and the `HIT-002` requirement-registry summary with that approved contract.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `hitl2-node`: Align its purpose, legacy interrupt wording, and full-fake scenario
  with the accepted autonomous continuation requirement.
- `research-graph-lifecycle`: Restrict the graph-owned interrupt/resume contract to
  the current HITL1 surface and remove stale HITL2 raw-route interaction claims.

## Impact

- The approved disposition remains in this change's `proposal.md`. It is not runtime
  state, a typed contract, or an authority over graph routing.
- Affected planning surfaces are the two modified capability specs and
  `openspec/governance/req-registry.yaml`; source-audited evidence remains limited to
  HITL2's real/fake nodes and focused graph/contract tests.
- No modification is proposed under `backend/` or `frontend/`, and this change does
  not modify `agent/` runtime code, prompts, capabilities, tools, state, routes,
  checkpoints, lifecycle behavior, or public APIs.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/graph/nodes/hitl2/`
  owns the current autonomous continuation and is the only runtime surface reviewed
  to decide whether a human decision belongs there.
- **Question:** How do the accepted HITL2 and lifecycle requirements, registry
  summary, and evidence references state the approved autonomous no-change outcome
  without treating the legacy raw-route menu as a product interface?
- **Necessary adjacent/external contracts:** `openspec/specs/hitl2-node/spec.md` and
  `openspec/specs/agent-led-research-decisions/spec.md` establish the current
  autonomous contract; `openspec/specs/research-graph-lifecycle/spec.md` and
  `openspec/governance/req-registry.yaml` identify the stale raw-route requirement
  and `HIT-002` summary to reconcile. No runtime contract is modified by this change.
- **Evidence seam:** `agent/tests/unit/test_hitl2_real.py::TestRealHitl2Factory::test_validated_state_routes_proceed_without_a_human_response`
  and `agent/tests/graph/test_hitl_nodes.py::test_fake_hitl2_consumes_its_fixture_route_without_an_interrupt`
  prove the real and fake autonomous paths; `agent/tests/graph/test_research_graph.py::test_happy_path_completes_after_scope_with_autonomous_hitl2`
  proves the full-fake graph reaches completion without a HITL2 suspension; and
  `agent/tests/contract/test_deferred_activation_dossiers.py` proves the precondition
  and exact successor relationship.
- **Not in scope:** any trigger or interaction implementation; a visible decision
  brief or control; raw-route UX; model assistance; prompt or capability resources; a
  `PendingResearchInterrupt`; human-response parsing; typed request/result changes;
  route, graph, checkpoint, lifecycle, runtime, backend, frontend, API, or live-model
  changes. A future behavior change must own those choices.
- **Triggered charter policies:** change-admission, human-interaction-integrity
