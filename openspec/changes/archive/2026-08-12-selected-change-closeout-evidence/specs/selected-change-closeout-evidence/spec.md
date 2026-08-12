## MODIFIED Requirements

### Requirement: Closeout evidence remains task-led and non-authoritative

For a `boundary-verified` range, the capability SHALL allow a structured evidence
record with only the non-authoritative dispositions `review-required` or
`inconclusive`. A persisted record request SHALL supply the attestation again, and the
capability SHALL re-verify its Git facts in that same invocation immediately before it
writes the record; a receipt from an earlier invocation is inspection evidence only.
A `review-required` record SHALL include one or more non-empty references that exactly
match current unchecked task labels in the selected change's `tasks.md`; an
`inconclusive` record SHALL include a non-empty evidence limitation. When a caller
requests a persisted record, its resolved output path SHALL resolve within that
selected change's dedicated `guardrail-evidence/` subdirectory of the active change
root. The capability SHALL preserve the declared boundary and references in the record
without evaluating their semantic truth. It SHALL NOT create, complete, or rewrite
tasks; invoke, wrap, or block native OpenSpec archive; emit `clear`, `approved`, or
semantic-pass dispositions; or alter runtime behavior.

#### Scenario: An actionable finding stays in the normal task ledger
- **WHEN** a reviewer records a `review-required` result for a verified boundary
- **THEN** the record retains the exact boundary and one or more references to
  ordinary unfinished tasks, while the capability does not write those tasks itself

#### Scenario: Uncertainty is recorded without fabricated clearance
- **WHEN** a reviewer cannot establish sufficient evidence for a verified boundary
- **THEN** the capability records `inconclusive` with its stated evidence limitation
  and does not substitute a semantic-pass or archive-ready result

#### Scenario: A stale task reference cannot create a review record
- **WHEN** a `review-required` payload names a task label that is absent or no longer
  unchecked in the selected change's `tasks.md`
- **THEN** the capability rejects the payload without writing a closeout-evidence
  record or modifying the task ledger

#### Scenario: Persistent evidence cannot escape the selected change
- **WHEN** a caller requests an output path that resolves outside the selected
  change's dedicated `guardrail-evidence/` subdirectory (including a change artifact
  such as `tasks.md` or `proposal.md`)
- **THEN** the capability rejects the output request without writing any record

#### Scenario: A prior receipt cannot authorize a later persisted record
- **WHEN** Git state changes after an earlier boundary receipt and before a caller
  requests persisted closeout evidence
- **THEN** the capability re-verifies the supplied attestation, returns
  `missing-boundary` when the current state no longer satisfies it, and writes no
  evidence record

#### Scenario: Boundary failure has no operational side effect
- **WHEN** boundary verification returns `missing-boundary`
- **THEN** the capability does not create or modify a task, invoke archive, or change
  native OpenSpec operation state
