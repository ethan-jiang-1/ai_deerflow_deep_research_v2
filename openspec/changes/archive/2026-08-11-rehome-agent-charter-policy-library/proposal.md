## Why

The Deep Research Charter and nine policy documents are hidden under a
`governance/agent-charter/policies/` subtree while `openspec/policies/` holds only
one related policy. The split obscures the reader route and falsely suggests two
policy systems even though one Charter route and one checker registry select all ten.

## What Changes

- Rehome the Charter index and durable principles to `openspec/agent-charter/`.
- Make `openspec/policies/` the single canonical library for all ten trigger-bearing
  policy documents, categorized as Charter-routed or cross-cutting review guidance.
- Retire the misleading external-policy and deferred-V2 terminology while preserving
  every existing policy trigger, review record, posture, and non-authority boundary.
- Update current structural inventory, checker/test routes, and active documentation
  links so the old nested tree has no canonical or compatibility copy.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deep-research-agent-charter`: Replaces the permanent Charter/policy topology and
  clarifies the unified policy-library, cross-cutting control-placement, and advisory
  closeout-evidence terminology in `DRC-001`, `DRC-005`, `DRC-009`, and `DRC-010`.
- `project-structure`: Restores the currently header-declared but body-missing
  `PRS-009` requirement with the replacement exact Charter/policy path inventory.

## Change Focus

- **Primary module / causal owner:** `openspec/agent-charter/` canonical local routing topology, owned by the `deep-research-agent-charter` capability.
- **Seam classification:** wiring - this relocates canonical documents, registry entries, checker routes, and navigation without changing runtime or policy decision semantics.
- **Question:** Can a contributor discover one Charter entry and one complete policy library directly from `openspec/` without a duplicate legacy tree or a second authority model?
- **Necessary adjacent/external contracts:** `project-structure` and `openspec/governance/project-structure.toml` define the exact required paths; `check_agent_charter.py` and `test_agent_charter_governance.py` define the mechanical navigation contract.
- **Evidence seam:** focused charter checker and contract test, followed by the repository governance and deterministic verification gates.
- **Not in scope:** `deerflow/`, Harness runtime behavior, policy trigger/posture/review-record semantics, SCC command behavior, semantic review automation, native archive authority, or historical archives.
- **Triggered review policies:** change-admission, agent-information-map

## Impact

Changes only OpenSpec governance documentation, active authoring pointers, the
structure registry, and their deterministic checker/test. No application API,
dependency, runtime route, or upstream DeerFlow surface changes.
