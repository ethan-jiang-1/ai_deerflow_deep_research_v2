# BUG-009: HITL2 zero-tool fixture omits the required Wave2 predecessor

> 严重级别: P2 | 发现: 2026-07-25 | 状态: 活跃

## 症状

`cd agent && UV_OFFLINE=1 make verify` reaches the deterministic integration lane
and fails `test_hitl2_is_deterministic_zero_tool_node` with
`ValueError("hitl2_state_invalid")`. The fixture supplies an empty
`execution_trace`, even though the real HITL2 boundary accepts only a state that
arrived from a passing `wave2_synthesis` visit.

## 根因

The HITL2 predecessor validator was tightened in `3fda3446` to require a non-empty
tuple ending in `wave2_synthesis`. The older zero-tool conformance fixture retained
an empty trace, so it no longer constructs the legal input state its test intends to
exercise. The production validator and its unit tests correctly fail closed on that
empty predecessor.

## 复现

```bash
cd /Users/bowhead/ai_deerflow_deep_research/agent
UV_OFFLINE=1 uv run --locked --no-sync --extra operations \
  pytest tests/integration/test_zero_tool_node_conformance.py::test_hitl2_is_deterministic_zero_tool_node
```

## 修复关联

Verification maintenance while completing OpenSpec change
`establish-deep-research-agent-charter`. The fix updates only the integration
fixture to represent the valid Wave2-pass predecessor; it does not relax HITL2
validation or change runtime behavior.
