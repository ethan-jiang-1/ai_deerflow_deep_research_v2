# Deep Research Product Context

> role: concise product-context reading map
> authority: navigation only; definitions, requirements, runtime facts, and LLM-node authoring remain with their named owners

## What Is Product-Specific

Deep Research turns a research question into a useful research outcome with evidence,
scope and assumptions, and material uncertainty visible to the person receiving it.
This identifies product orientation only; it does not define a workflow, node, route,
state write, tool permission, recovery action, or current runtime fact.

## Read By Question

| Question | Open | Why it owns the answer |
| --- | --- | --- |
| What do Deep Research terms mean? | [Product glossary](../../deep_research_harness/CONTEXT.md) | It owns terminology. |
| What behavior is approved or pending? | [Approved main specs](../specs/) and any [active delta](../changes/) when one exists | They own required behavior. |
| What does the application do now, and what proves it? | [Code](../../deep_research_harness/src/deerflow_deep_research/), typed contracts, and [tests](../../deep_research_harness/tests/) | Code, typed contracts, and tests own current facts and proof. |
| How is an LLM-Bearing Node authored or reviewed? | [LLM-node authoring gate](../change-guidance/profiles/node-agent/node-agent.md) | It owns the exact cognitive-program-first route. |

## Boundary

Use this page to choose what to read next. For a product detail, follow its named
owner rather than adding a glossary, handbook, runtime Markdown configuration, or
second specification here.
