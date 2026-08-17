## MODIFIED Requirements

### Requirement: Query soft bundle state and content through the root

The CLI SHALL support `status`, `path`, `inspect`, `phases`, `verify`, and `list` commands. `status`, `path`, `inspect`, `phases`, and `verify` accept only `soft_bundle_root`; `list` SHALL scan only the operator soft-bundle parent (default `.deep-research-demo-runs/workspace/soft-bundles`) for directories containing a valid `manifest.json`. `status` SHALL show the manifest facts and current bundle id. `path` SHALL print only the repository-relative `bundle_local_path`, never an absolute host path. `inspect` SHALL report the bound bundle's observed summary and journal health. For a mode-001 bundle it SHALL delegate to the existing `demo-sessions` inspection route. For a mode-002 (scripted-real) bundle, whose bundle is published in an independent run workspace and trusted scope that the fixed demo scope cannot see, it SHALL resolve the recorded bundle's local content and render that bundle's contained diagnostics read-only, reporting the same observed-summary and journal-health facts; it SHALL NOT create, reopen, recover, or control a Bundle through that record. `phases` SHALL read the recorded local bundle content and print per-phase outputs. `verify` SHALL check the bound bundle's terminal state, execution trace, journal summary, `events.jsonl` completed node coverage for every required graph phase, and mode-specific report expectations, then print `RESULT: PASS` or `RESULT: FAIL`. After `run` binds a bundle, the CLI SHALL automatically run the same verification and report the verdict. (`SBC-004`)

#### Scenario: Path prints repository-relative location only
- **WHEN** a caller runs `soft-bundle path <root>` for a bound soft bundle
- **THEN** the CLI prints a path beginning with `.deep-research-demo-runs/...` and does not print a filesystem absolute path

#### Scenario: Inspect delegates to the existing operator route
- **WHEN** a caller runs `soft-bundle inspect <root>` for a bound mode-001 soft bundle
- **THEN** the CLI invokes the existing `demo-sessions` inspection command with the recorded `bundle_id`

#### Scenario: Inspect mode 002 renders the recorded bundle diagnostics
- **WHEN** a caller runs `soft-bundle inspect <root>` for a bound mode-002 soft bundle whose recorded bundle content exists under the operator workspace
- **THEN** the CLI prints the bundle's observed summary and journal health from the recorded bundle's contained diagnostics and does not report it as unavailable

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
