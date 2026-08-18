> req: SBC-002

## MODIFIED Requirements

### Requirement: Run research and bind the resulting bundle

The CLI SHALL run the selected operator mode using existing Harness entry surfaces, parse a valid `bundle_id` from the run output, resolve the repository-relative `bundle_local_path`, record it under `bundles/<bundle_id>.json`, and update the soft bundle manifest's `current_bundle_id`. Before invoking the operator mode, the CLI SHALL remove all prior run-bundle content under the operator workspace `deep-research` subtree so each control-environment run starts clean. The CLI SHALL perform local path resolution only after a valid `bundle_id` is available, and SHALL NOT use path scanning to discover or select a bundle. (`SBC-002`)

The CLI SHALL bind and record a resolved `bundle_id` whenever the run produced a
valid, resolvable bundle directory, **including when the operator entry exits
non-zero** (for example a blocked terminal): the manifest SHALL be updated to
`current_bundle_id` and the `bundles/<bundle_id>.json` record SHALL be written
before the CLI returns the run's own exit code. The CLI SHALL still return the
operator run's non-zero exit code so the blocked/failed status is preserved, SHALL
print the raw run output to stderr on that failure path so the underlying failure
reason stays visible, and SHALL NOT report the run as successful. A run that
produces no valid `bundle_id` or no resolvable bundle directory keeps the existing
behavior: it SHALL fail without binding and leave `current_bundle_id` unchanged.
(`SBC-002`)

The CLI SHALL support mode 003 (real-auto): `run <root> --mode 003` SHALL
execute the fixed real-auto embedded-smoke entry (`make demo-real-scripted
--question "<fixed>"`), parse the returned `Run Bundle: b_xxx` id, resolve the
bundle's repository-relative local location, record it, and print the bound id
and local path. Mode 003 uses the fixed bounded question `What is one bounded
fact about China's EV battery market in 2024?`. `verify` SHALL require
`final/report.md` for mode 003 (like mode 002) plus the common
terminal/trace/journal checks. (`SBC-002`, `SBC-004`)

#### Scenario: Mode 001 run binds the newest valid bundle
- **WHEN** a caller runs `soft-bundle run <root> --mode 001`
- **THEN** the CLI invokes the existing 001 entry, parses the returned `Run Bundle: b_xxx`, records the repository-relative local path, and sets `current_bundle_id` to that bundle

#### Scenario: Run without a valid bundle id fails without binding
- **WHEN** the underlying run exits successfully but no valid `bundle_id` can be parsed or resolved
- **THEN** the CLI fails with a bounded error and leaves `current_bundle_id` unchanged

#### Scenario: Run starts from a clean run-bundle workspace
- **WHEN** a caller runs `soft-bundle run <root> --mode 001` and prior run bundles exist under the operator workspace `deep-research` subtree
- **THEN** the CLI removes those prior run bundles before invoking the operator mode

#### Scenario: Mode 002 produces a final Markdown report
- **WHEN** a caller runs `soft-bundle run <root> --mode 002`
- **THEN** the CLI runs the scripted-real workflow and verification requires `final/report.md` to exist

#### Scenario: Run mode 003 binds the real-auto bundle
- **WHEN** a caller runs `soft-bundle run <root> --mode 003` and the real-auto
  entry completes
- **THEN** the CLI records and prints the bundle id and its repository-relative
  local path, then prints the verification verdict

#### Scenario: Verify mode 003 requires a report
- **WHEN** a caller runs `soft-bundle verify <root>` for a bound mode-003 bundle
  without `final/report.md`
- **THEN** the CLI prints `RESULT: FAIL` naming the missing report and returns a
  non-zero exit code

#### Scenario: A blocked run still binds its resolved bundle
- **WHEN** a mode-003 run exits non-zero (blocked terminal) but its output still
  contains a valid `Run Bundle: b_xxx` and the bundle directory resolves under the
  operator workspace
- **THEN** the CLI records the bundle (`current_bundle_id` + `bundles/<id>.json`)
  and `bundle_local_path`, prints the raw run output to stderr so the failure reason
  stays visible, prints the bound id/local path, returns the run's non-zero exit
  code, and keeps the run reported as failed

#### Scenario: A failed run without a resolvable bundle still fails without binding
- **WHEN** a run exits non-zero and no valid `bundle_id` or bundle directory can be
  resolved
- **THEN** the CLI prints the raw run output, does not modify `current_bundle_id`,
  and returns a non-zero exit code