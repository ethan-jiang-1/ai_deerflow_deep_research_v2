# Wave1 Source Worksheet

> Status: completed source notes, 2026-07-29
>
> This is pre-implementation evidence for `roll-out-node-reader-interfaces`. It is
> not a runtime authority or a second behavior specification.

## Cognitive Job

Wave1 runs a bounded, baseline-aware deep-evidence worker per planner topic. The
normal worker uses exactly one permitted retrieval call to propose sources, claims,
and open questions; the separate repair is zero-tool. The model does not admit a
candidate, append the ledger, materialize critic results, or choose the next route.

Sources: `wave1/prompts.py::build_wave1_worker_prompt`,
`::build_wave1_repair_prompt`, `wave1/subgraph.py::_wave1_worker`, and `wave1-node`
WON-001 through WON-007.

## Deterministic Owners

| Decision | Current owner | Lowest responsible proof |
| --- | --- | --- |
| Initial exactly-one-search request and zero-tool repair request | `wave1/prompts.py` builders and `subgraph.py::_wave1_worker` | `tests/integration/test_wave1_work_units.py::test_real_wave1_crosses_worker_context_artifact_validator_and_ledger` |
| Candidate artifact construction and work-unit submission path | `wave1/subgraph.py::_wave1_worker` and `::run_wave1_work_units_real` | `tests/integration/test_wave1_work_units.py::test_real_wave1_malformed_repair_has_no_artifact_admission` |
| Caller-supplied Wave0 baseline duplicate marking | `subgraph.py::_wave1_worker` with its `wave0_urls` argument | `tests/integration/test_wave1_work_units.py::test_real_wave1_baseline_duplicate_is_not_admitted_as_new_coverage` |
| Wrapper gate route after the node returns a work-unit gate view | `engine/gate_fixtures.py::build_wave1_real_gate_def` and `graph/builder.py::_node_wrapper` | `tests/engine/test_wave0_gate.py::test_real_wave0_gate_is_completion_only` is the analogous shared-completion gate seam; Wave1's definition is source-reviewed here |

## Reader-Facing Cross-Module Facts

1. The initial request binds `wave1-evidence-extraction`, requires exactly one
   retrieval call, and carries a supplied baseline list. The repair binds
   `wave1-evidence-extraction-repair`, exposes no tool, and cannot add a source,
   URL, claim, or open question outside retained observations.
2. `_wave1_worker` writes contained attempt artifacts and creates a candidate;
   the shared component/validator/ledger own whether its submission is accepted.
   A model result or generated artifact is not accepted evidence by itself.
3. **Implemented limitation:** `wave1/node.py::build_real` currently creates an
   empty `wave0_urls` set and leaves both intended ledger/state collection loops as
   `pass` before calling `run_wave1_work_units_real`. The baseline-duplicate test
   proves the direct subgraph seam when a caller supplies the set; it does not prove
   top-level real-node baseline loading. Fixing that path belongs to an owning Wave1
   behavior change, not this documentation change.
4. **Implemented limitation:** the current `build_wave1_real_gate_def` contains only
   the shared completion/drain rule. Do not infer critic-verdict or open-question
   route enforcement from a worker candidate or from this projection; reconcile any
   such behavior with the owning Wave1/gate change before modifying prompts or edges.

## Fixed Reader Task

Symptom: a Wave0-baseline URL appears as a Wave1 source and is treated as new during
a full top-level Wave1 run.

Given only the eventual package-local `workflow.md`, a reader must identify
`wave1/node.py::build_real` as the first owner for baseline loading,
`wave1/subgraph.py::_wave1_worker` as the caller-supplied baseline classification
seam, and
`tests/integration/test_wave1_work_units.py::test_real_wave1_baseline_duplicate_is_not_admitted_as_new_coverage`
as a direct-subgraph proof that does not cover the top-level load. The reader must
label the missing load as an implemented limitation and reject prompt-only, ledger,
or graph-edge edits as a first fix.
