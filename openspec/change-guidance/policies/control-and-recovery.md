# Control And Recovery Policy

> role: bounded recovery and actionable failure design guidance
> trigger: adding retry, backoff, fallback, terminal incident, cancellation path, or control check
> authority: guidance only; phase behavior, budgets, and routes remain with their owning capability

## Rule

Control must remain simpler than the work it governs. Start from the direct owning
fact, identify the earliest actionable failure, and return one legal next action.
Recovery belongs to the phase or runtime contract that owns the invocation; a CLI,
TUI, diagnostic bundle, or model explanation cannot quietly become a retry controller.

## Bounded Recovery

An automatic recovery design names all of the following in its owning spec:

- the closed condition eligible for recovery;
- the operation/phase that owns it;
- the maximum attempt or time budget and cancellation behavior;
- the terminal disposition after exhaustion; and
- the nearest legal action after that disposition.

Do not use unbounded retry, silent fallback, a guessed resumption point, or a generic
"try again" message that hides whether the system already tried. Non-transient,
authorization, configuration, integrity, or unknown failures remain fail-closed until
their owning contract supplies a valid path.

## Participant Feedback

Feedback should make the failure category, phase/owner, retry disposition, safe
diagnostic reference, and allowed next action visible when those facts are available.
It must also state unavailable actions honestly; retained inspection is not execution
resume unless the lifecycle contract explicitly says it is.

## Boundary

This policy does not set a provider timeout, retry count, command, or state field. It
does not grant a bypass for an invariant or require a human to repeat mechanical work
the system is already authorized to perform. Those choices belong to the relevant
capability delta and runtime owner.
