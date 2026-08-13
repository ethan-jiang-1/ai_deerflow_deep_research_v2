# TODO: N-002 policy-routing cardinality

> 状态: 提案完成，待 apply 授权 | 优先级: 中 | 更新: 2026-08-13
> 上游: Stage 7 final alignment audit | 下游: alignment-audit plan closeout

## Why

The canonical routing model permits every actually triggered policy: the Charter route
table and `openspec/config.yaml` require comma-separated canonical policy names. But
the policy-library index and DRC-001 still say a contributor selects `one relevant
policy`. This can cause contributors to omit applicable reviews.

## 现状对齐

This is a current main-spec/policy-index wording conflict, not runtime behavior, and
not a reason to change the agent-charter checker. Existing multiple-policy proposal
grammar already passes governance.

## Current Direction

Use one small docs/spec OpenSpec change to choose consistent cardinality language across
the policy-library README, DRC-001, and any directly linked wording. Preserve the
separate rule that each change has one primary causal owner.

## Design Questions

- Should concise index wording say `select every relevant policy` or point directly to
  the Charter's trigger-based route?
- Which exact DRC-001 scenario demonstrates multiple simultaneously triggered policies
  without making policies runtime authority?
- What focused checker/test evidence proves that singular residual text is gone without
  adding semantic-policy automation?

## Non-Goals

- Do not change runtime authority, policy applicability semantics, or Focus Card parser
  behavior.
- Do not fold A-002, A-004-T01, or A-009 into this small wording change.

## Next Step

The `skip_specs: false` OpenSpec change
[`reconcile-policy-routing-cardinality`](../../openspec/changes/reconcile-policy-routing-cardinality/)
now contains a validated proposal, DRC-001 delta, design, and task checklist. Apply
only after separate authorization.
