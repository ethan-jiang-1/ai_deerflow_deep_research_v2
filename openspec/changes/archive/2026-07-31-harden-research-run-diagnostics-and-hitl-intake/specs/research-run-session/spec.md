## ADDED Requirements

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
