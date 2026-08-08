> req: PRS-006

## MODIFIED Requirements

### Requirement: Run-session ownership is canonical and runtime-bound

The run-session contracts SHALL live at
`agent/src/deerflow_deep_research/domain/run_session.py`, while frozen
session-discovery and operation projections SHALL live at
`agent/src/deerflow_deep_research/domain/session_operations.py`. The manifest,
lifecycle-trace, retention, locking, diagnostic binding, and inspection operations
SHALL live at `agent/src/deerflow_deep_research/runtime/run_session.py`; the trusted
historical resolver and authorized operation broker SHALL live at
`agent/src/deerflow_deep_research/runtime/session_operations.py`. These paths and
their focused contract, resolver, lifecycle, and file-SQLite restart tests SHALL be
registered in `openspec/governance/project-structure.toml` and the generated
`agent/AGENTS.md` block. Domain contracts depend only on stdlib/Pydantic/domain;
runtime is the only layer that receives trusted host workspace or lifecycle facts.

Frozen local-workbench contracts SHALL live at
`agent/src/deerflow_deep_research/domain/session_workbench.py`, and the broker-bound
timeline, catalog, and contained artifact reader SHALL live at
`agent/src/deerflow_deep_research/runtime/session_workbench.py`. The dedicated
`agent/scripts/session_workbench.py` entry is permitted only as a thin terminal
presentation adapter over that runtime surface. Its contract, runtime, containment,
and terminal integration tests SHALL be registered in the same structure registry and
generated guide block.

No run-session domain, storage, inspection, retention, lock, workbench contract, or
workbench runtime implementation shall be placed under `agent/scripts`, `backend`,
`frontend`, or a generic helpers/utils/common module. `agent/scripts/demo_sessions.py`
and `agent/scripts/session_workbench.py` are permitted only as thin presentation
adapters over runtime operations. The downstream-owned `agent/.gitignore` SHALL contain
only `.deep-research-demo-runs/`, be registered in the same structure registry/generated
block, and shall not restore superseded profile ignore rules or alter upstream-owned root
`.gitignore`. (`PRS-006`)

#### Scenario: Run-session paths pass structural governance
- **WHEN** the architecture checker scans the implemented run-session capability
- **THEN** canonical contracts, runtime stores, the owned `agent/.gitignore`, thin
  adapters, and focused session-operation tests appear in the registry, while domain
  has no runtime import

#### Scenario: Workbench paths preserve the downstream boundary
- **WHEN** the architecture checker scans the local session workbench implementation
- **THEN** its domain/runtime modules and focused tests appear in canonical `agent/`
  paths, the terminal script is a thin adapter, and no Deep Research source appears in
  `backend` or `frontend`
