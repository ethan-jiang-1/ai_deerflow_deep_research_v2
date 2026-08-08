# research-run-session Specification

> req: RUS-001, RUS-002, RUS-003, RUS-004, RUS-005, RUS-006, RUS-007

## Purpose

Define retained local run bundles, bounded lifecycle observations, and safe session
inspection without creating an alternative lifecycle controller.
## Requirements

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

### Requirement: Retained Wave0 diagnosis preserves closed worker failure classes

The retained event journal and terminal diagnosis projection SHALL carry only the
closed Wave0 worker-failure classification defined by
`deep-research-wave0-worker-failure-classification`.  An `attempt` event SHALL expose
the exact terminal attempt class.  An `exhaustion` event and terminal incident for one
work item SHALL expose that class when all failed attempts agree, otherwise `mixed`.
The terminal incident SHALL retain its existing route failure code and carry this
aggregate in a separate optional diagnosis field. The ordered bounded timeline SHALL
remain available for per-attempt inspection. Legacy
events without a classification SHALL remain an unavailable observation.  No retained
summary, event, inspection, workbench, or CLI projection SHALL expose raw exception
text, traceback, model/tool content, URL, path, prompt, answer, or credential. (`RUS-005`)

#### Scenario: Exhaustion with one cause stays specific
- **WHEN** every failed attempt for a Wave0 work item has the same closed worker class
- **THEN** the attempt timeline, exhaustion event, and terminal incident carry that
  class with the existing diagnostic correlation reference

#### Scenario: Mixed attempts do not invent a root cause
- **WHEN** failed attempts for one Wave0 work item have different closed classes
- **THEN** each attempt event retains its own class while exhaustion and terminal
  diagnosis expose only `mixed`

#### Scenario: Hostile diagnostic content is rejected
- **WHEN** recorder or presentation input includes a raw exception, secret, host path,
  prompt, answer, URL, or provider/tool body alongside a worker category
- **THEN** the unsafe content is rejected or redacted before persistence and no view
  emits it

#### Scenario: Worker category is not a validation code
- **WHEN** an attempt fails with a worker category and has no submission validation
  result
- **THEN** its event stores the class only in a distinct closed worker-category field
  and leaves `validation_code` absent

### Requirement: Retained session diagnostics project classified workflow outcomes

For a record-bearing terminal lifecycle result, the retained session/event journal
SHALL project the checkpointed terminal incident or controller-derived worker failure
category, phase, safe diagnostic reference, and bounded recovery chronology when
available. The journal SHALL retain no raw exception, provider body, or prompt text,
and session inspection SHALL remain read-only rather than becoming a retry or resume
controller.

#### Scenario: A direct provider failure is inspectable without raw provider data
- **WHEN** a terminal topic-planning provider failure creates a retained run bundle
- **THEN** its session diagnostics contain the safe category, phase, diagnostic
  reference, and observed recovery disposition but not the raw timeout exception or
  provider response

#### Scenario: Inspection cannot alter a classified outcome
- **WHEN** an operator inspects a retained terminal session with workflow failure
  facts
- **THEN** inspection returns only the derived observation and cannot start a retry,
  resume the graph, or change the terminal incident

### Requirement: Supplied terminal diagnostics are published before retained projections

For every record-bearing terminal carrying an opaque diagnostic reference, the
retained-session store SHALL atomically publish a frozen bounded redacted diagnostic
record with that exact reference before publishing a terminal event, lifecycle trace,
summary, manifest diagnostic path, inspection projection, or terminal session view that
refers to it. For a provider-diagnostic terminal, `RecordBearingLifecycleFact` SHALL
carry the optional
`recovery_trigger_timeout_origin` and `final_timeout_origin` facts copied from their
corresponding terminal-incident observations; for every other terminal those origins
remain absent. The record SHALL retain only those role-bound origins and the existing
safe terminal facts. It SHALL not retain raw exceptions, prompts, answers, provider
bodies, credentials, full URLs, or host paths. The store SHALL never derive a
replacement reference when one was supplied.

For a later identical publication of that terminal fact, the store SHALL retain and
revalidate the same single frozen record rather than append a second matching JSONL
entry. A conflicting, duplicate, or malformed retained record SHALL make the diagnostic
proof unavailable; no later terminal projection may use it to claim bundle diagnostic
availability. (`RUS-004`, `RUS-006`)

`RecordBearingLifecycleFact` SHALL reject a diagnostic reference unless it is a terminal
fact with a non-null `failure_category` that passes the existing safe field validation.
That check SHALL not introduce a storage-local failure registry or synthesize a category;
a legacy or corrupted retained file that violates the relationship remains an unavailable
inspection observation and SHALL not receive a diagnostic record. (`RUS-004`, `RUS-006`)

