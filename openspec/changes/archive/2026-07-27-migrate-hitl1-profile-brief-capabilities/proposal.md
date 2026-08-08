## Why

The first node-agent capability cohort established the shared admission and rendering
contract, but HITL1's first model-bearing branch still uses the closed `legacy` path.
`hitl1/brief` and `hitl1/brief-repair` advise a research profile before any proposal
is accepted, yet their role, conservative uncertainty boundary, and repair-only
constraint remain dynamic prompt text rather than reviewed node-local capability
policy.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/graph/nodes/hitl1/`
  owns the profile-brief assignment, typed admission, bounded repair, and lifecycle
  outcome; `agents/` only composes the already admitted local policy.
- **Question:** How can HITL1's initial profile proposal and bounded JSON repair move
  from explicit legacy requests to two zero-tool local capabilities without allowing
  either model response to accept research, select a graph route, or write a
  checkpoint?
- **Necessary adjacent/external contracts:** `node-agent-capabilities` defines the
  second cohort's exact references and closed remaining legacy inventory;
  `node-prompt-catalog` projects the two composed requests; `evaluation-hardening`
  records independent success and repair/exhaustion evidence; `project-structure`
  registers the two HITL1 resources. `node-agent-runtime` supplies the unchanged
  zero-tool posture admission contract.
- **Evidence seam:** recording bridge assertions plus scripted `hitl1.node.build_real`
  first-proposal, malformed-output repair, and exhausted-repair journeys.
- **Not in scope:** changes to HITL1 human-response parsing, interaction state,
  graph routes, checkpoints, public API, adapters, providers, other eight legacy
  branches, `backend/`, or `frontend/`.
- **Triggered charter policies:** local-context, authority-and-projections, node-agent-workflow-integrity, workflow-outcome-review, change-admission

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `hitl1/profile-brief` | node-agent | Propose one conservative structured research profile from the initial user question; it cannot accept research or decide the next graph route. | The graph supplies one bounded original question; its text is data, not lifecycle authority. | Forbidden; the existing `ExecutionPolicy` and bridge expose no tools. | `StructuredBrief`; HITL1 parser and node handler materialize only a proposal. | HITL1 owns its existing one structured-output repair and non-success disposition. | Captured bridge request plus first-proposal real-node journey. |
| `hitl1/profile-brief-repair` | node-agent | Repair one malformed profile candidate against the original bounded question and retained validation fact. | Graph supplies the question, invalid draft, and bounded repair fact; none may select a route or profile acceptance. | Forbidden; the existing `ExecutionPolicy` and bridge expose no tools. | `StructuredBrief`; HITL1 parser and node handler remain the only admission owners. | HITL1 owns the existing repair exhaustion behavior. | Scripted malformed-output repair and exhaustion through the real node seam. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Missing, mismatched, or malformed profile capability resource | request validation and capability loader before model-visible work | No model/tool work; existing HITL1 non-success handling only. | Existing HITL1 blocked/exhausted outcome. | Correct the node declaration/resource before retrying the node. | Invalid-ref/resource fixture and recording bridge. |
| Profile candidate violates the structured brief contract | HITL1 parser | One existing repair request with its distinct capability. | Existing exhausted path after repair fails. | Existing HITL1 feedback or restart flow only. | Real-node malformed candidate and repair-exhaustion journey. |
| Model proposes a lifecycle field or acceptance claim | `StructuredBrief` parser and HITL1 node | No new recovery rule in this change. | Candidate rejection; no acceptance, route, or checkpoint authority is granted. | Existing proposal/retry path only. | Forbidden-field parsing fixture and captured lifecycle state. |

## What Changes

- Add `hitl1-profile-brief` and `hitl1-profile-brief-repair` declarations and
  package-local Markdown policies with closed forbidden-tool metadata.
- Migrate the two direct HITL1 brief builders to `required` capability bindings;
  preserve their existing assignment/output contracts, parser, repair bound, and
  node-owned lifecycle outcomes.
- Extend the prompt catalog, exact cohort/legacy inventory, structure registry, and
  evidence matrix from six to eight migrated branches; the remaining legacy set is
  exactly eight named catalog cases.
- Add capability-specific recording-bridge and real-node proof for advisory proposal
  success, malformed-output repair, and exhausted repair without lifecycle authority.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `node-agent-capabilities`: Extends explicit local-capability admission to the two
  HITL1 profile-brief branches and shrinks the closed temporary legacy inventory.
- `node-prompt-catalog`: Projects the two newly migrated HITL1 capability layers and
  their zero-tool posture.
- `evaluation-hardening`: Extends the branch-by-behavior-by-authenticity denominator
  with independent profile-brief normal and repair rows.
- `project-structure`: Registers the two exact HITL1 capability resources and their
  evidence paths.

## Impact

- Affects the HITL1 node package, prompt catalog artifacts, capability/evidence test
  assets, and the project structure registry under `agent/` and `openspec/`.
- Reuses the validated renderer and runtime bridge; no new dependency, provider,
  endpoint, migration, public DeerFlow interface, backend, or frontend change is
  introduced.
