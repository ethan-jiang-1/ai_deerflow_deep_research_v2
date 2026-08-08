## Why

Deep Research has six real model-invocation owners, but their non-success paths do
not share one outcome contract. `BUG-010` exposed the consequence: a classified
provider timeout was discarded by topic planning and presented as an opaque,
non-retryable `research.blocked`. The same audit found equivalent loss of failure
meaning in later workflow phases. This change turns that recurring UX symptom into
a system-level runtime, lifecycle, evidence, and governance concern before more
one-off bug fixes accumulate.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/domain/run_experience.py`, which owns the bounded typed failure and terminal-incident facts that every lifecycle projection must share.
- **Question:** How can every production `run_agent` owner preserve a known invocation failure through its phase-specific recovery and terminal behavior, so the workflow presents one actionable, truthful outcome rather than a generic blocked result?
- **Necessary adjacent/external contracts:**
  - `runtime/node_agent_bridge.py`: Which safe failure facts and phase execution budgets arrive from the raw provider binding?
  - `graph/nodes/*`: Which phase owns retry, work-attempt categorization, route, and terminal incident creation?
  - `runtime/research.py` and `runtime/session_operations.py`: How does a checkpointed incident become the single shared lifecycle/session projection?
  - `scripts/demo_real.py` and the demo TUI: How do adapters render that projection without inferring control state?
  - `openspec/governance/agent-charter`: Which recurring review trigger prevents future model/tool workflow changes from omitting the outcome contract?
- **Evidence seam:** a new deterministic workflow-outcome conformance inventory, backed by scripted real-node cases and lifecycle projection assertions; it must discover every production `run_agent` owner and reject missing declared outcome coverage.
- **Not in scope:** DeerFlow host changes, frontend application changes, new provider credentials, provider-side reliability, unbounded automatic retry, or cross-process resume beyond the existing lifecycle contract.
- **Triggered charter policies:** workflow-outcome-review, authority-and-projections, participant-outcomes, control-and-recovery, change-admission

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| provider timeout or unavailable | Runtime bridge `NodeProblem` and safe provider observation, then the owning phase or worker controller | Topic planning has one provider retry; worker phases retain their existing bounded controller attempts | Direct phase incident or controller-derived worker diagnosis; no generic replacement | The checkpointed terminal result's single recorded action, never a presentation-inferred retry | Scripted real-node outcome cases plus lifecycle or controller projection assertions |
| structured-output failure | Owning phase validator and result contract | Each phase's declared bounded repair only | Phase-specific repair exhaustion or closed worker failure | The action recorded by the owning terminal result | Deterministic phase validator and scripted repair cases |
| non-retryable provider, configuration, or local unknown failure | Runtime bridge or local phase boundary normalized through the workflow-outcome seam | No fabricated recovery | Fail closed with the preserved safe category or bounded unknown | The terminal result's one legal action | Direct phase and worker/controller failure-outcome tests |
| cancellation | Task/runtime cancellation authority | No conversion to recovery | Existing cancellation semantics | Existing lifecycle cancellation control | Cancellation contract and real-node conformance selectors |

## What Changes

- Introduce a bounded workflow-failure outcome contract for every production
  `run_agent` owner. A phase must preserve a safe classified failure, record its
  bounded recovery disposition when applicable, and produce one legal next action;
  it may not replace a known failure with an unclassified exception or generic
  blocked route.
- Repair topic planning as the first affected phase: give planning a
  phase-appropriate execution budget, preserve provider timeout/unavailable
  incidents, and distinguish provider recovery from structured-output repair.
- Audit and align Wave0, Wave1, Wave2 synthesis, and targeted evidence with the
  shared contract while preserving each phase's existing work-unit, gate, and
  evidence authorities. The change will not make all phases share one retry policy.
- Extend the canonical workflow-node inventory from “every model owner has a
  workflow test” to “every model owner has deterministic outcome coverage for its
  admissible failure classes.”
- Make the operator-facing CLI/TUI and machine-facing run result project the same
  typed terminal incident: category, phase, observed bounded recovery, safe
  diagnostic reference, durability truth, and nearest legal action.
- Add a focused Agent Charter policy and OpenSpec admission requirement for changes
  that add or modify model/tool/provider workflow calls. The policy requires a
  failure-outcome table and a named evidence seam, without turning the charter or
  diagnostics into a runtime controller.

## Capabilities

### New Capabilities

- `workflow-failure-outcomes`: Closed, phase-owned failure outcome handling from a
  real model invocation through checkpointed terminal incident, retained diagnosis,
  and human/AI projections; includes the workflow-wide deterministic coverage
  inventory.

### Modified Capabilities

- `deep-research-agent-charter`: Add a triggered workflow-outcome review policy
  and route it through OpenSpec change admission.
- `node-agent-runtime`: Expose phase-appropriate bounded execution policies and
  retain safe classified invocation failures for downstream phase handling.
- `research-graph-lifecycle`: Preserve phase-owned terminal incidents across the
  graph rather than collapsing known invocation failures into generic blocking.
- `research-run-experience`: Project terminal incidents consistently as actionable
  lifecycle outcomes for both human and machine consumers.
- `research-run-session`: Retain the same classified outcome and bounded recovery
  facts in event/session diagnostics without creating a second lifecycle authority.
- `research-demo-tui`: Render the shared typed outcome without inferring retry,
  resumability, or recovery from prose or local state.
- `research-cli-onboarding`: Render the shared typed outcome for the standalone
  real CLI demo without reducing it to generic blocked text.
- `topic-planning-node`: Treat provider failure and structured-output repair as
  distinct bounded paths and preserve a terminal incident on exhaustion.
- `wave0-node`, `wave1-node`, `wave2-synthesis-node`, `targeted-evidence-loop`:
  Align existing real invocation paths with the shared workflow-failure outcome
  contract while retaining their own domain-specific routes and work-unit behavior.
- `evaluation-hardening`: Require every syntax-discovered real `run_agent` owner
  to supply deterministic failure-outcome conformance evidence.

## Impact

- Affected source is limited to `agent/`: domain outcome contracts, runtime
  node-agent binding and run projection, run-session diagnostics, the six real
  graph-node owners, CLI/TUI adapters, and their focused tests/evidence inventory.
- `openspec/config.yaml` and the Agent Charter governance may gain admission rules;
  no governance document becomes a runtime authority.
- No `backend/` or `frontend/` changes, no provider credential/configuration
  changes, no unbounded retries, and no automatic resume across a same-process
  durability boundary.
- Existing terminal records remain readable; any expanded incident field must be
  optional and backward compatible.
