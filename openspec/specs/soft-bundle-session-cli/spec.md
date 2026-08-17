# soft-bundle-session-cli Specification

> req: SBC-001, SBC-002, SBC-003, SBC-004, SBC-005

## Purpose

Provide an operator-only soft bundle CLI that uses a stateless root handle to create, run, bind, inspect, and query local Deep Research bundles without exposing absolute host paths or creating a second lifecycle authority.

## Requirements

### Requirement: Create a soft bundle root

The CLI SHALL create a `soft_bundle_root` directory when no existing valid soft bundle is present. The caller MAY supply `--root`, `--name`, and `--mode`; when `--root` is omitted, the CLI SHALL generate a root under the default operator workspace `.deep-research-demo-runs/workspace/soft-bundles/<generated>/`. The research question is fixed to `What is the capital of France?` and the CLI SHALL NOT accept a caller-supplied question argument. The CLI SHALL accept only safe repository-relative `--root` values and SHALL reject absolute paths, `.`/`..` segments, empty segments, or paths outside the repository root. The CLI SHALL return both `soft_bundle_root` and `name`. If the root already contains a valid `manifest.json`, the CLI SHALL NOT overwrite it and SHALL return the existing root. If the root exists but is not a soft bundle directory, the CLI SHALL fail without writing. (`SBC-001`)

#### Scenario: Create with no arguments returns generated root and name
- **WHEN** a caller runs `soft-bundle create` without `--root` or `--name`
- **THEN** the CLI creates a new soft bundle root under the default parent, writes a valid `manifest.json` with the fixed question `What is the capital of France?`, and prints the generated `soft_bundle_root` and `name`

#### Scenario: Create with explicit root is idempotent
- **WHEN** a caller runs `soft-bundle create --root <existing-valid-root>` twice
- **THEN** the second invocation returns the same root and does not overwrite the existing manifest

#### Scenario: Create refuses a non-soft-bundle existing directory
- **WHEN** a caller runs `soft-bundle create --root <existing-non-soft-bundle-dir>`
- **THEN** the CLI fails with a bounded error and does not create or modify files inside that directory

### Requirement: Run research and bind the resulting bundle

The CLI SHALL run the selected operator mode using existing Harness entry surfaces, parse a valid `bundle_id` from the run output, resolve the repository-relative `bundle_local_path`, record it under `bundles/<bundle_id>.json`, and update the soft bundle manifest's `current_bundle_id`. Before invoking the operator mode, the CLI SHALL remove all prior run-bundle content under the operator workspace `deep-research` subtree so each control-environment run starts clean. The CLI SHALL perform local path resolution only after a valid `bundle_id` is available, and SHALL NOT use path scanning to discover or select a bundle. (`SBC-002`)

#### Scenario: Mode 001 run binds the newest valid bundle
- **WHEN** a caller runs `soft-bundle run <root> --mode 001`
- **THEN** the CLI invokes the existing 001 entry, parses the returned `Run Bundle: b_xxx`, records the repository-relative local path, and sets `current_bundle_id` to that bundle

#### Scenario: Run without a valid bundle id fails without binding
- **WHEN** the underlying run exits successfully but no valid `bundle_id` can be parsed or resolved
- **THEN** the CLI fails with a bounded error and leaves `current_bundle_id` unchanged

#### Scenario: Run starts from a clean run-bundle workspace
- **WHEN** a caller runs `soft-bundle run <root> --mode 001` and prior run bundles exist under the operator workspace `deep-research` subtree
- **THEN** the CLI removes those prior run bundles before invoking the operator mode

### Requirement: Bind an existing bundle id to a soft bundle root

The CLI SHALL accept a `bundle_id` supplied by the caller, resolve its repository-relative local record location through operator-side lookup, and record it in the selected soft bundle root. The CLI SHALL NOT accept a path or filesystem root as the bundle selector. (`SBC-003`)

#### Scenario: Bind a known bundle id
- **WHEN** a caller runs `soft-bundle bind <root> b_xxx` for a bundle that exists under the operator workspace
- **THEN** the CLI records `b_xxx` and its repository-relative local path, and sets `current_bundle_id` to `b_xxx`

#### Scenario: Bind a foreign or unknown bundle id is unavailable
- **WHEN** a caller runs `soft-bundle bind <root> b_unknown` and no such bundle is available under the operator workspace
- **THEN** the CLI returns a bounded unavailable result and does not create a bundle record

### Requirement: Query soft bundle state and content through the root

The CLI SHALL support `status`, `path`, `inspect`, `phases`, `verify`, and `list` commands. `status`, `path`, `inspect`, `phases`, and `verify` accept only `soft_bundle_root`; `list` SHALL scan only the operator soft-bundle parent (default `.deep-research-demo-runs/workspace/soft-bundles`) for directories containing a valid `manifest.json`. `status` SHALL show the manifest facts and current bundle id. `path` SHALL print only the repository-relative `bundle_local_path`, never an absolute host path. `inspect` SHALL delegate to the existing `demo-sessions` inspection route. `phases` SHALL read the recorded local bundle content and print per-phase outputs. `verify` SHALL check the bound bundle's terminal state, execution trace, journal summary, and mode-specific report expectations, then print `RESULT: PASS` or `RESULT: FAIL`. After `run` binds a bundle, the CLI SHALL automatically run the same verification and report the verdict. (`SBC-004`)

#### Scenario: Path prints repository-relative location only
- **WHEN** a caller runs `soft-bundle path <root>` for a bound soft bundle
- **THEN** the CLI prints a path beginning with `.deep-research-demo-runs/...` and does not print a filesystem absolute path

#### Scenario: Inspect delegates to the existing operator route
- **WHEN** a caller runs `soft-bundle inspect <root>` for a bound soft bundle
- **THEN** the CLI invokes the existing `demo-sessions` inspection command with the recorded `bundle_id`

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

### Requirement: Records and paths never become lifecycle authority

All soft bundle records, manifests, and repository-relative paths SHALL remain operator-side observations. They SHALL NOT be accepted as inputs to `start`, `resume`, `refine`, `status`, or `cancel` lifecycle actions, and SHALL NOT be used to reconstruct, recover, or reopen a deleted or foreign Bundle. (`SBC-005`)

#### Scenario: Path output is not accepted as a bundle selector
- **WHEN** a caller passes a repository-relative `bundle_local_path` as the bundle selector to `bind`
- **THEN** the CLI rejects it because only an opaque `bundle_id` is accepted as the bundle selector

#### Scenario: Deleted bundle record cannot recover the bundle
- **WHEN** a recorded soft bundle points to a local path that no longer exists
- **THEN** the CLI reports the bundle as unavailable and does not recreate, recover, or reopen it through the record
