# Deep Research Agent Charter

> role: local product constitution for Deep Research design and change admission
> scope: `deep_research_harness/` and its OpenSpec governance; root DeerFlow guidance remains an upstream constraint
> authority: guidance only; current facts and behavior remain with their owning contracts
> @impl DRC-001
> @impl DRC-005
> @impl DRC-010

## Product Boundary

Deep Research is the downstream product owned by `deep_research_harness/`. DeerFlow is its host
runtime. The root repository guides, `backend/`, and `frontend/` establish upstream
facts and boundaries; they are not the default place to design a local Deep Research
change. This charter neither edits nor overrides root `AGENTS.md` or `CLAUDE.md`.

## Principles

### 1. Start From The Primary Module

Every change starts by naming the smallest module that owns the semantic decision.
Read that module's specification, implementation, and evidence seam before expanding
context. A cross-layer patch still has one causal owner; adapters and neighboring
layers are explicit contracts, not an invitation to scan the whole repository. A
possible future use is not enough to expand scope: name the contract and the decision
it must answer first. If the local evidence still cannot identify an owner, clarify
the Focus Card instead of widening into host code for general orientation.

### 2. Facts Have An Owner

The owner of control state, accepted evidence, content, permission, or a typed result
remains authoritative. A summary, diagnostic, UI view, model output, cache, or
Markdown file may explain an owned fact but does not become a second way to decide it.
When an owner is unclear, stop and locate the owning contract before adding a record.

### 3. Participants Need Actionable, Shared Truth

People need to understand what happened, why it matters, and the nearest legal next
action. AI consumers need stable bounded facts rather than a prose-parsing task. When
both consume an outcome, their projections derive from the same typed source and keep
the same safe disclosure boundary.

### 4. Recovery Is Explicit And Bounded

Retries and fallbacks belong to the phase or contract that owns the operation. They
must state their closed trigger, bound, terminal disposition, and legal next action.
Do not hide an outage behind a silent retry, turn a presentation into a controller, or
claim resume/repair that the lifecycle contract does not provide.

### 5. Evidence Matches The Decision

Use the smallest deterministic test or checker that can prove the changed behavior.
Expand to a scripted workflow, live dependency, or full pipeline only when the claim
requires it. Documentation is a navigation aid, not proof that a control path works.

### 6. Principles Evolve Through The Right Layer

Keep durable project posture here. Put repeatable, triggered design rules in a focused
policy. Put observable behavior in an owning specification. Put operational steps in
a scoped runbook. This separation keeps the charter useful without turning it into a
parallel architecture or runtime protocol.

### 7. Cognition Proposes; Deterministic Owners Decide

Cognition proposes; deterministic owners validate, admit, and route. A human judgment
is a typed input to its owning interaction contract. Neither review prose, a model
candidate, nor a presentation can bypass an invariant or create a lifecycle effect.

### 8. Operation Guidance Is Advisory

For a proposal that selects `control-placement`, the authoring route keeps plan-review
and archive-closeout-review work in ordinary `tasks.md` records. OpenSpec operation
guidance is general advisory text, so the current agent first confirms the selected
proposal declares that policy. Guidance can route attention and prompt an actionable
finding into an ordinary task; it cannot run commands, write or complete a task,
evaluate semantic quality, or decide a native apply/archive transition.

### 9. Cognitive Programs Are The First Modification Seam

An LLM-Bearing Node is a two-part program: a Node Cognitive Control Program
(capability Markdown, prompt builder, model-visible context, structured feedback)
directs model behavior, while a Deterministic Control Boundary admits only legal
candidates, state, and routes. When a node's behavior is wrong, the first
modification seam is the cognitive control program; the deterministic shell is the
guardrail that proves it, not a substitute repair site. Editing a parser, gate,
route, or bridge for a node-behavior symptom requires a seam classification that
shows the cognitive program was already the adjusted or rejected-first seam.
Presence or absence of a direct `run_agent` branch is current-mechanism evidence,
never a node's product identity.

## Non-Authority Boundary

This charter does not grant a mutation right, create a waiver, define a provider
response, or make a retained record authoritative. A conflict is resolved by the
owning accepted specification, active delta, typed contract, or current runtime
authority. Changing those facts requires the normal governed change path.
