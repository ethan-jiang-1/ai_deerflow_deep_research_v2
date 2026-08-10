> req: RUS-001, RUS-002, RUS-003, RUS-004, RUS-006, RUS-007, RUS-008

## ADDED Requirements

### Requirement: Retained session inspection exposes truthful event-journal observations

For an available selected Bundle, retained-session inspection SHALL expose the
Bundle-local Event Journal only as a bounded read-only observation. It SHALL disclose its health and
the permitted safe correlation and failure facts defined by `run-event-journal`, and it
SHALL mark legacy events that cannot establish the required generation, correlation, or
completeness facts as incomplete rather than inventing them. It SHALL not expose a
retained root, Bundle path, checkpoint, session binding, raw diagnostic body, provider
body, prompt, answer, credential, full URL, or host path. Journal inspection remains
independent of lifecycle authority and cannot change a selected Bundle result. (`RUS-008`)

#### Scenario: Read-only inspection exposes a specific validation rule
- **WHEN** an available selected Bundle has a complete journal containing a failed work
  validation event
- **THEN** supported inspection exposes its bounded generation, phase, work id, attempt
  id, and canonical validation code without exposing the validation message or a control
  action derived from the event

#### Scenario: Legacy correlation remains explicitly incomplete
- **WHEN** an otherwise readable retained journal lacks a required correlation fact from
  an earlier schema
- **THEN** inspection marks the journal incomplete and does not infer the missing fact
  from event order, a checkpoint, or a Bundle path

#### Scenario: Inspection has no external diagnostic fallback after Bundle loss
- **WHEN** a selected Bundle is unavailable or has been deleted
- **THEN** inspection returns an unavailable Journal observation without reading a
  historical external record, and the shared lifecycle result has no journal-derived
  resume or recovery

## MODIFIED Requirements

### Requirement: A canonical local Run Bundle is discovered within trusted scope

An available local Deep Research Run SHALL be represented directly by one contained Run
Bundle whose opaque `bundle_id` is its only Run/control identity. Local demo retention
uses `deep_research_harness/.deep-research-demo-runs/`; every retained per-Run
diagnostic observation SHALL remain in the selected available Bundle's protected
diagnostics subtree. The trusted conversation scope may contain any number of retained
ended Bundles and at most one active Bundle. Discovery SHALL inspect only those actual
directories and their Bundle-local State; it SHALL not publish a global diagnostic root,
manifest/index/session record, or external observation as a Run locator, active pointer,
recovery source, or post-loss diagnostic source. A retained diagnostic/session projection
may describe a Bundle result while that Bundle is available but SHALL not alter existence,
lifecycle, or retention truth. (`RUS-001`)

#### Scenario: Available Bundle is discovered without a session index
- **WHEN** a trusted local context has no Current Bundle Handle and exactly one active available Bundle
- **THEN** the runtime selects that Bundle from scoped directories/State and does not read a session index or retained manifest

#### Scenario: Ended Bundles remain inspectable without blocking a fresh Run
- **WHEN** a trusted scope contains retained ended Bundles and no active Bundle
- **THEN** supported inspection may target an available Bundle id and a fresh start may publish a distinct Bundle without reusing session metadata

### Requirement: A bounded Bundle-local Journal records verified lifecycle observations

Any retained lifecycle observation SHALL be represented only in the selected Bundle's
bounded, redacted Event Journal. It retains the existing sequence, size, safe-category,
pending-input-summary, and no-raw-data guarantees, but records a bounded `bundle_id`
only where that disclosure is valid. A Journal, timeline, manifest, or diagnostic reader
SHALL not invoke a provider, authorize a Bundle selection, provide pending-response
correlation, infer a lifecycle result when Bundle-local State is unavailable, or seek an
external historical observation after Bundle loss. (`RUS-002`)

#### Scenario: Journal cannot authorize a deleted Run
- **WHEN** a selected Bundle is deleted or unavailable
- **THEN** no retained lifecycle observation is available through inspection and all control and inspection resolution returns the shared unavailable outcome

### Requirement: Local developer inspection resolves a safe run reference

Local developer inspection SHALL accept only a bounded `bundle_id` selected through the
same trusted-scope lifecycle result as other Deep Research controls. It SHALL not accept
or expose a session reference, raw root, provider key, checkpoint namespace, or legacy
research identity. Inspection may read only the selected available Bundle's contained
diagnostics. An unavailable, foreign, or deleted Bundle SHALL return a bounded unavailable
observation; inspection SHALL not create, recover, rebind, resume, or seek an external
historical Journal or diagnostic record for the Run. (`RUS-003`)

#### Scenario: Inspection cannot revive a deleted Run
- **WHEN** a developer supplies the former id of a deleted Bundle
- **THEN** inspection returns unavailable, performs no provider, graph, State, or content
  write, and returns no historical Journal or terminal diagnostic from another location

### Requirement: Retained session diagnosis is summarized, correlated, and redacted

Retained summaries, event journals, manifests, and terminal diagnostic observations SHALL
remain inside the selected Bundle's protected diagnostics subtree. For Deep Research they
SHALL correlate only to the typed Bundle result and, where disclosure is valid, its
`bundle_id`; they SHALL not retain or accept `research_id`, a Bundle locator/path, a
session binding, or an external checkpoint as a lifecycle identity or recovery source.
Their absence, corruption, retention loss, or Bundle deletion is an observation condition
only and cannot alter the typed lifecycle result. The system SHALL NOT retain an external
diagnostic, Support Handoff, or fallback Journal after Bundle loss. (`RUS-004`, `RUS-006`)

#### Scenario: Retained diagnosis outlives a Bundle without reviving it
- **WHEN** an event journal, summary, or terminal diagnostic was contained by a selected
  Bundle that is later deleted
- **THEN** inspection reports the Bundle and its diagnostics unavailable, does not disclose
  a historical external copy, and cannot derive a target, open a provider, recreate State,
  or re-enable a control

### Requirement: Retained session material is observation-only after Bundle authority migration

Any retained session manifest, trace, diagnostic, or historical inspection material that is
readable by Deep Research SHALL be contained by an available Run Bundle and remain an
observation of that Bundle's outcome only. It SHALL not establish a Run's existence, select
an active Run, authorize status/control, recover a missing Bundle, or block a fresh
independent Run. Its projections SHALL use the available Bundle result when one exists and
SHALL report a lost Bundle and its Journal as unavailable without fabricating a terminal
State or consulting an external historical record. (`RUS-007`)

#### Scenario: Retained record cannot recover a deleted Run
- **WHEN** a Run Bundle is deleted
- **THEN** inspection exposes no historical session material, and no session operation can
  reopen, resume, cancel, or recreate that Run
