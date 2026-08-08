## Why

Deep Research has a deterministic LangGraph lifecycle and multiple bounded model
invocations, but contributors currently have no shared admission record for the
semantic role of a node agent, its tool posture, or the deterministic owner that
may accept its result. The generic prompt catalog made this gap visible: it can
show what a branch receives without requiring a proposal to explain what the
branch is allowed to decide.

Before changing the sixteen current model-invocation branches, the project needs a
small, non-runtime governance mechanism that makes this split reviewable and keeps
future prompt work from reintroducing generic agent behavior or model-owned routes.

## Change Focus

- **Primary module / causal owner:** `openspec/governance/agent-charter/` admission policy and its checker.
- **Question:** How can every future node-agent change record the bounded cognitive job, deterministic handoff, tool posture, and evidence seam without letting governance prose create runtime authority?
- **Necessary adjacent/external contracts:** `deep-research-agent-charter` defines the permanent guidance and mechanically checked proposal shape; `openspec/config.yaml` supplies the concise authoring route; `openspec/governance/check_agent_charter.py` answers whether an active proposal that selects the policy contains the required review record. No DeerFlow public interface is needed.
- **Evidence seam:** isolated charter-checker fixture tests and the repository charter governance command validate policy routing, proposal-table shape, and fail-closed missing/invalid records.
- **Not in scope:** `NodeExecutionRequest`, prompt rendering, local capability resources, runtime bridge behavior, tool resolution, graph routes, retries, user-facing lifecycle behavior, `backend/`, and `frontend/`.
- **Triggered charter policies:** local-context, change-admission

## What Changes

- Add a routed `node-agent-workflow-integrity` Agent Charter policy for changes
  that add, remove, or materially revise a node-agent invocation, capability
  policy, output parser, tool posture, or model/non-model classification.
- Define a compact `## Node Agent Review` proposal record required only when that
  policy is selected. The record distinguishes `node-agent` from `no-agent`,
  names the bounded cognitive question and candidate-result handoff, and records
  the runtime tool enforcer, deterministic admission owner, failure owner, and
  evidence seam.
- Extend the charter checker and its focused tests to recognize the policy and
  fail closed when a selected policy lacks a complete, well-formed review record.
- Update the charter index, authoring context, requirement registry, and owning
  charter specification so the new rule is discoverable and remains guidance
  rather than a second controller.
- Record the approved OpenSpec change train in the architecture plan: this change
  governs admission; a subsequent `establish-node-agent-capabilities` change will
  make the node-local capability contract executable across the existing model
  branches.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deep-research-agent-charter`: route and mechanically validate the focused
  node-agent workflow integrity review without granting runtime authority.

## Impact

- Affects `openspec/governance/agent-charter/`, `openspec/config.yaml`,
  `openspec/governance/check_agent_charter.py`, its focused contract tests,
  requirement/evidence registration, and the architecture plan.
- Adds no provider, model, tool, graph, sandbox, state, API, or dependency change.
- Leaves the existing `make-node-prompts-auditable` and
  `establish-human-interaction-contract` changes' runtime scope intact; their
  future revisions can select the new policy when they alter a node-agent surface.
