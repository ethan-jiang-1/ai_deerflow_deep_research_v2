## Context

See `proposal.md` for motivation. `openspec/change-guidance/` currently carries both
generic change-admission rules and Deep Research wording, while `openspec/config.yaml`
repeats enough product context to be useful but has no compact product-oriented
destination. The structural registry and Change Guidance checker already own exact
paths and entry-map shape; those owners must be extended rather than bypassed.

## Goals / Non-Goals

**Goals:**

- Give every human and Coding Agent one stable `openspec/product/deep-research.md`
  route for the concerns unique to the Deep Research product.
- Keep generic Change Guidance and governance navigation small, role-specific, and
  easier to reuse across different agent-workflow products.
- Retain one exact LLM-node authoring gate and all current fact/behavior authorities.
- Make the product directory's path, small shape, links, and non-authority boundary
  deterministically reviewable.

**Non-Goals:**

- Establish a `platform/` knowledge layer, documentation generator, second glossary,
  or generic agent-workflow handbook.
- Move runtime facts, specification prose, path enumeration, registry data, prompts,
  node routes, or operational procedures into product context.
- Change the DeerFlow dependency boundary, LangGraph execution, or any product
  behavior.

## Decisions

### One product-context entry, separate from Change Guidance

Create `openspec/product/deep-research.md` as the sole product-context entry. It is a
short reading map: it says what is research-specific and links to the existing product
glossary, capability specifications, node-authoring map, runtime architecture, and
evidence owners. It does not reproduce their details.

Alternative considered: add a `product/` policy under Change Guidance. Rejected
because it would confuse a product orientation with a trigger-bearing admission rule
and make the policy route a second product index.

### Preserve three distinct navigation roles

`openspec/README.md` is the top-level navigation map. `openspec/config.yaml` is the
small default context injected into OpenSpec authoring. `openspec/change-guidance/README.md`
is the policy-selection route. Each gains only a concise product-context link; each
retains its existing role and does not repeat the product explanation. Governance
navigation remains a checker/registry route, not a product reference manual.

Alternative considered: put all Deep Research explanation in `config.yaml`. Rejected
because default context would grow into a handbook and would make ordinary generic
change authoring pay an unnecessary attention cost.

### Product context is a projection, not an authority

The product document labels itself as navigation only. It points to
`deep_research_harness/CONTEXT.md` for terminology, approved main specs/active deltas
for requirements, code/typed contracts/tests for current behavior and evidence, and
`node-edit-map.md` for LLM-node authoring. It never grants runtime permissions or
declares an operational fact.

Alternative considered: consolidate these sources into the product document. Rejected
because copied facts would drift and because Markdown cannot become an alternate
runtime or specification owner.

### Keep the product map smaller than default authoring context

The existing Agent Information Map policy and Change Guidance checker shall treat the
product map as an entry document with a 60-line warning threshold and an 80-line hard
maximum. Its job is to name the research-specific orientation and direct a reader to
the owning glossary, specification, source/evidence, or LLM-node authoring route; it
does not enumerate nodes, copy product terminology, or explain runtime architecture.

Alternative considered: rely on prose review alone. Rejected because the existing
entry-document policy already uses a line budget to reveal attention-cost growth before
a map turns into a handbook.

### Reuse the structural and guidance guards

Extend `project-structure.toml`/architecture governance for the new directory and
document, and extend the Change Guidance checker plus its planted fixtures for the
required product link, one-file directory shape, and non-authority boundary. Do not
add a standalone documentation checker.

Alternative considered: leave `product/` unregistered as optional documentation.
Rejected because an unregistered entry surface can silently disappear or accumulate
competing copies.

## Risks / Trade-offs

| Risk | Mitigation |
| --- | --- |
| Product document grows into a handbook | Keep it a route-only document; enforce its exact structural shape and non-authority anchors; retain existing entry-document budgets |
| Product wording remains scattered through generic entry maps | Move only Deep Research-specific orientation; retain concise pointers and guard them with planted omission fixtures |
| New directory becomes a second policy or glossary root | Keep policies under `change-guidance/policies/`, definitions in `CONTEXT.md`, and reject a second product index or `platform/` tree |
| Structural registration becomes a second prose architecture | Record only the directory/file paths in TOML; keep rationale and routing in the owned Markdown documents |

## Migration Plan

1. As the first apply mutation, register `DRC-014` so project-wide requirement
   governance is restored before verification; add red fixtures for a missing product
   route, duplicate product entry, authority claim, forbidden platform root, and an
   oversized product map.
2. Add the registered `openspec/product/deep-research.md` reading map and concise
   links from the three entry routes.
3. Remove or shorten only duplicated Deep Research orientation from Change Guidance,
   config, and governance navigation while retaining their generic mechanics.
4. Run focused Change Guidance/architecture checks, strict validation, and the full
   deterministic verification gate. Rollback removes the new directory and restores
   the prior small navigation text together; no runtime or persisted migration exists.
