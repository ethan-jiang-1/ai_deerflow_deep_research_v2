> req: REG-015, REG-016

## ADDED Requirements

### Requirement: Correlated human input supports advertised closed actions

The existing graph-owned human-input protocol SHALL support `response_kind=action` in
addition to text and choice without making action strings implicit text authority. A
pending request SHALL advertise a bounded closed `action_ids` collection separate from
the existing HITL2 choice `options`; an action response SHALL carry exactly one
advertised `action_id`. Direct and brokered resume SHALL preserve request/message
correlation and reject an action that is unadvertised, mismatched, replayed, malformed,
or encoded as text before node execution. HITL1 may advertise only `accept_suggestion`;
other nodes retain their existing response modes and no action may alter lifecycle
identity or routing outside its owning node. (`REG-015`)

#### Scenario: Advertised action passes correlation checks
- **WHEN** a pending HITL1 request advertises `accept_suggestion` and a matching typed action response arrives
- **THEN** the generic extractor accepts that action once and HITL1 decides its profile effect from checkpointed proposal state

#### Scenario: Text cannot spoof a closed action
- **WHEN** a response sends `accept_suggestion` as ordinary text or sends an action not advertised by the pending request
- **THEN** generic validation rejects it before graph-node execution and no response is consumed

### Requirement: Canonical bundle locator is checkpointed physical-root state

`ResearchState` SHALL carry a bounded optional controller-owned `bundle_directory` that
selects the canonical physical root for graph content artifacts and retained session
metadata. Every new lifecycle start, including an all-fake recipe, sets the trusted
timestamp-prefixed locator before graph invocation; it is not derived from user input,
mutable by nodes/workers, or a replacement for `research_id`. A full-fake locator SHALL
remain session-metadata-only and SHALL not imply graph artifact materialization.
Compatible existing checkpoints without the field SHALL deterministically use legacy
`r_<research-id>` roots without migration. (`REG-016`)

#### Scenario: Locator does not replace lifecycle identity
- **WHEN** a new timestamp-prefixed locator is checkpointed
- **THEN** research scope, namespace derivation, binding, marker identity, and CLI inspect argument remain the opaque `research_id`

#### Scenario: Full-fake run has a stable metadata-only locator
- **WHEN** a new all-fake lifecycle starts
- **THEN** its checkpoint and retained session use the same trusted timestamp-prefixed locator, while inspect continues to identify the content layout as session metadata only unless a real bootstrap marker exists
