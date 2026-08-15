## Why

OpenSpec's Change Guidance and authoring context currently mix reusable change
discipline with facts that are specific to the Deep Research product. A reader who
wants to understand what makes this product a research workflow has no single small
entry point, while a reader who needs a generic governance rule must traverse product
wording that does not apply to every DeerFlow/LangGraph agent workflow.

## What Changes

- Add `openspec/product/deep-research.md` as the one concise, non-authoritative
  product-context route for the properties that distinguish Deep Research from other
  DeerFlow/LangGraph agent workflows.
- Simplify OpenSpec, Change Guidance, and governance navigation so generic process
  rules remain at their current owners and link to the product route only when
  Deep-Research-specific context is needed.
- Preserve `openspec/change-guidance/node-edit-map.md` as the exact LLM-node
  authoring gate, and preserve `deep_research_harness/CONTEXT.md`, approved specs,
  code, typed contracts, and tests as their existing authorities.
- Add deterministic navigation and non-authority guards for the product document,
  without adding a `platform/` directory or moving machine-readable governance data.

## Change Focus

- **Primary module / causal owner:** `deep-research-agent-charter` -- it owns contributor entry maps, their authority boundaries, and the deterministic guidance checker.
- **Seam classification:** wiring -- this changes how OpenSpec routes readers to existing product context; it does not change product behavior, model cognition, or deterministic control.
- **Question:** How can `openspec/` expose one easily referenced Deep Research product-context document while keeping generic Change Guidance/governance concise and preserving every existing fact authority?
- **Necessary adjacent/external contracts:** `project-structure` -- which newly required OpenSpec documentation paths must remain structurally registered and checked?; `deerflow`: none -- no upstream interface, source, or behavior changes.
- **Evidence seam:** Change Guidance governance fixtures/checker, architecture governance, strict OpenSpec validation, and focused navigation/non-authority tests.
- **Not in scope:** a `platform/` directory; changes to DeerFlow, LangGraph, runtime behavior, prompts, node roles, routes, state, provider/tool posture, requirement registry semantics, project-structure data ownership, or product fact authorities; a duplicate glossary, authoring handbook, runtime Markdown configuration, or generated documentation dump.
- **Triggered review policies:** local-context, agent-information-map, change-admission

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deep-research-agent-charter`: Separate the Deep Research product-context route
  from generic OpenSpec guidance while preserving bounded entry documents and their
  authority limits.
- `project-structure`: Register the product-context directory and its canonical entry
  alongside the existing OpenSpec navigation and Change Guidance structural contract.

## Impact

- Affected OpenSpec routes: `openspec/README.md`, `openspec/config.yaml`,
  `openspec/change-guidance/`, and `openspec/governance/README.md` only where their
  concise navigation must distinguish generic rules from product context.
- New checked documentation surface: `openspec/product/deep-research.md`, registered
  structurally and guarded as a routing/projection document rather than an authority.
- Affected deterministic evidence: Change Guidance and architecture governance
  checkers/fixtures that own entry-map shape and required-path validation.
- `DRC-014` is pending registration: the first apply mutation restores the
  project-wide requirement checker before any full verification is expected to pass.
- No public API, persisted data, runtime behavior, external dependency, or DeerFlow
  gitlink change.
