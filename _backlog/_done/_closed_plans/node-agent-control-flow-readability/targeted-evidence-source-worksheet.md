# Targeted Evidence Source Worksheet

> Status: completed source notes, 2026-07-29
>
> This is pre-implementation evidence for `roll-out-node-reader-interfaces`. It is
> not a runtime authority or a second behavior specification.

## Cognitive Job

Targeted evidence has two bounded model roles. One worker performs exactly one
retrieval for one gate-projected gap, then may use a zero-tool structured repair.
SourceDiagnostic and ClaimVerifier are separate read-only, zero-tool critics over
assigned references. No model role admits evidence, writes a ledger, materializes a
critic artifact, or selects the next executable graph edge.

Sources: `targeted_evidence/node.py::build_real`,
`subgraph.py::materialize_gap_intents`, `::run_gap_workers`, and
`::dispatch_critic`; `materializer.py`; and `targeted-evidence-loop` TEL-001 through
TEL-005.

## Deterministic Owners

| Decision | Current owner | Lowest responsible proof |
| --- | --- | --- |
| One same-gap work intent from a canonical gate projection | `subgraph.py::materialize_gap_intents` | `tests/graph/test_targeted_evidence_real.py::test_gap_router_consumes_only_gate_owned_gap_ids` |
| Initial one-search worker request and zero-tool repair | `subgraph.py::run_gap_workers` and `prompts.py` builders | `tests/graph/test_targeted_evidence_real.py::test_targeted_invalid_first_response_repairs_once_without_tools` |
| Candidate validation, admission, retry, and accepted submission | shared work-unit component/validator/controller/ledger | `tests/graph/test_targeted_evidence_real.py::test_gap_worker_crosses_real_resolver_artifact_validator_and_ledger` |
| Critic assignment validation and artifact publication | `node.py::build_real` plus `materializer.py` | `tests/graph/test_targeted_evidence_real.py::test_claim_verifier_rejects_unassigned_reference_without_artifact` |
| Executable return to Wave2 | `graph/builder.py::build_research_graph` | `tests/graph/test_topology_and_implementation.py::test_wave2_topology_includes_bounded_exhausted_terminal` |

## Reader-Facing Cross-Module Facts

1. The worker receives only a canonical `unresolved_gaps` id from the current Wave2
   gate. `materialize_gap_intents` rejects invalid or duplicate ids; gap prose and a
   model result do not create work.
2. `run_gap_workers` can produce attempt-scoped source/result artifacts and a
   `CandidateResult`, but shared validation/controller/ledger determine admission.
   `dispatch_critic` returns model candidates; `materializer.py` validates their
   references before publishing critic artifacts. Neither path grants route or
   evidence authority to a model.
3. `node.py` returns `route="next"`, but it is not an executable branch decision:
   the graph builder has an unconditional `targeted_evidence -> wave2_synthesis`
   edge. A return-edge symptom therefore starts in the builder after the node's
   admission fact has been settled.

## Fixed Reader Task

Symptom: a targeted worker returns a valid same-gap candidate, but a maintainer
believes the node's `route="next"` should be changed to send it elsewhere.

Given only the eventual package-local `workflow.md`, a reader must identify
`subgraph.py::run_gap_workers` and the shared admission boundary for the candidate,
`graph/builder.py::build_research_graph` as the executable return-edge owner, and
`tests/graph/test_targeted_evidence_real.py::test_gap_worker_crosses_real_resolver_artifact_validator_and_ledger`
as the narrow worker/admission proof seam. The reader must reject a direct route
field, critic prompt, or ledger edit as the first change for the return-edge symptom.
