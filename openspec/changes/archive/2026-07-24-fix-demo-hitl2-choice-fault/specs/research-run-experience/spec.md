> req: RER-003

## MODIFIED Requirements

### Requirement: Failures are safe, categorized, and diagnosable

The runtime SHALL classify failures at their source into the existing closed
run-failure registry. A user-visible `Fault` or terminal outcome SHALL identify the
safe category, known phase when available, certainty, a concrete next action,
retryability, and an opaque diagnostic reference when a record exists; it SHALL never
print only "retry". Unknown exceptions remain `internal-unexpected`, and a terminal
checkpoint retains only the existing compact safe incident projection.

Before a record-bearing bind exists, a warranted standalone-demo diagnostic record
SHALL remain in the documented project-relative support journal. A bind requires a
validated returned result with non-null research id, status, phase, and generation; an
id alone is insufficient. After bind, including a later local transport fault while the
session remains bound, a warranted diagnostic record SHALL be bounded and redacted at
`diagnostics/records.jsonl` beneath that retained bundle. Each record contains only
opaque reference, time, action/phase, closed category, certainty, and a fingerprint
derived exclusively from those closed safe fields plus run mode. It SHALL not
incorporate raw exception/message text, prompt or answer text, provider content, URLs,
paths, credentials, or a hash of any such value.

After `ResearchRunExperience` has returned a validated `AwaitingInput` HITL2 choice
prompt, it SHALL recognize a recoverable invalid choice only for the result of its
own immediately preceding `resume` dispatch. The decoded result SHALL have action
`resume`, code `response_invalid`, the current research ID, an empty execution trace,
and no bundle directory, status, phase, generation, request/pending projection, or
terminal projection. The experience SHALL also still hold the validated HITL2 choice
request and the complete prior `AwaitingInput` update. The denial SHALL be an ordinary
mapping result, not a `Command` carrying a new human-input artifact; the cached
snapshot pending projection, prompt, and request SHALL still agree on request ID and
choice mode. Before ordered trace validation or trace mutation, it SHALL return an
immutable copy of that update with
`rejection_category=choice_input_invalid` and an empty trace delta; it SHALL NOT
reconstruct its snapshot from the denial or current mutable fields.

This re-prompt path SHALL not decode or display raw rejected input, accept a route,
publish a session fact, change durability, mutate the previously verified trace,
create checkpoint state, invoke graph nodes, or create a diagnostic record. A later
canonical response SHALL continue through normal lifecycle transport and graph-owned
human-input validation.

Any denial with an unexpected outbound action, result action, code, research ID,
trace, record-bearing field, missing cached complete update/request, non-choice
prompt, new request artifact, malformed wire shape, or correlation error SHALL retain
the normal fail-closed protocol/failure handling. In particular, `response_mismatch`
SHALL NOT be re-presented as a user-correctable choice prompt.
(`RER-003`)

#### Scenario: A post-bind diagnostic is discoverable with its retained run
- **WHEN** a record-bearing validated lifecycle result binds a research id and then a
  classified terminal or local failure is projected
- **THEN** its opaque diagnostic reference is retained under that bundle's
  `diagnostics/records.jsonl`, while preflight/no-record failures remain only in the
  global support journal

#### Scenario: Changing a raw source cannot change the persisted fingerprint
- **WHEN** two otherwise identical classified failures carry distinct sentinel
  exception messages, prompts, answers, paths, or provider bodies
- **THEN** their diagnostic fingerprint is identical and neither sentinel nor a
  source-dependent digest appears in the record

#### Scenario: Model configuration failure is actionable without leaking configuration
- **WHEN** the real brief cannot start because no usable model configuration is available
- **THEN** the user sees that model configuration is missing, why it is required, the next configuration action, and a diagnostic reference; no key name value, path, exception body, provider request, or raw stack is displayed

#### Scenario: Unknown implementation failure is not falsified
- **WHEN** an unrecognized exception escapes a lifecycle source
- **THEN** the outcome category is `internal-unexpected` with unknown certainty and a safe support action, not checkpoint-inconsistent or a false provider diagnosis

#### Scenario: Invalid HITL2 choice retains the same safe suspension
- **WHEN** a validated HITL2 `AwaitingInput` prompt has a non-empty verified trace
  and its subsequent resume returns a same-research `response_invalid` denial with
  no record-bearing lifecycle state
- **THEN** the shared experience returns `AwaitingInput` for the same request and
  choices with closed invalid-choice feedback, preserves the prior trace and safe
  snapshot, and does not return `protocol.invalid_result`

#### Scenario: A later valid choice resumes through graph authority
- **WHEN** a recoverable invalid choice has been re-presented and the user later
  submits an advertised option ID
- **THEN** the experience dispatches the later response normally and reports only
  the graph-returned trace/result without treating the prior invalid answer as a
  graph transition

#### Scenario: Correlation or wire anomalies remain fail-closed
- **WHEN** a purported invalid-choice denial follows a non-`resume` dispatch, has a
  different research ID, a non-choice cached prompt, a non-empty trace,
  `response_mismatch` code, record-bearing fields, a new request artifact, or
  malformed control data
- **THEN** the shared experience returns the existing safe non-retryable fault path
  and does not re-present a cached prompt
