# Deep Research LLM-Node Authoring Gate

> role: compact first-read route for an LLM-Bearing Node or direct model branch
> scope: `deep_research_harness/` authoring, review, and OpenSpec admission
> authority: guidance only; never runtime control, permission, state, route, or behavior truth

For a Coding Agent creating, changing, or reviewing an LLM-Bearing Node, use this map
before implementation navigation. The product glossary in
[`CONTEXT.md`](../../deep_research_harness/CONTEXT.md) owns definitions; approved
specifications, code, typed contracts, and tests own behavior and current facts.

## LLM-Node Authoring Route

Read in order. Do not start by changing a parser, gate, route, bridge, or test merely
because it is the first Python file found.

1. **Classify the surface**: record `cognitive-program`,
   `deterministic-guardrail`, `human-decision`, or `wiring` on the Focus Card. A
   behavior symptom reaches the cognitive program first unless its causal owner is
   explicitly rejected; a deterministic-only or human-decision change does not
   fabricate a prompt obligation.
2. **Node Cognitive Control Contract and local capability**: read the local capability
   and owning contract to state the bounded cognitive responsibility, the useful
   candidate, uncertainty/degradation posture, and what the model cannot decide.
3. **Prompt builder and model-visible context**: read the exact builder to distinguish
   trusted assignment and output-contract inputs from delimited untrusted content, and
   to identify the requested method/tool posture and its runtime enforcer.
4. **Structured output, feedback, and repair**: trace candidate shape, feedback source,
   recipient, bounded repair, and the condition that stops repair; feedback is data, not
   authority to widen a task or select a route.
5. **Focused proof and applicable cognitive evaluation**: start with the lowest
   deterministic proof for composition/admission, then inspect the branch's existing
   cognitive-program evidence and any applicable evaluation limitation before asserting
   a model-quality claim.
6. **Deterministic handoff owners**: only after the cognitive route, inspect the parser,
   materializer, ledger, gate, and graph owner that admits a legal candidate and chooses
   the observable effect. A deterministic symptom names that owner and why cognition is
   not causal.

Open the node package's `workflow.md` next. It links the exact local capability,
prompt/context, feedback/repair, proof/evaluation, and deterministic-handoff sources;
it is a reader projection, not runtime configuration or a second specification.

## Non-Model Work

For a deterministic guardrail, human decision, or wiring change with no model-bearing
behavior symptom, start with the actual typed, domain, engine, graph, or adapter owner.
Record why no cognitive program owns the decision. Do not create a capability, prompt,
or repair surface to make the change look model-directed.
