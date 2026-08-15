# Workflow Outcome Review Policy

> role: workflow-failure design and review guidance
> trigger: adding or changing a model, tool, provider, worker, retry, terminal, diagnostic, or lifecycle-projection path
> authority: guidance only; the owning capability contract and runtime authority define behavior

## Rule

Before implementation, record the triggered policies in the proposal's
`## Change Focus`. When this policy is selected, add one `## Workflow Outcome
Review` table. Each row states a failure class, its fact owner, recovery owner and
bound, terminal disposition, legal next action, and deterministic evidence seam.
The table exposes missing decisions to review; it does not establish a retry, route,
state field, permission, or lifecycle transition.

Use canonical policy names separated by commas. Select `none: <short rationale>`
only when no policy is triggered. Do not select this policy for an ordinary
documentation-only change merely to satisfy a template.

## Review Questions

- Which typed fact owns the failure before any projection or diagnostic exists?
- Which phase or controller owns recovery, and what is its explicit bound?
- What terminal disposition and one legal next action can the owner record?
- Which deterministic seam proves the outcome without relying on a live provider?

## Boundary

The proposal record and governance checker validate declared shape only. They cannot
infer semantic correctness, execute recovery, authorize a retry, or replace the
checkpointed lifecycle authority. Exact behavior remains in the owning active delta,
accepted specification, typed contract, and executable evidence.
