# Wave2 Pilot Source Worksheet

> Status: completed source notes, 2026-07-29
>
> This is pre-change evidence for `add-wave2-reader-interface`. It is not a
> runtime authority or a second behavior specification.

## Cognitive Job

Wave2 asks an LLM to synthesize accepted evidence into structured findings,
relations, and gaps. The model proposes a candidate only; it does not admit
evidence, write the synthesis artifact, set the graph route, or schedule later
work.

Sources: `wave2_synthesis/prompts.py::build_synthesis_prompt`,
`wave2_synthesis/node.py::build_real`, and `wave2-synthesis-node` WSN-001 to
WSN-005.

## Deterministic Owners

| Decision | Current owner | Lowest responsible proof |
| --- | --- | --- |
| Parse, semantic admission, one bounded repair, artifact write, and typed Wave2 preview | `graph/nodes/wave2_synthesis/node.py::build_real` and `::_validate_synthesis_semantics` | `tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_repairs_gaps_only_output_when_accepted_evidence_exists` |
| Searchable-gap control update and gate outcome | `graph/nodes/gate_adapter.py::evaluate_gate_for_node` and the Wave2 gate definition | `tests/graph/test_gate_integration.py` Wave2 gate cases |
| Executable target for the gate outcome | `graph/builder.py::_route` and the conditional edges registered for `wave2_synthesis` | `tests/graph/test_topology_and_implementation.py::test_wave2_topology_includes_bounded_exhausted_terminal` |

## Reader-Facing Cross-Module Facts

1. The local capability Markdown body is part of the rendered system policy;
   capability identity and tool posture are deterministic binding/enforcement
   facts, not automatically model-visible prompt text. Sources:
   `agents/phase_prompt.py::render_phase_agent_prompt`,
   `runtime/node_agent_bridge.py::RuntimeNodeAgentBridge.run_agent`, and
   `tests/unit/test_phase_prompt.py::test_renderer_composes_a_declared_local_capability_after_base_policy`.
2. `build_real` catches `ValueError` from parsing or semantic admission and
   calls `build_synthesis_repair_prompt(result.summary, evidence)`. The
   builder accepts only draft and evidence, so the original validation code
   (for example `synthesis_findings_required`) is not delivered to the repair
   model. This is an implemented limitation, not a behavior claim to repair in
   this documentation change. The closest proof is
   `tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_repairs_gaps_only_output_when_accepted_evidence_exists`;
   it proves the second request, not feedback delivery.
3. The node publishes only a typed Wave2 gate preview. The wrapper invokes the
   gate, and the graph builder consumes its route through conditional edges;
   the model does not own routing. Sources:
   `graph/nodes/gate_adapter.py::evaluate_gate_for_node` and
   `graph/builder.py::_node_wrapper` / conditional-edge registration.

## Fixed Reader Task

Symptom: an initial candidate fails `synthesis_findings_required`, and the
repair repeats the same mistake.

Given only the eventual package-local `workflow.md`, a reader must identify
`wave2_synthesis/node.py::build_real` as the first control-flow owner,
`wave2_synthesis/prompts.py::build_synthesis_repair_prompt` as the repair
request owner, and
`tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_repairs_gaps_only_output_when_accepted_evidence_exists`
as the narrow proof seam. The reader must also state that repair triggering
does not mean the validation code reached the model, and must not start by
changing the parser, gate, or graph wiring.
