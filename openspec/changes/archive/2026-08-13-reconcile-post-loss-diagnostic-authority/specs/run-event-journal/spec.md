## MODIFIED Requirements

### Requirement: An admitted Run has one correlated event journal before execution

After the Bundle lifecycle has admitted a valid Run and before any graph producer can
execute, the system SHALL establish that Run's Event Journal in the selected Bundle's
protected diagnostics subtree. The Journal shares the Bundle's supported lifetime: it
SHALL NOT be persisted as an external Run observation, read after Bundle deletion, or
presented to a participant after Bundle loss. Its identity is the admitted opaque
`bundle_id`; it does not prove the Bundle exists, select a Bundle, or authorize
execution. Every retained event SHALL have a schema version, a stable monotonically
increasing Bundle-local journal sequence, timestamp, refinement generation, phase, and
bounded event kind. Where a work item or attempt exists, the event SHALL retain its
bounded `work_id` and `attempt_id`. The Event Journal SHALL distinguish a process fact
from a terminal diagnostic conclusion and from ephemeral progress rendering. This
requirement does not assert physical secure erasure or that storage has no residual
bytes; residual bytes, if any, are not a supported Journal reader or participant
presentation. (`REJ-001`)

#### Scenario: First graph event is retained for a newly admitted Run
- **WHEN** a newly admitted Run starts graph execution before its first returned
  lifecycle projection
- **THEN** read-only inspection can find the journal's admitted execution and first
  graph event with the same Bundle correlation, generation, and phase

#### Scenario: A later refinement does not merge with an earlier generation
- **WHEN** one retained Bundle begins a later legal refinement generation
- **THEN** events from both generations remain distinguishable by their retained
  generation facts without creating a new lifecycle identity or Bundle locator

#### Scenario: A rejected request does not create a ghost journal
- **WHEN** a request is rejected before the Bundle lifecycle admits a Run
- **THEN** the caller receives only its immediate safe result and no Bundle or persistent
  Event Journal is created for that request

### Requirement: Event journal inspection is read-only and safe for people and agents

Supported inspection SHALL expose only an available selected Bundle's bounded Journal
health, sequence, generation, phase, event kind, work/attempt correlation, validation
stage, closed final response shape when present, canonical validation codes, safe
failure category, and opaque diagnostic reference when independently available. It
SHALL derive no lifecycle state from event ordering and SHALL not use a journal,
diagnostic, or progress event to start, resume, cancel, refine, route, recover, or
recreate a Run. A missing, malformed, foreign, or post-loss Journal produces an
unavailable bounded observation result; inspection SHALL NOT seek, read, or present an
external historical Journal, diagnostic, or Support Handoff. Support Handoff remains a
planned capability and, if implemented, SHALL not create a post-loss Journal reader.
The absence of a supported reader or participant presentation does not assert that
physical storage contains no residual bytes. (`REJ-004`)

#### Scenario: Operator inspection explains a failed attempt without granting control
- **WHEN** an operator inspects a retained Run with a failed validated work attempt
- **THEN** the inspection displays its safe correlation, validation stage, applicable
  response shape, and canonical facts but offers only the legal action supplied by the
  typed Bundle lifecycle result

#### Scenario: Bundle loss removes retained diagnostic evidence
- **WHEN** an admitted Bundle is deleted or becomes unavailable
- **THEN** inspection reports the Bundle and its Event Journal unavailable, does not
  read or present an external Journal, diagnostic, or Support Handoff, and offers no
  journal-derived recovery
