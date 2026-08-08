> req: HIN-007

## ADDED Requirements

### Requirement: HITL1 makes profile proposal acceptance and answer feedback durable

After validating a first-visit `StructuredBrief`, real HITL1 SHALL checkpoint a bounded controller-owned advisory proposal before it interrupts. The proposal SHALL contain only validated profile fields and a schema version; it SHALL not contain raw model output or become final profile authority. A correlated typed closed response action `accept_suggestion` SHALL materialize that proposal only when it is complete and matches the current HITL1 request. The node SHALL not invoke brief generation again when resumed at the same persisted proposal.

HITL1 SHALL parse structured JSON and a documented deterministic Chinese/English alias set into at most one value per profile dimension. `must_answer` SHALL be visible in the prompt projection. A response that recognizes no valid field or answer content SHALL leave profile progress, consumed response ids, and accepted-answer round unchanged; HITL1 SHALL reissue bounded feedback naming the supported input forms. It SHALL checkpoint the rejected message id only as a bounded next-interrupt cursor, so the fresh feedback request starts after that message without treating it as a consumed accepted response. A separate controller-owned rejection counter SHALL permit at most three consecutive rejected responses in the same ongoing HITL1 intake; feedback may issue a new request id while preserving proposal/progress/counter correlation. The third SHALL terminally block using the existing `terminal_reason=gate_blocked` and compact `RunFailureCode.INPUT_INVALID_RESPONSE` incident, with presentation category `profile_input_unrecognized`, a deterministic runtime diagnostic reference, and structured-input recovery guidance. A recognized response, acceptance, cancellation, or terminal result SHALL clear the transient rejection cursor/counter as applicable. A recognized but incomplete response SHALL durably merge only the recognized fields, reset that counter, and consume one accepted-answer round. The bounded final degradation policy applies only to accepted incomplete answers, never to rejected zero-recognition input. (`HIN-007`)

#### Scenario: Explicit acceptance adopts only the checkpointed proposal
- **WHEN** a matching HITL1 response selects `accept_suggestion` for a complete checkpointed proposal
- **THEN** HITL1 writes that proposal as the final profile and clears transient proposal and feedback state without calling a model again

#### Scenario: Localized input receives deterministic feedback
- **WHEN** a user answers `标准深度`
- **THEN** HITL1 recognizes `depth=standard`, reports the remaining required fields including `must_answer`, and consumes exactly one accepted-answer round

#### Scenario: Unrecognized input is not silently degraded
- **WHEN** a user answers `你来定义吧` or another value with no closed accepted meaning
- **THEN** HITL1 keeps the pending profile/proposal and accepted-answer round unchanged, returns a bounded feedback prompt, and does not route toward degraded finalization

#### Scenario: Rejected input cannot replay against a feedback request
- **WHEN** HITL1 rejects one response and reissues feedback with a new request id
- **THEN** the next interrupt cursor starts after the rejected message, that message is not in accepted consumed ids, and only a later matching response is eligible for the fresh request

#### Scenario: Rejection feedback cannot loop forever
- **WHEN** three consecutive responses in one ongoing HITL1 intake have no closed accepted meaning
- **THEN** the first two preserve accepted-answer state and reissue correlated feedback, while the third records blocked `gate_blocked` plus `input.invalid_response` incident with a deterministic `diag_` reference and presentation category `profile_input_unrecognized` with the JSON recovery form and no degraded profile

#### Scenario: Ambiguous phrase cannot populate two dimensions
- **WHEN** an alias phrase could match more than one profile dimension
- **THEN** the parser rejects that phrase rather than guessing, and feedback names the structured JSON alternative
