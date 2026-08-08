## Why

Recent repair work exposed recurring design-time placement failures: a provider fact
was admitted through a node-name special case instead of its shared execution policy,
and comparison scope, language, and confirmation could be inferred by a model instead
of accepted as typed facts. Existing charter reviews cover node-agent handoff and
workflow outcomes, but no focused record asks a change author to relate a changed
control fact to its deterministic owner, legal recovery, avoided duplicate control,
and proof seam.

V1 adds that review mechanism without claiming it can eliminate regressions or create
runtime behavior. It is deliberately separate from the later cross-session guardrail
work, which needs its own evidence and orchestration contract.

## What Changes

- Add an external `control-placement` OpenSpec policy under `openspec/policies/` and
  a concise index that distinguish policy guidance from charter routing, governance
  checks, and the deferred guardrail layer.
- Replace the proposal Focus Card field `Triggered charter policies` with `Triggered
  review policies`, allowing canonical charter and external policy names in one list.
- Require a single, exact seven-column `## Control Placement Review` only when an
  active proposal selects `control-placement`. Its closed design postures are
  `advisory`, `bounded-repair`, `human-decision`, and `non-bypassable`.
- Extend the deterministic charter checker and its isolated contract tests to validate
  canonical policy lookup, field migration, selected-record shape, closed postures,
  complete rows, and the required `human-interaction-integrity` combination for a
  `human-decision` row. The checker will not infer applicability, evaluate prose, or
  grant runtime authority.
- Update the authoring route, requirement registry, structure inventory, and evidence
  registration for `DRC-009`; record the two 2026-08-02 archived repairs as replay
  evidence and keep V2 explicitly deferred in the long-term backlog plan.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deep-research-agent-charter`: route and mechanically validate the external
  control-placement review while preserving existing charter policy records and their
  non-runtime authority boundary.

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_agent_charter.py` and
  its OpenSpec review-admission route own canonical policy lookup and mechanical
  active-proposal conformance.
- **Question:** How can a change that moves or adds a control fact, admission,
  recovery, or human/model boundary record the direct deterministic owner and smallest
  proof seam without creating a second governance or runtime controller?
- **Necessary adjacent/external contracts:** `deep-research-agent-charter` owns the
  stable proposal-admission requirements; `openspec/governance/agent-charter/` remains
  the route for focused local policies; `openspec/config.yaml` provides concise
  authoring guidance; `openspec/governance/project-structure.toml` owns the exact
  structural inventory; `deerflow_research/tests/contract/test_agent_charter_governance.py`
  is the isolated checker evidence seam. The two archived 2026-08-02 repairs are
  historical replay inputs only and are not rewritten.
- **Evidence seam:** isolated charter-checker fixtures and the repository governance
  command prove registry resolution, Focus Card migration, conditional review shape,
  policy-combination checks, and preserved independent Node Agent/Workflow Outcome
  Review enforcement.
- **Not in scope:** DeerFlow runtime behavior, graph routes, state/checkpoint schema,
  provider/model/tool policy, prompt text, external-session orchestration, automatic
  semantic review, source scanning for policy applicability, `openspec/guardrails/`,
  `backend/`, and `frontend/`.
- **Triggered review policies:** change-admission, authority-and-projections, agent-information-map, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Active proposal admission and selected-review lookup | Change author records a proposed policy selection | Charter checker registry and structural validator | advisory | Only canonical declared policies and complete selected records pass admission | Reuse one registry and existing selected-review validators instead of adding a governance controller | Isolated charter-governance contract test |

## Impact

- Affects OpenSpec governance and authoring documents, the Agent Charter route,
  `openspec/config.yaml`, the standard-library charter checker, its focused contract
  tests, requirements/evidence registration, and the long-term policy plan.
- Adds no runtime dependency, API, provider, model, tool, sandbox, graph, persistence,
  or user-facing lifecycle behavior.
