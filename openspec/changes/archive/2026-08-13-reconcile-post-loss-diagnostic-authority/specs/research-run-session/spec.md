## MODIFIED Requirements

### Requirement: Retained session diagnosis is summarized, correlated, and redacted

Retained summaries, event journals, manifests, and terminal diagnostic observations SHALL
remain inside the selected Bundle's protected diagnostics subtree. For Deep Research they
SHALL correlate only to the typed Bundle result and, where disclosure is valid, its
`bundle_id`; they SHALL not retain or accept `research_id`, a Bundle locator/path, a
session binding, or an external checkpoint as a lifecycle identity or recovery source.
Their absence, corruption, retention loss, or Bundle deletion is an observation condition
only and cannot alter the typed lifecycle result. The system SHALL NOT retain, read, or
present an external diagnostic, Support Handoff, or fallback Journal after Bundle loss.
This requirement makes no assertion about possible physical residual bytes after storage
deletion; such bytes are not a supported retained diagnostic, reader, or participant
presentation. Support Handoff remains planned and, if implemented, SHALL operate only
while its selected Bundle is available. (`RUS-004`, `RUS-006`)

#### Scenario: Retained diagnosis outlives a Bundle without reviving it
- **WHEN** an event journal, summary, or terminal diagnostic was contained by a selected
  Bundle that is later deleted or unavailable
- **THEN** inspection reports the Bundle and its diagnostics unavailable, does not
  disclose a historical external copy, and cannot derive a target, open a provider,
  recreate State, or re-enable a control

### Requirement: Retained session material is observation-only after Bundle authority migration

Any retained session manifest, trace, diagnostic, or historical inspection material that is
readable by Deep Research SHALL be contained by an available Run Bundle and remain an
observation of that Bundle's outcome only. It SHALL not establish a Run's existence, select
an active Run, authorize status/control, recover a missing Bundle, or block a fresh
independent Run. Its projections SHALL use the available Bundle result when one exists and
SHALL report a lost Bundle and its Journal as unavailable without fabricating a terminal
State or consulting an external historical record, diagnostic, or Support Handoff. This
supported-reader boundary does not claim that storage deletion removes every physical byte.
(`RUS-007`)

#### Scenario: Retained record cannot recover a deleted Run
- **WHEN** a Run Bundle is deleted
- **THEN** inspection exposes no historical session material, reads no external
  diagnostic or Support Handoff, and no session operation can reopen, resume, cancel,
  recreate, or diagnostically present that Run
