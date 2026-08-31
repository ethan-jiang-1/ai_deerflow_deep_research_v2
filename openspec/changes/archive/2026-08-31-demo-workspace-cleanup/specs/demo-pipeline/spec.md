# demo-pipeline Delta

> req: DPL-014

## ADDED Requirements

### Requirement: Demo operator workspace exposes a read-only report and a guarded cleanup through the soft-bundle handle

The demo-pipeline operator handle SHALL provide a `workspace-report` verb and a
`workspace-clean` verb over the local demo workspace; the pre-existing `clean`
verb (archive prior runs with bounded retention) SHALL keep its current semantics. The report SHALL list every run bundle
found under the workspace scopes with its opaque bundle id, its lifecycle status
read from the bundle's own run summary (`completed`, `stopped`, `cancelled`, or
`blocked` are terminal), and its content size, SHALL flag every non-terminal bundle
as resumable, SHALL summarize the log and archive subtrees separately, and SHALL
state that it is an operator view over local files rather than a lifecycle
authority. The workspace-clean verb SHALL default to a dry run that lists what would be
deleted and what would be kept without deleting anything, SHALL delete only
terminal bundle directories and their soft-bundle records, and only when an
explicit confirmation (`CONFIRM=1`) is set, SHALL neither modify nor delete
non-terminal bundles or the soft-bundle root, SHALL clean log files only through a
separate explicit logs scope under the same confirmation gate, and SHALL print an
exact-bundle baseline invalidation warning after any deletion. A bundle whose run
summary cannot be read SHALL be treated as non-terminal. The bounded auto-run
retention policy (DPL-007) remains unchanged. (`DPL-014`)

#### Scenario: Report inventories bundles with lifecycle status

- **WHEN** the operator runs the workspace report
- **THEN** every bundle under the workspace scopes is listed with its bundle id,
  lifecycle status, and size, non-terminal bundles are flagged resumable, log and
  archive subtrees are summarized separately, and the output states its
  operator-view (non-authority) posture

#### Scenario: Cleanup defaults to a dry run

- **WHEN** the operator runs the workspace-clean verb without the confirmation flag
- **THEN** nothing is deleted, and the output lists would-delete (terminal) and
  would-keep (non-terminal) entries

#### Scenario: Confirmed cleanup deletes only terminal bundles

- **WHEN** the operator runs the workspace-clean verb with `CONFIRM=1`
- **THEN** only terminal bundle directories and their soft-bundle records are
  deleted, and a baseline invalidation warning is printed

#### Scenario: Non-terminal bundles are never modified

- **WHEN** a cleanup runs in dry-run or confirmed mode over a workspace containing
  a suspended or otherwise non-terminal bundle
- **THEN** that bundle's directory and its soft-bundle record are neither modified
  nor deleted, and it remains attachable

#### Scenario: Unreadable status is treated as non-terminal

- **WHEN** a bundle's run summary is missing or undecodable
- **THEN** the report flags it as non-terminal (status unknown) and the cleanup
  keeps it

#### Scenario: Logs are cleaned only through the separate scope

- **WHEN** the workspace-clean verb runs without the logs scope, or with the logs
  scope but without `CONFIRM=1`
- **THEN** log files are not deleted; with the logs scope and `CONFIRM=1` they are

#### Scenario: Auto-run retention policy is unchanged

- **WHEN** any demo run executes its pre-run sweep, or the operator invokes the
  pre-existing `clean` verb
- **THEN** the bounded archive-retention behavior (DPL-007) is unchanged by this
  requirement, and its interaction with resumable bundles remains a recorded
  known interaction outside this cleanup surface
