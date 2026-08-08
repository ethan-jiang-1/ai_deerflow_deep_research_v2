# targeted_evidence — Resolve a gate-projected evidence gap

> Reader interface only. This file is not a runtime resource or configuration.
> Code, typed contracts, approved specifications, and tests remain the authority.
> Participation mode: bounded cognitive program
> Commitment state: current accepted
> Current operating mechanism: source-audited retrieval, repair, and read-only critic branches
> Primary cognitive/control program surface: same-gap evidence or diagnostic candidate
> Deterministic authority boundary: worker admission, critic materializer, ledger, and builder own effects and route
> Current model-branch evidence: audit only; four direct branches

## Node Identity

Workers and critics propose bounded candidates; they do not admit evidence, publish
critic artifacts, or select the graph's return edge.

## From Symptoms

| Symptom | First owner | Proof seam |
| --- | --- | --- |
| Wrong gap or worker request | `subgraph.py::materialize_gap_intents` | `tests/graph/test_targeted_evidence_real.py` |
| Candidate or critic artifact is invalid | worker admission or `materializer.py` | `tests/graph/test_targeted_evidence_real.py` |
| Return target is wrong | `graph/builder.py::build_research_graph` | `tests/graph/test_topology_and_implementation.py` |

## Three Cross-Module Facts

1. Work starts only from gate-owned canonical gap ids.
2. Evidence admission and critic artifact materialization have distinct deterministic owners.
3. Returned `route="next"` is not an executable choice: builder unconditionally returns to Wave2.

## Route Facts

The unconditional `targeted_evidence -> wave2_synthesis` edge, not worker/critic
output, determines the next graph node.

## Evaluation and Verification Order

Test router, worker/admission, or materializer first; inspect the builder only for an
executable return-edge symptom.
