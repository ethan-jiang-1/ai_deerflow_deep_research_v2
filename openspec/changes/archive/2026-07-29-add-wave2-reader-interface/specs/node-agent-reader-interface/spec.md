> req: NRI-001, NRI-002

## ADDED Requirements

### Requirement: Wave2 provides a node-local, non-runtime reader interface

The Wave2 synthesis node package SHALL colocate one `workflow.md` reader
projection. The projection SHALL state that code, typed contracts, approved specs,
and tests remain the authority, and SHALL not be loaded, rendered, or interpreted
by the runtime. It SHALL identify Wave2's bounded cognitive job and distinguish it
from deterministic candidate admission, artifact materialization, gate evaluation,
and executable route selection. It SHALL direct readers to the current owning
source/specification/test surfaces rather than reproducing `build_real` as a
second line-by-line workflow.

#### Scenario: Reader opens the package-local projection
- **WHEN** a maintainer begins a Wave2 behavior investigation from the node package
- **THEN** the maintainer can identify the model's bounded job, the deterministic
  owners, and the authoritative source/specification/test surfaces without treating
  `workflow.md` as runtime configuration or a second behavior authority

### Requirement: Wave2 reader interface routes consequential symptoms to owners

The Wave2 reader projection SHALL provide symptom-driven navigation to exact source
owners and narrow deterministic proof seams for model-output shape, candidate
admission, repair behavior, and gate-route outcomes. It SHALL distinguish the
capability Markdown body that enters the rendered system policy from capability
metadata and runtime tool enforcement. For the symptom where a candidate fails
`synthesis_findings_required` and repair repeats the error, it SHALL identify
`node.py::build_real`, `prompts.py::build_synthesis_repair_prompt`, and the narrow
Wave2 repair test, and SHALL state that the current validation code is not passed to
the repair builder. It SHALL identify the gate/wrapper as route writer and the graph
builder as executable route consumer without assigning route authority to the model.

#### Scenario: Reader investigates repeated gaps-only repair
- **WHEN** a reader receives the fixed gaps-only repair symptom and only the Wave2
  `workflow.md`
- **THEN** the reader identifies the first modification owner, repair-request
  owner, narrow proof seam, and current feedback-delivery limitation without first
  changing the parser, gate, or graph wiring

#### Scenario: Reader investigates a route outcome
- **WHEN** a valid Wave2 result reaches an unexpected `evidence_needed`, `pass`, or
  `exhausted` outcome
- **THEN** the reader can distinguish the typed preview producer, gate writer, and
  graph-builder consumer and open the corresponding deterministic tests
