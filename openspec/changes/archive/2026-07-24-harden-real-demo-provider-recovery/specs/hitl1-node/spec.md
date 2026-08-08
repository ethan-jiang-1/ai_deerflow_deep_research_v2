> req: HIN-008

## MODIFIED Requirements

### Requirement: HITL1 generates a validated structured brief from the original question

The real HITL1 node SHALL call `capabilities.run_agent()` with a bounded zero-tool
`NodeExecutionRequest` derived from `state["request_text"]` and validate the result
summary as one `StructuredBrief` JSON object before presenting it to a user. Both the
initial request and the existing malformed-output repair request SHALL set
`tools_enabled=false`. The frozen extra-forbid `StructuredBrief` contract SHALL retain
its current schema, closed profile enums, bounds, and advisory-only status.

Each fresh brief-generation visit SHALL perform at most two total bridge/model
invocations.
Only a retry-eligible `provider.timeout` or `provider.unavailable` returned from the
first invocation SHALL record its scheduled observation through the optional injected
event recorder, wait exactly 1,000 milliseconds through a cancellable backoff, and
repeat the identical initial brief request once. Retry eligibility requires the
bridge-supplied valid `ProviderObservation` for that zero-tool HITL1 result; a matching
code without it, a tools-enabled result, authentication, configuration, tool, policy,
unknown, and cancellation paths SHALL not receive this retry. Recorder absence or
failure SHALL not change this control path. The retry consumes the second and last
invocation slot. The count is a graph bridge/model-invocation count, not a physical
provider HTTP-request count; provider SDK retry policy remains outside this requirement.
`CancelledError` SHALL propagate without awaiting, shielding, or forcing a
post-cancellation recorder write.

When a retry-eligible transient provider result occurs, HITL1 SHALL write a validated
`ProviderRecoveryProjection` only if the visit subsequently blocks. That projection
SHALL contain the trigger category, its required safe `ProviderObservation`, trigger
invocation ordinal, model invocation count, automatic retry count, and exactly one disposition:
`exhausted`, `retry_followed_by_terminal_failure`, or
`retry_not_started_budget_consumed`. `exhausted` requires two invocations and one
automatic retry, a trigger ordinal of one, and both calls ending in retry-eligible
transient provider categories.
`retry_followed_by_terminal_failure` requires two invocations and one automatic retry,
with a trigger ordinal of one, where the second invocation ends in a non-transient
typed failure or invalid structured output. `retry_not_started_budget_consumed`
requires two invocations, zero automatic retries, and a trigger ordinal of two, where
a successful but malformed first output consumed the repair slot and that repair
invocation then returns a retry-eligible transient provider result. The projection
SHALL be absent when no retry-eligible transient provider result occurred. A
repair-slot transient requires the same bridge-supplied valid `ProviderObservation`;
a matching code without it SHALL not create this projection.

For every blocked result, HITL1 SHALL retain a final safe provider observation whenever
the bridge supplied one, including a non-retryable direct public HTTP response; it
SHALL not fabricate one for a legacy authentication mapping. A provider-diagnostic
terminal is a blocked incident with either a recovery projection or a final safe
provider observation. For every provider-diagnostic terminal, HITL1 SHALL derive one
safe opaque diagnostic reference from only a canonical subset of terminal-safe facts
before writing `ResearchState.latest_incident`: research id, generation, stable HITL1
node-attempt identity, final category, and, when present, recovery trigger
category/ordinal, model-invocation count, automatic-retry count, disposition, and the
trigger/final observation response kind plus bounded HTTP status. The subset SHALL
exclude configured-service label, configured endpoint authority, question, prompt, raw
exception, provider body, full URL, credential, and every other presentation field.
Changing only the label or authority SHALL not change the diagnostic reference. That
checkpointed incident remains the sole terminal owner; the event journal and
presentation consume it as projections.

