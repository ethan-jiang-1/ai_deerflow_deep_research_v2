## 1. Admission And Red Evidence

- [x] 1.1 Confirm `ToolPolicyMiddleware.awrap_model_call` is the sole owner of the
  per-request tool window, that `BudgetMiddleware` retains the outer
  `ExecutionBudget` per-response/parallel caps, and that the Wave1 worker request
  (`tool_call_limit=1`) is the primary consumer. Done when the focused review names
  the truncation seam and confirms no other component needs the change.
  Review conclusion: `ToolPolicyMiddleware.awrap_model_call` owns the window; the
  `BudgetMiddleware` per-response/parallel caps are separate; the Wave1 worker request
  (`tool_call_limit=1`) is the primary consumer; zero-tool nodes (topic planning,
  HITL1) are unaffected because their requests carry no window.
- [x] 1.2 Change the locked unit contract in `tests/unit/test_tool_policy.py`
  (`test_tool_window_rejects_parallel_calls_exceeding_remaining_request_quota`) to
  assert that an over-request is truncated to the remaining window and does not raise.
  Run the focused test and record the expected failure before changing
  `agents/middleware.py`.
  Red baseline: the rewritten contract
  `test_tool_window_truncates_eager_parallel_calls_to_remaining_quota` failed on the
  current middleware (`AgentPolicyError: [policy_denied] request tool-call limit
  exceeded`); 17 other tool-policy tests passed.

## 2. Implement The Window Truncation

- [x] 2.1 Change `ToolPolicyMiddleware.awrap_model_call` to keep the first
  `remaining` calls of an over-request and drop the excess, returning the truncated
  message, without raising. Preserve the existing cumulative counter and
  tools-removal-after-window behavior, and keep `awrap_tool_call` authorization
  (forged tool/path denial) unchanged.
- [x] 2.2 Run the focused `tests/unit/test_tool_policy.py` selection; the previously
  failing contract passes and existing authorization contracts still pass.
  Evidence: `tests/unit/test_tool_policy.py` = 18 passed;
  `tests/unit/test_node_agent_bridge.py` + `tests/unit/test_research_runtime_capabilities.py`
  = 96 passed.

## 3. Real-Wave1 And Full Verification

- [x] 3.1 Attempt `make demo-real-scripted` with the default question. Two real runs
  after the change did not reach Wave1: one blocked at `topic_planning` with
  `budget.exhausted` (zero-tool node, unrelated to this change), the other at `wave0`
  with `structured_output` (model JSON non-compliance for one of three topics). These
  are pre-existing model-vs-contract failures, recorded in `_backlog`; they do not
  exercise the window truncation, whose behavior is unit-validated by
  `test_tool_window_truncates_eager_parallel_calls_to_remaining_quota`. The change is
  archived as a correct middleware fix without claiming it makes the whole flow
  reliably complete.
- [x] 3.2 Run the focused runtime/capability suites, `UV_OFFLINE=1 make verify`,
  `openspec validate tool-window-truncates-eager-parallel-calls --strict`,
  `openspec validate --specs`, and `git diff HEAD --check`.
  Evidence: `UV_OFFLINE=1 make verify` passed (governance/lock/lint/assets/reqs all
  green; fast=2395, integration=234 + 4 expected skips, workflow=35),
  `openspec validate tool-window-truncates-eager-parallel-calls --strict` passed,
  `openspec validate --specs` = 48/48 passed, `git diff HEAD --check` clean.
- [x] 3.3 Sync the `node-agent-runtime` main spec, archive the change to
  `openspec/changes/archive/`, and record evidence here.
  Evidence: `openspec archive tool-window-truncates-eager-parallel-calls -y` applied
  the `node-agent-runtime` delta (1 modified requirement) and archived the change as
  `2026-08-10-tool-window-truncates-eager-parallel-calls`. The main spec now states
  the bounded request window is an executed-call cap with an eager-over-request
  truncation scenario. The real-demo flakiness observation was recorded as
  `_backlog/bugs/BUG-024-real-demo-flaky-against-model-contracts.md`.
