# BUG-011: Completed final delivery skips its gate and loses declared repair routes

> Severity: P1 | Discovered: 2026-07-26 | Status: fixed (2026-07-26)

## Symptom

The full deterministic gate fails at
`tests/graph/test_research_graph.py::test_readiness_and_final_repairs_converge_before_completion`.
A full-fake run whose declared final-delivery fixture sequence is
`repair`, `evidence_blocked`, `pass` completes after only one `final_delivery`
visit. It therefore bypasses the declared final-delivery repair and readiness
return routes instead of exercising them before completion.

## Root Cause

The active `harden-deep-research-workflow-outcomes` change added a guard in
`graph/builder.py` that skips gate evaluation whenever a node result has any
`terminal_status`. That preserves a direct non-success Wave2 terminal incident,
but both fake and real final delivery deliberately set `terminal_status=completed`
before the existing final-delivery gate evaluates its `repair`,
`evidence_blocked`, or `pass` route. The broad guard skips that gate and leaves
the prior readiness `pass` route in control, ending the graph after one visit.

This is a graph-control regression, not a provider diagnosis issue. The direct
terminal outcome contract must retain its non-completed gate bypass without
changing completed final-delivery gate ownership.

## Reproduction

```bash
cd agent
env -u VIRTUAL_ENV uv run --extra operations pytest \
  tests/graph/test_research_graph.py::test_readiness_and_final_repairs_converge_before_completion -q
```

Observed twice before remediation: `1 failed in 1.72s`, with
`final_delivery` visited once rather than three times.

## Fix Relationship

Repair within the active OpenSpec change
`harden-deep-research-workflow-outcomes`. Gate evaluation must bypass only a
non-completed direct terminal result. Keep the existing Wave2 terminal test as
the proof that a blocked direct incident does not require a success-only gate
preview, and keep the failing fake-graph route test as the regression proof for
completed final delivery.

## Resolution

Resolved in archived OpenSpec change `harden-deep-research-workflow-outcomes`.
`graph/builder.py` now bypasses gate evaluation only for a non-completed direct
terminal result. The final-delivery repair/readiness routes remain gate-owned, while
the direct Wave2 terminal still avoids an unauthorized success-only preview. Both
focused regressions and the complete `UV_OFFLINE=1 make verify` gate passed on
2026-07-26.
