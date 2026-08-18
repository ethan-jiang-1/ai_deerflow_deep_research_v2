## MODIFIED Requirements

### Requirement: LLM-Bearing Node execution has explicit budgets

The wave2 synthesis node budget SHALL provide bounded headroom for real model
output as a scale-independent product fix: ≈ `max_model_calls=4,
total_token_budget=64_000, per_call_output_token_cap=16_384,
structured_result_bytes=16_384, wall_time_seconds=300`. This remains a hard,
positive, admission-controlled cap. Readiness and final-delivery node budgets,
wave worker budgets, and all other budgets SHALL remain at today's values until
real runs demonstrate a need (evidence-driven). (`NOA-002`, `NOA-011`)

#### Scenario: Work completes within budget
- **WHEN** a replay model returns a valid structured result within all configured limits
- **THEN** the adapter returns a successful normalized result with recorded usage and
  finish reason

#### Scenario: Budget exhaustion stops execution
- **WHEN** a fake model exceeds a declared model-call, tool-call, parallelism, token,
  tool-result, structured-result, or wall-time limit
- **THEN** execution terminates without another tool call and reports the exhausted
  budget as a failure

#### Scenario: Parallel response cannot cross request quota
- **WHEN** one tool call has already run under a two-call request limit and the next
  model response proposes two parallel calls
- **THEN** middleware rejects the response before either new call dispatches and
  observed request tool calls remain one

#### Scenario: Missing usage cannot disable the token budget
- **WHEN** a model response omits usable token accounting
- **THEN** the runtime emits terminal `usage_unavailable`, strips tool calls, and does
  not make another model request

#### Scenario: Wave2 synthesis budget has real-output headroom
- **WHEN** the wave2 synthesis node runs a real model
- **THEN** its policy budget is the raised, finite, admission-controlled cap

#### Scenario: Other budgets stay default
- **WHEN** a wave worker, the readiness node, or the final-delivery node runs
- **THEN** its budget is today's value, unchanged
