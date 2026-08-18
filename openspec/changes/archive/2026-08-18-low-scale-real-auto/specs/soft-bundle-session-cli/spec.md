## MODIFIED Requirements

### Requirement: Run research and bind the resulting bundle

The CLI SHALL support mode 003 (real-auto): `run <root> --mode 003` SHALL execute
the fixed real-auto embedded-smoke entry (`make demo-real-scripted --question
"<fixed>"`), parse the returned `Run Bundle: b_xxx` id, resolve the bundle's
repository-relative local location, record it, and print the bound id and local
path. Mode 003 uses the fixed bounded question `What is one bounded fact about
China's EV battery market in 2024?`. `verify` SHALL require `final/report.md` for
mode 003 (like mode 002) plus the common terminal/trace/journal checks. (`SBC-002`,
`SBC-004`)

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
