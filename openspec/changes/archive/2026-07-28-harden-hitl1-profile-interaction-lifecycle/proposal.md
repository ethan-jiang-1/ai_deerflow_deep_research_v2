## Why

HITL1's profile-brief and semantic-intake capabilities now have local policies, but
their human-facing contract has not been accepted through the complete journeys a
person actually takes: natural confirmation, revision with first-party source and
citation constraints, a proposal question, ambiguity, and model-failure fallback.
Existing focused tests prove individual seams; this change makes the full bounded
lifecycle evidence explicit and repairs only a demonstrated contract gap.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/graph/nodes/hitl1/`
  owns the correlated interaction visit, semantic candidate admission, proposal
  lifecycle, feedback projection, and route; the semantic capability only returns
  an untrusted candidate.
- **Question:** Can a complete checkpointed profile proposal reliably keep the
  human in control across confirmation, a source-constrained revision, a question,
  ambiguity, and semantic-model failure while its deterministic presentation and
  closed fallback avoid schema teaching and the model retains no lifecycle authority?
- **Necessary adjacent/external contracts:** `human-interaction-contract` defines
  bounded candidates, visible controls, and feedback; `hitl1-node` owns the actual
  lifecycle/route contract; `evaluation-hardening` owns the independently collected
  lifecycle evidence claims. Each answers the named contract question only; no
  DeerFlow interface is required.
- **Evidence seam:** scripted `hitl1.node.build_real` multi-visit transcripts with
  fake node-agent capabilities, correlated human responses, recording bridge
  requests, and checkpointed/projection assertions.
- **Not in scope:** migration of the eight remaining legacy branches, new model
  capability resources, changes to graph topology, checkpoint schema, adapters,
  public API, providers, live paid-model evaluation, research-quality calibration,
  `backend/`, or `frontend/`.
- **Triggered charter policies:** authority-and-projections, human-interaction-integrity, node-agent-workflow-integrity, control-and-recovery, workflow-outcome-review, change-admission

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `hitl1/semantic-intake` | node-agent | Classify one raw reply about the current profile as confirmation, full revision, bounded question, or clarification; it cannot accept research or choose a route. | The graph supplies the current checkpointed proposal and original question; the human reply remains untrusted data. | Forbidden; the existing execution policy and runtime bridge expose no tools. | `SemanticCandidate`; HITL1/domain validation admits only a valid candidate and the node owns every state write and route. | HITL1 permits at most three calls per reply, sharing transient retries and one repair; cancellation propagates. | Scripted real-node confirmation, revision, question, ambiguity, and failed-intake transcripts. |
| HITL1 proposal materialization and feedback | no-agent | Deterministic correlated request validation, candidate resolution, proposal versioning, visible control projection, and recovery feedback must not be delegated to a model. | Checkpointed proposal and typed response own the facts; a candidate never becomes route or checkpoint authority. | No model/tool invocation; node/domain contracts enforce the transition. | `resolve_semantic_candidate`, node handler, and profile materializer own admission. | Existing non-terminal feedback after semantic failure preserves a confirmable proposal. | Multi-visit transcript assertions over route, profile state, proposal version, feedback, and visible control. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Ambiguous or underspecified human proposal reply | Validated semantic candidate plus domain resolution | HITL1 reissues one fresh correlated request; this is not a profile-rejection round. | Non-terminal; current proposal and visible control remain intact. | Clarify the intended confirmation, revision, or question against the current proposal. | Ambiguity transcript with unchanged proposal and focused clarification. |
| Semantic output is malformed or fails deterministic validation | Semantic parser and HITL1 node | At most one structured-output repair within the existing three-call cap. | Non-terminal semantic-invalid feedback with the current proposal retained. | Confirm the visible current proposal or submit a clearer reply. | Invalid candidate/repair transcript with the fallback control. |
| Semantic provider failure exhausts its bound | Runtime result/typed problem and HITL1 node | At most two retry-eligible transient retries within the existing three-call cap; no retry for non-transient failure. | Non-terminal semantic-unavailable feedback with the current proposal retained. | Confirm the visible current proposal or retry the reply later. | Three-failure transcript with preserved proposal/control and no profile write. |
| Cancellation while semantic intake is pending | Runtime cancellation | No recovery; cancellation propagates without post-cancellation state work. | Existing cancellation behavior. | Use the existing run lifecycle after cancellation. | Focused cancellation test remains the owner evidence. |

## What Changes

- Add one scripted lifecycle acceptance suite at the real HITL1 node seam. It will
  cover natural confirmation, a full revision carrying first-party-source/citation
  constraints, a bounded proposal question, ambiguity/clarification, and exhausted
  semantic-model fallback.
- Remove the current deterministic `complete JSON profile` instruction and duplicated
  action token from complete-proposal context while retaining the trusted descriptor
  action binding and visible current-proposal control. Assert concise ordinary
  confirmation/revision/question context and closed fallback without schema/JSON or
  hidden-token teaching. Scripted semantic question/clarification candidates prove
  routing and projection only, not live language quality.
- Preserve the current authority split: the semantic capability emits only a
  candidate; deterministic HITL1/domain code alone validates correlation, promotes
  a proposal, publishes a profile, selects a route, and owns recovery.
- Implement the confirmed complete-proposal presentation correction; make any further
  focused implementation correction only when a transcript exposes a failure of the
  existing lifecycle contract.
- Register independent central evidence claims for the lifecycle success and
  highest-risk recovery journeys, without reusing an aggregate or capability-migration
  claim.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `hitl1-node`: Makes the complete semantic proposal-interaction journeys and their
  authoritative lifecycle outcomes explicit at the real node seam.
- `human-interaction-contract`: Requires focused, human-usable feedback and visible
  recovery throughout the accepted lifecycle journeys.
- `evaluation-hardening`: Requires distinct collected evidence for lifecycle
  acceptance and highest-risk semantic-failure recovery.

## Impact

- Affects HITL1 node/domain tests and test-owned evidence assets under `agent/`, plus
  the three scoped OpenSpec delta specs.
- Reuses existing zero-tool semantic capabilities, graph routes, checkpoint fields,
  bridge contracts, and fake-capability test infrastructure.
- Introduces no dependency, persistence migration, provider, public DeerFlow API,
  backend, or frontend change.
