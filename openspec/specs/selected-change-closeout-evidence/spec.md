# Selected Change Closeout Evidence Specification

> req: SCC-001, SCC-002, SCC-003

## Purpose

Defines bounded, reproducible evidence for a selected OpenSpec change review without
equating an advisory review record with semantic approval or archive authority.

## Requirements

### Requirement: A selected-change boundary is explicit and Git-verified

The closeout-evidence capability SHALL accept a caller- or adapter-declared boundary
attestation containing canonical `change_name`, repository identity, `base_commit`,
and `head_commit`, with the range interpreted only as `base..head`. It SHALL resolve
`change_name` to an active change root in the current OpenSpec planning home, verify
that the attestation names the current repository, both commits resolve locally,
`base_commit` is an ancestor of `head_commit`, current `HEAD` equals `head_commit`,
and the worktree is clean. For a valid attestation, it SHALL emit a structured record
that binds those exact inputs and a deterministic diff summary. A verified boundary
record SHALL not claim semantic clearance or that all worktree changes were reviewed.

#### Scenario: A committed range is recorded exactly
- **WHEN** a caller supplies a complete attestation for the current clean repository
  whose base is an ancestor of the current HEAD
- **THEN** the capability emits a `boundary-verified` record containing the canonical
  change name, repository identity, resolved base and head commits, and a diff
  summary for exactly `base..head`

#### Scenario: A shared worktree is not inferred as a selected range
- **WHEN** a caller supplies only a branch name, a file list, or an otherwise
  incomplete attestation
- **THEN** the capability emits `missing-boundary` without scanning the worktree or
  claiming selected-change coverage

#### Scenario: A boundary cannot bind an unknown or archived change
- **WHEN** the attestation's `change_name` does not resolve to an active change root
  in the current planning home
- **THEN** the capability emits `missing-boundary` with an `unknown-change` condition
  and does not create an evidence record

#### Scenario: An attestation cannot outlive the verified repository state
- **WHEN** the declared repository differs, either commit cannot resolve, the base
  is not an ancestor of the head, HEAD differs from the declared head, or the
  worktree is dirty
- **THEN** the capability emits `missing-boundary` with the failed deterministic
  condition and emits no coverage or semantic-clearance claim

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
tasks; invoke, wrap, or block native OpenSpec archive; emit `clear`,
`approved`, or semantic-pass dispositions; or alter runtime behavior.

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

### Requirement: Boundary evidence has deterministic local coverage

The project SHALL retain zero-API deterministic fixtures for the boundary and record
contract. The fixtures SHALL cover one valid committed range and each rejection for an
unknown change, missing field, wrong repository, unknown commit, non-ancestor range,
HEAD drift, and dirty worktree. They SHALL assert the exact record class and the
absence of task or archive side effects. The fixtures SHALL not use provider
credentials, model evaluation, or a full-worktree coverage claim.

#### Scenario: The verifier rejects every defined invalid boundary class
- **WHEN** the deterministic fixture suite exercises each defined invalid boundary
  class
- **THEN** each case records `missing-boundary` and the suite demonstrates no task or
  archive side effect
