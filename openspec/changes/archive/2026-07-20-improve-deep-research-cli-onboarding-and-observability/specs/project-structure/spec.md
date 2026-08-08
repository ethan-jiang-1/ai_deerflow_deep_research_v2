> req: PRS-005

## ADDED Requirements

### Requirement: Run-experience contracts use the canonical domain and runtime ownership layers

The shared run-experience implementation SHALL add only these canonical downstream
production paths: agent/src/deerflow_deep_research/domain/run_experience.py,
agent/src/deerflow_deep_research/runtime/run_experience.py, and
agent/src/deerflow_deep_research/runtime/run_diagnostics.py. The domain module
shall contain frozen, serializable run intent/update/failure/pending-input
contracts and depend only on the standard library, Pydantic, and existing domain
contracts. The runtime modules shall own lifecycle-wire parsing, transport binding,
redacted diagnostic publication, and source failure projection.

These paths SHALL be registered in openspec/governance/project-structure.toml and
reflected in the generated agent/AGENTS.md block. No source for this capability
shall be added under backend, frontend, agent/scripts, a generic helpers/utils/
common module, or an ad hoc session package. Demo scripts remain presentation
adapters and do not own the contracts. (PRS-005)

#### Scenario: Run-experience ownership passes the architecture checker
- **WHEN** the structure contract inspects the implemented run-experience change
- **THEN** the three modules appear at their canonical paths, domain has no runtime
  import, runtime is the only lifecycle-wire and diagnostic binding owner, and no
  Deep Research source appears in backend or frontend
