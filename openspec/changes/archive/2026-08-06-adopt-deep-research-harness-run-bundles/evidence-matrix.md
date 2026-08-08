# Apply Evidence Matrix

Each requirement ID from the active delta appears exactly once below. IDs are grouped
only when the same direct production handoff and deterministic proof exercise every
member of the group. A projection/adapter test never serves as the sole proof for a
lifecycle authority claim.

| Requirement(s) | Direct production seam | Red proof | Green proof | Command |
| --- | --- | --- | --- | --- |
| `DRH-001`, `BON-001`, `BON-006` | Bundle publication plus Bootstrap boundary | fresh opaque id, staging, and invalid marker tests | published State/content and contained Bootstrap tests | `pytest tests/unit/test_bundle.py tests/unit/test_bootstrap_bundle.py tests/unit/test_state_contracts.py` |
| `DRH-002`, `DRH-004`, `DRH-008`, `REG-005`, `REG-006`, `REG-007`, `REG-011`, `REG-012`, `REG-013`, `REG-014`, `REG-020` | Bundle State reader/writer and graph lifecycle adapter | State active/ended, atomic writer, corruption, and reload tests | state persistence/reducer/graph lifecycle tests | `pytest tests/unit/test_state_persistence.py tests/unit/test_state_reducers.py tests/integration/test_research_lifecycle_tool.py` |
| `DRH-003`, `DRH-004`, `RDO-001`, `RDO-002`, `RDO-004`, `RDO-007` | Trusted-scope Bundle lifecycle resolver | valid/absent/foreign/malformed/ambiguous Handle cases | lifecycle and resolver cases | `pytest tests/integration/test_research_lifecycle_tool.py tests/unit/test_session_operation_resolver.py` |
| `DRH-005`, `REG-003`, `REG-004`, `REG-021`, `RDO-003`, `RDO-005`, `RDO-006`, `RUI-001`, `RUI-006` | Lifecycle `resume` and `refine` admission boundary | correlated response, required text, pending-preservation, ended-target, safe-point tests | lifecycle/HITL reducer integration tests | `pytest tests/integration/test_research_lifecycle_tool.py tests/integration/test_hitl1_lifecycle.py tests/unit/test_state_reducers.py` |
| `DRH-006`, `REG-009`, `REG-010`, `REG-016`, `RUI-011`, `RES-006`, `RUS-007` | Bundle availability validation before State/content access | deletion before control/write/completion while legacy observations remain | lifecycle, binding, and state loss cases | `pytest tests/integration/test_research_lifecycle_tool.py tests/integration/test_session_lifecycle_binding.py tests/unit/test_state_persistence.py` |
| `DRH-007`, `CES-008` | Scoped directory discovery and evaluation storage boundary | foreign-scope and evaluation candidate negative cases | core Bundle/lifecycle tests | `pytest tests/unit/test_bundle.py tests/integration/test_research_lifecycle_tool.py` |
| `BON-002`, `BON-004`, `BON-007` | Bootstrap node binding route and selected reference | invalid/missing/mismatched selected Bundle tests | bootstrap graph and blocking I/O tests | `pytest tests/unit/test_bootstrap_bundle.py tests/blocking_io/test_bootstrap_bundle_runtime.py` |
| `HIN-001`, `HIN-002`, `HIN-004`, `HIN-005`, `HIN-015` | HITL1 node plus request Bundle store | Bundle-local request/correlation/profile tests | node and lifecycle tests | `pytest tests/graph/test_hitl1_node.py tests/integration/test_hitl1_lifecycle.py tests/unit/test_request_bundle.py` |
| `TOP-008`, `WON-009`, `WSN-007` | Topic/Wave1/Wave2 selected Bundle contexts | node loss/legacy override tests | topic, Wave1, Wave2 focused suites | `pytest tests/graph/test_topic_planning_node.py tests/integration/test_wave1_work_units.py tests/graph/test_wave2_synthesis_real.py` |
| `WOU-001`, `WOU-003`, `WOU-004`, `WOU-005`, `WOU-006`, `WOU-009`, `WOU-011` | Work-unit and ledger stores | rejected legacy identity/path and loss-before-publication tests | bundle/work-unit/store tests | `pytest tests/domain/test_work_unit_bundle.py tests/unit/test_work_unit_store.py tests/integration/test_work_unit_submit_boundary.py` |
| `NOA-007`, `NOA-008`, `NOA-014` | Runtime node-agent bridge context projection | path/identity-like agent input cannot select a Bundle | bridge/capability cohort tests | `pytest tests/unit/test_node_agent_bridge.py tests/domain/test_node_agent_capability.py tests/graph/test_node_agent_capability_cohort.py` |
| `RUI-002`, `RUI-003`, `RUI-004`, `RUI-007`, `RUI-008`, `RUI-009`, `RUI-010` | Tool schema, RuntimeAdapter, GraphHost boundary | legacy identity rejection and no generic-checkpoint recovery tests | lifecycle/replay tests | `pytest tests/integration/test_research_lifecycle_tool.py tests/integration/test_public_entry_replay.py` |
| `RER-001`, `RER-002`, `RER-003`, `RER-006`, `RER-007`, `RER-009`, `RER-013` | Shared run-experience result projection | unavailable and legal-next-action projection tests | run-experience contracts | `pytest tests/contract/test_run_experience_contract.py tests/contract/test_run_experience_failures.py` |
| `RUS-001`, `RUS-002`, `RUS-003`, `RUS-004`, `RUS-006` | Retained run-session observations | historical trace/manifest cannot select or recover a Bundle | run-session store and lifecycle binding tests | `pytest tests/unit/test_run_session_store.py tests/integration/test_session_lifecycle_binding.py` |
| `RES-001`, `RES-002`, `RES-003`, `RES-004` | Binding observation store | retained binding cannot authorize a Run | binding unit/integration tests | `pytest tests/unit/test_session_lifecycle_binding.py tests/integration/test_session_lifecycle_binding.py` |
| `RSV-001`, `RSV-002`, `RSV-003`, `RSV-004` | Fixed artifact catalog and contained reader | unavailable/foreign/artifact path cases | workbench contract/runtime tests | `pytest tests/contract/test_session_workbench_contract.py tests/contract/test_session_workbench_runtime.py` |
| `RWB-001`, `RWB-002`, `RWB-003`, `RWB-005`, `RWB-006`, `RWB-007`, `RWB-008` | Local workbench adapter | stale visible control and no broker recovery cases | workbench integration tests | `pytest tests/contract/test_session_workbench_contract.py tests/integration/test_session_workbench.py` |
| `REC-004`, `REC-005`, `REC-006`, `REC-008`, `RED-002`, `RED-008`, `FCO-001`, `FCO-002`, `DPL-001`, `DPL-004`, `DPL-005`, `DPL-007`, `DPL-010` | CLI/TUI/demo adapters consuming typed lifecycle result | no adapter-derived identity/recovery tests | demo/public-skill tests | `pytest tests/integration/test_demo_real.py tests/integration/test_demo_tui.py tests/contract/test_public_skill.py` |
| `DEC-003`, `DEC-006`, `LCP-001`, `LCP-002`, `LCP-003`, `LCP-005`, `LCP-006` | Prepare, Docker, profile, and public-skill configuration | old-root/no-fallback configuration tests | prepare/Docker/profile contracts | `pytest tests/contract/test_prepare.py tests/contract/test_docker_compose.py tests/contract/test_local_profiles.py` |
| `FSI-001`, `FSI-003` | fixture package/build source boundary | fixture root cannot enter production/discovery | import/architecture contracts | `pytest tests/contract/test_import_boundaries.py tests/contract/test_architecture_governance.py` |
| `NPC-002` | prompt catalog and prompt dump script | stale root detector and temporary review-tree test | prompt catalog/dump tests | `pytest tests/graph/test_prompt_catalog.py tests/graph/test_prompt_dump.py` |
| `PRS-001`, `PRS-004`, `PRS-005`, `PRS-006`, `PRS-011`, `PRS-014`, `PRS-015`, `PRS-017`, `DRC-002`, `DRC-006`, `DRC-011` | structural registry and generated module locator | canonical-root/no-alias/locator fixture tests | architecture and charter contracts | `python3 openspec/governance/check_project_architecture.py` |
| `EVH-005`, `EVH-010`, `EVH-025`, `EVH-026` | test/evidence registry and detectors | invalid root/unknown requirement detector fixtures | assets and requirement coverage checks | `UV_OFFLINE=1 make test-assets && UV_OFFLINE=1 make test-req-coverage` |
| `EVH-024`, `RUI-011` | Bundle-bound public release execution boundary | legacy identity/checkpoint/GraphHost/workspace observation rejection, reauthorization of selected Bundle-local State, and loss without a contained-store fallback | release control-plane cases; separately tracked manual full-real acceptance | `pytest tests/unit/test_release_control_plane.py` |

## Mandatory Direct Cases

- **`resume` versus `refine`:** the lifecycle integration/HITL/state-reducer tests
  prove that only a current correlated `AcceptedHumanResponse` reaches `resume`, while
  bounded refinement text is admitted separately without consuming the pending response.
- **Bundle loss:** deletion tests retain a legacy session/binding/checkpoint observation
  and prove the lifecycle result is unavailable with no replacement directory/State.
- **Root move:** architecture, Docker, profile, and prompt-dump detector cases prove
  that `deep_research_harness/` is the one active physical root and that a stale scan
  cannot pass empty.
- **EVH-024 release proof:** the release control-plane case proves that the sole
  model-led public-entry runner receives lifecycle and report facts from one selected
  Bundle and cannot use a legacy identity, GraphHost, checkpoint, or workspace path.
  A successful credentialed run is retained as manual issue evidence, not substituted
  by a fixture or required by this change's deterministic closeout.
