# Change Admission Policy

> role: lightweight admission and policy-placement guidance
> trigger: opening, revising, reviewing, or applying an OpenSpec change
> authority: guidance only; the active delta and accepted spec own behavior
> @impl DRC-004

## Focus Before Work

An active Deep Research proposal begins with the Focus Card defined by the
[local context policy](local-context.md). The card is intentionally short: it makes
the primary causal module, only necessary interfaces, proof seam, and exclusions
reviewable before the implementation expands.

The card is not a second design document. It is an admission boundary. A missing
primary owner, evidence seam, or exclusion is a signal to clarify the change before
adding code or browsing unrelated modules.

Each non-`none` adjacent/external contract names the question it must answer. A
possible future use, general orientation, or a search for analogous code does not
admit another module into scope. When local evidence exposes a genuinely necessary
new contract, revise the Focus Card before expanding; when it exposes ambiguous
ownership, clarify that owner instead of using a wider host scan to guess.

## Decide The Right Home

Use this order:

1. If the statement changes observable behavior, a command, state schema,
   permission, route, or retry contract, write or modify the owning capability delta.
2. If it is a recurring design question with a specific trigger across capabilities,
   add or revise a focused policy and route it from the charter index.
3. If it is durable product posture spanning those policies, revise
   [`agent-charter/charter.md`](../agent-charter/charter.md).
4. If it is a procedure for an operator after behavior already exists, write a
   scoped operational document instead.

No policy or charter text can be used as a shortcut around an owning requirement,
test, or runtime authority.

## Evidence And Review

Every change identifies the lowest responsible evidence seam. A direct validator gets
an invalid fixture; a control path gets its narrow deterministic contract or scripted
workflow test; live behavior is supplemental when the claim actually needs it. Review
the primary module first, then only named adjacent contracts.

## Boundary

The deterministic charter checker verifies only the permanent navigation and Focus
Card shape. It cannot certify that a proposed module owner, prose explanation, or
architecture decision is semantically correct. That judgment remains with review,
the owning specification, and executable evidence.
