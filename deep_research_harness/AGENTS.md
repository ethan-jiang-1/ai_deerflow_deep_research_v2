# Deep Research Coding Guide

This file is the code-change information map for `deep_research_harness/`. Use it to decide what to
read next; it is not a product handbook, a runtime-status report, or a full path
inventory. `deerflow/` is the upstream gitlink leveraged by this downstream product.
Do not modify or source-browse it for Deep Research work unless a separately approved
change explicitly owns that boundary.

<!-- BEGIN: DEEP-RESEARCH-FOCUS-GATE -->
## Deep Research Focus Gate

Start at the [Agent Charter](../openspec/agent-charter/README.md), then
select one primary module or causal owner. Read that module's active capability
spec/delta, closest implementation, and lowest responsible test seam before widening
scope. Root `AGENTS.md` and `CLAUDE.md` remain upstream constraints; this guide does
not modify or override them.

Before opening an adjacent module or DeerFlow source, name the contract and the
interface, authority, compatibility, or observed-failure question it must answer.
A possible future use is not enough to expand scope.
If local evidence does not identify an owner, clarify the proposal's `## Change Focus`
card instead of browsing host code or sibling changes for orientation.
Record canonical comma-separated `Triggered review policies` on that card, then add
only the conditional review record required by the selected policy route.

For an LLM-Bearing Node behavior symptom, classify the seam first: capability Markdown,
prompt builder, and feedback are the first modification seam; a parser, gate, route, or
bridge edit is a guardrail, not a substitute. Declare `Seam classification` on the Focus
Card and follow the
[local-context policy](../openspec/policies/local-context.md)
seam rule before a deterministic edit for a node symptom. For the one-page terminology
map that routes each term to its first edit, see the
[concept map](../openspec/agent-charter/concepts.md).

| Central question | Primary owner to inspect first |
| --- | --- |
| Typed meaning, invariant, or pure data contract | `domain/` |
| Deterministic validation, gate, or retry policy | `engine/` |
| Bounded model role, prompt, middleware, or structured result | `agents/` |
| Phase composition, routing, or capability injection | `graph/` |
| DeerFlow binding, trusted context, I/O, persistence, or lifecycle adapter | `runtime/` |
| Presentation-only command or documentation | Its adapter/doc and the named owning result contract |
<!-- END: DEEP-RESEARCH-FOCUS-GATE -->

## Information Map

| Need | Read this first | Do not load by default |
| --- | --- | --- |
| Product use, setup, demo, or operator journey | [`README.md`](README.md) reading map | Its entire operational reference for an ordinary code edit |
| Durable cross-capability design rule | [Agent Charter](../openspec/agent-charter/README.md) | Every policy in the library; choose only the triggered one |
| Behavior to change | Owning OpenSpec main spec and active delta | Historical changes or broad roadmap material |
| Exact paths, layer grammar, and import rules | [`project-structure.toml`](../openspec/governance/project-structure.toml) and its policy | A copied path inventory in this guide |
| OpenSpec authoring context | [`openspec/config.yaml`](../openspec/config.yaml) | Full DeerFlow/runtime reference material |
| Test-evidence strategy | [`test-evidence-policy.md`](../openspec/governance/test-evidence-policy.md) | Test catalogs or README detail before a change needs them |
| Commands and targets | [`Makefile`](Makefile) | A duplicate command catalog here |

## Boundaries

- Keep current facts in their owning code, typed contract, test, checkpoint, ledger,
  or content authority. A guide, summary, or diagnostic is not a second authority.
- Keep observable required behavior in its owning OpenSpec capability spec/delta.
- Do not add nested `AGENTS.md` files to repeat this routing. Add a focused charter
  policy only for a recurring, cross-capability rule with a clear trigger.
- `deep_research_harness/CLAUDE.md` imports this guide for Claude Code. Do not add a second local
  instruction set there.

## Verification

Run the narrowest relevant test first. The complete deterministic gate is
`cd deep_research_harness && UV_OFFLINE=1 make verify`; inspect `Makefile` for focused targets.

## Structural Authority

The active `project-structure` spec owns structural requirements. Exact enumerable
structure lives in `openspec/governance/project-structure.toml`; do not edit the
generated block below by hand. Update the owning change and registry, then render it
with the listed architecture checker.

<!-- BEGIN GENERATED: PROJECT-STRUCTURE -->
## Canonical Structure Locator

Exact inventory: `openspec/governance/project-structure.toml`

- Source root: `deep_research_harness/src/deerflow_deep_research/`
- Fixture source root: `deep_research_harness/src_fake/deerflow_deep_research_fixtures/`
- Test root: `deep_research_harness/tests/`
- Ownership layers: `runtime`, `domain`, `engine`, `agents`, `graph`
- Node grammar: `deep_research_harness/src/deerflow_deep_research/graph/nodes/` packages export `NODE_SPEC`; see the registry for files
- Validate: `python3 openspec/governance/check_project_architecture.py`
<!-- END GENERATED: PROJECT-STRUCTURE -->
