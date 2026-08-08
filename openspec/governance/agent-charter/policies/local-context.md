# Local Context Policy

> role: focus selection for Deep Research changes
> trigger: beginning a change, choosing a code-reading scope, or explaining a cross-layer patch
> authority: guidance only; module ownership and behavior remain in the owning spec and code
> @impl DRC-002

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

## Boundary

This policy does not make a module authoritative over facts it does not own, and it
does not prohibit necessary dependency inspection. It only makes that expansion
explicit, reviewable, and proportional to the named change.
