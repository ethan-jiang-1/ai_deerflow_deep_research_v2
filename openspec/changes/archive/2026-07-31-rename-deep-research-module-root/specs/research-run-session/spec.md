> req: RUS-001

## MODIFIED Requirements

### Requirement: A canonical local run bundle is a discoverable derived session

The session runtime SHALL use
`deerflow_research/.deep-research-demo-runs/` as its default retained root and
`deerflow_research/.reports/deep-research-diagnostics/` as its default global
diagnostic-journal root after the checkout rename. It SHALL provide one explicit,
operator-confirmed local migration for the corresponding old `agent/` roots before
session inspection, discovery, resume, or global-diagnostic lookup relies on the new
defaults. The operator SHALL quiesce Deep Research processes before migration.

The command SHALL require an explicit confirmation, accept only contained regular
files beneath those two source roots, stage copies before publication, and preserve the
old roots. For each destination root, an absent source is `not_present`, an absent
destination is copied, and an existing destination succeeds as `already_migrated` only
when its complete relative regular-file tree is byte-equivalent to the source; every
other existing destination, symlink, unsupported entry, source-read failure, staging
failure, or mismatch SHALL fail closed without overwriting or deleting either source
or published destination. A partial two-root outcome SHALL be reported as partial and
remain safely retryable under those same equivalence rules; it SHALL never be reported
as a complete migration.

The migration SHALL not copy `.env`, `.venv`, arbitrary module files, secrets, test or
release reports outside the named diagnostic-journal root, or untrusted symlinks. The
operator SHALL separately copy/recreate `.env` through an approved secret-handling
path and rebuild `.venv`. Legacy data remains untouched until the operator explicitly
removes it after confirming the copied state; reverting the tracked rename SHALL not
modify operator-migrated local data. (`RUS-001`)

#### Scenario: Operator migrates an intact retained root once
- **WHEN** the quiesced old retained root and diagnostic-journal root exist, their
  new counterparts are absent, and the operator confirms migration
- **THEN** the runtime creates byte-equivalent new roots without deleting or modifying
  either old root, and a later invocation reports `already_migrated` for each
  equivalent destination

#### Scenario: Conflict fails without data loss
- **WHEN** a target root has a different relative entry or bytes from its old source
- **THEN** that root fails before overwrite or deletion, reports a bounded conflict,
  and leaves both roots available for operator inspection

#### Scenario: Unsafe local material is excluded
- **WHEN** the old module root contains a `.env`, `.venv`, symlink, test/release
  report, or file outside the named retained-state and diagnostic-journal roots
- **THEN** migration does not read, copy, or delete it

#### Scenario: One root cannot masquerade as a complete two-root migration
- **WHEN** a staged retained-root copy succeeds but the diagnostic-journal root cannot
  be published or verified
- **THEN** the command reports a bounded partial outcome, preserves both old roots,
  and a later confirmed invocation may complete only the missing root
