# Core Change Practice

> authority: guidance only; owning specifications and executable contracts define behavior
> trigger: change admission, context selection, authority, and projections

## Principles

1. Start from the smallest owner of the changed semantic decision.
2. Admit an adjacent contract only with the concrete question it must answer.
3. Keep fact authority distinct from writers, projections, summaries, and diagnostics.
4. Select every policy whose trigger applies; one policy cannot waive another.
5. Match evidence to the changed decision and include the material negative path.
6. Give migration, recovery, retirement, and deletion a terminal invariant.

Guidance and review records never grant runtime behavior, state writes, routes,
permissions, tools, retries, or native workflow transitions.

## Change Admission

Name one primary causal owner, the question being answered, necessary adjacent
contracts, the lowest responsible evidence seam, exclusions, and every triggered
policy. A possible future use or general orientation does not admit another boundary.
Observable behavior belongs in its owning specification. A recurring question with a
specific trigger may become focused guidance; an operational procedure cannot
substitute for required behavior.

Use a planted invalid input for a deterministic validator and the narrowest real
handoff for a cross-boundary fact. A failed migration stays active for repair,
rollback, or explicit re-scope; it never silently narrows the approved outcome.

## Authority And Projections

Name the owner of every fact before adding a projection. Record who may propose a
write, which deterministic boundary admits it, and how conflict or absence is handled.
A model output, summary, journal, view, cache, or explanation cannot replace the owner
or decide a transition. If no owner exists, establish one through the owning contract
rather than inventing a receipt that makes uncertainty look complete.

## Context Selection

Start with the owning specification, closest implementation, and lowest responsible
evidence seam. Before opening an adjacent module or upstream source, name the
interface, authority, compatibility, or observed-failure question it must answer.
A possible future use is not enough to expand scope. If local evidence still cannot
identify an owner, clarify admission instead of scanning unrelated code.
