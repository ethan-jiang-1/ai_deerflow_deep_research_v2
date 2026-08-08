> req: HIN-009, HIN-010

## ADDED Requirements

### Requirement: HITL1 resolves natural proposal replies through bounded semantic intake

For a complete checkpointed HITL1 proposal, a raw text reply SHALL be passed to a
zero-tool structured semantic-intake request and treated only as a candidate intent.
HITL1 SHALL retain graph authority for correlated acceptance, profile publication,
proposal version, state mutation, and routing. A candidate confirmation SHALL publish
only the current complete checkpointed proposal. A full candidate revision SHALL create
a new visible advisory proposal version and require a new confirmation. A bounded
proposal question or clarification SHALL preserve the proposal and reissue a fresh
correlated request. (`HIN-009`)

#### Scenario: Natural confirmation is graph-authorized
- **WHEN** a matching current HITL1 reply such as a natural confirmation resolves to
  `accept_current_proposal`
- **THEN** HITL1 writes the current checkpointed proposal as the final profile without
  parsing the reply as profile fields or requiring an adapter action alias

#### Scenario: Revision becomes visible before acceptance
- **WHEN** a matching current reply resolves to a full changed proposal
- **THEN** HITL1 checkpoints the new advisory proposal, increments its version, renders
  every material value, and does not write `profile.json` until a later confirmation

#### Scenario: Question leaves a proposal pending
- **WHEN** a matching current reply asks why a suggested value was chosen
- **THEN** HITL1 returns one bounded explanation and a fresh request for the unchanged
  proposal without consuming an accepted-answer or rejection round

### Requirement: HITL1 semantic-intake failure is bounded non-terminal feedback

HITL1 SHALL make at most three semantic bridge/model calls per raw proposal reply. It
MAY make at most two automatic retries only for a valid retry-eligible transient
provider result and at most one structured-output repair, sharing that three-call cap.
Cancellation SHALL propagate. Exhaustion, non-transient provider failure, or invalid
structured output SHALL preserve the current proposal, write closed interaction
feedback, reset no final profile authority, and reissue a request with a visible
fallback control. These outcomes SHALL not increment `profile_rejection_round` or
terminally block the lifecycle. (`HIN-010`)

#### Scenario: Transient semantic failures stop at three calls
- **WHEN** the first three semantic calls for one reply each return a retry-eligible
  provider failure
- **THEN** HITL1 makes exactly three calls, records non-terminal semantic feedback,
  and keeps the current proposal confirmable

#### Scenario: Invalid semantic output has one repair
- **WHEN** the first semantic output is malformed and its one repair is malformed
- **THEN** HITL1 does not issue another repair, preserves the proposal, and returns
  closed feedback with the visible fallback control
