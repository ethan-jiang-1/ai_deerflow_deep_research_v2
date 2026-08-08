## Context

Wave2's `build_real` already makes its local sequence visible: read accepted
evidence, build a request, admit a candidate, perform at most one repair, and
write the validated result. The costly maintenance facts sit at module boundaries:
the renderer places the capability Markdown body in the system policy, the repair
builder receives only draft and evidence, and the wrapper/gate/builder own the
route after the node emits a typed preview.

The change adds a reader projection only. Existing code, typed contracts, main
specifications, and tests remain the authority for every runtime fact.

## Goals / Non-Goals

**Goals:**

- Colocate one compact, symptom-driven Wave2 maintenance map with the node.
- Route a reader from common symptoms to exact source owners and the narrowest
  existing proof seams.
- Make the current repair-feedback limitation explicit without changing it.
- Demonstrate a reusable method while leaving each future node free to expose its
  own relevant causal facts.

**Non-Goals:**

- Change model roles, prompts, capability bodies, tool posture, candidate
  admission, graph routing, state, gate behavior, or tests.
- Create a parser, Markdown schema, checker, generated inventory, shared
  documentation module, or `workflow_review.py`.
- Modify `backend/` or `frontend/`.

## Decisions

### One package-local Markdown projection

Add `graph/nodes/wave2_synthesis/workflow.md` beside the implementation rather
than under a global documentation tree. It is a maintenance entry point, not a
runtime resource: no loader, builder, or NodeSpec will read it. This keeps the
projection close to the causal owner while preserving code/spec/test authority.

Alternative considered: a shared node-workflow directory and generated index.
Rejected because one pilot has not established a stable cross-node schema, and an
index would create maintenance infrastructure before there is evidence it helps a
reader find the correct owner.

### Keep only decision-changing cross-module facts

The document will link to `node.py::build_real` for the local sequence instead of
rephrasing it. Its substantive content will be a symptom map plus three causal
facts: capability body versus metadata, repair trigger versus delivered feedback,
and gate writer versus route consumer. This follows the selected v1 method and
limits drift risk.

Alternative considered: a complete branch-by-branch workflow narrative. Rejected
because it would duplicate implementation detail without improving the reader's
first modification decision.

### Treat repair feedback omission as an implemented limitation

`build_real` catches `ValueError` and calls
`build_synthesis_repair_prompt(result.summary, evidence)`. The validation exception
is not an argument to the builder. The projection will state this exactly and point
to the existing repair test, which proves the bounded second request but does not
claim the code reaches the model. Any change to feedback delivery belongs in an
owning behavior change with a red-green test.

### Use the fixed reader task as acceptance evidence

The reader task asks where to change behavior when a gaps-only candidate fails
`synthesis_findings_required` and repair repeats it. Passing requires identifying
the first control-flow owner, the repair prompt owner, the narrow proof seam, and
surfaces that must not be changed first. This is a focused manual review of the
projection; existing deterministic tests retain all runtime verification.

## Risks / Trade-offs

- [Source references drift] -> Cite exact paths and symbols, review each citation
  against source/spec/test before archive, and keep the interface deliberately
  small.
- [Reader mistakes repair triggering for feedback delivery] -> State the omission
  as a current implementation limitation and identify the required behavior-change
  boundary.
- [Pilot becomes an accidental template] -> The requirement specifies outcomes for
  navigation and authority, not fixed headings, tables, or control-flow wording.
- [Projection is mistaken for runtime configuration] -> Put the non-runtime
  boundary at the top of the file and avoid importing, registering, or rendering it.
