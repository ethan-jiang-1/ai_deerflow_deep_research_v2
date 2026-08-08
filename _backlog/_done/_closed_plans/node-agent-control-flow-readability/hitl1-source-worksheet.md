# HITL1 Source Worksheet

> Status: completed source notes, 2026-07-29
>
> This is pre-implementation evidence for `roll-out-node-reader-interfaces`. It is
> not a runtime authority or a second behavior specification.

## Cognitive Job

HITL1 uses two bounded, zero-tool model roles. The profile-brief role proposes an
advisory `StructuredBrief` from the original question. The semantic-intake role
classifies one correlated human reply against one current proposal as a candidate
intent. Neither model role accepts a proposal, publishes `profile.json`, writes
checkpoint authority, or chooses a graph route.

Sources: `hitl1/prompts.py::build_brief_prompt`,
`hitl1/prompts.py::build_semantic_intake_prompt`, and `hitl1-node` HIN-001,
HIN-009 through HIN-011.

## Deterministic Owners

| Decision | Current owner | Lowest responsible proof |
| --- | --- | --- |
| Brief generation, initial advisory-proposal checkpoint, interrupt lifecycle, and profile publication | `graph/nodes/hitl1/node.py::build_real` and `::_generate_brief` | `tests/graph/test_hitl1_node.py::test_first_visit_generates_brief_and_interrupts` and `::test_natural_confirmation_writes_current_proposal_and_routes_accepted` |
| Bounded semantic candidate/retry/repair and non-terminal fallback | `graph/nodes/hitl1/node.py::_classify_proposal_reply` and `prompts.py::build_semantic_intake_prompt` | `tests/graph/test_hitl1_node.py::test_semantic_invalid_output_repairs_once_then_preserves_proposal` |
| Candidate acceptance, revision, and feedback meaning | `domain/human_interaction.py::resolve_semantic_candidate`, then `build_real` | `tests/graph/test_hitl1_node.py::test_semantic_revision_publishes_new_visible_proposal_before_acceptance` |
| Executable continuation after HITL1 returns a typed route | `graph/builder.py` HITL1 conditional edges | `tests/graph/test_topology_and_implementation.py::test_hitl1_route_contract_and_topology_include_followup_and_exhausted` |

## Reader-Facing Cross-Module Facts

1. `capabilities.py` binds four separate local resources: brief, brief repair,
   semantic intake, and semantic repair. Their Markdown bodies describe different
   bounded cognitive roles; the capability ref and tool posture remain deterministic
   binding/enforcement facts. A semantic-reply symptom starts with the semantic
   builder, not the profile-brief builder.
2. `build_real` checkpoints an advisory proposal before `interrupt()` so replay has
   a current proposal to show. A correlated action may accept that existing proposal;
   a semantic candidate still goes through `resolve_semantic_candidate` before
   HITL1 writes `profile.json` or emits `accepted`.
3. Semantic invalid output and exhausted transient recovery preserve the current
   proposal with non-terminal feedback and `needs_followup`. This is distinct from
   a rejected free-text profile answer and from an initial brief failure; do not
   treat either semantic fallback as permission to write a degraded profile or to
   change graph routing.

## Fixed Reader Task

Symptom: a user replies naturally to a complete current proposal, but the first
semantic candidate is invalid and its repair is invalid too.

Given only the eventual package-local `workflow.md`, a reader must identify
`hitl1/node.py::_classify_proposal_reply` as the bounded repair owner,
`hitl1/prompts.py::build_semantic_intake_prompt` as the request owner, and
`tests/graph/test_hitl1_node.py::test_semantic_invalid_output_repairs_once_then_preserves_proposal`
as the narrow proof seam. The reader must conclude that HITL1 preserves the current
proposal and returns non-terminal feedback, not that the model can accept the
proposal, write `profile.json`, or decide a terminal route.
