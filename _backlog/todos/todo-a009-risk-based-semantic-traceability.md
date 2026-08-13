# TODO: A-009 risk-based semantic traceability

> 状态: 候选，未排期 | 优先级: 低 | 更新: 2026-08-13
> 上游: Stage 7 final alignment audit | 下游: future high-risk requirement changes

## Why

Current `@impl` coverage proves that every alive requirement ID has a deterministic
test reference. It does not parse assertions or establish scenario-by-scenario semantic
equivalence. This is an honest evidence limit, not evidence of missing implementations.

## 现状对齐

The existing evidence system intentionally centralizes richer claims only for selected
policy/inventory requirements. Requiring assertion-semantic mapping for every existing
requirement would duplicate the test catalog and conflict with that design.

## Current Direction

If higher assurance is needed, design a bounded policy for materially changed or
high-risk requirements: map a named requirement/risk to the lowest responsible
deterministic assertion seam, without trying to infer test meaning from arbitrary Python.

## Design Questions

- Which risk classes require the additional mapping?
- Is the mapping reviewable metadata, a test fixture convention, or a bounded checker?
- How does it avoid duplicate exhaustive catalogs and false semantic claims?

## Non-Goals

- Do not claim universal semantic equivalence from `@impl` annotations.
- Do not retroactively annotate every historical requirement.
- Do not weaken existing ID-level coverage or evidence selection rules.

## Next Step

Keep unplanned until a high-risk requirement change needs stronger traceability; then
open a focused evidence-governance proposal.
