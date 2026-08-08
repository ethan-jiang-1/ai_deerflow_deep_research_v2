> req: DRC-009

## ADDED Requirements

### Requirement: Control-placement guidance is externally routed and non-authoritative

The Deep Research Agent Charter SHALL route an external `control-placement` policy
for a change that adds or changes a gate, validator, readiness check, candidate
admission, retry/fallback/recovery, next-action diagnostic, durable control fact,
checkpoint/state writer, or cognitive/control boundary between a Node Agent, a human
decision, and a deterministic owner. The external policy SHALL remain under
`openspec/policies/`, distinguish itself from charter routing, governance checks, and
deferred cross-session guardrails, and state that it creates no runtime route, state
write, permission, retry, model role, or lifecycle action.

The policy SHALL use only the closed design postures `advisory`, `bounded-repair`,
`human-decision`, and `non-bypassable`. It SHALL direct an author to identify a
cognitive candidate or human judgment, the direct fact and its deterministic
owner/evaluator, protected invariant or legal recovery, reused/avoided control, and
the lowest responsible deterministic evidence seam. It SHALL direct a change with a
human-decision posture to the existing `human-interaction-integrity` policy rather
than inventing a waiver or human-action contract.

#### Scenario: A changed admission boundary has a focused review route
- **WHEN** a change moves comparison, acceptance, retry, or other control admission
  between a candidate/human surface and a deterministic owner
- **THEN** the charter index and concise authoring route identify
  `control-placement` as the focused external review policy without treating the
  policy as runtime authority

#### Scenario: A durable fact has a handoff-aware evidence expectation
- **WHEN** a selected control-placement review names a direct fact that crosses a
  producer/consumer boundary or is persisted for later consumption
- **THEN** the policy directs its deterministic evidence seam to cover the real
  handoff or the write/reload/direct-consumer chain rather than a hand-built
  consumer fixture or presentation-only assertion

#### Scenario: A human choice remains a typed capability decision
- **WHEN** a selected review uses the `human-decision` posture
- **THEN** the proposal also selects `human-interaction-integrity`, and the policy
  does not claim that human text or review prose can bypass an invariant or create a
  lifecycle effect

### Requirement: Selected control-placement records are mechanically bounded

Every active Deep Research proposal SHALL use one Focus Card list item named `Triggered
review policies` to declare a comma-separated list of canonical charter and external
review-policy names, or `none: <short rationale>` when no review policy applies. A proposal selecting
`control-placement` SHALL contain exactly one complete `## Control Placement Review`
table with this header, separator, and at least one row:

```text
| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
```

Every table cell SHALL be non-empty. `Design posture` SHALL be one of the closed
postures named by the external policy. A changed feature that has both a human input
and a non-bypassable invariant SHALL use distinct rows, so one posture does not hide
the other effect. Existing Node Agent and Workflow Outcome Review requirements SHALL
remain independently enforced whenever their selected policies require them.

The deterministic charter checker SHALL validate only canonical policy lookup,
declared policy document availability, Focus Card field shape, conditional record
shape, closed posture values, and the `human-decision` policy combination. It SHALL
not infer whether a proposal ought to select the policy, inspect source code, judge
the truth of a review row, or grant runtime authority.

#### Scenario: A complete selected control-placement review is accepted
- **WHEN** an active proposal selects `control-placement` and supplies one or more
  complete rows with valid postures in the exact table format
- **THEN** the charter checker accepts its control-placement record while preserving
  the proposal's separate selected-review validation

#### Scenario: A malformed selected control-placement review fails closed
- **WHEN** an active proposal selects `control-placement` but the external policy is
  unavailable, the Focus Card field is malformed, the review is missing, its header
  differs, a cell is empty, or a posture is not closed
- **THEN** the charter checker reports deterministic conformance failure without
  attempting to infer or repair the missing semantic decision

#### Scenario: Human-decision posture requires the existing interaction review
- **WHEN** a selected control-placement review contains a `human-decision` row but
  `human-interaction-integrity` is absent from Triggered review policies
- **THEN** the charter checker rejects the proposal while leaving the owning human
  interaction contract responsible for any actual input schema, control, state
  effect, or route

#### Scenario: Existing conditional reviews remain distinct
- **WHEN** an active proposal selects control-placement together with
  `node-agent-workflow-integrity` or `workflow-outcome-review`
- **THEN** the charter checker requires every corresponding review record and does
  not treat the Control Placement Review as a substitute for candidate handoff or
  failure/recovery behavior

#### Scenario: Archived proposals remain historical records
- **WHEN** the field migration is applied to the active planning home
- **THEN** archived change artifacts remain unmodified and the checker evaluates only
  active proposals against the current admission contract
