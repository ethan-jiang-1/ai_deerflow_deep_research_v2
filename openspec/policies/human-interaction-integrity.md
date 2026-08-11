# Human-Interaction Integrity Policy

> role: review guidance for human decision and semantic-input surfaces
> trigger: adding or revising a human decision, semantic input, visible control, or interaction recovery surface
> authority: guidance only; exact behavior, state writes, and permissions remain in the owning capability specification and typed contracts

## Rule

Treat a human interaction as a bounded subject and a legal next-action surface, not
as a prompt string or an adapter-specific input convention. Before changing one,
identify the current semantic subject, the authority that turns raw input into a
candidate, the graph or controller that authorizes an effect, and the controls that a
person can actually see and use.

## Review Questions

- What current subject and material facts must the person see to make this decision?
- Which bounded contract interprets raw text, and can that interpretation only propose
  a candidate rather than create an action, route, correlation, or state write?
- Which graph or controller remains authoritative for validation, transition, and
  checkpoint mutation?
- Which legal controls are visible now, and where does trusted code bind a selected
  control to the current advertised action?
- What happens after ambiguity, malformed input, provider failure, cancellation, or
  a stale control, and which owner has the explicit recovery bound?
- What is the lowest deterministic transcript that proves a first-time user can
  recover without knowing a hidden transport token?

## Boundary

This policy does not define an input schema, action id, retry count, checkpoint field,
route, or adapter command. Those observable choices belong in the relevant capability
specification, active delta, typed contract, and runtime authority.
