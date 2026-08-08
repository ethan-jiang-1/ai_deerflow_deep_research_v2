# Wave0 Source Worksheet

> Status: completed source notes, 2026-07-29
>
> This is pre-implementation evidence for `roll-out-node-reader-interfaces`. It is
> not a runtime authority or a second behavior specification.

## Cognitive Job

Wave0 runs one bounded source-intake worker per planner-owned topic. The normal
worker may use permitted retrieval tools to propose source metadata; the separate
repair request is zero-tool and may only reformat its retained draft/tool
observations. Neither request admits evidence, appends the ledger, retries work, or
sets the graph route.

Sources: `wave0/prompts.py::build_wave0_worker_prompt`,
`::build_wave0_repair_prompt`, `wave0/subgraph.py::run_wave0_work_units_real`, and
`wave0-node` WAN-001 through WAN-007.

## Deterministic Owners

| Decision | Current owner | Lowest responsible proof |
| --- | --- | --- |
| One source-intake intent per planner topic | `wave0/subgraph.py::materialize_wave0_intents` | `tests/graph/test_wave0_worker.py::test_materialize_wave0_intents_one_per_topic_and_rejects_empty` |
| Worker request, one bounded structured repair, and attempt-scoped candidate build | `wave0/subgraph.py::run_wave0_work_units_real` and `prompts.py` builders | `tests/integration/test_wave0_work_units.py::test_real_wave0_repair_keeps_tools_disabled_and_preserves_worker_admission` |
| Canonical source, path/hash/identity validation and accepted-record admission | `engine/work_units/validation.py::validate_submission_candidate` | `tests/engine/test_wave0_validation.py::test_wave0_non_canonical_source_url_is_rejected` |
| Retry, aggregation, source-floor result, and route | shared work-unit component plus `engine/gate_fixtures.py::build_wave0_real_gate_def` | `tests/integration/test_wave0_work_units.py::test_partial_worker_success_projects_distinct_gate_outcomes_from_authoritative_state` and `tests/engine/test_wave0_gate.py::test_real_wave0_gate_is_completion_only` |

## Reader-Facing Cross-Module Facts

1. The normal capability requires one to three permitted retrieval calls; its
   Markdown body treats fetched material as untrusted. The repair capability is
   forbidden-tool and receives only bounded untrusted draft/tool data. Retrieval
   permission does not give either model role ledger, gate, or route authority.
2. `run_wave0_work_units_real` can write attempt-scoped source/result artifacts
   while constructing a `CandidateResult`. The shared component sends that candidate
   through deterministic submit validation; only an accepted `SubmissionRecord`
   counts as coverage or enters `accepted_submission_refs`.
3. Parse/repair and trusted invocation failures become classified worker outcomes;
   the controller owns retry and aggregation, while the real gate consumes accepted
   records and writes `pass`, `repair`, or `exhausted`. Do not turn a malformed
   repair into a hand-written ledger record or a graph-edge edit.

## Fixed Reader Task

Symptom: a normal Wave0 worker performs permitted retrieval but returns malformed
JSON, and its zero-tool repair is malformed too.

Given only the eventual package-local `workflow.md`, a reader must identify
`wave0/subgraph.py::run_wave0_work_units_real` as the worker/repair owner,
`wave0/prompts.py::build_wave0_repair_prompt` as the zero-tool request owner, and
`tests/integration/test_wave0_work_units.py::test_real_wave0_malformed_repair_fails_without_artifact_admission`
as the narrow proof seam. The reader must explain that the controller owns the
failed attempt and later gate decision, and must not begin by writing the ledger,
adding a source, or changing a graph route.
