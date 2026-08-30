> req: WSN-012

## ADDED Requirements

### Requirement: Provider-transient timeouts retry within the model-call budget

wave2_synthesis SHALL classify a failed synthesis invocation whose typed failure
fact carries a provider-timeout origin (`bridge_wall_time_budget` or
`provider_sdk_timeout`) as provider-transient, distinct from budget-class
exhaustion, and SHALL retry the same bounded invocation within the phase's
existing model-call policy envelope before any degradation or terminal
disposition is considered. Each retry SHALL consume one model-call ordinal from
that envelope and SHALL be journaled as its own model-tool attempt fact with the
same phase and node attempt identity. A provider-transient classification
SHALL NOT, by itself, write terminal state, hand back budget exhaustion, or
alter the wave2 gate's routing authority. When the envelope's remaining
model-calls are all consumed by provider-transient failures, the node SHALL
enter the existing budget-class failure handling unchanged, and the existing
gate machinery alone SHALL decide the honest degraded pass or the typed blocked
terminal. Invocations that fail without a provider-timeout origin SHALL keep
their pre-change classification and disposition exactly. (`WSN-012`)

#### Scenario: First provider timeout retries without degrading
- **WHEN** the first synthesis invocation fails with a provider-timeout origin
  and the policy envelope still has unused model-calls
- **THEN** the node retries the invocation consuming the next call ordinal,
  writes no terminal state, and emits no budget-exhaustion hand-back

#### Scenario: A successful retry behaves as if the timeout never happened
- **WHEN** a retried invocation returns a candidate
- **THEN** the node continues through the unchanged validation and one-shot
  repair path, and the phase outcome is indistinguishable from a run whose
  first invocation succeeded

#### Scenario: Retry exhaustion falls back to existing budget handling
- **WHEN** every remaining model-call in the envelope fails with a
  provider-timeout origin
- **THEN** the node enters the existing budget-class failure handling, and the
  gate's existing first-exhaustion degrade / repeated-exhaustion block rules
  alone decide the disposition

#### Scenario: Non-transient failures are unaffected
- **WHEN** an invocation fails without a provider-timeout origin (token budget
  exhausted, structured output invalid, or an internal failure)
- **THEN** classification and disposition match the pre-change behavior exactly

#### Scenario: Retry attempts are individually observable
- **WHEN** any provider-transient retry sequence occurs
- **THEN** the event journal records one model-tool attempt fact per invocation
  with continuing call ordinals, so a downstream reader can reconstruct which
  ordinal timed out and which succeeded without string-searching capability
  names
