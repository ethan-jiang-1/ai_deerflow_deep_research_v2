# Topic Planning Source Worksheet

> Status: completed source notes, 2026-07-29
>
> This is pre-implementation evidence for `roll-out-node-reader-interfaces`. It is
> not a runtime authority or a second behavior specification.

## Cognitive Job

Topic planning asks an LLM for a bounded `TopicPlan` candidate from the confirmed
HITL1 profile held in checkpoint short fields. The model does not read
`request/profile.json`, assign stable ids/slugs, write the topic registry, create a
`WorkSpec`, or choose the next graph target.

Sources: `topic_planning/prompts.py::planner_inputs_from_state`,
`::build_planner_prompt`, `topic_planning/node.py::_generate_plan`, and
`topic-planning-node` TOP-001 through TOP-006.

## Deterministic Owners

| Decision | Current owner | Lowest responsible proof |
| --- | --- | --- |
| Read confirmed checkpoint profile and build the initial/repair zero-tool request | `topic_planning/prompts.py::planner_inputs_from_state` and `::build_planner_prompt` | `tests/graph/test_topic_planning_node.py::test_valid_plan_routes_next_and_records_registry` |
| Parse a candidate, materialize coverage, make one structured repair, and convert failure to terminal exhaustion | `topic_planning/node.py::_generate_plan` and `::_materialize` | `tests/graph/test_topic_planning_node.py::test_uncovered_question_is_repaired_then_exhausts` |
| Stable topic ids/slugs, overlap rejection, and must-answer coverage | `domain/topics.py::materialize_topic_plan` | `tests/graph/test_topic_planning_node.py::test_invalid_plan_retries_once_then_records` |
| Executable `next` and `exhausted` targets | `graph/builder.py` topic-planning conditional edge | `tests/graph/test_topic_planning_node.py::test_repeated_invalid_plan_exhausts_without_topic_state` |

## Reader-Facing Cross-Module Facts

1. The planner reads only checkpoint fields through `planner_inputs_from_state`; it
   does not reopen the HITL1 bundle. A profile-authority symptom starts with the
   checkpoint/profile owner, not this planner's prompt builder.
2. `TopicPlan` is advisory. `_materialize` calls `materialize_topic_plan`, which
   derives stable ids/slugs and validates coverage, duplicate, and overlap facts.
   A model-generated id or route is never the correct first edit.
3. A successful invalid plan consumes the one structured repair through
   `build_planner_prompt(inputs, repair_error=...)`; a safe provider failure follows
   the separate bounded provider-recovery path. Repeated invalid coverage fails
   closed with no `topic_registry`, rather than advancing to Wave0.

## Fixed Reader Task

Symptom: a confirmed-profile planner candidate leaves one must-answer question
uncovered, and its one repair leaves the same question uncovered.

Given only the eventual package-local `workflow.md`, a reader must identify
`topic_planning/node.py::_generate_plan` as the bounded repair/exhaustion owner,
`topic_planning/prompts.py::build_planner_prompt` as the request owner,
`domain/topics.py::materialize_topic_plan` as the coverage owner, and
`tests/graph/test_topic_planning_node.py::test_uncovered_question_is_repaired_then_exhausts`
as the narrow proof seam. The reader must reject changing `profile.json`, a
model-proposed topic id, or graph wiring before the planner/materializer boundary.
