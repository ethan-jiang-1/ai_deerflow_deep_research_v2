# Local Context Policy

> role: focus selection for Deep Research changes
> trigger: beginning a change, choosing a code-reading scope, or explaining a cross-layer patch
> authority: guidance only; module ownership and behavior remain in the owning spec and code

## Rule

Use one primary module or causal owner as the unit of attention. The primary owner is
the module that owns the changed semantic decision, not merely the first file opened
or the presentation adapter that displays it.

| Central question | Start with |
|---|---|
| Typed meaning, invariant, or pure data contract | `domain/` |
| Deterministic rule, validation, gate, or retry policy | `engine/` |
| Bounded model role, prompt, middleware, or structured result | `agents/` |
| Phase composition, routing, or capability injection | `graph/` |
| DeerFlow binding, trusted context, I/O, persistence, or lifecycle adapter | `runtime/` |
| Presentation-only behavior | Its adapter plus the named owning result contract |

## Minimum Context

For an ordinary change, read only:

1. the primary module's active capability spec/delta;
2. the closest implementation and its narrowest responsible test seam;
3. each explicitly named adjacent contract; and
4. a DeerFlow public API only if the local change invokes or depends on it.

Expand further only through the Context Expansion Gate below. Do not use "understand
the repository" as a reason to read unrelated host code.

## Bounded Program Context

Program form: `## Program Focus` with at least two registered
`### Workstream Focus: <stable-id>` records is only for a declared, frozen set of
owners. Read the declared budget, order, archive invariant, and recovery rule, then
read each workstream through its own owner, contracts, evidence seam, and selected
policy reviews. The program decision authority approves scope, order, and archive
closure only; it never owns runtime facts, writes, or a workstream's semantic choice.
Apply/archive review compares the approved program scope with actual tasks, diff, and
evidence. A workstream that cannot close remains active for approved repair, rollback,
or plan-level re-scope; it cannot archive independently.

## Context Expansion Gate

Before opening an adjacent module, upstream source, or reference document, name the
contract and the decision it must answer. A possible future use is not enough to
expand scope. The following are valid admission reasons:

1. a named interface, authority, compatibility, or observed-failure question;
2. an import, call, type, or failing local evidence seam that identifies the contract;
   or
3. a public DeerFlow interface that the local change will invoke or whose compatibility
   it changes.

General repository orientation, searching for analogous implementations, and a
potentially useful directory are not admission reasons on their own. Read the admitted
contract only as far as its question requires, then return to the primary module. If
the local spec, implementation, and evidence seam still do not identify an owner,
pause and clarify the Focus Card rather than widening into `backend/`, `frontend/`,
root material, or sibling changes.

## Focus Card

Every active change writes the following compact boundary in its proposal:

```md
## Change Focus

- **Primary module / causal owner:** ...
- **Seam classification:** one of `cognitive-program | human-decision | deterministic-guardrail | wiring`, written bare, plus a short rationale
- **Question:** ...
- **Necessary adjacent/external contracts:** ...
- **Evidence seam:** ...
- **Not in scope:** ...
```

`none` is valid for an adjacent or external contract when none is needed. A
cross-layer change names one causal owner and lists other layers only as interfaces.
For every non-`none` adjacent/external contract, state the contract and the question
it answers; this is an admission record, not a list of sources that might be useful.
If two modules both appear to own the decision, resolve the ownership ambiguity before
implementation instead of silently creating a shared helper or duplicate control path.

## Seam Classification

An LLM-Bearing Node is a two-part program: its cognitive-program seam (capability
Markdown, prompt builder, model-visible context, structured feedback) directs model
behavior, and its Deterministic Control Boundary admits only legal candidates, state,
and routes. A node-behavior symptom — a wrong role or model-visible policy, wrong
context or tool posture, malformed or misaligned candidate or feedback, unexpected
admission, or wrong route or terminal — routes its first inspection through the
cognitive-program seam before any deterministic edit:

| Symptom | First seam |
|---|---|
| Wrong node role or model-visible policy | Capability Markdown, prompt builder, model-visible context, structured feedback |
| Wrong context or tool posture | Context projection and tool window policy |
| Malformed or misaligned candidate or feedback | Candidate schema, parser feedback, repair loop |
| Unexpected admission | Parser, materializer, controller, or ledger boundary |
| Wrong route or terminal | Gate, wrapper, or route seam |

A cognitive-program edit states its cognitive hypothesis and the observable result
or evaluation that will show whether the edit worked. The first-owner rule is specific
to the declared classification:

- **cognitive-program:** start at the local capability, prompt/context, and
  feedback/repair surfaces; state the bounded cognitive responsibility and the evidence
  that could disconfirm the change.
- **deterministic-guardrail:** start at the named typed, parser, materializer, gate, or
  route owner. For a model-bearing behavior symptom, record that the cognitive program
  was considered or rejected first; a deterministic-only change does not fabricate a prompt obligation.
- **human-decision:** start at the semantic subject, typed input boundary, and graph
  authority. Do not infer a model role or prompt from a person making a decision.
- **wiring:** start at the composition, injection, or adapter boundary. Inspect a
  cognitive program only when the wiring change alters model-visible behavior.

Presence or absence of a direct `run_agent` call is current-mechanism evidence, never
a node's product identity; never infer a seam from the first file opened.

Every active proposal declares exactly one closed value on its Focus Card's `Seam
classification` field, written bare (no backticks, no punctuation inside the value),
with a short rationale. The closed values are `cognitive-program`,
`human-decision`, `deterministic-guardrail`, and `wiring`; this policy owns the
canonical values and the substantive cognitive-hypothesis and deterministic-owner
requirements. The Change Guidance checker mechanically enforces presence, closed-value
membership, and a non-empty rationale without judging which classification is
semantically true for a change.

## Boundary

This policy does not make a module authoritative over facts it does not own, and it
does not prohibit necessary dependency inspection. It only makes that expansion
explicit, reviewable, and proportional to the named change.
