## MODIFIED Requirements

### Requirement: Critic runs under bounded read-only policy

The real readiness critic SHALL run through the existing bounded Node Agent path with
one invocation, zero allowed tools, no writable roots, a finite model/token/wall-time
budget, and a closed `ReadinessCriticOutput` candidate. Missing, malformed, duplicate,
out-of-scope, incomplete, or failed execution output SHALL be deterministically
projected to conservative `blocked_repair_required` verdicts for the affected supplied
questions; it SHALL NOT silently use the all-ready fallback. (`REA-006`)

The critic node policy's admission envelope SHALL be coherent with the request
builder's declared maximum input: the builder's full evidence projection budget
(`MAX_READINESS_EVIDENCE_BYTES`) plus request scaffolding, the trusted system prompt,
and the per-call output token cap SHALL together stay within the policy's
`total_token_budget`, so that a builder-maximal request is admissible before the
network and is never refused as `token_admission` by construction. This coherence
SHALL be locked by a deterministic regression test that builds a builder-maximal
request and asserts the envelope inequality against the assembled policy.

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
