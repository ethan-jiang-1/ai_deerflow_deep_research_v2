## Context

Deep Research already separates graph composition, bounded runtime invocation, and
node-local result handling in code, but the contributor governance surface does not
ask a change author to make that separation explicit. The current charter checker
validates a Focus Card and, when selected, a `workflow-outcome-review` failure table.
It has no equivalent record for whether an affected node is intentionally
deterministic or what a bounded LLM result is allowed to influence.

The pending prompt-catalog change makes the shared prompt text inspectable without
changing its semantics. The capability-remediation plan identifies sixteen current
model branches, but it is not an executable admission rule. This change creates that
admission rule only; it does not make the planned capability contract runtime truth.

## Goals / Non-Goals

**Goals:**

- Add one concise, routed charter policy for node-agent workflow changes.
- Require a mechanically shaped `Node Agent Review` only when a proposal selects
  that policy.
- Preserve the distinction between bounded LLM cognition and deterministic graph,
  parser/evaluator, tool-enforcement, and recovery owners.
- Keep `workflow-outcome-review` as the existing, separate review for failure and
  recovery behavior.
- Record a formal OpenSpec change train so the governance change leads to the
  executable capability migration rather than becoming a terminal documentation
  exercise.

**Non-Goals:**

- Do not add a `NodeAgentCapability` type, Markdown capability resource, registry,
  runtime policy field, prompt-composition behavior, or agent factory.
- Do not modify a model/tool configuration, graph route, retry bound, checkpoint,
  node output parser, user interaction, or provider integration.
- Do not infer whether arbitrary existing or future code "really" contains an LLM
  change from source text or proposal prose.
- Do not modify `backend/` or `frontend/`.

## Decisions

### 1. Add one focused `node-agent-workflow-integrity` policy

The Agent Charter gains one policy with a concrete trigger: a change adds, removes,
or materially changes a node's LLM-bearing cognitive role, node-local capability
policy, tool posture, output-admission boundary, repair semantics, or
model/non-model classification.

The policy explains four owners: deterministic graph/node handler, bounded Node
Agent, runtime bridge, and parser/evaluator/materializer. It directs authors to
name the handoff rather than to move lifecycle authority into a prompt. It states
that policy prose is guidance only and that concrete behavior belongs in the owning
capability delta.

Alternative considered: create a full parallel agentic-workflow handbook with
separate queue, worker, and execution-model policies. Rejected because existing
charter policies already cover focus, authority, recovery, and information maps;
the current recurring gap is one specific node-agent admission question.

### 2. Make policy selection require a compact Node Agent Review table

When `Triggered charter policies` includes `node-agent-workflow-integrity`, the
proposal must contain exactly one `## Node Agent Review` table with these columns:

```text
Surface | Classification | Bounded cognitive question or no-agent rationale |
Input authority boundary | Tool posture and runtime enforcer |
Candidate result and deterministic admission owner | Failure owner and bound |
Deterministic evidence seam
```

`Classification` is `node-agent` or `no-agent`. A row for an intentionally
deterministic surface is therefore a first-class decision, not an omission. A
node-agent row identifies what the LLM may do and which deterministic owner accepts
or rejects its candidate result; it does not claim that a prompt grants that owner
permission.

The table deliberately records a bounded question instead of a final prompt or a
future capability ID. The later capability migration owns executable resource IDs
and request contracts. This keeps the governance rule useful before and after that
migration without creating duplicate prompt authority.

Alternative considered: require the review table on every change. Rejected because
ordinary documentation, pure deterministic work, and unrelated lifecycle changes
would gain meaningless rows. Selection remains an explicit human design judgment.

### 3. Extend the existing checker rather than create another governance runner

`check_agent_charter.py` already parses Focus Cards, canonical policy names, and the
conditional Workflow Outcome Review. It will gain the policy name, table constants,
authoring-pointer anchors, and a second conditional table validator. The validator
checks exact header, separator, at least one complete row, and valid classifications.
It does not evaluate the truth of a claimed role, inspect source code, parse a
prompt, or authorize a route.

When both `node-agent-workflow-integrity` and `workflow-outcome-review` are
selected, both records are required. The former answers role and authority handoff;
the latter answers the failure/recovery path. Neither replaces the other.

Alternative considered: infer applicability by scanning `run_agent()` or prompt
files. Rejected because a proposal can change an invocation surface before such code
exists, while a source-faithful catalog may touch prompt rendering without changing
role semantics. A static scan would both miss planned behavior and create false
requirements.

### 4. Keep configuration roles separate

The policy and authoring configuration will say that root `config.yaml` and profiles
own operator/provider/sandbox settings, while `openspec/config.yaml` owns concise
authoring guidance. Neither becomes a node-role, prompt, route, or runtime
permission authority. The later capability change will place reviewed cognitive
policy beside its node and keep runtime enforcement in `ExecutionPolicy`.

Alternative considered: establish a generic YAML node-agent policy registry now.
Rejected because it would introduce a mutable second authority before the capability
contract, resource resolution, and validation seam exist.

### 5. Make the OpenSpec sequence explicit

This change modifies only `deep-research-agent-charter` and adds `DRC-008`. It
records `establish-node-agent-capabilities` as the next change that will modify
`node-agent-runtime`, the prompt catalog, and the six current LLM-bearing node
owners. Human-interaction behavior and research-quality evaluation remain separate
follow-up changes after that foundation is accepted.

## Risks / Trade-offs

- [A reviewer selects the wrong policy] -> The checker cannot infer semantics; the
  charter route, Focus Card review, and normal code review retain that judgment.
- [The table becomes ceremony] -> It is conditional, has one row per changed
  surface, and requires concrete handoff, enforcement, and evidence fields rather
  than a generic prompt summary.
- [The policy duplicates recovery review] -> It explicitly delegates failure and
  recovery records to `workflow-outcome-review` when that policy is also triggered.
- [Governance is mistaken for runtime behavior] -> The policy, spec, checker, and
  plan all state the non-authority boundary and name the future capability change.
- [Existing active changes are retroactively widened] -> This change does not alter
  their runtime scope. A subsequent semantic revision to one of their node-agent
  surfaces must select the new policy; source-faithful prompt catalog work that
  preserves semantics does not need a fabricated role record.

## Migration Plan

1. Add `DRC-008` to the requirement registry and this change's charter delta.
2. Add the policy, route, authoring pointer, checker support, focused fixture tests,
   and requirement-evidence registration in one change set.
3. Update the architecture plan with the concrete change train and verify the
   governance command plus strict OpenSpec validation.
4. Open `establish-node-agent-capabilities` only after this change is accepted; that
   change will define runtime behavior and compatibility migration for the sixteen
   current branches.

Rollback removes the policy route and checker branch together. It has no persistent
state, provider, or runtime-data migration.

## Open Questions

None. The review record remains intentionally structural and conditional; exact
capability IDs and prompt/resource contracts belong to the next change.
