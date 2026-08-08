## ADDED Requirements

### Requirement: Work-unit terminal projection carries diagnosis without control authority

The shared work-unit component SHALL preserve one closed controller-owned worker failure
classification for each failed Wave0 attempt through its terminal update, checkpoint
projection, retry/exhaustion observation, and terminal incident input.  The
classification SHALL be additive diagnosis only: it SHALL NOT alter attempt identity,
status transition validity, retry eligibility, submission validation, ledger commit,
gate failure code/classification, or lifecycle route.  Legacy terminal updates lacking
the field SHALL remain readable as classification unavailable. (`WOU-010`)

#### Scenario: Categorized failure retries as before
- **WHEN** a classified failed attempt has remaining Wave0 retry budget
- **THEN** the component allocates the same next attempt and gate behavior it would
  have allocated before classification was added

#### Scenario: Category cannot forge control state
- **WHEN** a caller supplies an unknown/free-form worker category or a category that
  conflicts with the trusted terminal update
- **THEN** contract validation rejects it before checkpoint or event publication and
no ledger or gate authority changes

#### Scenario: Only typed validation rejection becomes a validation attempt
- **WHEN** the lower submission seam raises its frozen closed-code validation exception
- **THEN** the component creates its existing `validation_failed` terminal attempt with
  `submission_validation`, while any other submission/storage exception propagates
  unchanged
