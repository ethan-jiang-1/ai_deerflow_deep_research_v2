> req: RUS-001, RUS-002, RUS-003, RUS-004, RUS-006, RUS-007

## ADDED Requirements

### Requirement: Retained session material is observation-only after Bundle authority migration

Any retained session manifest, trace, diagnostic, or historical inspection material
that remains after migration SHALL be an observation of a Run Bundle outcome only. It
SHALL not establish a Run's existence, select an active Run, authorize status/control,
recover a missing Bundle, or block a fresh independent Run. Its projections SHALL use
the available Bundle result when one exists and SHALL report a lost Bundle as
unavailable without fabricating a terminal State. (`RUS-007`)

#### Scenario: Retained record cannot recover a deleted Run
- **WHEN** a retained session record survives after its referenced Run Bundle is deleted
- **THEN** inspection may expose bounded historical observation facts but no session operation can reopen, resume, cancel, or recreate that Run

## RENAMED Requirements

- FROM: `### Requirement: A canonical local run bundle is a discoverable derived session`
- TO: `### Requirement: A canonical local Run Bundle is discovered within trusted scope`
- FROM: `### Requirement: A bounded lifecycle trace records verified session facts`
- TO: `### Requirement: A bounded lifecycle trace records verified Bundle lifecycle observations`

## MODIFIED Requirements

### Requirement: A canonical local Run Bundle is discovered within trusted scope

An available local Deep Research Run SHALL be represented directly by one contained Run
Bundle whose opaque `bundle_id` is its only Run/control identity. Local demo retention
uses `deep_research_harness/.deep-research-demo-runs/`; optional global diagnostic
observations use `deep_research_harness/.reports/deep-research-diagnostics/`. Neither
root is a recovery source or an old-root fallback. The trusted
conversation scope may contain any number of retained ended Bundles and at most one
active Bundle. Discovery SHALL inspect only those actual directories and their
Bundle-local State; it SHALL not publish a manifest/index/session record as a Run
locator, active pointer, or recovery source. A retained diagnostic/session projection
may describe a Bundle result but SHALL not alter existence, lifecycle, or retention
truth. (`RUS-001`)

#### Scenario: Available Bundle is discovered without a session index
- **WHEN** a trusted local context has no Current Bundle Handle and exactly one active available Bundle
- **THEN** the runtime selects that Bundle from scoped directories/State and does not read a session index or retained manifest

#### Scenario: Ended Bundles remain inspectable without blocking a fresh Run
- **WHEN** a trusted scope contains retained ended Bundles and no active Bundle
- **THEN** supported inspection may target an available Bundle id and a fresh start may publish a distinct Bundle without reusing session metadata

### Requirement: Local developer inspection resolves a safe run reference

Local developer inspection SHALL accept only a bounded `bundle_id` selected through the
same trusted-scope lifecycle result as other Deep Research controls. It SHALL not accept
or expose a session reference, raw root, provider key, checkpoint namespace, or legacy
research identity. An unavailable/foreign/deleted Bundle SHALL return a bounded
observation outcome; inspection SHALL not create, recover, rebind, or resume the Run.
(`RUS-003`)

#### Scenario: Inspection cannot revive a deleted Run
- **WHEN** a developer supplies the former id of a deleted Bundle while a retained session record remains
- **THEN** inspection returns unavailable and performs no provider, graph, State, or content write

### Requirement: A bounded lifecycle trace records verified Bundle lifecycle observations

Any retained `diagnostics/lifecycle.jsonl` trace SHALL be a bounded, redacted,
atomically published observation of a shared typed Bundle lifecycle result. It retains
the existing sequence, size, safe-category, pending-input-summary, and no-raw-data
guarantees, but records a bounded `bundle_id` only where that disclosure is valid. A
trace, timeline, manifest, or diagnostic reader SHALL not invoke a provider, authorize
a Bundle selection, provide pending-response correlation, or infer a lifecycle result
when Bundle-local State is unavailable. (`RUS-002`)

#### Scenario: Trace cannot authorize a deleted Run
- **WHEN** a valid retained lifecycle trace refers to an externally deleted Bundle
- **THEN** it remains a bounded historical observation and all control/inspection
  resolution returns the shared unavailable outcome

### Requirement: Retained session diagnosis is summarized, correlated, and redacted

Retained summaries, event journals, manifests, and diagnostic observations MAY preserve
the existing bounded redaction, causal ordering, provider-recovery observation, and
atomic-publication guarantees. For Deep Research they SHALL correlate only to the
typed Bundle result and, where disclosure is valid, its `bundle_id`; they SHALL not
retain or accept `research_id`, a Bundle locator/path, a session binding, or an external
checkpoint as a lifecycle identity or recovery source. Their absence, corruption, or
continued presence after Bundle loss is an observation condition only and cannot alter
the unavailable result. (`RUS-004`, `RUS-006`)

#### Scenario: Retained diagnosis outlives a Bundle without reviving it
- **WHEN** an event journal and summary remain after the selected Bundle is deleted
- **THEN** they may disclose their permitted safe historical facts but cannot be used to
  derive a target, open a provider, recreate State, or re-enable a control
