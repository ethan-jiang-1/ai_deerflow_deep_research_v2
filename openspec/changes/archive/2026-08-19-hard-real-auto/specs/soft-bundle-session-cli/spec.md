# soft-bundle-session-cli Delta

> req: SBC-002, SBC-004

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

The CLI SHALL support mode 004 (hard real-auto): `run <root> --mode 004` SHALL
execute the fixed real-auto embedded-smoke entry with an explicit
`--profile-intent none` selection (`make demo-real-scripted --question "<fixed>"
--profile-intent none`), parse the returned `Run Bundle: b_xxx` id, resolve the
bundle's repository-relative local location, record it, and print the bound id
and local path. Mode 004 uses the fixed comparison question `Compare China and
US EV battery market in 2024.`. `verify` SHALL require `final/report.md` for
mode 004 (like modes 002 and 003) plus the common terminal/trace/journal
checks. (`SBC-002`, `SBC-004`)

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

#### Scenario: Run mode 004 binds the real-auto bundle without an intent declaration
- **WHEN** a caller runs `soft-bundle run <root> --mode 004` and the real-auto
  entry completes
- **THEN** the CLI invokes the embedded-smoke entry with `--profile-intent none`
  and the fixed comparison question, records and prints the bundle id and its
  repository-relative local path, then prints the verification verdict

#### Scenario: Verify mode 004 requires a report
- **WHEN** a caller runs `soft-bundle verify <root>` for a bound mode-004 bundle
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

### Requirement: Query soft bundle state and content through the root

The CLI SHALL support `status`, `path`, `inspect`, `phases`, `verify`, and `list` commands. `status`, `path`, `inspect`, `phases`, and `verify` accept only `soft_bundle_root`; `list` SHALL scan only the operator soft-bundle parent (default `.deep-research-demo-runs/workspace/soft-bundles`) for directories containing a valid `manifest.json`. `status` SHALL show the manifest facts and current bundle id. `path` SHALL print only the repository-relative `bundle_local_path`, never an absolute host path. `inspect` SHALL report the bound bundle's observed summary and journal health. For a mode-001 bundle it SHALL delegate to the existing `demo-sessions` inspection route. For a mode-002, mode-003, or mode-004 bundle, whose bundle is published in an independent run workspace and trusted scope that the fixed demo scope cannot see, it SHALL resolve the recorded bundle's local content and render that bundle's contained diagnostics read-only, reporting the same observed-summary and journal-health facts; it SHALL NOT create, reopen, recover, or control a Bundle through that record. `phases` SHALL read the recorded local bundle content and print per-phase outputs. `verify` SHALL check the bound bundle's terminal state, execution trace, journal summary, `events.jsonl` completed node coverage for every required graph phase, and mode-specific report expectations, then print `RESULT: PASS` or `RESULT: FAIL`. After `run` binds a bundle, the CLI SHALL automatically run the same verification and report the verdict. (`SBC-004`)

#### Scenario: Path prints repository-relative location only
- **WHEN** a caller runs `soft-bundle path <root>` for a bound soft bundle
- **THEN** the CLI prints a path beginning with `.deep-research-demo-runs/...` and does not print a filesystem absolute path

#### Scenario: Inspect delegates to the existing operator route
- **WHEN** a caller runs `soft-bundle inspect <root>` for a bound mode-001 soft bundle
- **THEN** the CLI invokes the existing `demo-sessions` inspection command with the recorded `bundle_id`

#### Scenario: Inspect mode 002 renders the recorded bundle diagnostics
- **WHEN** a caller runs `soft-bundle inspect <root>` for a bound mode-002 soft bundle whose recorded bundle content exists under the operator workspace
- **THEN** the CLI prints the bundle's observed summary and journal health from the recorded bundle's contained diagnostics and does not report it as unavailable

#### Scenario: Inspect mode 004 renders the recorded bundle diagnostics
- **WHEN** a caller runs `soft-bundle inspect <root>` for a bound mode-004 soft bundle whose recorded bundle content exists under the operator workspace
- **THEN** the CLI prints the bundle's observed summary and journal health from the recorded bundle's contained diagnostics read-only and does not report it as unavailable

#### Scenario: Inspect mode 002 with a missing bundle is unavailable
- **WHEN** a caller runs `soft-bundle inspect <root>` for a bound mode-002 soft bundle whose recorded bundle content no longer exists
- **THEN** the CLI reports the bundle as unavailable, returns a non-zero exit code, and does not recreate, recover, or reopen the bundle through the record

#### Scenario: Phases prints recorded per-phase content
- **WHEN** a caller runs `soft-bundle phases <root>` for a bound soft bundle with recorded local content
- **THEN** the CLI prints the bundle's execution trace, per-work fixture/output content, and final report existence from the recorded local path

#### Scenario: List returns valid soft bundle roots from the operator parent
- **WHEN** a caller runs `soft-bundle list` and the default operator soft-bundle parent contains directories with valid `manifest.json` files
- **THEN** the CLI prints those soft bundle roots without revealing absolute host paths or scanning Harness `deep-research/scopes`

#### Scenario: Verify prints PASS for a completed control run
- **WHEN** a caller runs `soft-bundle verify <root>` for a bound bundle whose terminal state, trace, and journal summary are complete
- **THEN** the CLI prints `RESULT: PASS`

#### Scenario: Run prints FAIL when verification fails
- **WHEN** a caller runs `soft-bundle run <root> --mode 001` and the bound bundle does not satisfy verification
- **THEN** the CLI prints `RESULT: FAIL` and returns a non-zero exit code
