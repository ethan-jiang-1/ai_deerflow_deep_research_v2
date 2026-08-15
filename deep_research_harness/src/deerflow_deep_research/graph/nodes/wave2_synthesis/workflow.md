# wave2_synthesis — Synthesize accepted evidence into findings and research gaps

> Reader interface only. This file is not a runtime resource or configuration.
> Code, typed contracts, approved specifications, and tests remain the authority.
> Participation mode: bounded cognitive program
> Commitment state: current accepted
> Current operating mechanism: runtime-loaded accepted-evidence method and zero-tool structured-repair loop
> Primary cognitive/control program surface: findings, relations, and gaps candidate
> Deterministic authority boundary: semantic admission, gate preview, gate, and builder own publication and route
> Current model-branch evidence: runtime-loaded method, bounded invocation data, zero-tool bridge, and deterministic handoff only

## Node Identity

The model proposes structured synthesis; it does not accept evidence, publish an
artifact, or choose an executable route.

## LLM-Node Authoring Route

For a model-bearing behavior symptom, read these local owners in order before changing
semantic admission, a gate, or graph routing.

1. **Capability and contract:** [`capabilities.py`](capabilities.py) and [`contracts.py`](contracts.py) define the accepted-evidence synthesis and repair responsibility.
2. **Prompt and context:** [`prompts.py`](prompts.py) projects trusted assignment/output facts and delimited accepted evidence or draft context.
3. **Feedback and repair:** [`node.py`](node.py) turns closed parser/semantic feedback into the bounded zero-tool repair request.
4. **Proof and evaluation:** [`test_wave2_synthesis_real.py`](../../../../../tests/graph/test_wave2_synthesis_real.py) and the [cognitive-program evidence board](../../../../../tests/assets/node_agent_capabilities.py) retain synthesis/repair proof and the separate quality limitation.
5. **Deterministic handoff:** [`node.py`](node.py) and [`materializer.py`](materializer.py) validate and materialize candidates before the preview, gate, and builder determine publication or route.

## From Symptoms

| Symptom | First owner | Proof seam |
| --- | --- | --- |
| Wrong model role or output request | `prompts.py` and capability body | `tests/graph/test_wave2_synthesis_real.py` |
| Candidate backing refs or findings are invalid | `node.py::_validate_synthesis_semantics` | `tests/graph/test_wave2_synthesis_real.py` |
| Route outcome is wrong | gate adapter and `graph/builder.py` | `tests/graph/test_gate_integration.py` |

## Three Cross-Module Facts

1. Capability body is model-visible reusable method; metadata is not.
2. Python passes only trusted assignment/output/category facts and delimited untrusted
   evidence or draft; those data cannot grant instruction authority.
3. The runtime bridge, rather than capability prose, enforces the zero-tool posture.
4. Parser and semantic admission decide whether a candidate can reach materialization;
   the preview, gate, and builder retain projection and route authority.
5. The deterministic Wave2 corpus records resource, prompt, grounding, repair, and
   invalid-candidate non-publication handoffs only. It is not selected-live or provider-quality evidence.

## Route Facts

The gate produces `evidence_needed`, `pass`, or `exhausted`; their executable
consumers are the graph's registered conditional edges.

## Evaluation and Verification Order

Start at the named prompt/admission/gate proof. Use a live evaluation only as
supplemental evidence for a quality claim.
