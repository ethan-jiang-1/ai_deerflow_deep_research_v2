> req: RWB-009

## ADDED Requirements

### Requirement: Read-only diagnosis is available for non-terminal bundles

The local session workbench's read-only diagnosis projection SHALL be available
for a Run Bundle whose journal is present and consistent regardless of the
bundle's terminal disposition: a suspended or otherwise non-terminal bundle
with a complete journal SHALL yield an available diagnosis view carrying its
observed summary and events, so an operator can inspect what a recoverable run
was doing before deciding to resume or discard it. Existing refusal semantics
SHALL be unchanged for absent journals, invalid bundle references, and
unreadable or inconsistent records, and the diagnosis SHALL remain presentation
only — never a lifecycle or recovery authority. (`RWB-009`)

#### Scenario: A suspended bundle with a complete journal is inspectable
- **WHEN** the diagnosis projection reads a suspended bundle whose journal
  manifest and records are present and consistent
- **THEN** the view is available with the bundle's observed summary and recent
  events, regardless of the bundle's non-terminal status

#### Scenario: Existing refusal semantics are unchanged
- **WHEN** the diagnosis projection reads a bundle whose journal is absent,
  whose bundle reference is invalid, or whose records are unreadable or
  inconsistent
- **THEN** the view is unavailable exactly as before, and no recovery or
  lifecycle authority is implied by any diagnosis output
