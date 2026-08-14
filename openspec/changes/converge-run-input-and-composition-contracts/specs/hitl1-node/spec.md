## ADDED Requirements

### Requirement: HITL1 admits only the current versioned profile and proposal matrix

HITL1 SHALL consume and write only the source-controlled current profile-content and
proposal/checkpoint schema rows. An absent schema, legacy version, legacy alias,
unknown field, malformed shape, or unregistered external profile/proposal/checkpoint
input SHALL be rejected before it produces a profile reference, proposal, visible
control, State mutation, or graph continuation. The rejection SHALL not infer
comparison, language, or other profile facts, and shall not rewrite the input. (`HIN-003`,
`HIN-004`, `HIN-007`, `HIN-009`, `HIN-015`)

#### Scenario: Unsupported profile checkpoint cannot create a proposal
- **WHEN** a HITL1 read/reload receives an unsupported profile or proposed-profile
  mapping
- **THEN** it rejects that input before proposal/control projection, State write, or
  continuation and preserves the stored mapping byte-for-byte

#### Scenario: Current writer round-trips through HITL1
- **WHEN** HITL1 reads a profile/proposal emitted by the current source-controlled
  writer
- **THEN** it preserves the current bounded profile facts and existing correlation/
  acceptance behavior without invoking a legacy reader

