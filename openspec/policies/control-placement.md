# Control Placement Policy

> trigger: a change adds or changes candidate admission, a validator, readiness check,
> retry/fallback/recovery, next-action diagnostic, durable control fact, checkpoint or
> state writer, or a cognitive/control boundary between a Node Agent, human decision,
> and deterministic owner
> authority: guidance only; never runtime control, permission, or current-state truth
> @impl DRC-009

Use this policy to locate a changed decision or fact before it turns into a competing
controller. It complements the Deep Research Agent Charter policies; it does not
replace Node Agent Review, Workflow Outcome Review, human-interaction-integrity,
authority-and-projections, or control-and-recovery.

## Closed Postures

Choose one posture for each changed decision or fact:

| Posture | Meaning |
|---|---|
| `advisory` | A cognitive candidate or diagnostic informs a deterministic owner; it cannot admit or mutate by itself. |
| `bounded-repair` | The owning deterministic phase applies an explicitly bounded legal recovery. |
| `human-decision` | A person supplies a typed capability decision; select `human-interaction-integrity` as well. |
| `non-bypassable` | A deterministic invariant, evaluator, or admission boundary must hold before the legal next action. |

Do not invent another posture. A change with both a human choice and a non-bypassable
invariant uses distinct rows; prose cannot make one effect waive the other.

## Review Record

When selected, add exactly one `## Control Placement Review` table to the proposal:

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| What changes hands or is decided? | What may propose or what may the person decide? | Which direct fact exists and who accepts/evaluates it? | Which closed posture applies? | What cannot be bypassed, or what bounded recovery is legal? | Which control is reused, or which competing control is avoided? | What lowest responsible deterministic proof covers it? |

For each row, ask whether a cognitive candidate can only propose, whether a human
choice is a typed capability decision, which deterministic owner receives the direct
fact, and which invariant or legal recovery bounds the next action. A
`human-decision` row must compose with the existing `human-interaction-integrity`
policy; it is not a waiver or a human-action contract.

## Evidence Boundary

When the direct fact crosses a producer-to-consumer boundary, use evidence that
observes the real handoff rather than a hand-built consumer fixture or a
presentation-only assertion. When the fact is durable, cover the write, reload, and
direct consumer chain. Keep the evidence at the lowest responsible deterministic
seam, while any owning capability requirement continues to define the behavior.

## Non-Authority Boundary

This policy creates no runtime route, state write, permission, retry, model role,
lifecycle action, schema, or evaluator. It does not scan source, infer applicability,
or judge review prose. It does not implement V2
`add-cross-session-cognitive-guardrails`: there is no guardrail directory, runner,
dossier, hook, or semantic evaluator here.
