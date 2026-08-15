## Why

The retained real-demo run misclassified a zero-tool topic-planning
`USAGE_UNAVAILABLE` stop as `tool.execution_failed`, and a real
`httpx.ReadTimeout` as `internal.unexpected` without a safe provider observation.
The first gives an incorrect user action; the second prevents topic planning's
already-specified one-shot provider recovery from running through the real bridge.

## Change Focus

- **Primary module / causal owner:**
  `deerflow_research/src/deerflow_deep_research/runtime/node_agent_bridge.py`.
  The bridge owns the deterministic projection of a node-agent stop or direct
  provider exception into the typed `NodeProblem` consumed by a graph node.
- **Question:** How does a zero-tool node-agent termination or direct provider
  exception reach topic planning with a truthful closed category and, only when a
  named execution policy authorizes it, the safe observation required by the
  node's existing recovery table?
- **Necessary adjacent/external contracts:** `node-agent-runtime` defines the
  one-invocation bridge and execution-policy admission question;
  `topic-planning-node` defines the phase-owned one-retry recovery table;
  `workflow-failure-outcomes` defines preservation of a known `NodeProblem`
  through a direct phase; `research-run-experience` defines the shared terminal
  projection of the resulting closed category and opaque diagnostic reference.
  These
  contracts answer respectively who may classify, retry, preserve, and present
  the fact; none creates another route or retry controller.
- **Evidence seam:** deterministic scripted bridge exceptions in
  `tests/unit/test_node_agent_bridge.py`, the topic-planning node's recovery
  seam in `tests/graph/test_topic_planning_node.py`, real-bridge lifecycle
  replay in `tests/integration/test_topic_planning_lifecycle.py`, and the shared
  failure projection contract in `tests/contract/test_run_experience_contract.py`.
- **Not in scope:** `backend/`, `frontend/`, new provider vendors, SDK retry
  policy, changes to topic planning's one-retry bound, generic tool-policy
  rewrites, raw exception display, a new error controller, or a new graph route.
- **Triggered charter policies:** workflow-outcome-review, node-agent-workflow-integrity, control-and-recovery, authority-and-projections, participant-outcomes, change-admission

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| A zero-tool `NodeAgentStop` with `USAGE_UNAVAILABLE`, `BUDGET_EXHAUSTED`, or `POLICY_DENIED` | `RuntimeNodeAgentBridge` maps the trusted stop reason to the closed `NodeProblem` category and preserves the result finish reason; `TerminalIncidentProjection` later retains that typed code. `ResearchRunExperience` subsequently derives or preserves an opaque diagnostic reference from typed terminal facts. | No provider recovery is admitted. Topic planning receives one non-provider result and follows its existing terminal path. | The direct topic-planning terminal retains the actual closed non-tool category without a provider observation or recovery projection. | Use only the existing category-specific terminal new-start or support action; no automatic provider retry is claimed. | Raise each typed stop from a scripted zero-tool bridge and assert the problem, terminal incident, shared failure code and opaque diagnostic reference, and absence of a provider recovery. |
| Direct `httpx.ReadTimeout` from an authorized topic-planning zero-tool invocation | `RuntimeNodeAgentBridge` classifies the direct public exception and derives the safe `ProviderObservation` from its explicit model binding. | `topic_planning` owns exactly one retry of the identical initial planner request; the bridge remains one invocation and never retries. | A successful retry continues normally. A second eligible transient result is a provider terminal with the existing exhausted recovery projection; a non-provider second result retains its actual category. | The existing terminal `fresh_start` action after an exhausted transient provider result; never resume the failed graph. | Drive the actual bridge into the topic-planning node with two scripted timeout exceptions; assert two bridge calls, attempt/retry/exhaustion facts, retained incident, and shared terminal projection. |
| A non-authorized zero-tool request or a tools-enabled request raises a direct transport exception | The bridge's execution-policy admission remains the only authority for attaching a model-service observation. | No new recovery is admitted by this change. | Existing safe mapping and terminal behavior remain unchanged. | Existing behavior only. | Assert a non-admitted policy and a tools-enabled request do not obtain the topic-planning observation or retry eligibility. |
| Cancellation during bridge invocation or topic-planning backoff | The task cancellation remains the runtime/graph control fact. | No retry or terminal projection is created after cancellation. | `CancelledError` continues to propagate. | Existing cancellation/status behavior only. | Reuse and extend cancellation-focused bridge/node regression tests as needed. |

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Bridge stop projection and provider-observation admission for the existing topic-planning model call | no-agent | Closed enum and direct-public-exception matching is deterministic classification, not a model judgment. No new node-agent role, prompt, route, or model call is introduced. | Trusted `NodeAgentContext` supplies phase attribution; immutable `ExecutionPolicy` supplies explicit observation admission; `NodeExecutionRequest.tools_enabled` must remain false; the resolver binding supplies only vetted label/authority facts. | Topic planning remains zero-tool. `RuntimeNodeAgentBridge`, its policy, budget middleware, and tool-policy middleware enforce the posture before and during one invocation. | The existing topic-planning agent candidate is still admitted only by the topic parser/materializer. The bridge admits only a bounded `NodeProblem` and optional `ProviderObservation`; it cannot write state or choose a route. | The bridge classifies one invocation and propagates cancellation. Topic planning alone owns at most one provider retry and its terminal incident. | Inject `AgentBudgetError`, `AgentPolicyError`, and `httpx.ReadTimeout` through the real bridge; assert the node's existing recovery table sees only the correctly typed result. |

