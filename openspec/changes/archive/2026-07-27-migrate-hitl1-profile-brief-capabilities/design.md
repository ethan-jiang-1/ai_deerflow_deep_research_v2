## Context

The completed first cohort already supplies a validated local-resource loader, four
prompt layers, forbidden-tool bridge admission, a prompt catalog, and branch evidence
rows. HITL1 brief generation is still deliberately in the closed legacy inventory:
one builder returns a `StructuredBrief` proposal from the original question and the
same builder's repair branch repairs one invalid result. The graph, not either model
response, owns proposal display, acceptance, state, and recovery.

## Goals / Non-Goals

**Goals:**

- Replace the two HITL1 brief legacy bindings with exact local capability refs and
  static policies.
- Preserve zero-tool execution, typed brief parsing, one repair bound, and advisory
  proposal semantics.
- Expand catalog, inventory, structure, and evidence governance from six to eight
  migrated branches without weakening the remaining legacy closure.

**Non-Goals:**

- Do not change profile fields, user-response semantics, route selection, checkpoint
  writes, retry counts, provider policy, UI text, or any non-HITL1 branch.
- Do not introduce optional tool posture, generic fallback policy, or a new runtime
  execution path.

## Decisions

### 1. Use two distinct zero-tool capabilities

`hitl1-profile-brief` describes conservative advisory profile construction;
`hitl1-profile-brief-repair` describes schema-only repair against the original
question and invalid draft. Both reside in the existing HITL1 package and use the
validated forbidden posture. This follows the first cohort's repair-as-distinct-work
rule rather than encoding repair mode in mutable assignment text.

Alternative considered: reuse the semantic-intake policy. Rejected because semantic
intent classification and profile proposal have different output contracts, input
authority, and completion conditions.

### 2. Keep the existing HITL1 parser and lifecycle seam

The builders add only `required` refs. `parse_brief_output`, the proposal materializer,
and the node's one-repair/exhaustion behavior remain unchanged owners. Capability
metadata and Markdown are static policy only and cannot select a route, accept a
proposal, mutate state, or carry a live tool.

Alternative considered: let the capability resource encode lifecycle advice. Rejected
because it would turn reviewed cognition text into graph authority.

### 3. Extend closed inventories and evidence atomically

The migrated set becomes eight direct catalog cases. The legacy set removes only
`hitl1/brief` and `hitl1/brief-repair`, leaving exactly eight named cases. Two new
matrix rows bind distinct collected success and high-risk real-node selectors; catalog
or aggregate tests remain supporting checks, not substitute evidence.

## Risks / Trade-offs

- [Capability text accidentally gains acceptance authority] → metadata stays extra-
  forbid and real-node assertions prove only a proposal is produced.
- [Brief repair silently receives tools] → forbidden posture, request window, and
  recording bridge all assert no model-visible tools.
- [A later cohort gets counted by owner aggregation] → exact eight-migrated/eight-
  legacy inventory and two dedicated evidence rows fail closed on drift.

## Migration Plan

1. Add the two refs/resources and migrate the builders.
2. Regenerate the review catalog and register the exact structural paths.
3. Extend inventory, matrix, requirement registry, impacts, and `@impl` coverage.
4. Run focused lifecycle/bridge/catalog checks, then the full offline gate.

Rollback is code-only: restore both builders to the explicit legacy bindings and
remove their resources/matrix rows together; no persisted data or public API changes.

## Open Questions

None. The profile capability boundaries, zero-tool posture, parser ownership, and
evidence seam are decided by the remediation plan and first-cohort contract.
