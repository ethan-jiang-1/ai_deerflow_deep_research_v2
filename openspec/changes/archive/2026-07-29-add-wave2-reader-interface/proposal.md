## Why

Wave2's local code makes its normal control flow readable, but a maintainer still
has to reconstruct several consequential cross-module facts before addressing a
symptom: what the model sees, whether repair receives validation feedback, and who
owns the route after candidate admission. The selected v1 design demonstrates that
a compact, package-local reader projection can direct that work without becoming a
second runtime authority.

## What Changes

- Add a non-runtime, package-local `workflow.md` for the Wave2 synthesis node.
- Define the first `node-agent-reader-interface` requirement around a compact,
  symptom-driven maintenance map and an explicit authority boundary.
- Record the current repair-feedback limitation accurately: triggering repair does
  not mean the validation code is delivered to the repair model.
- Validate the interface with the fixed reader task and existing narrow Wave2,
  gate, runtime-capability, and topology evidence; do not change their behavior.

## Change Focus

- **Primary module / causal owner:**
  `agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/` reader
  projection.
- **Question:** Can a small `workflow.md` let a new maintainer distinguish Wave2
  model candidate work, deterministic admission, gate routing, and repair feedback
  well enough to find the correct first edit and proof seam?
- **Necessary adjacent/external contracts:** `wave2-synthesis-node` answers the
  required synthesis/admission behavior; `node-agent-capabilities` answers
  capability-body and tool-posture authority; `research-graph-lifecycle` answers
  the wrapper and executable-route facts.
- **Evidence seam:** The fixed Wave2 reader task plus existing Wave2 real-node,
  gate, runtime-capability, bridge, and topology tests cited by the projection.
- **Not in scope:** Runtime behavior, gate/route wiring, state schema, prompt
  catalog, capability body, tool posture, test behavior, checker/index/generator
  work, `backend/`, and `frontend/`.
- **Triggered charter policies:** authority-and-projections, change-admission

## Capabilities

### New Capabilities

- `node-agent-reader-interface`: A non-runtime, node-local maintenance projection
  that routes reader symptoms to existing code, specification, and test authority.

### Modified Capabilities

- None. Existing runtime requirements remain unchanged.

## Impact

- Adds `agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/workflow.md`.
- Adds OpenSpec change artifacts and the new capability delta only.
- Does not change APIs, dependencies, runtime behavior, `backend/`, or `frontend/`.
