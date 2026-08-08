> req: PRS-006

## ADDED Requirements

### Requirement: Run-session ownership is canonical and runtime-bound

The run-session contracts SHALL live at
`agent/src/deerflow_deep_research/domain/run_session.py`; the manifest,
lifecycle-trace, retention, locking, diagnostic binding, and inspection operations
SHALL live at `agent/src/deerflow_deep_research/runtime/run_session.py`. Both paths
SHALL be registered in `openspec/governance/project-structure.toml` and the generated
`agent/AGENTS.md` block. Domain contracts depend only on stdlib/Pydantic/domain;
runtime is the only layer that receives trusted host workspace or lifecycle facts.

No run-session domain, storage, inspection, retention, or lock implementation shall
be placed under `agent/scripts`, `backend`, `frontend`, or a generic
helpers/utils/common module. `agent/scripts/demo_sessions.py` is permitted only as a
thin command adapter over the runtime operation. The downstream-owned
`agent/.gitignore` SHALL contain only `.deep-research-demo-runs/`, be registered in
the same structure registry/generated block, and shall not restore superseded profile
ignore rules or alter upstream-owned root `.gitignore`. (`PRS-006`)

#### Scenario: Run-session paths pass structural governance
- **WHEN** the architecture checker scans the implemented run-session capability
- **THEN** canonical contracts, runtime stores, the owned `agent/.gitignore`, and thin
  adapters appear in the registry, while domain has no runtime import
