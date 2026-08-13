# TODO: N-002 policy-routing cardinality

> 状态: 已完成并归档 | 优先级: 中 | 完成: 2026-08-13
> 上游: Stage 7 final alignment audit | 下游: alignment-audit plan closeout

## Why

The canonical routing model permits every actually triggered policy: the Charter route
table and `openspec/config.yaml` require comma-separated canonical policy names. But
the policy-library index and DRC-001 still say a contributor selects `one relevant
policy`. This can cause contributors to omit applicable reviews.

## 现状对齐

This was a current main-spec/policy-index wording conflict, not runtime behavior, and
not a reason to change the agent-charter checker. The archive
`2026-08-13-reconcile-policy-routing-cardinality` aligned the four current entry
points and DRC-001; existing multiple-policy proposal grammar remains unchanged.

## Current Direction

The completed docs/spec OpenSpec change aligned the policy-library README, DRC-001,
`openspec/config.yaml`, and the Harness Focus Gate. It preserves the separate rule
that each change has one primary causal owner.

## Non-Goals

- Do not change runtime authority, policy applicability semantics, or Focus Card parser
  behavior.
- Do not fold A-002, A-004-T01, or A-009 into this small wording change.

## Completion Evidence

Archived change:
[`2026-08-13-reconcile-policy-routing-cardinality`](../../../openspec/changes/archive/2026-08-13-reconcile-policy-routing-cardinality/).

Post-archive checks passed: `openspec validate --all --strict` (`49 passed, 0 failed`),
`openspec doctor --json`, Agent Charter governance, requirement-to-test coverage, and
`git diff --check`. The full deterministic `UV_OFFLINE=1 make verify` gate had passed
before archive; its four Gateway skips remain an environment limit, not real-Gateway
evidence. The final wording search found no `one relevant policy` or `choose only the
policy` residual in the four current authority targets.
