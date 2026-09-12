# Test Assets (support library, not tests)

This directory is **not a test lane and contains no tests**. `pytest` collects nothing
here. It is the test-owned support library for two callers:

- `tests/**` — test modules import these vocabularies, validators, and inventory tables.
- `scripts/checks/check_test_assets.py` — the `make test-assets` governance gate.

## What lives here

- Evidence and requirement vocabulary plus validators (`evidence.py`,
  `requirement_evidence.py`).
- Inventory tables and their mechanical checks (`inventory.py`, `fault_matrix.py`,
  `node_conformance.py`, `cognitive_program_board.py`, `workflow_nodes.py`,
  `node_agent_capabilities.py`, `provider_shapes.py`, `release_attestation.py`,
  `deferred_activation_dossiers.py`).
- Lane selector constants (`selection.py`) consumed by the lane contract tests and the
  asset gate.

## Boundaries

- This is a support namespace, not a second source of behavior. Current facts and
  required behavior remain in the owning specs and executable tests; this file only
  states the directory's role.
- Governance for these assets is owned by the `evaluation-hardening` capability
  (`EVH-*`) and the `make test-assets` gate.
- A collected test belongs in a test lane such as `tests/contract/`, not here. The
  former sole collected test lives at
  `tests/contract/test_main_spec_requirement_sources.py`.
