## Why

The prompt catalog now makes a node-agent request inspectable, but a request still
does not identify a node-local cognitive contract. A reviewer can see prompt text
without being able to verify the bounded job, admitted candidate, tool posture, or
deterministic evidence that belongs to a particular model-bearing branch. The fast
test total also says little about whether those agentic boundaries are exercised.

This change establishes the executable foundation for node-local capabilities, but
only for a representative vertical cohort. The preceding governance and prompt-catalog
changes are archived and their accepted contracts are the implementation baseline;
the cohort still begins by re-confirming that baseline and running its full
deterministic gate rather than treating focused evidence as an acceptance bypass.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/agents/` capability-rendering contract.
- **Question:** How can a bounded node-agent branch select a reviewed local cognitive
  capability while the graph retains routing and admission, the runtime remains the
  only execution/tool enforcer, and the catalog exposes the exact composed request?
- **Necessary adjacent/external contracts:** `node-agent-runtime` answers capability
  reference admission and actual model-visible tool binding; `graph` answers which
  branch builds the trusted assignment and owns parser/evaluator/materializer and
  recovery; `evaluation-hardening` answers branch-by-behavior-by-authenticity
  evidence registration; the accepted `node-prompt-catalog` capability answers the
  review projection. No DeerFlow public interface is changed.
- **Evidence seam:** deterministic declaration/resource/renderer and catalog checks,
  recording bridge bindings, and scripted real-node journeys for each migrated branch
  through its parser or materializer and highest-risk failure/repair boundary.
- **Not in scope:** model-quality or live-research claims; conversion of deterministic
  nodes; new graph routes, checkpoint owners, or human-interaction semantics;
  generic arbitrary system-prompt overrides; broad migration of the remaining ten
  catalog branches; `backend/`; `frontend/`.
- **Triggered charter policies:** local-context, authority-and-projections, node-agent-workflow-integrity, workflow-outcome-review, change-admission

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `hitl1/semantic-intake` | node-agent | Interpret a human reply against the accepted research-profile subject and return a candidate semantic intent; it cannot decide the lifecycle transition. | Graph supplies the validated interaction subject and user reply; reply text is data, not route authority. | Zero tools; `ExecutionPolicy` and runtime bridge expose no tools. | Typed intent candidate; HITL1 parser/evaluator and node handler accept or reject it. | HITL1 owns its existing bounded semantic repair and feedback path. | Captured renderer/bridge input plus scripted semantic-intake success. |
| `hitl1/semantic-intake-repair` | node-agent | Repair one malformed semantic-intake candidate against the same bounded reply/subject. | Graph supplies the validated subject, reply, and bounded repair fact; none is route authority. | Zero tools; `ExecutionPolicy` and runtime bridge expose no tools. | Typed intent candidate; HITL1 parser/evaluator and node handler admit or reject it. | HITL1 owns exhaustion and its existing feedback path. | Scripted malformed-output repair/exhaustion journey. |
| `wave0/worker` | node-agent | Produce a candidate source-intake document from a bounded topic assignment and permitted retrieval alternatives. | Graph supplies the work specification and topic assignment; tool/source output stays untrusted evidence. | At least one call through the closed Wave0 retrieval-name set; `ExecutionPolicy`, middleware, sandbox, and bridge enforce names, paths, call limits, and actual binding. | Typed source candidate; Wave0 parser, source validation, artifact materializer, and ledger controller admit it. | Wave0 owns work-unit failure aggregation; no model route authority. | Recording binding plus scripted worker success and no-permitted-tool failure. |
| `wave0/repair` | node-agent | Reformat one bounded untrusted worker draft and its retained tool observations into the existing source-intake contract. | Graph supplies the bounded draft and untrusted tool observations; neither grants ledger or route authority. | Zero tools; the repair is not a retrieval continuation. | Typed source candidate; Wave0 parser, source validation, artifact materializer, and ledger controller admit it. | Wave0 owns the existing one repair and work-unit failure aggregation. | Scripted malformed candidate repair/failure journey with no model-visible tool. |
| `wave2-synthesis/synthesis` | node-agent | Synthesize only accepted evidence into a candidate finding/gap result without inventing acceptance or graph control. | Graph supplies topic registry and accepted evidence; evidence remains untrusted content. | Zero tools under a Wave2-specific runtime policy, not an inherited HITL1 bridge policy. | Typed synthesis candidate; Wave2 parser/evaluator/materializer accepts findings or gaps. | Wave2 owns its existing one repair and terminal failure boundary. | Captured renderer/bridge input plus scripted accepted-evidence success. |
| `wave2-synthesis/repair` | node-agent | Repair one bounded synthesis draft against the same accepted evidence. | Graph supplies the untrusted draft and accepted evidence; neither grants artifact or route authority. | Zero tools under the same Wave2-specific runtime policy. | Typed synthesis candidate; Wave2 parser/evaluator/materializer accepts or rejects it. | Wave2 owns terminal behavior after its existing repair bound. | Scripted malformed-output repair/terminal journey. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Missing or malformed migrated capability reference/ref | Request validation before node invocation | No node invocation or model call; no fallback capability. | Rejected request/configuration input. | Correct the builder/declaration before retrying the request. | Direct invalid-binding fixtures proving no node/model/tool invocation. |
| Unknown or mismatched migrated capability resource | Capability-resource loader before invocation | Owning node performs no model call and uses its existing failure handling; no fallback capability. | Existing node-owned non-success path. | The node's existing declared failure/blocked route only. | Invalid-resource fixtures and recording bridge proving no model/tool invocation. |
| Requested and runtime-resolved tool posture disagree | Runtime bridge and `ExecutionPolicy` admission boundary | No model call or tool dispatch; no retry is created by this change. | Existing node-owned non-success path. | The node's existing declared failure/blocked route only. | Recording tool-binding fixture for required, forbidden, and unavailable tools. |
| Candidate violates the branch output contract | Branch parser/evaluator/materializer | Existing branch-local repair bound, then its existing failure path. | Existing node-owned terminal or work-unit disposition. | Existing graph route after deterministic rejection. | Scripted malformed candidate and exhausted-repair journey through the real node seam. |

## What Changes

- Add an agents-owned typed `NodeAgentCapability` declaration and a trusted,
  node-local capability-resource loader. The execution interface stays small: a
  `legacy`/`required` capability selector with an exclusive reference
  invariant (`legacy` has no reference; `required` has one valid reference), trusted
  assignment, expected output contract, and numeric execution limits.
  Parser/evaluator/materializer, catalog source, repair owner, and evidence metadata
  remain node-owned governance projections rather than request fields.
- Make the final prompt renderer compose base policy, validated local capability
  policy, graph-provided assignment/output contract, and delimited untrusted data.
  The runtime bridge admits the declared capability and resolves its actual tool
  binding; it does not accept arbitrary full-system-prompt replacement.
- Migrate only the first vertical cohort: `hitl1/semantic-intake`,
  `hitl1/semantic-intake-repair`, `wave0/worker`, `wave0/repair`,
  `wave2-synthesis/synthesis`, and `wave2-synthesis/repair`. Each migrated branch
  carries a stable capability reference, local resource, closed tool posture,
  candidate contract, and deterministic admission owner. Unmigrated branches remain
  explicitly legacy for now and cannot silently inherit a generic capability.
- Extend the deterministic prompt catalog and evidence registry for the migrated
  branches to show capability ID, local source path, four-layer composition, and the
  requested-versus-runtime tool policy. Add a six-case cohort matrix with distinct,
  collected success and highest-risk claims per branch.
- Make missing capability/resource, catalog drift, generic fallback, and tool-posture
  disagreement fail closed before model-visible work. Preserve existing graph routes,
  retry bounds, and lifecycle outcomes.

## Capabilities

### New Capabilities

- `node-agent-capabilities`: Defines the executable node-local capability reference,
  resource, composition boundary, migrated-cohort admission behavior, and branch
  evidence matrix.

### Modified Capabilities

- `node-agent-runtime`: Admits a validated capability reference and binds actual
  tools according to its closed posture without granting graph authority.
- `project-structure`: Registers the node-local capability declaration/resource
  grammar, the three exact node-package locations, and deterministic evidence
  locations.
- `evaluation-hardening`: Records the migrated-cohort branch-by-behavior-by-
  authenticity evidence denominator rather than treating aggregate pytest count as
  node-agent coverage.

## Impact

- Affects `agent/src/deerflow_deep_research/agents/`, `domain/`,
  `runtime/research.py` and the node-agent bridge, the three named graph-node
  packages, the prompt catalog after its owning change is accepted, deterministic
  tests and evidence registries, and the project structure registry.
- Uses the accepted `define-node-agent-workflow-governance` and
  `make-node-prompts-auditable` contracts as its baseline. Implementation re-confirms
  that no active competing delta changes the catalog/runtime surface and records a
  clean protected-path baseline before modifying the cohort.
- Adds no provider dependency, DeerFlow API, checkpoint migration, backend change,
  or frontend change.
