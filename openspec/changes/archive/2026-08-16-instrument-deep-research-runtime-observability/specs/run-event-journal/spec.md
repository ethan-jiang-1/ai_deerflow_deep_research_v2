# run-event-journal Specification

> req: REJ-005

## MODIFIED Requirements

### Requirement: DeerFlow runtime context is a non-controlling projection boundary

The system SHALL treat DeerFlow runtime context and configured standard Python logging
only as best-effort ingress and projection boundaries for an already-safe Deep
Research fact. A standard log SHALL not imply that a Bundle-local Event Journal append
succeeded, and it SHALL not become a Journal record, replay source, Bundle identity,
or lifecycle authority. Trusted DeerFlow runtime context MAY supply safe correlation,
but an outer DeerFlow run identifier SHALL NOT become a Bundle or Event Journal
identity.

Log absence, filtering, reordering, malformed-observation rejection, or delivery
failure SHALL NOT change Journal persistence, Journal health, graph execution,
checkpointed State, retry policy, terminal classification, or a legal lifecycle
action. The system SHALL not use a raw stream writer, custom event, or private Gateway
store as a Journal-adjacent progress transport. (`REJ-005`)

#### Scenario: A logging failure cannot erase diagnostic evidence
- **WHEN** configured logging cannot accept a safe material observation for an
  admitted Run
- **THEN** the Bundle-local Journal still follows its own persistence and health
  contract, and the Run follows its existing lifecycle behavior

#### Scenario: A log is not a second Journal record
- **WHEN** an already-safe domain fact is logged
- **THEN** the record carries no Journal sequence or persistence claim, cannot be
  used to recover or control a Bundle, and does not replace the Journal's bounded
  retained evidence
