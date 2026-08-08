## Context

The archived Wave2 pilot established `workflow.md` as a small, package-local reader
projection: it directs a maintainer to current source, typed contracts, approved
specifications, and tests without becoming a runtime resource or a second behavior
specification. The remaining LLM-bearing packages have materially different
authority boundaries: HITL1 includes a human interaction lifecycle, topic planning
has a deterministic materializer, Wave0 and Wave1 use shared work-unit admission,
and targeted evidence combines gate-owned gap work with read-only critics.

This change adds projections only. Existing node code, domain contracts, work-unit
controller, ledger, gate, graph builder, capability bodies, and tests continue to
own all runtime facts. `backend/` and `frontend/` remain outside the change.

## Goals / Non-Goals

**Goals:**

- Colocate one concise `workflow.md` with each remaining LLM-bearing node package.
- Record a local worksheet and a fixed symptom-driven reader task before each
  projection is accepted.
- Let each projection expose only the cross-module facts that change a maintainer's
  first edit or proof seam.
- Promote the Wave2 pilot requirement into a six-node reader-interface capability.

**Non-Goals:**

- Change model roles, prompts, capability Markdown, tool policy, state, work-unit
  behavior, critic admission, route wiring, retry/recovery behavior, or tests.
- Create a shared document schema, parser, checker, index, metadata record,
  generated inventory, or `workflow_review.py`.
- Impose Wave2 headings, symptom rows, or repair semantics on a different node.

## Decisions

### Keep projections package-local and non-runtime

Each of `hitl1`, `topic_planning`, `wave0`, `wave1`, and `targeted_evidence` gets
one `workflow.md` beside its implementation. Every file begins with its
non-runtime/authority boundary and links to source instead of restating local control
flow.

Alternative considered: a central documentation tree with a common template. It is
rejected because the five ownership shapes differ and a central template would make
the projection easier to mistake for shared runtime semantics.

### Use a per-node worksheet and reader task as admission evidence

Each worksheet names the bounded cognitive job, deterministic owners, lowest
responsible proof, and at most three causal facts that change a maintenance decision.
Its reader task gives only the final `workflow.md` plus a node-specific symptom. The
result must identify the first owner, the proof seam, and surfaces that must not be
changed first.

Alternative considered: a documentation parser or a static completeness checker. It
is rejected because the intended benefit is reader navigation, not machine-enforced
uniform prose, and the Wave2 pilot does not establish a stable shared schema.

### Preserve each node's actual authority boundary

| Node | Bounded model job | Deterministic authority that the projection must preserve |
| --- | --- | --- |
| HITL1 | Brief and semantic-intent candidate | Human response correlation, proposal acceptance, profile publication, and routes remain with HITL1/domain/graph. |
| Topic planning | Confirmed-profile `TopicPlan` candidate | `materialize_topic_plan` owns stable identifiers and coverage; the node owns bounded repair/exhaustion. |
| Wave0 | Retrieval-backed source candidate | Work-unit controller, submit validator, ledger, and gate own admission, retries, and routes. |
| Wave1 | Baseline-aware evidence and claim candidate | Validator/controller/ledger and critic/gate seams own new-source admission and outcomes. |
| Targeted evidence | Same-gap evidence candidate or read-only critic candidate | Gate-owned gap ids, materializers, controller/ledger, and the graph's unconditional return edge retain authority. |

Each projection points to the relevant capability body only when a symptom concerns
the model-visible role or tool posture. Capability metadata, runtime enforcement,
and graph behavior remain separately owned facts.

### Retain unresolved behavior as an implemented limitation

If source, spec, and lowest-responsibility tests do not establish a feedback,
recovery, or route fact, the projection will label it an implemented limitation or
leave it to the owning behavior change. The documentation change cannot manufacture a
causal claim to make navigation feel complete.

### Wave1 baseline and gate evidence boundary

The Wave1 projection has one source/spec discrepancy that a reader task must make
visible rather than normalize away. `wave1/node.py::build_real` creates an empty
`wave0_urls` set and leaves its proposed ledger/state collection loops as `pass`
before it calls `run_wave1_work_units_real`. By contrast,
`wave1/subgraph.py::_wave1_worker` correctly classifies a duplicate only when its
caller supplies `wave0_urls`, and
`test_real_wave1_baseline_duplicate_is_not_admitted_as_new_coverage` proves that
injected-subgraph seam only. It is not top-level real-node baseline-loading evidence.

Similarly, `engine/gate_fixtures.py::build_wave1_real_gate_def` currently supplies
only `WorkUnitCompletionRule`; it does not establish the broader critic-verdict or
open-question checks described in `wave1-node`. The projection SHALL identify these
as implemented limitations and direct a behavior change to the owning Wave1/gate
surfaces. It SHALL not describe either limitation as fixed, use the injected test as
full-node proof, or propose a runtime repair in this documentation-only change.

## Risks / Trade-offs

- [A local document drifts from source] -> Cite exact paths/symbols, recheck every
  row against current source/spec/test, and keep the file short.
- [Readers infer a shared workflow schema] -> State node-specific boundaries and
  avoid repeating Wave2's table or repair narrative where it does not affect a
  decision.
- [Projection is mistaken for runtime configuration] -> State its non-runtime
  boundary at the top and do not import, register, render, or validate it.
- [A reader task exposes ambiguous ownership] -> Stop the rollout for that fact and
  record an implemented limitation or route it to the owning behavior change.
