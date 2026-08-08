## Why

HITL2, readiness, and final delivery have materially different deferred or conditional
responsibilities, but current reader cards can only direct a maintainer to a later
change. Without a reviewable dossier, a later proposal can mistake a source-audited
fallback for a product decision, or invent a model loop or interaction before its
trigger and deterministic authority are admitted.

## What Changes

- Add three non-runtime activation dossiers: one for HITL2's conditional human decision,
  one for readiness's accepted-but-deferred evidence critic, and one for final delivery's
  accepted-but-deferred report composer.
- Require each dossier to state product responsibility, commitment and current mechanism,
  trusted/untrusted boundaries, candidate or choice contract, deterministic admission owner,
  bounded failure posture, lowest proof seam, and the exact next change it informs.
- Require HITL2 to state an unresolved, user-approved non-inferable preference or irreversible
  authorization trigger before any interaction implementation; readiness and final delivery
  state accepted deferred roles without claiming an active model branch.
- Add deterministic dossier validation and test-evidence registry entries without modifying runtime
  nodes, `workflow.md` behavior claims, prompts, capabilities, tools, state, routes, or APIs.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `cognitive-node-interface`: Extend the non-runtime reader contract with three separately
  validated deferred-cognitive/human-decision activation dossiers.

## Impact

- Affected files are limited to a test-owned dossier collection, its focused contract evidence,
  and the established test-evidence registries under `agent/tests/`; the three current reader
  projections remain unchanged and do not become dossier authority.
- No modification is proposed under `backend/` or `frontend/`. No model call, capability Markdown,
  prompt builder, tool policy, interrupt, typed state, checkpoint, graph route, lifecycle outcome,
  provider policy, or public API changes.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/graph/nodes/hitl2/` owns
  the conditional human-decision boundary; readiness and final delivery enter only to record
  their separately accepted deferred activation contracts.
- **Question:** What evidence must a later HITL2 decision experience, readiness critic, or final
  report composer proposal supply before it can legitimately change runtime behavior, without
  treating present fallback code or absent `run_agent` calls as that decision?
- **Necessary adjacent/external contracts:** `graph/nodes/readiness/` establishes the current
  deterministic critic/materializer/route seam; `graph/nodes/final_delivery/` establishes the
  formatter, integrity-gate, publisher, and terminal seam; `cognitive-node-interface` establishes
  the non-runtime validation boundary and the closed three-dossier denominator.
- **Evidence seam:** focused source/contract tests for HITL2 autonomous continuation, readiness
  hard-rule/materializer outcomes, final-delivery publisher outcomes, and
  `tests/contract/test_deferred_activation_dossiers.py`, which validates the exact collection and
  confirms no production import or behavior mutation.
- **Not in scope:** behavior activation for `introduce-hitl2-human-decision-experience`,
  `activate-readiness-evidence-critic-loop`, or `activate-final-report-composition-loop`; prompts,
  capability Markdown, `run_agent`, tool posture, human interrupt/resume, typed state, checkpoint,
  route, lifecycle, graph topology, provider configuration, backend, frontend, live model execution,
  or model-quality claims.
- **Triggered charter policies:** change-admission
