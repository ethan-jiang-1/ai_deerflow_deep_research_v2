> req: REJ-011

## MODIFIED Requirements

### Requirement: Suspension attempts are journaled as suspension, not unexpected failure

When a node visit suspends because the graph raises its human-interrupt signal
(a normal suspension awaiting recovery), the node attempt's journal fact SHALL
NOT record `internal.unexpected` as its failure category; the recorded attempt
outcome SHALL be the closed persisted value `suspended`, carried by the existing
schema-version-3 event outcome enumeration, so a journal reader can tell
"awaiting recovery" from "crashed" without external knowledge. The live
observation projection SHALL carry the same suspended fact and SHALL NOT relabel
a suspended node attempt as a failure. Unexpected exceptions SHALL continue to
be recorded with their existing failure categories and SHALL still propagate.
The event schema's existing fields and schema version SHALL be reused; no new
event category is introduced. (`REJ-011`)

#### Scenario: Human-interrupt suspension is not labelled internal.unexpected
- **WHEN** a node visit suspends through the graph's human-interrupt signal
- **THEN** the journaled attempt fact does not carry
  `failure_category=internal.unexpected`, and its persisted outcome is the
  closed value `suspended` rather than failed-by-crash

#### Scenario: Suspension survives the real persisted round trip
- **WHEN** a real Bundle recorder and store serialize a node attempt's `started`
  and `suspended` facts into `diagnostics/events.jsonl` and a runtime reader
  reads the journal back
- **THEN** the reader returns the suspended fact with its sequence, phase, and
  attempt correlation, and no fact in the journal labels the suspended attempt
  `internal.unexpected`

#### Scenario: The live projection keeps suspension distinct from failure
- **WHEN** the same suspension is projected to the live observation stream
- **THEN** the projected attempt outcome is `suspended`, not `failed`, and
  routing, recovery, and terminal classification are identical to a run where
  the projection is absent

#### Scenario: Real unexpected exceptions keep their labels and propagate
- **WHEN** a node visit fails with an exception that is not the graph's
  human-interrupt signal
- **THEN** the journal records the existing `internal.unexpected` failure
  category and the exception still propagates to the graph machinery
