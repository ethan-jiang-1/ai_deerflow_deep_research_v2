# Verification Gate Evidence

> Task 5.1 evidence, recorded on 2026-08-15.

## In-Scope Focused Commands

All narrow commands required by tasks 2.3, 2.6, and 3.5 passed:

| Command | Result |
| --- | --- |
| `UV_OFFLINE=1 make test-strict-checkpoint` | 73 passed |
| Checkpoint/Bundle/state/restart/replay suite from task 2.6 | 117 passed |
| `UV_OFFLINE=1 make test-retained-observation` | 12 passed |
| Journal/terminal/CLI/TUI/participant suite from task 3.5 | 96 passed |
| Direct Journal store suite | 26 passed |
| Retained migration and Journal store regression suite | 40 passed |

`UV_OFFLINE=1 .venv/bin/python scripts/retained_run_data_migration.py` also
matches `tests/fixtures/retained_run_data/initial_zero_inventory_dry_run.json`.

## Deterministic Gate

`UV_OFFLINE=1 make verify` passed these prerequisites before stopping at the
pre-existing `test-assets` registry check:

- project requirements, specs, architecture, and Agent Charter governance;
- `uv lock --check`;
- Ruff check and format check (`483 files already formatted`).

The gate remains evidence-limited by three unrelated existing selector/evidence
registry failures:

```text
tests/unit/test_graph_host.py::test_legacy_checkpointer_is_refused_before_action_saver_factory
tests/unit/test_non_interactive.py::test_tool_rejects_the_retired_marker_before_sandbox_or_graph_selection
tests/unit/test_node_agent_bridge.py::test_retired_selected_endpoint_aliases_are_omitted_even_when_they_match_base_url
```

The failures report missing or uncollected impact claims in the existing test
asset registry. They do not reference the retained-data requirements, fixtures,
or selectors introduced by this change. No unrelated selector was modified.
The remaining verify targets are run independently below so this limitation does
not conceal an in-scope failure.

## Independent Remaining Targets

`make test-req-coverage` passed. The affected demo regression suite passed after
the current-scope fix: `tests/integration/test_demo_cli.py`,
`tests/integration/test_demo_tui.py`, and `tests/unit/test_demo_core.py` report
`59 passed`.

The full `test-fast` target is additionally evidence-limited by 34 failures, all
from `tests/eval/test_cognitive_evaluation_suite.py` with
`evaluation_runtime_control_digest_mismatch`. The full workflow target has the
same independent baseline: 34 workflow tests pass and
`test_wave2_cognitive_program_production_scenarios_record_only_declared_handoffs`
fails on that digest mismatch. Neither failure class references this change's
retained-data implementation, and the exact same issue was present before this
change's cutover work.

The integration target was rerun after the fixture scope fix. Its two former
`test_demo_cli.py` failures now pass; no retained-data failure remains in the
affected demo, Journal, terminal, or lifecycle suites recorded above.