The existing `RunSessionView.terminal_diagnostic_ref` SHALL be a publication-proof
projection: it SHALL equal the supplied reference only after that exact record has been
atomically written and revalidated, and SHALL be absent when that proof is unavailable.
It SHALL not copy diagnostic-record content or timeout origins. (`RUS-004`, `RUS-006`)

If bundle diagnostic publication cannot be verified, the resulting retained projection
SHALL not claim an available bundle diagnostic for that reference. Existing legacy
bundles without an origin or diagnostic record remain inspection-safe unavailable
observations and SHALL not be rewritten during inspection. (`RUS-004`, `RUS-006`)

#### Scenario: Supplied terminal reference is retained exactly once
- **WHEN** a terminal arrives with an already-derived opaque diagnostic
  reference and a writable contained bundle
- **THEN** the bundle diagnostic record contains that exact reference before every
  terminal event, trace, summary, manifest, and session view that exposes it, with each
  present trigger/final timeout origin preserved in its role

#### Scenario: Diagnostic-file failure cannot create a false retained record
- **WHEN** atomic publication of the bundle diagnostic record fails for a provider
  terminal with a supplied reference
- **THEN** no retained projection claims that the bundle contains the reference, while
  lifecycle authority and the existing terminal category remain unchanged

#### Scenario: Non-provider supplied reference is not skipped
- **WHEN** a non-provider record-bearing terminal arrives with an already-derived opaque
  diagnostic reference
- **THEN** the bundle publishes that exact reference before every terminal projection
  and retains both timeout-origin roles as absent

#### Scenario: Category-less diagnostic reference is not published
- **WHEN** a record-bearing terminal fact carries a diagnostic reference without a
  non-null failure category accepted by the existing safe field validation
- **THEN** validation rejects publication and inspection neither synthesizes a category
  nor writes a diagnostic record

#### Scenario: Trigger-only origin does not create a final origin
- **WHEN** a provider retry trigger has a bridge-budget timeout origin but its later
  terminal observation has no timeout origin
- **THEN** the retained record preserves the trigger origin, leaves the final origin
  absent, and does not infer either role from category or retry counts

#### Scenario: Every session publisher preserves observed origin roles
- **WHEN** `ResearchSessionOperationBroker` republishes a blocked provider terminal
  with a supplied reference and role-bound timeout origins
- **THEN** the resulting record-bearing fact, exact retained record, and read-only
  inspection preserve those same roles in one record without deriving a new reference,
  appending a duplicate, or replacing a missing role

#### Scenario: Inspection does not upgrade an older bundle
- **WHEN** inspection opens a legacy bundle without a diagnostic record or timeout
  origin
- **THEN** it reports only validated existing facts and does not write a record,
  synthesize an origin, or alter the terminal lifecycle outcome

### Requirement: Read-only inspection projects only an exact verified terminal diagnostic

When a contained bundle has a validated terminal summary/view reference, inspection MAY
strictly parse the known bounded diagnostic-record schema and expose a typed diagnostic
projection only when exactly one record carries that exact reference. The projection
SHALL contain only the opaque reference, closed category, bounded phase, and optional
role-bound `recovery_trigger_timeout_origin` and `final_timeout_origin`. It SHALL not
expose a diagnostic JSONL body, arbitrary artifact content, fingerprint, timestamp,
action, provider observation, raw exception, prompt, answer, credential, full URL, or
host path. A missing, malformed, duplicate, stale, or differently referenced record
SHALL produce no diagnostic projection and no inferred origin; it SHALL remain a
read-only unavailable diagnostic fact and SHALL not change inspectability, lifecycle
outcome, retry, resume, or any other control authority.
(`RUS-003`, `RUS-004`)

#### Scenario: Inspect renders the persisted timeout origin without rendering a record body
- **WHEN** a terminal summary and its contained diagnostic record share one exact
  reference, has `bridge_wall_time_budget` as its recovery trigger origin, and has
  `provider_sdk_timeout` as its final origin
- **THEN** inspection exposes both origins through their typed roles and does not expose
  the JSONL body or attribute either observation to the provider

#### Scenario: A mismatched diagnostic record is unavailable rather than guessed
- **WHEN** a contained diagnostic file is present but has no valid record matching the
  terminal summary/view reference
- **THEN** inspection exposes no diagnostic projection or timeout origin, performs no
  write, and leaves the validated terminal state and inspection-only boundary unchanged

#### Scenario: Duplicate matching records do not select a diagnosis
- **WHEN** a contained diagnostic file has more than one otherwise valid record carrying
  the terminal summary/view reference
- **THEN** inspection exposes no diagnostic projection or timeout origin and does not
  choose, merge, or rewrite either record

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
