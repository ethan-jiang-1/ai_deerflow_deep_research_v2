## Why

Four explicitly profiled real-demo Bundles established two separate failure lines in
BUG-024. Three independent Bundles, across `deepseek-v4-pro` and
`deepseek-v4-flash`, stop in topic planning with the closed reason
`per_call_output_cap`; the existing 2048-token cap rejects a response after the
provider returns it. The model-visible TopicPlan contract permits a much broader
output than that cap can safely carry, while the structured-result adapter can also
truncate a JSON candidate at 4096 bytes.

The planner needs one internally consistent, bounded output envelope before the
remaining Wave1 failure can be investigated. Changing a default model or globally
relaxing budgets would neither address this deterministic mismatch nor preserve a
useful diagnosis boundary.

## What Changes

- Define a compact, model-visible TopicPlan output envelope for both initial planning
  and one-shot repair: concise titles and scopes, only necessary dimensions and
  exclusions, and no restatement of the assignment or unsupported prose.
- Preserve the existing authoritative TopicPlan parser and materializer bounds, but
  make the prompt's output contract explicitly narrower for normal planner candidates.
- Calibrate only the topic-planning execution policy as one admitted local budget
  envelope: a 4096 per-call output-token cap, 16384 structured-result byte cap, and
  12288 total-token budget. Preserve its one-call, zero-tool, wall-time,
  provider-recovery, route, checkpoint, and lifecycle contracts.
- Add deterministic prompt/policy tests and a bounded operator calibration record that
  proves explicitly selected `pro` and `flash` Bundles advance beyond topic planning
  without treating a live result as a model qualification.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `topic-planning-node`: the real planner's required model-visible output envelope and
  its explicitly admitted per-node execution bounds are aligned so a valid compact
  TopicPlan is not truncated or rejected by an incompatible local guard.

## Impact

- `deep_research_harness/src/deerflow_deep_research/graph/nodes/topic_planning/`
  capability Markdown and prompt projection.
- `deep_research_harness/src/deerflow_deep_research/runtime/research.py` for the
  topic-planning policy's local budget envelope only.
- Focused prompt/policy tests, real-demo calibration documentation, BUG-024 evidence,
  and the topic-planning main specification after the approved delta is synchronized.
- No changes under `deerflow/`, `backend/`, or `frontend/`; no provider credentials,
  model default, global budget, Wave0/Wave1 policy, retry, route, checkpoint, or
  lifecycle change.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/graph/nodes/topic_planning/` owns the planner's bounded cognitive output contract.
- **Seam classification:** cognitive-program -- the first repair is a compact model-visible candidate contract; the existing runtime policy remains its deterministic enforcer.
- **Question:** How can the zero-tool topic planner return one useful, valid JSON TopicPlan within a fixed bounded envelope, without changing what the parser, materializer, controller, or lifecycle may authorize?
- **Necessary adjacent/external contracts:** `runtime/research.py::_topic_planning_node_agent_policy()` answers which locally matched total/output/retention guards admit that compact candidate; `topic-planning-node` parser/materializer contract answers which existing broad legal candidates remain admissible after runtime retention; `node-agent-runtime` answers that budget exhaustion remains a closed runtime failure, not a planner recovery signal.
- **Evidence seam:** `tests/graph/test_topic_planning_prompts.py` proves the initial and repair output envelope; a focused real-composition policy test proves the calibrated limits; existing topic-planning graph tests prove validation, one repair, state admission, and exhausted routing remain unchanged; a bounded explicit-profile Bundle Journal run is supplemental evidence.
- **Not in scope:** default-model selection, credentials, provider behavior, global budget policy, TopicPlan parser/materializer maxima, Wave0 or Wave1 prompts/validators/budgets, new retries, state/checkpoint shapes, routes, terminal status, or DeerFlow source.
- **Triggered review policies:** node-agent-workflow-integrity, workflow-outcome-review

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TopicPlan initial and repair output contract | node-agent | How can one confirmed assignment be decomposed into a compact covering JSON TopicPlan without repeating the assignment or adding research facts? | Confirmed profile and current direction remain delimited assignment data; repair draft and feedback remain untrusted data | Zero tools; `RuntimeNodeAgentBridge` enforces the existing topic-planning policy | The agent returns one JSON candidate; `parse_plan_output` and `materialize_topic_plan` alone admit it to planner-owned state | Topic-planning owns one structured-output repair; bridge budget/provider outcomes keep their existing bounds | Prompt tests assert compact initial/repair envelope; graph tests assert valid admission and invalid-route behavior |
| Total-token, output-token, and structured-result limits | no-agent | Deterministic guardrail preserves one admitted response envelope after the cognitive contract asks for compact output | The execution policy is runtime-owned; neither profile text nor model output selects a limit | Zero tools; `BudgetMiddleware` and structured-output adapter enforce the local policy | No candidate is admitted by this surface; parser/materializer remain sole admission owners | Existing `budget.exhausted` and structured-output handling, recovery, route, and terminal disposition remain unchanged | Source-faithful fixed-demo admission, policy construction, middleware, and structured-output tests assert the calibrated limits without changing failure mapping |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Compact planner candidate still exceeds the local output-token cap | `BudgetMiddleware` records the existing closed `per_call_output_cap` reason | No added recovery; topic planning preserves its existing non-provider failure handling | Existing topic-planning exhausted route and blocked lifecycle result | Start a fresh run after a separately approved configuration or cognitive-program change | Policy/middleware tests prove the closed reason and topic-planning graph tests prove no topic state is admitted |
| Planner request plus its reserved output ceiling exceeds the local total-token budget | `BudgetMiddleware` records the existing closed `token_admission` reason before provider invocation | No added recovery; topic planning preserves its existing non-provider failure handling | Existing topic-planning exhausted route and blocked lifecycle result | Start a fresh run after a separately approved profile, prompt, or policy change | Source-faithful fixed-demo admission test proves the selected profile is admitted; middleware and graph tests prove the closed stop publishes no topic state |
| Candidate exceeds the structured-result envelope or fails parser/materializer validation | Existing structured-output adapter and topic planner parser/materializer | Existing one structured-output repair only | Existing exhausted route and blocked lifecycle result | Start a fresh run; no diagnostic can resume or change the Bundle | Prompt envelope tests and existing invalid-initial/repair graph tests |
| Compact valid candidate fits the local envelope | Topic planner parser/materializer | No recovery required | Existing `next` route and planner-owned topic registry write | Continue through the existing graph | Focused prompt/policy and topic-planning graph tests |
