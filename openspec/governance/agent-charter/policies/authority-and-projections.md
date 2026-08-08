# Authority And Projections Policy

> role: source-of-truth discipline for Deep Research changes
> trigger: adding state, a summary, diagnostic, status view, retained observation, cache, or recovery surface
> authority: guidance only; it never creates a state writer, route, or permission
> @impl DRC-005

## Rule

Name the existing owner of every fact before adding a projection of it. In Deep
Research, checkpointed control state owns lifecycle control, the validated submission
ledger owns accepted evidence, and contained sandbox artifacts own large content.
Typed contracts own their declared result fields; trusted runtime bindings own their
host/context facts.

An inspection file, event journal, CLI/TUI view, cache, or agent explanation may be
valuable, but it is a projection. It must not decide a transition, prove permission,
or supply a fact when the owner is unavailable or contradictory.

## Questions Before Design

- What exact fact is being communicated?
- Which current contract, state, ledger, or artifact already owns it?
- Who may write that source, and what validates it?
- Is the new data a bounded projection or an attempted second authority?
- Can a consumer recover only through the owner's existing interface?

If no answer names an owner, narrow the change or create an owning capability contract
through OpenSpec. Do not add a loose receipt, Markdown marker, or summary file to
make an uncertain operation look complete.

## Boundary

This policy does not define a new checkpoint field, retained-event schema, or
diagnostic payload. The owning capability spec and typed contract make those concrete
choices. The policy only prevents their design from displacing an existing authority.
