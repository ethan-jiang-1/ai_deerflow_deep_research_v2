> req: EVH-005

## MODIFIED Requirements

### Requirement: Release gate combines deterministic CI with optional LLM canary

The complete deterministic verification command SHALL be
`cd deerflow_research && UV_OFFLINE=1 make verify`; `make test` and `make install`
from that module SHALL retain their existing selection and lockfile semantics. CI
workflow path filters, working directories, artifacts, release attestation scopes,
protected-path checks, and deterministic source-annotation scans SHALL use
`deerflow_research/` as the physical downstream root. They SHALL preserve their
existing workflow filename, display name, job/status identity, test selection, and
evidence semantics unless an operator audit establishes a separately owned external
consumer change.

The renamed verification contracts SHALL reject a stale `agent/` root reference, a
path filter or artifact location that no longer observes downstream changes, or a
source scan that silently omits the canonical production root. (`EVH-005`)

#### Scenario: Deterministic verification starts from the renamed module
- **WHEN** a developer prepares the locked environment and invokes the canonical
  verification command
- **THEN** it runs the existing deterministic aggregate from `deerflow_research/`
  without provisioning, credentialed execution, or network access

#### Scenario: Workflow status identity is not renamed incidentally
- **WHEN** the filesystem paths in a deterministic or release workflow are migrated
- **THEN** its status-producing identity remains unchanged while its trigger, working
  directory, and artifact paths resolve under `deerflow_research/`
