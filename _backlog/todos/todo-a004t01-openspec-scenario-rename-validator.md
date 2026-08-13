# TODO: A-004-T01 OpenSpec scenario-rename validator

> 状态: 待设计 | 优先级: 中 | 更新: 2026-08-13
> 上游: Stage 5 A-004 reconciliation | 下游: research-run-experience spec maintenance

## Why

Two `research-run-experience` scenario titles preserve legacy `session-bundle` /
`support-journal fallback` wording even though their bodies correctly require
`bundle_journal` after verified publication or `unavailable` without an external
fallback. Current strict OpenSpec delta validation permits requirement rename but
rejects scenario-title rename.

## 现状对齐

This is a tooling/document-structure residue, not a post-loss runtime conformance gap.
The current main-spec bodies, glossary, and bounded local inspection use the selected
Bundle-local-only contract. The owning implementation/tooling surface must be identified
before any work begins; it may be upstream of this repository rather than a Harness
source path.

## Current Direction

Propose scenario-rename support with a red validator example that preserves scenario
identity, requirement content, and strict delta semantics. Only after that support is
available may a separately scoped RER maintenance change rename the two misleading
titles.

## Design Questions

- Is scenario-rename syntax owned by the installed OpenSpec CLI or by repository-local
  validation policy?
- What stable identity preserves review history when a scenario title changes?
- Can a delta declare the old and new titles without producing duplicate scenarios?

## Non-Goals

- Do not alter the selected A-004 behavior.
- Do not use a title change to reintroduce external retained diagnostics or Support
  Handoff fallback.
- Do not edit archived change artifacts.

## Next Step

Identify the authoritative validator owner, then create an independently authorized
tooling proposal with a minimal red validator test.
