> req: DPL-001, DPL-004, DPL-005, DPL-007, DPL-010

## ADDED Requirements

### Requirement: Demo pipeline carries Bundle identity through the shared lifecycle transport

The demo pipeline SHALL obtain Deep Research lifecycle identity, status, and legal
actions only from the shared typed Bundle lifecycle result. Fake and real composition
roots SHALL not derive `research_id`, session references, or Bundle paths, and demo
retention shall remain an observation of a Bundle rather than an independent resume
store. (`DPL-010`)

#### Scenario: Demo restart cannot revive a deleted Bundle
- **WHEN** a demo process restarts after a prior Bundle was deleted
- **THEN** its shared lifecycle transport reports unavailable for that identity and does not reuse a session/checkpoint record to resume it

## MODIFIED Requirements

### Requirement: Shared demo core provides infrastructure, lifecycle transport, and prerequisite checks

The agent project SHALL provide
`deep_research_harness/scripts/_demo_core.py` with the existing demo adapter, recipe
and host factories, idempotent cleanup, shared lifecycle transport adapter, and
non-network preflight primitives. Its real/fake composition, credential handling,
tool-provenance, and zero-API default-demo guarantees remain unchanged. The core SHALL
consume only the shared typed Bundle lifecycle result for Deep Research identity,
status, and legal control; it SHALL not derive `research_id`, select a Bundle path, or
make retained demo material a lifecycle recovery source. (`DPL-001`)

#### Scenario: Demo core remains in the canonical root
- **WHEN** any supported demo entry point imports its common transport implementation
- **THEN** it resolves `deep_research_harness/scripts/_demo_core.py` and receives only
  the shared Bundle lifecycle outcome for a Deep Research Run

### Requirement: CLI real demo validates and explains prerequisite readiness

`deep_research_harness/scripts/demo_real.py` SHALL retain the existing shared
preflight, supported-model and `TAVILY_API_KEY` validation, `--question` and
`--scripted` behavior, and explicit all-real recipe construction. It SHALL use the
shared Bundle lifecycle transport and shall not derive a Run/control identity from the
demo process, a checkpoint, or a retained-session record. (`DPL-004`)

#### Scenario: Real demo entry follows the canonical root
- **WHEN** an operator starts the real CLI demo from the downstream module
- **THEN** the executable path is `deep_research_harness/scripts/demo_real.py` and its
  lifecycle result remains Bundle-authoritative

### Requirement: Makefile provides targets for all demo variants

The `deep_research_harness/Makefile` SHALL retain the existing fake and real CLI/TUI
demo targets, `DEMO_ARGS` forwarding, and direct-extra selection. Its real targets
SHALL load `deep_research_harness/.env` when present; fake targets retain their
credential-free behavior. No target SHALL use `deerflow_research/` as a working
directory or fallback, and no `backend/` or `frontend/` file is changed. (`DPL-005`)

#### Scenario: Demo target loads the renamed local environment
- **WHEN** `make demo-real` runs from the canonical downstream module
- **THEN** it loads `deep_research_harness/.env` when present and does not resolve an
  old-root environment file

### Requirement: Local demos retain inspectable run bundles under bounded policy

Local demos SHALL retain only their own contained Run Bundles below the project-local
`deep_research_harness/.deep-research-demo-runs/` root, ignored by
`deep_research_harness/.gitignore`, and bounded observation-only diagnostics under the
shared Bundle lifecycle contract. They retain the existing lock, bounded cleanup, and
fixture/demo-composition guarantees. A demo may inspect an available Bundle through its
supported typed result, but SHALL not retain a session broker, `research_id`, checkpoint
namespace, or local path as a resume/control authority. Deleting a demo Bundle SHALL
make only that Run unavailable; a later demo may start a fresh independent Bundle
without recovering the prior one. (`DPL-007`)

#### Scenario: Demo retention does not become a recovery store
- **WHEN** a retained demo diagnostic refers to a deleted Bundle
- **THEN** the demo can show its bounded observation but returns unavailable for control and does not recreate State/content from a session or checkpoint record
