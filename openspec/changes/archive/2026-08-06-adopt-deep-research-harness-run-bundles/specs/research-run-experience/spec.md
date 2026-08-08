> req: RER-001, RER-002, RER-003, RER-006, RER-007, RER-009, RER-013

## ADDED Requirements

### Requirement: Shared run experience projects Bundle-owned outcomes and legal actions

The runtime-owned run-experience module SHALL derive human-readable and AI-consumable
run updates from the shared typed Bundle lifecycle result. It SHALL distinguish active,
awaiting-input, ended, conflict/ambiguous, and unavailable outcomes without exposing a
checkpoint key, session reference, host path, raw exception, or derived `research_id`.
For each outcome it SHALL expose only the legal next action supplied by the lifecycle
contract; presentation text SHALL not authorize, retry, or recover a Run. (`RER-013`)

#### Scenario: Unavailable result has one truthful next action
- **WHEN** the lifecycle result reports an unavailable Bundle
- **THEN** the shared experience identifies that the Run cannot be resumed and offers a fresh independent Run or permitted observation only

## RENAMED Requirements

- FROM: `### Requirement: Shared run updates expose safe session inspection facts`
- TO: `### Requirement: Shared run updates expose safe Bundle inspection observations`

## MODIFIED Requirements

### Requirement: One runtime Module owns lifecycle-to-presentation interpretation

`ResearchRunExperience` SHALL retain one runtime-owned shared presentation interface
with the existing safe `Ready`, `Working`, `AwaitingInput`, `Terminal`, and `Fault`
updates. Its closed input vocabulary SHALL distinguish `Start`, correlated response/
visible-control submission for `resume`, `Cancel`, `Status`, and a separate bounded
`Refine` intent. The module consumes one shared typed Bundle lifecycle result; it does
not derive a `research_id`, keep a durable session or Bundle cache, construct a Bundle
path, or create an alternative graph/state authority. (`RER-001`)

#### Scenario: Run experience keeps refine distinct from a response
- **WHEN** an available Bundle awaits input and a presentation adapter submits a refinement
- **THEN** the module dispatches the separate `refine` intent and leaves the correlated
  pending response available only to its resume path

### Requirement: Public lifecycle projection distinguishes committed state from pending input

The public lifecycle projection SHALL retain the existing phase/pending-input
distinction, but both committed and pending facts are derived from the selected
Bundle-local Research State. The graph interrupt remains the delivery artifact; it is
not a durable source independent of that State. A projection never includes a path,
raw context, or external-checkpoint data and cannot override Bundle lifecycle truth.
(`RER-002`)

#### Scenario: Pending projection cannot survive Bundle loss as authority
- **WHEN** a presentation cache still contains an earlier pending-input projection after
  the selected Bundle is deleted
- **THEN** the next status/control result is unavailable and the cache cannot re-present
  a legal resume action

### Requirement: Failures are safe, categorized, and diagnosable

The existing source-owned closed failure categories, safe diagnostic references,
redaction, and legal-next-action guarantees SHALL remain unchanged. A record-bearing
observation is correlated only from a shared typed Bundle lifecycle result and, where
valid, its `bundle_id`; it cannot bind a `research_id`, session, path, or checkpoint as
a replacement Run authority. An external diagnostic may outlive Bundle loss, but it
cannot turn unavailable into ended, inspectable, resumable, or recoverable. (`RER-003`, `RER-009`)

#### Scenario: Diagnostic fallback does not create a live Run projection
- **WHEN** a safe provider diagnostic is retained after its Bundle becomes unavailable
- **THEN** presentation preserves the safe category/reference while projecting only the
  shared unavailable outcome and its legal next action

### Requirement: Shared run updates expose safe Bundle inspection observations

Shared run updates SHALL expose a bounded inspection observation only after the Bundle
lifecycle boundary returns an available selected Bundle result. The view uses the
opaque `bundle_id`, availability/retention fact, durability fact, and at most one
closed observation failure; it contains no session reference, host path, checkpoint
payload, or lifecycle authority. Publication/inspection failure cannot replace a valid
pending or terminal result, retry a lifecycle action, or alter Bundle-local State.
(`RER-006`)

#### Scenario: Inspection observation cannot revive a lost Bundle
- **WHEN** a previously published inspection observation refers to a deleted Bundle
- **THEN** both presentation adapters suppress control/inspection actions and display the
  typed unavailable result

### Requirement: Shared run updates project bounded intake feedback and observed run state

The existing bounded HITL1 feedback and returned-only progress guarantees remain
unchanged. Every shared update SHALL use an opaque `bundle_id` only where it is present
in the typed lifecycle result; it SHALL not expose or derive a `research_id`, session
reference, checkpoint key, or Bundle path. (`RER-007`)

#### Scenario: Shared update does not expose retired identity
- **WHEN** a lifecycle update is rendered for an available or unavailable Run
- **THEN** the adapter receives only its permitted `bundle_id` and typed outcome, not a
  conversation-derived identity or storage locator
