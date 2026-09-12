# runtime/ — Reader Index

> This file is an index only. It is not a second authority and not runtime
> configuration: code, module docstrings, typed contracts, owning OpenSpec
> specifications, and tests remain the authority for current behavior. When a
> file here and its docstring disagree, the docstring wins; fix this index in
> the same PR.

Thirty-two modules plus the `evaluation/` subpackage, ~13.8k lines, in five
clusters. The layer owns DeerFlow
binding, trusted I/O, persistence, and lifecycle adapters — the boundary where
guessing is most expensive, so start from the cluster, then the module
docstring, then the owning spec.

## 1. Run Bundle lifecycle and control

The public `deep_research` tool's `start | resume | status | cancel | refine`
boundary: Bundle publication, scoped discovery, transitions, and graph
execution through one selected Bundle.

| Module | Responsibility | Owning evidence |
| --- | --- | --- |
| `bundle_lifecycle.py` | Run Bundle publication and scoped discovery where trusted scope, filesystem persistence, and lifecycle State meet | `deep-research-harness-run-bundles` |
| `bundle_control.py` | One runtime-owned controller for the five public Bundle lifecycle actions | `deep-research-harness-run-bundles` |
| `bundle_graph.py` | Execute the real research graph through one selected Run Bundle (Bundle owns checkpoint, ledger, content) | `deep-research-harness-run-bundles` |
| `bundle_transition.py` | Safe Bundle root participation checks for transitions | integration transition tests |
| `bootstrap_bundle.py` / `request_bundle.py` | Bootstrap / profile Bundle stores (atomic publish, `.bootstrap.lock` / `.profile.lock`) | `research-confirmation`, `bootstrap-node` |
| `checkpoint.py` | Checkpoint adapter (memory / Bundle-local file-backed) | `research-graph-lifecycle` (REG-005) |
| `control.py` | Control-plane seams shared by the lifecycle actions | `deep-research-harness-run-bundles` |

## 2. Graph and node execution

Trusted-envelope to graph-node plumbing: identity, projection, node-agent
bridge, HITL input, and recipes.

| Module | Responsibility | Owning evidence |
| --- | --- | --- |
| `projection.py` | The only place a research scope becomes model-facing structure (frozen, authority-reduced views) | `runtime-integration` (RUI-002) |
| `runtime_adapter.py` | DeerFlow runtime binding, sandbox/workspace mount surfaces | `runtime-integration` |
| `graph_host.py` | Generic graph host: recipes, namespaces, per-action providers | `runtime-integration` (RUI-004) |
| `research.py` | Research graph recipes and bounded node-capability policy helpers (no lifecycle ownership) | `research-graph-lifecycle` |
| `node_agent_bridge.py` | The only raw-binding owner; graph nodes reach bounded node-agents exclusively through it | `node-agent-runtime` (NOA-001/014) |
| `node_context_store.py` | Node context snapshots (`snapshot.json`) for inspection | `node-agent-reader-interface` |
| `human_input.py` | Trusted outer-message selection and HITL projection | `research-graph-lifecycle` (REG-003) |
| `identity.py` | Scope/user identity shaping for trusted envelopes | `runtime-integration` |
| `non_interactive.py` | Closed runtime-only inputs for a non-interactive graph start | `runtime-integration` |

## 3. Work units

| Module | Responsibility | Owning evidence |
| --- | --- | --- |
| `work_unit_store.py` | Runtime-owned atomic submission ledger store | `work-unit-kernel` (WOU-004/006) |
| `work_unit_storage_probe.py` | Storage readiness probe for the ledger store | `work-unit-kernel` |

## 4. Observation, experience, and evaluation

Evidence-shaped projections of an already-authorized Run — none of these can
discover, authorize, reopen, mutate, or recreate a Bundle.

| Module | Responsibility | Owning evidence |
| --- | --- | --- |
| `run_observation.py` | Bounded Bundle-local observations (`run-summary.json`); evidence, never a second Run locator | `runtime-observability` |
| `run_experience.py` | Lifecycle-to-presentation projection for standalone demos | `research-run-experience` (RER-*) |
| `events.py` | Safe standard-log and live projections for runtime facts | `runtime-observability` (RTO-*) |
| `trace_projector.py` | Durable facts in, honest versioned trace pages out (checkpoint is commit authority) | `runtime-observability` (LDO-*) |
| `gateway_observer.py` | Bounded public Gateway transport for local operator entrypoints | `gateway-operator-observer` (GOO-*) |
| `diagnostics.py` / `probe.py` | Readiness/diagnostic probes (opt-in dev tooling, not a security boundary) | `runtime-operations` |
| `startup_snapshot.py` | Startup snapshot (`v1`) of configured runtime facts | `runtime-operations` |
| `workspace_reader.py` | Composition-injected bounded read surface for the local operator | `runtime-integration` |
| `session_workbench.py` | Inspect and control only Bundles validated by one lifecycle boundary | `research-local-session-workbench` |
| `evaluation/` | Runtime-owned evaluation adapters | `evaluation-hardening` |

## 5. Debug driving

| Module | Responsibility | Owning evidence |
| --- | --- | --- |
| `debug_driver.py` | Headless local debug driver over the one real graph (sessions, leases, stop policies) | `local-workflow-debug-driving` (LDD-*) |
| `debug_driving.py` | Control lease persistence (`debug-lease.json`) | `local-workflow-debug-driving` |
