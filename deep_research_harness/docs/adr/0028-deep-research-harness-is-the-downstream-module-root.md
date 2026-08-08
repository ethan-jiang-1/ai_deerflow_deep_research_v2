# Deep Research Harness Is The Downstream Module Root

This decision supersedes ADR-0007's Durable Research Session lifecycle model.

The downstream module root is named `deep_research_harness` and is presented as the
Deep Research Harness: the stable project boundary that creates independent Deep
Research Runs and their retained, deletable Run Bundles. A finished Bundle remains
inspectable until it is no longer needed, then may be deleted without affecting another
Run or the Harness. This filesystem identity remains distinct from the generic
`deerflow-harness` framework and does not rename the existing distribution,
`deerflow_deep_research` import namespace, or `deep_research` public tool.

Each Run Bundle is the sole durable ownership boundary for one Run's control state,
evidence, and content. One outer conversation has at most one active Run, while ended
Bundles may coexist for inspection. A Run is active while its available Bundle-local
Research State is non-terminal, including while it waits for User input; it is ended
when its current Refinement Round is terminal. An explicit user refinement of an
available ended Bundle reactivates that Bundle for a later Refinement Round; earlier
reports and materials remain retained for inspection. Deleting a Bundle makes that Run
unavailable rather than ended, cannot be reactivated, and does not affect another Bundle
or the Harness. A
user-directed refinement of an active Run continues that same Bundle rather than
creating another Run. A refinement may be submitted at any time, is admitted into that
Bundle, and takes effect only at its next safe durable control point; an in-flight
writer is never rewritten directly. Each `start` creates a fresh opaque Run Bundle ID;
it identifies that Bundle while it exists and is neither a conversation-derived identity
nor a way to recover a deleted Run. The current conversation may retain that Bundle ID
as a Current Bundle Handle for its next refinement, but the handle is only a locator:
Bundle-local State must validate existence and lifecycle status. The Harness has no
durable active-Bundle pointer or independent Run registry: after restart, or when the
handle is absent, it discovers Runs only from Bundle directories and their contained
State in the trusted conversation scope. Bundle deletion is an external filesystem fact
that may occur while a Run is active; after it is detected, the Harness fails closed and
never recreates that Bundle or persists replacement Run state. Logs, diagnostics,
audits, and metadata may remain outside a Bundle only as non-authoritative observations;
none may establish existence, select an active Run, authorize an action, recover State,
or block a fresh Run.
