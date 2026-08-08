## Why

The research-start chain now has branch-level capability and behavior evidence, but
the accepted-evidence evaluation loop still cannot show that synthesis stays within
its assigned evidence, targeted retrieval follows an actual gap, or critics and
repairs remain read-only and non-inventive. This is the second, deliberately
separate Stage D change so those decisions can be reviewed without reopening the
planner, Wave0, or Wave1 cohort.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/graph/`; the
  Wave2 synthesis and targeted-evidence node handlers own placement and deterministic
  admission of candidates produced from accepted evidence or a bounded gap.
- **Question:** Can the real evidence-evaluation loop restrict model candidates to
  assigned accepted evidence or one gap-authorized retrieval, preserve read-only
  critic posture, and report incomplete evidence without manufacturing authority?
- **Necessary adjacent/external contracts:** `node-agent-capabilities` defines local
  capability admission and tool posture; `node-prompt-catalog` projects local policy
  for review; `wave2-synthesis-node` and `targeted-evidence-loop` own candidate
  validation, controller, ledger, and phase outcomes; `evaluation-hardening` owns
  collected proof claims. The runtime bridge remains the existing enforcement owner.
- **Evidence seam:** scripted real-node/runtime-bridge cases with fake model/tool
  adapters at synthesis materialization and targeted work-unit/critic admission
  seams, backed by exact catalog and capability checks.
- **Not in scope:** topic planning, Wave0, Wave1, graph topology, public interfaces,
  checkpoint schema, provider-policy changes, live research-quality claims,
  `backend/`, and `frontend/`.
- **Triggered charter policies:** node-agent-workflow-integrity, workflow-outcome-review

## What Changes

- Migrate the four remaining targeted-evidence direct branches from `legacy` to
  declared package-local capabilities with their bounded retrieval or zero-tool
  posture; retain Wave2's existing zero-tool capability bindings.
- Define acceptance evidence for assigned-evidence synthesis, gap-authorized targeted
  retrieval, read-only source/claim criticism, and repairs that cannot add evidence,
  claims, sources, or gaps.
- Extend catalog and central evidence governance with branch-specific claims while
  retaining distinct scripted real-workflow proof for bridge and admission paths.

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Wave2 synthesis / repair | node-agent | What reportable findings or structural repair can be derived only from accepted evidence? | Accepted ledger evidence is trusted assignment; model output is a candidate. | Forbidden; existing runtime bridge enforces a required zero-tool capability. | Existing synthesis parser/materializer owns admission. | Existing node repair/exhaustion owner retains its bound. | Scripted real synthesis node plus fake capabilities. |
| Targeted worker / repair | node-agent | What evidence can one assigned gap justify, or how can malformed bounded output be repaired? | Gap and retained observations are trusted assignment; model/tool material is untrusted. | Worker bounded retrieval; repair forbidden; existing runtime bridge enforces both. | Existing validator/controller/ledger owns admission. | Existing work-unit failure and repair owners retain bounds. | Scripted real worker bridge and ledger submission. |
| Source diagnostic / claim verifier | node-agent | What read-only diagnostic or verification follows from assigned evidence references? | Assigned references are trusted scope; evaluated text remains untrusted. | Forbidden; existing runtime bridge enforces zero-tool posture. | Existing parser/materializer admits only scoped critic output. | Malformed or out-of-scope output propagates from existing dispatch before materialization; this change adds no recovery or route. | Scripted real critic request with fake capabilities. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Invalid synthesis or repair candidate | Existing synthesis parser/materializer | Existing bounded structured repair | Existing non-publication/exhausted outcome | Existing phase handling | Scripted malformed then exhausted synthesis results |
| Missing gap or unavailable targeted retrieval | Existing targeted controller and runtime bridge | No new retry policy; existing worker/controller bound remains | Existing failed or honest incomplete outcome | Existing gate/controller handling | Scripted bridge call count and no-ledger-admission case |
| Critic output beyond assigned references | Existing critic parser/materializer | No recovery in this change; existing dispatch propagates the rejection | Node invocation exits before critic artifact materialization; this change adds no terminal projection | No new action; retain existing graph exception behavior | Scripted assigned-ref violation without tool access |

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `node-agent-capabilities`: migrate the remaining targeted-evidence direct branches
  into a closed local-policy cohort and preserve Wave2's existing binding.
- `node-prompt-catalog`: project the synthesis and targeted-evidence local policies
  and requested/runtime tool distinction.
- `wave2-synthesis-node`: define behavior evidence for assigned-evidence-only
  synthesis and non-inventive repair.
- `targeted-evidence-loop`: define behavior evidence for gap-authorized retrieval,
  read-only critics, and non-inventive repair.
- `evaluation-hardening`: register branch-specific deterministic claims without
  asserting live source truth or research quality.

## Impact

- Expected implementation scope is confined to `agent/src/deerflow_deep_research/graph/nodes/`,
  prompt/capability resources, catalog projection, and focused `agent/tests/` assets.
- Existing runtime bridge, graph topology, typed state, public APIs, `backend/`, and
  `frontend/` remain out of scope.
