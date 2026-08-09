## Context

See proposal.md for the motivation. `ToolPolicyMiddleware.awrap_model_call` currently
denies a model response when `tool_calls + len(pending_calls) > tool_call_limit`. With
`tool_call_limit=1` (Wave1), a model that fires two parallel web calls in one response
raises `AgentPolicyError`, the attempt is classified `agent_invocation_failed`, and
after three attempts the Wave1 gate blocks. The configured demo model fires parallel
calls reliably, so Wave1 cannot complete. The capability text already instructs
"exactly one retrieval call"; enforcement, not communication, must guarantee the
window.

## Goals / Non-Goals

**Goals:**

- Guarantee the request window is an executed-call cap regardless of model eagerness:
  an over-request is truncated to the remaining window, not a run failure.
- Preserve the existing cumulative-window contract: exactly `tool_call_limit` calls
  execute per run, and after the window is exhausted later model turns have tools
  removed.
- Keep `BudgetMiddleware` (per-response and parallel caps from `ExecutionBudget`) as
  the outer policy budget; only the per-request window changes.
- Prove the behavior with a deterministic unit contract and a real Wave1 run.

**Non-Goals:**

- Changing `tool_call_limit` values (the Wave1 "exactly one search" contract is
  spec-owned and unchanged).
- Changing the tool allow-list, provider selection, graph behavior, retry policy, or
  lifecycle authority.
- Silently ignoring security-relevant denials: forged tool names and path escapes
  still fail closed in `awrap_tool_call`.

## Decisions

### The window truncates the over-request instead of denying it

In `ToolPolicyMiddleware.awrap_model_call`, when `len(pending_calls) > remaining`
(`remaining = tool_call_limit - tool_calls`), keep the first `remaining` calls and
drop the excess, returning a message whose `tool_calls` contain only the kept calls.
The dropped calls never execute. This makes the window a cap on *executed* calls, so
the Wave1 worker always performs exactly one effective search even when the model
over-requests.

The existing denial path for genuinely unauthorized calls remains: `awrap_tool_call`
still raises `AgentPolicyError` for non-allow-listed tools, path escapes, ineligible
specs, and write-root violations. Truncation only relaxes the window bookkeeping when
an otherwise-authorized model over-fires within the configured tool set.

### The cumulative counter keeps the window semantics

After the truncated calls execute, `self.tool_calls` reaches `tool_call_limit`, so the
next model turn sees `tools=[]` and `tool_choice=None` and must produce the structured
answer — the existing "reserve a final answer turn" behavior is unchanged.

### Deterministic red evidence first

Before the implementation, change the locked unit contract
`test_tool_window_rejects_parallel_calls_exceeding_remaining_request_quota` to assert
truncation: with `tool_call_limit=2` and one call already used, a response requesting
two parallel calls yields a message with only the first call, and no `AgentPolicyError`
is raised. This fails on the current code and passes after the change.

### Spec scenario

Extend `node-agent-runtime` `NOA-003` with a scenario stating that a model response
over-requesting the remaining window is truncated to the window's first calls and does
not fail the run, while forged tools and path escapes still fail closed.