## What Changes

- Replace the blanket `NodeAgentStop -> tool.execution_failed` projection with
  a closed mapping that preserves the safe stop reason: add
  `provider.usage_unavailable`, `budget.exhausted`, and `policy.denied` to
  `RunFailureCode`; map `USAGE_UNAVAILABLE`, `BUDGET_EXHAUSTED`, and
  `POLICY_DENIED` respectively; map an unsupported generic stop fail-closed to
  the existing `internal.unexpected`; and ensure that no `NodeAgentStop` is
  projected as `tool.execution_failed`. Existing non-stop tools-enabled result
  mappings, including required-tool-count validation, remain unchanged. The
  bridge does not retain stop detail or raw exception text.
- Replace the HITL1 node-name predicate for provider observations with an
  immutable, named, type-validated `ExecutionPolicy` admission enum. Only the
  existing HITL1 and topic-planning zero-tool policies will opt in; every other
  policy remains denied by default. The admitted bridge path continues to use direct public
  `httpx`/OpenAI exception classes, a bounded `ProviderObservation`, and no
  exception-chain, body, URL, header, credential, or model-object inspection.
- Preserve topic planning's existing one-shot provider recovery ownership. An
  authorized initial `ReadTimeout` becomes `provider.timeout` with a valid safe
  observation, so the node invokes the planner exactly twice at most; structured
  output repair remains a separate path and is never reclassified as provider
  recovery.
- Carry the final closed code unchanged through `NodeProblem` and the
  topic-planning terminal incident, then through the shared
  `ResearchRunExperience` failure copy and its existing typed-fact diagnostic
  publication seam. New code-specific presentation is derived from those typed
  facts and does not infer a tool failure or create a new lifecycle action.
- Add red-before-green bridge, node, lifecycle, and shared-projection tests,
  including real bridge-to-topic-planning coverage so a hand-built
  `NodeProblem` fixture cannot mask admission regressions. Credentialed real
  demo replay remains supplemental evidence.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `node-agent-runtime`: project node-agent stops truthfully and admit safe
  model-provider observations through an explicit zero-tool execution policy.
- `topic-planning-node`: make the existing one-shot provider recovery observable
  through the real authorized bridge path without changing its bound or
  structured-output repair behavior.
- `workflow-failure-outcomes`: preserve the expanded closed `NodeProblem`
  categories through a direct phase without replacing them with an unclassified
  failure.
- `research-run-experience`: project the truthful terminal code and its existing
  safe diagnostic identity to shared human and machine consumers.

## Impact

- Implementation is limited to `deerflow_research/` execution-policy and bridge
  code, closed run-experience contracts/presentation copy, the existing
  topic-planning recovery seam, focused tests, and only the affected evidence
  metadata. `backend/` and `frontend/` remain untouched.
- `RunFailureCode` gains three closed values. They are additive for retained
  records; existing records remain readable and no historic terminal is
  reinterpreted.
- The change does not alter provider configuration, attempt budgets, graph
  topology, checkpoint schema, or retained diagnostic schema. It uses the
  existing terminal incident and provider-recovery projections as the single
  lifecycle authority.
