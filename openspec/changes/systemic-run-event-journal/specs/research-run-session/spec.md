> req: RUS-008

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
