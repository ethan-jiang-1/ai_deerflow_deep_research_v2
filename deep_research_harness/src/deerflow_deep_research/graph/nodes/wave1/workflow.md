# wave1 — Extract source-grounded evidence and bounded repair candidates

> Reader interface only. This file is not a runtime resource or configuration.
> Code, typed contracts, approved specifications, and tests remain the authority.
> Participation mode: bounded cognitive program
> Commitment state: current accepted
> Current operating mechanism: baseline-aware retrieval worker, zero-tool repair, and two bound zero-tool critics
> Primary cognitive/control program surface: evidence, claims, open-question candidate, and post-acceptance review
> Deterministic authority boundary: validator, controller, ledger, review materializer, and gate own admission and route
> Current model-branch evidence: audit only; worker, repair, SourceDiagnostic, and ClaimVerifier branches

## Node Identity

Workers and critics do not accept evidence, append a ledger record, update a
checkpoint, or select a graph route.

## From Symptoms

| Symptom | First owner | Proof seam |
| --- | --- | --- |
| Worker context/tool role is wrong | `prompts.py` and local capability | `tests/integration/test_wave1_work_units.py` |
| Baseline duplicate appears new | `node.py::build_real` | `tests/integration/test_wave1_work_units.py` |
| Candidate is unexpectedly accepted | `subgraph.py::_wave1_worker`, validator/controller | `tests/integration/test_wave1_work_units.py` |
| Bound critic review is absent or malformed | `review.py::build_wave1_gate_review` | `tests/integration/test_wave1_work_units.py` |
| Accepted work cannot pass the source floor or question disposition | real Wave1 gate | `tests/engine/test_wave1_gate_review.py` |

## Three Cross-Module Facts

1. Before every worker dispatch, `node.py::build_real` derives the Wave0 baseline
   from same-generation accepted Wave0 records; a missing required record fails
   before dispatch.
2. After Wave1 acceptance, SourceDiagnostic and ClaimVerifier receive only bounded
   assignments reconstructed from the accepted result. The review materializer binds
   each immutable artifact to that work attempt and its assignment hash.
3. Candidate and review artifacts are not accepted evidence or route authority. The
   non-checkpointed gate review exposes only source-floor, review-presence, and
   open-question disposition facts; malformed bindings fail before gate routing.

## Route Facts

The wrapper/gate writes the typed route; the graph builder consumes it.

## Evaluation and Verification Order

Begin at the direct worker/controller seam, then inspect the accepted-record review
materializer and the pure gate in that order. Source and critic quality remain outside
these deterministic guardrails. The runtime-loaded extraction and repair capability
Markdown owns the reusable cognitive method; `prompts.py` projects only trusted
assignment, closed response contract, repair category, and delimited untrusted data.
`wave1-cognitive-program@v1` binds those two resources and the worker schema to closed
scripted scenarios. It proves deterministic handoff and authority limits only, and is
not selected-live or source-quality evidence.
