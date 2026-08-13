# TODO: A-004-T01 OpenSpec scenario-rename validator

> 状态: 外部 owner 已确认，等待外部授权 | 优先级: 中 | 更新: 2026-08-13
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
Bundle-local-only contract. The owner investigation is complete: the installed
`@fission-ai/openspec@1.8.0` CLI, not Harness code or repository-local governance,
matches scenario title strings when it checks whether a `MODIFIED` requirement would
drop an existing scenario. That check is shared by strict validation and archive.

## Current Direction

Keep the two legacy headings as validation-compatible identifiers. A scenario rename
requires upstream OpenSpec support that provides an explicit, archive-consumable mapping
or stable scenario identity and proves with a red test that a genuine deletion still
fails. Only after that support is available may a separately scoped RER maintenance
change rename the headings.

## Owner Investigation

- **Owner:** installed upstream `@fission-ai/openspec@1.8.0`, published from
  `Fission-AI/OpenSpec`; it is outside this repository and not part of `deerflow/`.
- **Reason:** the package parses only requirement-level `RENAMED Requirements`. Its
  shared validation/archive function considers a changed `#### Scenario:` title to be
  a missing old scenario, even when the requirement and WHEN/THEN body are unchanged.
- **Local boundary:** `openspec/governance/check_project_specs.py` explicitly delegates
  active-delta validation to OpenSpec validate/archive, so a local checker adjustment
  would not make archive safe and would split the two authorities.
- **Evidence:** [owner research](../plans/alignment-audit-2026-08-12/alignment-audit-60-adjustments/a004t01-scenario-rename-owner-research/a004t01-scenario-rename-owner-research.md).

## Non-Goals

- Do not alter the selected A-004 behavior.
- Do not use a title change to reintroduce external retained diagnostics or Support
  Handoff fallback.
- Do not edit archived change artifacts.
- Do not patch, fork, or locally override the globally installed OpenSpec CLI.

## Next Step

Wait for one explicit user decision: authorize an upstream Fission-AI/OpenSpec issue or
proposal/PR, or authorize an upgrade investigation after a release explicitly supports
scenario identity/rename. Reopen this todo only under that authority. Before any later
RER maintenance change, reproduce the rename with a red validator/archive test and
confirm the supported CLI version accepts the explicit mapping without weakening a true
scenario-deletion rejection.
