# targeted-evidence-loop Delta

> req: TEL-008

## ADDED Requirements

### Requirement: A gap-less drained visit is a disclosed no-op fact

When a targeted-evidence visit finds no recorded unresolved searchable gaps, the node
SHALL complete as the existing drained no-op (route `next`, canonical empty gate view,
no planned or reconciled work) and SHALL record one node-level no-op fact in the run
journal carrying the closed reason `drained_no_op` and the observed gap count `0`. The
fact SHALL NOT carry gap bodies, worker output, or any non-closed value, and SHALL be
absent on visits that dispatch gap workers. This makes a repair loop that re-enters
targeted evidence with nothing to do directly visible as a repeated no-op pattern in
the journal.

#### Scenario: A gap-less visit records the no-op fact
- **WHEN** targeted evidence runs with an empty `unresolved_gaps` control field
- **THEN** the node completes as a drained no-op routing `next` and the journal carries
  one targeted-evidence node fact with the closed `drained_no_op` reason and gap
  count `0`

#### Scenario: A working visit records no no-op fact
- **WHEN** targeted evidence runs with at least one recorded unresolved searchable gap
  and dispatches gap workers
- **THEN** no `drained_no_op` fact is recorded for that visit
