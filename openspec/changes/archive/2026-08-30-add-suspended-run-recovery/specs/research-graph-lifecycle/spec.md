> req: REG-023

## ADDED Requirements

### Requirement: A suspended bundle without pending input is legally recoverable

When a Run Bundle's lifecycle projects an active suspended state whose pending
request id is absent — a process death that interrupted graph execution after a
human request was already consumed — the lifecycle SHALL project
`legal_next_action = RESUME` for that bundle, and the resume path SHALL
continue the run from its durable graph checkpoint without requiring or
fabricating any human response. Such a resume SHALL hold the existing execution
exclusion lease, SHALL re-enter the existing compiled graph at its persisted
checkpoint, and SHALL NOT write terminal state, mutate terminal invariance for
other bundles, or bypass any gate. A bundle whose suspended state carries a
pending human request SHALL keep the existing answer-resume path unchanged, and
terminal bundles SHALL keep REFINE/START unchanged. (`REG-023`)

#### Scenario: Orphaned mid-flight bundle projects RESUME
- **WHEN** the lifecycle projects a suspended bundle whose pending request id
  is absent and no live execution lease is held
- **THEN** the projected legal next action is RESUME rather than REFINE or
  STATUS

#### Scenario: Orphan resume continues from the durable checkpoint without a fabricated answer
- **WHEN** the resume path executes for such a bundle
- **THEN** the graph re-enters at its persisted checkpoint under the execution
  exclusion lease, no human response is constructed or required, and the run
  proceeds through its normal phase machinery to a natural terminal

#### Scenario: Pending-input and terminal contracts are unchanged
- **WHEN** a suspended bundle carries a pending human request, or a bundle is
  terminal
- **THEN** the projected legal next action matches the pre-change contract
  exactly (RESUME via answer for pending input; REFINE/START for terminals)
