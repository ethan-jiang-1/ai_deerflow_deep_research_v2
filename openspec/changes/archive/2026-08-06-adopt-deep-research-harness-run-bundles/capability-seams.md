# Accepted Capability And Seam Audit

This apply-time audit pairs every delta capability with the accepted main specification,
its closest causal implementation seam, and the lowest responsible existing/new test
seam. The main-spec wording was read as the old contract; the active delta is the one
pending replacement. `node-prompt-catalog` is included because its ignored review path
is a governed structural consumer, not because it owns lifecycle state.

| Capability | Direct production seam | Deterministic evidence seam | Apply task |
| --- | --- | --- | --- |
| `bootstrap-node` | `runtime/bootstrap_bundle.py`, `graph/nodes/bootstrap/node.py` | `tests/unit/test_bootstrap_bundle.py`, `tests/blocking_io/test_bootstrap_bundle_runtime.py` | 2.1, 2.6, 4.1-4.2 |
| `cognitive-evaluation-suite` | `runtime/evaluation/runner.py` | `tests/eval/test_cognitive_evaluation_suite.py` | 7.5 |
| `deep-research-agent-charter` | module guide and `check_agent_charter.py` | `tests/contract/test_agent_charter_governance.py` | 7.4 |
| `deep-research-harness-run-bundles` | new runtime lifecycle plus `domain/{bundle,lifecycle,state}.py` | bundle/state/lifecycle focused suites | 2.1-3.6 |
| `demo-pipeline` | `scripts/_demo_core.py`, demo entry scripts | `tests/unit/test_demo_core.py`, demo integration tests | 6.2, 7.3 |
| `deployment-configuration` | `scripts/prepare.py`, Docker config, public-skill materialization | `tests/contract/test_prepare.py`, `test_docker_compose.py`, `test_public_skill.py` | 6.3, 7.3 |
| `evaluation-hardening` | requirement/evidence assets and checker scripts | `tests/contract/test_requirement_test_coverage.py`, asset checker | 1.4, 8.1 |
| `fixture-source-isolation` | `src_fake/` composition and packaging metadata | `tests/contract/test_import_boundaries.py` | 7.3 |
| `hitl1-node` | `graph/nodes/hitl1/node.py`, `runtime/request_bundle.py` | `tests/graph/test_hitl1_node.py`, `tests/integration/test_hitl1_lifecycle.py` | 2.3, 2.6, 4.3 |
| `local-configuration-profiles` | `scripts/local_profiles.py`, `profiles/` | `tests/contract/test_local_profiles.py` | 7.3 |
| `node-agent-runtime` | `runtime/node_agent_bridge.py`, runtime graph context | `tests/unit/test_node_agent_bridge.py` | 4.4 |
| `node-prompt-catalog` | `graph/prompt_catalog.py`, prompt dump script | `tests/graph/test_prompt_catalog.py`, `test_prompt_dump.py` | 2.8, 7.1 |
| `project-structure` | `project-structure.toml`, architecture renderer | `tests/contract/test_architecture_governance.py` | 7.1-7.4 |
| `research-cli-onboarding` | real CLI/demo session projections | `tests/integration/test_demo_real.py`, public-skill contract | 6.2-6.3 |
| `research-demo-tui` | `scripts/demo_tui.py` | `tests/integration/test_demo_tui.py` | 6.2 |
| `research-fake-cli-onboarding` | README and fake demo command path | `tests/integration/test_demo_cli.py` | 6.2-6.3 |
| `research-graph-lifecycle` | `runtime/research.py`, `runtime/graph_host.py`, `domain/state.py` | state and lifecycle integration suites | 2.2-2.5, 3.2-3.6 |
| `research-local-session-workbench` | `runtime/session_workbench.py`, `scripts/session_workbench.py` | workbench contract/runtime/integration suites | 2.7, 5.3, 6.2 |
| `research-run-experience` | `domain/run_experience.py`, `runtime/run_experience.py` | run-experience contract tests | 2.7, 6.2 |
| `research-run-session` | `domain/run_session.py`, `runtime/run_session.py` | `test_run_session_store.py`, session integration tests | 2.5, 5.1 |
| `research-session-artifact-view` | artifact catalog/reader in `runtime/session_workbench.py` | session-workbench contract/runtime suites | 2.7, 5.3 |
| `research-session-discovery-and-operations` | `domain/session_operations.py`, `runtime/session_operations.py` | resolver/operations contract and integration suites | 2.2, 2.5, 5.2 |
| `research-session-lifecycle-binding` | binding domain/store | binding unit and integration suites | 2.5, 5.1 |
| `runtime-integration` | `tool.py`, `runtime/control.py`, `runtime/runtime_adapter.py` | public entry replay and lifecycle tool suites | 2.2, 2.7, 6.1 |
| `topic-planning-node` | `graph/nodes/topic_planning/node.py` | topic planning graph/integration suites | 2.6, 4.5 |
| `wave1-node` | Wave1 node/subgraph/review | Wave1 work-unit and graph suites | 2.6, 4.5 |
| `wave2-synthesis-node` | Wave2 synthesis node | Wave2 real graph suite | 4.5 |
| `work-unit-kernel` | bundle/work-unit domain and runtime stores | bundle/store/submission suites | 2.6, 4.1, 4.5 |

## Reconciliation Result

- Each classified authority hit in [impact-inventory.md](impact-inventory.md) has an
  owning delta requirement, a named task, and a deterministic proof seam.
- The retired external-checkpoint/session/binding topology is intentionally covered by
  the `research-graph-lifecycle`, `runtime-integration`, run-session, binding, and
  operations deltas rather than being hidden behind a compatibility adapter.
- No additional behavior-changing capability is unowned. The separate terminology
  collision in `CONTEXT.md` and ADR-0028 is tracked as task 1.7 before documentation
  is finalised.
