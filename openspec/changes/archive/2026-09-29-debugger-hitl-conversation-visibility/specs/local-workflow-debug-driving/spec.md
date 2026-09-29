# Spec Delta

> req: LDD-006

## ADDED Requirements

### Requirement: Session snapshots carry the parsed HITL prompt card and the node's last feedback

A debug session snapshot's pending-request projection SHALL carry, in addition to the
carried request id, phase, mode, node-authored title, and advertised options, a
presentation-ready typed prompt card parsed from the node-authored context when that
context follows the published hitl1 context schema: the goal summary, proposed
dimensions, missing fields, recognized fields, remaining accepted-answer rounds,
remaining unrecognized-retry rounds, the localized guidance, and a bounded answer
example. The projection SHALL NOT require any caller to parse machine JSON, and SHALL
leave the card absent when the context does not follow the published schema (no
fabricated card, while title, mode, and options remain carried).

The projection SHALL also carry the node's most recent typed feedback for the pending
conversation: taken from the checkpoint interrupt's own interaction projection when it
carries feedback, and otherwise from the Bundle's durable state interaction feedback
when present. The feedback is a carried projection, never lifecycle authority.
(`LDD-006`)

#### Scenario: A schema-following context becomes a typed card
- **WHEN** a session stops at a hitl1 request whose node-authored context follows the
  published context schema
- **THEN** the snapshot's pending-request projection carries the parsed card fields
  (goal, proposed dimensions, missing fields, remaining rounds, guidance, example)
  alongside the carried title, mode, and options

#### Scenario: Feedback follows the interaction projection first, durable state second
- **WHEN** the checkpoint interrupt carries an interaction projection with feedback,
  or carries none while the Bundle's durable state records interaction feedback
- **THEN** the projection reports that feedback as the node's last feedback, and
  reports none when neither channel has one

#### Scenario: An unparsed context stays honest
- **WHEN** the pending request's context does not follow the published schema
- **THEN** the projection carries no prompt card and does not fabricate card fields,
  while the title, mode, and advertised options remain carried as before
