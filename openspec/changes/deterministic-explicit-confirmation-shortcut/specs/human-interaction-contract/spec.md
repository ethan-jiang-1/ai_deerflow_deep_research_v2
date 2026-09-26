# Spec Delta

## ADDED Requirements

### Requirement: Explicit confirmation phrases admit deterministically

HITL1 SHALL map a reply consisting solely of a phrase from a frozen, closed explicit
confirmation list (for example `confirm` or `确认`) of a current complete proposal to
the accept-current-proposal resolution without any semantic-intake model call, exactly
as the bounded revision-phrase shortcut maps bounded revision phrases without a model
call. The deterministic mapping SHALL apply only when the current proposal is complete:
an incomplete proposal SHALL remain outstanding and re-enter bounded intake. The
mapping SHALL NOT accept partial matches, mixed content, or ambiguous replies; every
other reply SHALL retain the existing bounded semantic-intake path, its repair bound,
and its closed failure categories. Proposal admission SHALL remain owned by the
existing deterministic confirmation owner and its complete-proposal check. (`HIC-005`)

#### Scenario: Explicit confirmation phrase skips semantic intake
- **WHEN** the current proposal is complete and the reply consists solely of a phrase
  from the closed confirmation list
- **THEN** HITL1 resolves it to accept-current-proposal with zero model calls and
  admits the proposal through the existing deterministic confirmation owner

#### Scenario: Incomplete proposal keeps the confirmation outstanding
- **WHEN** the current proposal is missing material and the reply consists solely of a
  closed confirmation phrase
- **THEN** the proposal remains outstanding and HITL1 re-enters its bounded intake
  instead of accepting

#### Scenario: Non-matching replies keep the cognitive path unchanged
- **WHEN** a reply is not a phrase from the closed confirmation list
- **THEN** HITL1 classifies it through the existing bounded semantic-intake path with
  its unchanged repair bound and closed failure categories
