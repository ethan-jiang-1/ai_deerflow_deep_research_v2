# BUG-010: Topic planning timeout is reported as an opaque blocked research run

> 严重级别: P1 | 发现: 2026-07-25 | 状态: 已修复 (2026-07-26)

## 症状

The standalone real demo accepts the HITL1 research profile, then blocks at
`topic_planning` without returning a plan or a usable provider-timeout diagnostic.
The operator sees `research.blocked`, `可重试: 否`, and a diagnostic with unknown
certainty, despite the model call itself exceeding its configured time budget.

Captured run: `r_gXaOsn8iXATey82BNZHLWg3ITExO-c57gy4agmy0Ek8`

- `topic_planning` model invocation began at `2026-07-24T23:16:50.073591Z`.
- It was terminated at `2026-07-24T23:17:20.113778Z` after 30.04 seconds.
- No `model_tool.completed` or retry event was recorded.
- The terminal result was downgraded to `research.blocked` with diagnostic
  `diag_f35aee43c157c09a987cad04`.

## 根因

The real HITL1 and topic-planning nodes share the
`hitl1-structured-brief` execution policy, whose `wall_time_seconds` is 30.0.
When its bridge returns a non-success `NodeExecutionResult` after budget
exhaustion, topic planning discards the failure details and returns the same
`exhausted` graph route used for unrecoverable planning failure. The lifecycle
therefore exposes only a non-retryable, unknown `research.blocked` outcome rather
than the observed provider timeout and a defined recovery path.

## 复现

```bash
cd agent
make demo-real DEMO_ARGS='--question "OpenSpec 的普及程度、正面与负面影响；只采用有影响力团队或社区的一手资料，并给出引用。"'
```

At the HITL1 prompt, enter `采用建议`. Inspect the retained run with:

```bash
make demo-sessions DEMO_ARGS="inspect r_gXaOsn8iXATey82BNZHLWg3ITExO-c57gy4agmy0Ek8"
```

The deterministic unit seam is `agent/tests/graph/test_topic_planning_node.py`:
a failed or budget-exhausted `NodeExecutionResult` must preserve its failure
classification through the lifecycle result instead of becoming generic
`research.blocked`.

## 修复关联

Not yet assigned. Scope the follow-up around the topic-planning failure contract:
preserve provider timeout observability, define retry behavior, and set a
phase-appropriate wall-time budget rather than changing an unrelated global
timeout.

## Resolution

Resolved in archived OpenSpec change `harden-deep-research-workflow-outcomes`.
Topic planning now owns a distinct 60-second execution policy, preserves the bridge's
safe timeout classification, allows one bounded provider recovery separate from
structured-output repair, and retains a terminal incident on exhaustion without
writing topic authority. The deterministic lifecycle, session, and CLI regression
coverage passed in the complete `UV_OFFLINE=1 make verify` gate on 2026-07-26.
