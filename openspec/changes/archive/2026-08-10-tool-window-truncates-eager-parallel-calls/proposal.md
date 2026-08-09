## Why

A bounded worker request carries a `tool_call_limit` that caps how many tool calls
execute in one agent run (for example Wave1's `exactly one web search call`). The
`ToolPolicyMiddleware` currently enforces that window by raising `AgentPolicyError`
when a model response requests more parallel calls than the remaining window. With
the configured demo model, Wave1's worker reliably fires two or more web tool calls in
one response, so Wave1 fails `gate_blocked` on every real run after three attempts —
the whole deep research flow cannot complete.

The capability text already tells the model to use exactly one retrieval call, so
communication alone does not produce compliance. The enforcement should guarantee the
window by limiting how many calls *execute*, not by failing the run when an eager
model over-requests.

## What Changes

- Change `ToolPolicyMiddleware.awrap_model_call` so a model response whose parallel
  tool calls exceed the remaining request window is truncated to the window: the
  first `remaining` calls are kept and the excess calls are dropped, instead of
  raising `AgentPolicyError`.
- The request window becomes a cap on *executed* calls: after the truncated calls
  execute, the cumulative counter reaches the window and later model turns have tools
  removed, preserving the existing "exactly N effective calls per run" contract.
- Update the locked unit contract to assert truncation instead of denial.
- Add a spec scenario to `node-agent-runtime` `NOA-003` stating the window semantics.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `node-agent-runtime`: Extend the tool/path policy requirement (`NOA-003`) to state
  that a bounded request window is a cap on executed tool calls; an eager model
  response that exceeds the remaining window is truncated to the window's first calls
  and does not fail the run.

## Impact

- Primary module: `deep_research_harness/src/deerflow_deep_research/agents/middleware.py`
  `ToolPolicyMiddleware.awrap_model_call`.
- Adjacent contracts: `tests/unit/test_tool_policy.py` locks the window semantics;
  Wave1 worker requests (`graph/nodes/wave1/prompts.py`) declare
  `tool_call_limit=1` and are the primary beneficiary; `node-agent-runtime` `NOA-003`
  owns the middleware enforcement contract.
- No graph behavior, policy budget, tool allow-list, provider, lifecycle, or command
  change.
- DeerFlow framework, `backend/`, and `frontend/` are unchanged.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/agents/middleware.py`
  `ToolPolicyMiddleware`, which owns per-request tool-window enforcement.
- **Question:** How can the request tool window guarantee "exactly N effective tool
  calls per run" without failing the run when a real model over-requests parallel
  calls in one response?
- **Necessary adjacent/external contracts:** `node-agent-runtime` `NOA-003` (middleware
  enforcement owner), `ExecutionPolicy`/`ExecutionBudget` (allow-list and budget
  bounds remain the outer cap), Wave1 worker request `tool_call_limit=1` (the primary
  consumer), and the shared `ToolPolicyMiddleware` unit contract.
- **Evidence seam:** deterministic unit contract in `tests/unit/test_tool_policy.py`
  proving an over-request is truncated to the remaining window and only the kept
  calls execute, plus a real `make demo-real-scripted` run proving Wave1 no longer
  fails `gate_blocked`.
- **Not in scope:** changing the request `tool_call_limit` values, the policy tool
  allow-list, `BudgetMiddleware` per-response/parallel caps, graph behavior, provider
  selection, or lifecycle authority.
- **Triggered review policies:** node-agent-workflow-integrity

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Request tool window (`ToolPolicyMiddleware`) | node-agent | How many executed tool calls fit the bounded request window when a model over-requests parallel calls in one response? | The model response and the request `tool_call_limit` only; no graph, gate, ledger, or lifecycle authority. | windowed (`tool_call_limit`); `ToolPolicyMiddleware` enforces the executed-call cap and `BudgetMiddleware` retains the outer `ExecutionBudget` per-response/parallel caps. | The first calls that fit the window; the kept calls execute under the existing allow-list/path authorization. | Dropped excess calls are never executed; forged tool names, path escapes, and write-root violations still fail closed in `awrap_tool_call`. | `test_tool_window_truncates_eager_parallel_calls_to_remaining_quota` plus the existing window/authorization contracts. |
| Windowed workers (Wave0, Wave1, targeted evidence) | node-agent | No new cognitive judgment: the request window applies unchanged to each worker's bounded request. | The worker's own model response and request window only. | windowed; the same `ToolPolicyMiddleware` enforcer. | Same truncation under each worker's existing `tool_call_limit`. | Same as above; a worker no longer fails the whole run for an eager over-request. | Unit window contracts; real-run observation recorded in `_backlog` (deepseek-v4-flash also fails other pre-existing node contracts). |
