## Why

Wave2 already binds two runtime-loaded local capability resources, but their short
policy bodies do not yet own the synthesis and repair methods: `prompts.py` still
duplicates the decision branches, evidence-grounding rules, uncertainty handling,
and repair instructions. This leaves the model-visible cognitive program split
between dynamic Python objectives and static resources, despite the existing Wave2
contract requiring bounded accepted-evidence synthesis.

The restored deterministic gate makes the next progressive slice admissible. This
change makes the two existing Wave2 methods independently reviewable and testable
without widening into targeted evidence, readiness, or graph control.

## What Changes

- Make the two existing Wave2 capability Markdown resources the sole runtime source
  of cognitive method for initial accepted-evidence synthesis and its one zero-tool
  structured repair.
- Reduce Python request objectives to trusted assignment facts, the closed output
  contract, bounded validation category, and explicitly delimited untrusted draft or
  accepted-evidence data; preserve the existing parser, semantic validator,
  materializer, gate preview, gate, and route owners.
- Add branch-level deterministic renderer, prompt, real-node/bridge, repair, and
  evidence-corpus coverage that observes the production resource handoff and the
  unchanged bounded outcome paths.
- Extend the typed evaluation contract and control loader with one closed Wave2-only
  case family, then add versioned evidence only for the two Wave2 branches; live
  quality assessment remains credentialed and supplemental.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave2_synthesis/`; it constructs the two model requests and owns the bounded initial-candidate-to-one-repair handoff.
- **Question:** Can the existing initial synthesis and one structured repair make their bounded evidence-grounding, uncertainty, self-check, and completion methods runtime-loaded Markdown policy, while deterministic owners continue to admit candidates, persist artifacts, derive searchable-gap projections, and select routes?
- **Necessary adjacent/external contracts:** `domain/synthesis.py` and `wave2_synthesis/node.py::_validate_synthesis_semantics` answer the typed candidate and non-bypassable admission question; `agents/capabilities.py` and `agents/phase_prompt.py` answer whether the exact declared resource reaches the renderer; `runtime/research.py::_wave2_synthesis_node_agent_policy` answers zero-tool runtime enforcement; `materializer.py`, `domain.synthesis.build_wave2_gate_preview`, and the Wave2 gate answer artifact, control-fact, and route ownership; `domain/evaluation.py` owns the closed typed evaluation fixture and its runtime-control identity while `runtime/evaluation/controls.py` owns its contained registry/rubric validation, neither of which may create live eligibility or graph authority; `tests/graph/test_wave2_synthesis_real.py`, the node-agent capability matrix, and the Wave2 rows of the evidence-judgment corpus answer the smallest deterministic and bounded-quality seams.
- **Evidence seam:** exact production policy rendering plus scripted real Wave2 node/bridge tests for accepted-evidence-only admission and one repair, with Wave2-only corpus cases for a normal backed finding, a backed finding plus an honest uncertainty gap, unsupported or authority-injection containment, malformed output, and invalid repair. The corpus records request/repair/admission handoffs and invalid-candidate non-publication only; it does not treat a successful internal materializer call, preview, or gate outcome as evaluation proof. No provider or web call is needed for deterministic proof.
- **Not in scope:** `targeted_evidence`, readiness, HITL2, final delivery, graph topology, gate budgets/routes, `SynthesisResult` schema, accepted-evidence selection, materializer output path, Bundle lifecycle, public APIs, live provider execution, `backend/`, and `frontend/`.
- **Triggered review policies:** node-agent-workflow-integrity, workflow-outcome-review, control-placement

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Initial Wave2 synthesis | node-agent | What supported findings, relations, and honest gaps can be proposed from exactly the accepted evidence? | Trusted topic/accepted-evidence assignment and output contract; evidence remains untrusted data | Forbidden; `_wave2_synthesis_node_agent_policy` and runtime bridge enforce it | `SynthesisResult`; parser plus `_validate_synthesis_semantics` admit it | Wave2 node may invoke one closed zero-tool repair | Renderer projection and scripted real-node accepted-evidence test |
| Wave2 synthesis repair | node-agent | Can one invalid draft be reformatted or narrowed to an evidence-grounded candidate under the same assignment? | Same accepted evidence, closed validation category, and untrusted draft only | Forbidden; same dedicated runtime policy | `SynthesisResult`; same parser/validator own admission | One repair only; malformed/failed repair follows the existing non-publication or terminal-failure path | Scripted malformed-output and repair-bound tests |
| Materializer, preview, and gate | no-agent | Deterministic persistence, searchable-gap projection, and route selection are not cognitive roles | Validated synthesis result only | No model/tool posture | Materializer, preview builder, and Wave2 gate remain direct owners | Existing gate budget and typed terminal outcome | Materialization and gate integration tests |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Initial candidate is malformed, gaps-only, or has unassigned support | Parser and Wave2 semantic validator | Wave2 node supplies one closed validation category to one zero-tool repair | No artifact or gate preview until a valid candidate exists | Existing bounded repair, then normal admission only on success | Real-node malformed-candidate/repair test |
| Repair invocation or result cannot produce an admitted candidate | Invocation normalizer and parser/validator | No second repair; existing node failure handling remains bounded | Existing non-publication or typed blocked failure path | Surface the deterministic outcome; do not route from candidate prose | Scripted failed-repair regression |
| Provider/configuration/cancellation failure | Invocation normalizer and `_exhausted_update` | No model-side retry beyond existing phase policy | Typed Wave2 terminal incident when terminally blocked | Existing lifecycle result and route only | Direct invocation-failure test |

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Evidence-grounded findings, relations, and gaps | Wave2 proposes one `SynthesisResult` candidate | Parser and `_validate_synthesis_semantics` determine schema validity and accepted backing refs | non-bypassable | No unsupported reference can materialize or reach a preview | Reuses current parser/semantic boundary; avoids model admission | Real-node accepted-evidence and forged-reference tests |
| One repair opportunity | Initial validation may request a bounded candidate correction | Wave2 node derives a compact closed category and limits the call count | bounded-repair | One zero-tool repair only; no new evidence or lifecycle authority | Reuses existing repair branch; avoids generic retry controller | Repair composition and malformed-repair tests |
| Searchable-gap control fact | Candidate may propose gaps but cannot select a route | Materializer/preview builder and Wave2 gate derive and consume the typed projection | advisory | Candidate prose cannot publish a gap projection or route targeted work | Reuses current preview/gate handoff; avoids a capability-owned route | Preview/gate integration test |

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `wave2-synthesis-node`: Specify that Wave2's initial and repair cognitive methods are runtime-loaded local policy, with deterministic admission and outcome owners retained.
- `evaluation-hardening`: Specify branch-level Wave2 evidence for method injection, bounded repair, accepted-evidence grounding, and supplemental live-quality evaluation.

## Impact

Changes are confined to `deep_research_harness/` Wave2 capability resources, prompt
builders, the parallel typed Wave2 evaluation fixture/control-loader branch, direct
tests, and their versioned evidence assets, plus the two owning OpenSpec deltas. No
upstream DeerFlow module, public interface, persistent Bundle schema, runtime route,
generic evaluation-runner abstraction, or selected-live eligibility changes.
