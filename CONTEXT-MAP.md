# Context Map

This repository has three related contexts. Each has its own vocabulary so product
responsibility, host integration, and change governance do not blur together.

## Contexts

- [DeerFlow Host](./CONTEXT.md) - provides the host platform and public integration boundary.
- [Deep Research Product](./deep_research_harness/CONTEXT.md) - helps people obtain research outcomes.
- [OpenSpec Governance](./openspec/CONTEXT.md) - turns agreed product decisions into reviewable changes.

## Relationships

- **DeerFlow Host -> Deep Research Product**: the host supplies the runtime boundary; the product owns its user-facing research outcome.
- **OpenSpec Governance -> Deep Research Product**: approved requirements constrain product changes; governance does not become runtime behavior.
- **DeerFlow Host <-> OpenSpec Governance**: host boundaries constrain a change's scope; governance records rather than expands those boundaries.
