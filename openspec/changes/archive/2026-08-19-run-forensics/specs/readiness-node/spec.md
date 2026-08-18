## MODIFIED Requirements

### Requirement: Critic runs under bounded read-only policy

The real readiness critic SHALL run through the existing bounded Node Agent path with
one invocation, zero allowed tools, no writable roots, a finite model/token/wall-time
budget, and a closed `ReadinessCriticOutput` candidate. Missing, malformed, duplicate,
out-of-scope, incomplete, or failed execution output SHALL be deterministically
projected to conservative `blocked_repair_required` verdicts for the affected supplied
questions; it SHALL NOT silently use the all-ready fallback. (`REA-006`)

Whenever the conservative projection substitutes for a critic result — execution
failure or an inadmissible candidate — the node SHALL emit one node-level
`readiness_critic_fallback` observation carrying a closed reason
(`execution_failed` or `candidate_invalid`). The event SHALL be absent when the
critic candidate is admitted, SHALL NOT carry the rejected raw output, prompt text,
or provider payload, and SHALL NOT alter the existing conservative projection,
route calculation, or repair counting.

The checkpointed critic summary SHALL contain only the admitted, bounded typed
per-question projection consumed by the materializer. Raw provider output, prompt
text, sandbox paths, rejected candidate content, and unused critic-only fields SHALL
NOT be checkpointed. The critic contract SHALL bound retained field/cardinality values;
the existing policy's structured-result byte budget remains a separate hard cap on raw
bridge success output.

#### Scenario: Invalid output fails closed to existing repair
- **WHEN** the critic result is malformed or does not provide one valid verdict for
  every supplied question
- **THEN** readiness projects repair-required verdicts and follows the existing
  `repair_targeted` route calculation

#### Scenario: Execution failure cannot claim readiness
- **WHEN** the bounded Node Agent reports timeout, configuration, provider, or policy
  failure
- **THEN** no question is projected as `ready_substantive` solely from that failure
  and the existing repair path is the only legal next action

#### Scenario: A fallback is visible as a first-class event
- **WHEN** the conservative projection substitutes for the critic result because the
  invocation failed or the candidate was inadmissible
- **THEN** one `readiness_critic_fallback` node event with the closed reason is
  recorded in the run journal, without raw output or prompt text, and the projection
  and route are unchanged

#### Scenario: Tool posture is enforced
- **WHEN** the readiness critic request and effective runtime policy are inspected
- **THEN** they permit no web, sandbox, or other tool calls and no writable root

#### Scenario: Builder-maximal evidence stays admissible
- **WHEN** the critic request is built with evidence filling the builder's full
  evidence-projection budget and the assembled node policy is inspected
- **THEN** the projected request bytes plus the trusted system prompt plus the
  per-call output cap do not exceed the policy's total token budget, so the call
  reaches the provider instead of being refused by admission control

#### Scenario: Rejected output is not retained as checkpoint authority
- **WHEN** critic output fails admission
- **THEN** checkpoint state records only the conservative projected verdicts and no
  raw rejected output, provider diagnostic, or prompt text

#### Scenario: Unused parseable critic fields are not retained
- **WHEN** an otherwise admitted candidate includes critic-only limitations, synthesis
  flaws, or contradiction identifiers that the report-plan materializer does not read
- **THEN** `readiness_critic_summary` contains only the bounded admitted per-question
  projection and none of those extra fields