A successful response that fails `StructuredBrief` validation may receive the existing
single repair request only when the two-invocation visit budget remains available. If
the budget has been consumed or the repair response is invalid, HITL1 SHALL fail
closed with `output.structured_invalid`. Any non-success result that is not covered by
the transient-provider policy SHALL preserve its typed category through the existing
blocked path. No failure path may call `interrupt()` or write profile state.

The real recipe SHALL continue to inject the existing zero-tool,
one-bridge/model-invocation-per-call node-agent bridge. Full-fake paths SHALL never
call a model. (`HIN-001`, `HIN-008`)

#### Scenario: One timeout recovers within the visit budget
- **WHEN** the first HITL1 brief invocation returns `provider.timeout` and the next
  identical invocation returns valid structured brief JSON
- **THEN** HITL1 records one bounded retry observation, calls the agent exactly twice,
  and proceeds to the existing profile interrupt

#### Scenario: Initial and repair brief requests are both zero-tool
- **WHEN** HITL1 builds either its initial brief request or its malformed-output repair
  request
- **THEN** each request has `tools_enabled=false`, so the trusted HITL1 bridge policy
  can classify only those two bounded bridge/model invocations

#### Scenario: Second transient failure is exhausted safely
- **WHEN** the first and second HITL1 brief invocations return either
  `provider.timeout` or `provider.unavailable`
- **THEN** HITL1 emits one exhaustion observation and follows its existing blocked
  route without an interrupt or partial profile, preserving the final provider
  category, model_attempts=2, automatic_retries=1, `exhausted`, and one terminal
  diagnostic reference in the terminal incident

#### Scenario: Non-transient failure is not retried
- **WHEN** the first brief invocation returns authentication, configuration, tool,
  policy, structured-output, or unknown failure
- **THEN** HITL1 takes the existing failure route after one invocation and emits no
  provider retry/backoff observation

#### Scenario: Unproven provider code is not admitted to recovery
- **WHEN** the first brief invocation returns `provider.timeout` or
  `provider.unavailable` without the bridge-supplied valid `ProviderObservation`
- **THEN** HITL1 takes the existing fail-closed route after one invocation and emits
  no provider retry/backoff observation or recovery projection

#### Scenario: Non-retryable HTTP response remains safe terminal feedback
- **WHEN** the first brief invocation returns a non-retryable direct public HTTP
  response with a safe `400` observation
- **THEN** HITL1 blocks after one invocation, retains that final observation in its
  terminal incident with one safe diagnostic reference, and writes no recovery
  projection or retry/backoff observation

#### Scenario: Label and authority do not affect terminal correlation
- **WHEN** two otherwise identical provider-diagnostic HITL1 terminals differ only in
  their vetted configured-service label or sanitized endpoint authority
- **THEN** they derive the same diagnostic reference and retain neither value as a
  diagnostic-reference input

#### Scenario: Structured repair and transient recovery share one ceiling
- **WHEN** a transient provider failure consumes the second permitted invocation and
  that retry returns malformed structured output
- **THEN** HITL1 blocks with `output.structured_invalid` and does not issue a third
  repair request, preserving `retry_followed_by_terminal_failure` with two model
  attempts and one automatic retry

#### Scenario: Repair-slot provider failure cannot create a third call
- **WHEN** the first invocation returns a successful but malformed structured brief
  and its second repair invocation returns `provider.unavailable`
- **THEN** HITL1 blocks after exactly two invocations with
  `retry_not_started_budget_consumed`, zero automatic retries, and no third call

#### Scenario: Cancellation during provider backoff remains cancellation
- **WHEN** the first brief invocation returns `provider.timeout` and the outer task is
  cancelled during the 1,000 millisecond backoff
- **THEN** `CancelledError` propagates, no second invocation or exhaustion incident is
  created, no post-cancellation recorder write is required, and no interrupt or
  profile state is written

#### Scenario: Cancellation during the automatic retry remains cancellation
- **WHEN** the first brief invocation returns `provider.unavailable`, the fixed backoff
  completes, and the outer task is cancelled while the second invocation is in flight
- **THEN** `CancelledError` propagates, no terminal recovery incident or exhaustion
  event is created, and no interrupt or profile state is written
