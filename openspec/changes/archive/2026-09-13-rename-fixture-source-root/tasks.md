# Tasks

## 1. Rename the fixture source root

- [x] 1.1 `git mv deep_research_harness/src_fake deep_research_harness/src_fixtures` and verify the internal package `deerflow_deep_research_fixtures/` is unchanged (path now `deep_research_harness/src_fixtures/deerflow_deep_research_fixtures/`).
- [x] 1.2 Update `deep_research_harness/pyproject.toml` `pythonpath` entry `src_fake` → `src_fixtures` and verify plain `python -m pytest tests/contract/test_research_node_packages.py -q` still collects.

## 2. Update harness execution references

- [x] 2.1 Update every `PYTHONPATH=src_fake` occurrence in `deep_research_harness/Makefile` (10 lines) to `src_fixtures` and verify `rg "src_fake" deep_research_harness/Makefile` returns nothing.
- [x] 2.2 Update `deep_research_harness/scripts/_demo_core.py` fixture path references and verify `UV_OFFLINE=1 make demo-scripted` completes the zero-credential fixture-graph lifecycle.
- [x] 2.3 Update the literal-path assertions in `tests/contract/test_demo_commands.py`, `tests/contract/test_docker_compose.py`, `tests/contract/test_entry_environment_regression_workflow.py`, `tests/integration/test_demo_cli.py`, and `tests/unit/test_checkpoint_msgpack.py`, and verify `uv run pytest <those five files> -q` passes.

## 3. Update CI path filter

- [x] 3.1 Update `.github/workflows/agent-entry-environment-regression.yml` `src_fake/**` → `src_fixtures/**` and verify the contract test `tests/contract/test_entry_environment_regression_workflow.py` passes against the edited workflow.

## 4. Synchronize governance registry

- [x] 4.1 Update `openspec/governance/project-structure.toml` `fixture_root`, the `check_project_architecture.py` literal `"src_fake"`, the six fixture entries in `required-paths.toml`, and the FSI-001 description in `req-registry.yaml`, then verify from the repository root that `UV_OFFLINE=1 python3 openspec/governance/check_project_architecture.py` exits 0.
- [x] 4.2 Re-render the `deep_research_harness/AGENTS.md` generated structure-locator block from the registry (`check_project_architecture.py --render-guide`) and verify the checker reports no block drift.

## 5. Update living documentation

- [x] 5.1 Update `README.md`, `deep_research_harness/README.md`, `deep_research_harness/docs/runtime-architecture.md`, and `deep_research_harness/docs/local-operations.md` and verify `rg "src_fake" README.md deep_research_harness/README.md deep_research_harness/docs` returns nothing.

## 6. Verification and closeout

- [x] 6.1 From `deep_research_harness/`, run `UV_OFFLINE=1 make verify` and confirm every lane (lock-check, lint, test-assets, test-fast, test-integration, test-workflow) exits 0.
- [x] 6.2 From the repository root, run `python3 openspec/governance/check_project_gate.py --phase closeout`, then `openspec validate rename-fixture-source-root --strict`, then `git diff HEAD --check`, and record each exit code directly (no pipes).
- [x] 6.3 Confirm no live `src_fake` reference remains with `rg --hidden "src_fake" --glob '!**/.venv/**' --glob '!openspec/changes/archive/**' --glob '!_backlog/**' .` and record that `_backlog/` and archived changes intentionally retain the historical path.
