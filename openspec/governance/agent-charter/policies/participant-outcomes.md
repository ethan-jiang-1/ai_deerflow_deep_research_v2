# Participant Outcomes Policy

> role: human and AI consumer contract guidance
> trigger: changing a lifecycle result, failure, diagnostic, CLI/TUI/API output, or machine-consumed outcome
> authority: guidance only; exact result fields remain owned by the relevant capability contract
> @impl DRC-003

## Rule

When an outcome is consumed by a person and another AI, derive both projections from
the same owning typed result. Human language explains the observed outcome, the
relevant owner or phase, and the nearest legal next action. Machine-facing data uses
stable bounded fields or closed enums so another agent need not infer control state
from natural language.

The same rule applies to success, waiting, denial, cancellation, and terminal
failure. A participant should never need to guess whether a retry occurred, whether
an action is permitted, or whether an inspection record can resume execution.

## Design Questions

- What is the owning typed source for the outcome?
- What must a person understand and do next?
- Which bounded facts must another AI receive without prose parsing?
- Which action is legal now, and which superficially plausible action is unavailable?
- What information is safe to disclose at this surface?

For an external failure, likely dimensions include a closed category, owner/phase,
attempt or recovery disposition when observed, safe correlation reference, and one
allowed next action. These are not a universal schema: an owning spec decides which
fields exist and how they are validated.

## Safe Disclosure

Do not surface credentials, raw exceptions, provider bodies, prompt/user text, full
URLs, host paths, or an inferred internal state. A safe configured label, sanitized
authority, observed closed response category, and diagnostic reference may be useful
when the owning contract permits them.

## Boundary

Presentation and machine projections are not lifecycle controllers. They cannot
resume, authorize, or rewrite the checkpoint merely because they contain a run
reference or a helpful recommendation.
