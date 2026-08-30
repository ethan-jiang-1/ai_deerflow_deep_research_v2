> req: REJ-011

## ADDED Requirements

### Requirement: Suspension attempts are journaled as suspension, not unexpected failure

When a node visit suspends because the graph raises its human-interrupt signal
(a normal suspension awaiting recovery), the node attempt's journal fact SHALL
NOT record `internal.unexpected` as its failure category; the recorded attempt
outcome SHALL distinguish suspension from an unexpected internal failure so a
journal reader can tell "awaiting recovery" from "crashed" without external
knowledge. Unexpected exceptions SHALL continue to be recorded with their
existing failure categories and SHALL still propagate. The event schema's
existing fields and schema version SHALL be reused; no new event category is
introduced. (`REJ-011`)

#### Scenario: Human-interrupt suspension is not labelled internal.unexpected
- **WHEN** a node visit suspends through the graph's human-interrupt signal
- **THEN** the journaled attempt fact does not carry
  `failure_category=internal.unexpected`, and the recorded outcome identifies
  the attempt as suspended rather than failed-by-crash

#### Scenario: Real unexpected exceptions keep their labels and propagate
- **WHEN** a node visit fails with an exception that is not the graph's
  human-interrupt signal
- **THEN** the journal records the existing `internal.unexpected` failure
  category and the exception still propagates to the graph machinery
