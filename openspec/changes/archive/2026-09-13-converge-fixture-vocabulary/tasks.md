## 1. Canonical term and its guard

- [x] 1.1 Add a `Fixture Composition` glossary record to `deep_research_harness/CONTEXT.md` in the System Boundary section: it defines the closed composition set `fixture | mixed | all_real` and lists the `full-fake` composition alias under `_Avoid_`. Verify: the record matches the existing `**Term**:` / `_Avoid_:` shape used by neighbouring records.
- [x] 1.2 Extend `deep_research_harness/tests/contract/test_glossary_record_contract.py` so `Fixture Composition` is a required glossary record with an `_Avoid_` boundary. Verify: `UV_OFFLINE=1 uv run --no-sync python -m pytest tests/contract/test_glossary_record_contract.py -q` passes and fails if the record is removed.

## 2. Production identifier rename

- [x] 2.1 Rename `MAX_FAKE_RERUN_GENERATIONS` to `MAX_RERUN_GENERATIONS` in `deep_research_harness/src/deerflow_deep_research/domain/lifecycle.py` (definition, field bounds, validator, `__all__`) and update every importer: `domain/state.py`, `runtime/bundle_graph.py`, `graph/nodes/rerun/planner.py`. Verify: `rg -n "MAX_FAKE_RERUN_GENERATIONS" deep_research_harness/src` returns nothing and the value stays `2`.
- [x] 2.2 Clarify the production rerun-route comments in `deep_research_harness/src/deerflow_deep_research/graph/builder.py` so the legacy `"next"` key is described as a retained legacy alias rather than a `fake` route. Verify: the comments name no `fake` implementation and the conditional-edge map is byte-identical.
- [x] 2.3 Update the `rerun-node` requirement's normative reference from `MAX_FAKE_RERUN_GENERATIONS` to `MAX_RERUN_GENERATIONS` (already carried by this change's `rerun-node` delta). Verify: the delta's only constant mention uses the new name.

## 3. Living documentation

- [x] 3.1 Replace composition-sense `full-fake` wording with `fixture` in `deep_research_harness/README.md`, `docs/testing-and-evaluation.md`, and `docs/regression-descent.md`, leaving test-double uses of `fake` untouched. Verify: `rg -n "full-fake|full fake" deep_research_harness/README.md deep_research_harness/docs` returns only intentional test-double or scenario-label uses.
- [x] 3.2 Confirm the fifteen delta specs in this change are the only spec authority touched and that no requirement ID, scenario set, or route changed. Verify: `openspec validate converge-fixture-vocabulary --strict` passes.

## 4. Program verification

- [x] 4.1 Run the application gate from `deep_research_harness/`: `UV_OFFLINE=1 make verify`. Verify: every lane exits 0.
- [x] 4.2 Run the root governance plan gate: `python3 openspec/governance/check_project_gate.py --phase plan --change converge-fixture-vocabulary`. Verify: exit 0 with no reservation requiring registration.
