# Deep Research Testing And Evaluation

This reference explains test selection and evidence posture for contributors and
operators. Exact selectors and `TestEvidenceClaim` records remain in the central
test-owned registry; this document is not the enumerable catalog or a runtime behavior
authority. For code-change routing, begin with [`../AGENTS.md`](../AGENTS.md) and its
lowest responsible test seam.

## Test Command Route

Run commands from `deep_research_harness/`. During an ordinary edit, run the smallest relevant target
first, then use `UV_OFFLINE=1 make verify` as the complete deterministic gate.

| Goal | Command |
| --- | --- |
| Format and lint | `make format`, `make lint` |
| Complete deterministic gate | `UV_OFFLINE=1 make verify` |
| Pytest-only union of deterministic selections | `make test` |
| Fast asset/contract/domain/engine/unit/graph/evaluation selection | `make test-fast` |
| HITL profile parsing and lifecycle slice | `make test-intake` |
| Retained-summary/event-journal slice | `make test-retained-observation` |
| Ledger and work-unit controller slice | `make test-work-unit` |
| Strict msgpack checkpoint compatibility | `make test-strict-checkpoint` |
| Validate the `test-fast` JUnit duration report | `make test-duration-policy` |
| Reference fast-lane collection/setup/call benchmark | `make benchmark-fast` |
| Generate the ignored local node-prompt review catalog | `make prompt-dump` |
| Validate an existing local node-prompt review catalog without writing | `make prompt-dump-check` |
| Deterministic integration/blocking-I/O correctness | `make test-integration` |
| Deterministic real-loop workflow conformance | `make test-workflow` |
| Maintained low-frequency clean-copy entry regression | `UV_OFFLINE=1 make test-entry-environment-regression` |
| Viability, durability, or blocking-I/O slices | `make test-viability`, `make test-durability`, `make test-blocking-io` |
| Asset and requirement-coverage governance | `make test-assets`, `make test-req-coverage` |
| Credentialed bounded live canaries | `make test-live` |

## Node Prompt Review Catalog

When a node prompt builder or the shared Node Cognitive Control Program changes, run `make
prompt-dump` and inspect the generated files below `.node-prompt-review/`. Each file is a
code-owned synthetic case with the final system policy, final human message, and the
request's tool policy; it is intentionally not a locally resolved tool inventory.
The workspace is ignored and optional. `make prompt-dump-check` validates an already
generated workspace without writing; a missing workspace is a precondition failure only
for that opt-in command.

The fast deterministic selection retains source-level catalog inventory, shared-renderer,
and temporary-tree generation proof. It neither creates nor requires `.node-prompt-review/`,
so `make verify` remains valid in a clean checkout. The generated Markdown is not runtime
authority or a prompt-editing surface. Do not edit it by hand: update the owned Python prompt
source or canonical catalog fixture, then regenerate it.

## Evidence Classes

Deep Research maintains three active asset classes. Code-correctness tests cover
deterministic domain, engine, runtime, checkpoint, sandbox, store, and filesystem
contracts. Agent-workflow conformance tests run real nodes, graph prefixes, middleware,
policies, budgets, parsers, submit, gates, and artifacts with scripted model/tool
adapters. Behavioral evaluation runs bounded real model/tool canaries and separates hard
invariants from non-blocking quality and cost metrics. The retained full-real selector
is suspended diagnostic material, not an active asset class or release gate.

Every test and report carries an authenticity claim from this ladder:

1. `FAKE_GRAPH` proves topology and graph-owned control flow.
2. `REAL_NODE_FAKE_CAPABILITIES` proves a real node's typed state and route behavior.
3. `SCRIPTED_REAL_WORKFLOW` proves the real bridge, middleware, policy, loop, stores,
   and gates.
4. `LIVE_REAL_DEPENDENCIES` proves observed model/tool-provider behavior under explicit
   bounds.
5. `FULL_REAL_PIPELINE` describes the retained full-real scenario; it is currently
   suspended and does not prove a current release result.

A lower level cannot satisfy a higher claim. The preferred stable test seams, from
narrowest to broadest, are domain/engine interfaces; `NodeSpec` plus
`NodeExecutionCapabilities`; runtime adapter/bridge/store protocols; lifecycle handlers
plus mixed graphs; and the real public entry.

Reusable manifests live in `tests/scenarios/`. Each scenario declares a stable id, risk
family, requirement and optional regression ids, entrypoint, authenticity,
preconditions, scripted/live inputs, expected route and terminal outcome,
artifacts/citations, hard invariants, metrics, and permitted degradation. Internal nodes,
middleware, gates, validators, and stores stay real when a scenario claims workflow
conformance; only true external model/tool, time, randomness, and supported fault
boundaries may be replaced. Deterministic scenarios require no credential or public
network.

Use the terms precisely: a scripted case drives a real production loop with short
deterministic external responses; a provider-shape fixture is a minimized redacted
payload passed through the production normalization/validation seam; a persisted trace replay
is reserved for a reviewed temporal/interleaving need and is not a synonym for either.
Raw provider responses are not retained as test fixtures.

## Workflow Outcome Conformance

`tests/assets/workflow_nodes.py` syntax-discovers every production graph-node package
that invokes `run_agent`. Each discovered owner declares its applicable closed failure
outcome classes and references collected deterministic evidence for both the phase seam
and its lifecycle or work-controller projection. `scripts/check_test_assets.py` rejects
a missing owner, declared class, collected selector, or projection assertion, including
an empty or mis-scoped discovery root. The inventory is a traceability join, not a retry
or lifecycle authority; the scripted real-node and controller/lifecycle tests remain
the behavioral proof.

## Direction-Loop Evidence

The direction-loop proofs stop at their actual handoff. The ordinary-controller tests
materialize the dedicated Agent, observe canonical `read_file` loading of the committed
public skill and captured skill context, then observe a later exclusive lifecycle call.
They use scripted external model choices, so they prove the real loader, middleware,
tool, typed-result, and lifecycle handoff, not that a model will make a good semantic
choice in production. Prewritten lifecycle calls remain wiring evidence only.

The refinement workflow proofs establish one pending direction, pending-response
separation, terminal-safe-point application, same-Bundle rerun, canonical profile read,
runtime-loaded topic-planning capability, zero-tool bridge, and deterministic topic
materialization. They prove that accepted notes and a current-round direction reach the
planning program as bounded data; they do not prove planning quality.

The source-controlled `public-controller-direction-loop@v1` and
`topic-planning-direction-loop@v1` Cognitive Evaluation Cases add supplemental judgment
coverage. Their declarations pin control digests, expected/forbidden effects, telemetry,
review criteria, and three fresh repetitions. A selected live run requires the declared
credential preflight. Missing credentials create no production Bundle, Evaluation Bundle,
or Review Record and are recorded as limited evidence, never as a deterministic pass,
implementation defect, or release result.

## Deterministic And Live Lanes

Selection is intentionally non-overlapping. The rapid gate is `make test-fast`,
`make test-integration`, and `make test-workflow`; `make test` is their pytest-only
union and excludes `requires_llm`, `release_e2e`, and `periodic`. `make verify` is the
canonical complete rapid deterministic gate and adds root governance, lock consistency,
lint, asset governance, and requirement coverage; it also leaves
`.reports/test-fast.xml` for the separate CI/local `make test-duration-policy` check.
Requirement impact metadata is maintained beside the existing evidence policy in
`tests/assets/requirement_evidence.py`. Prepare the project with `make install` and run
the rapid gate offline as `UV_OFFLINE=1 make verify`.

`tests/scenarios_periodic/` holds maintained deterministic public-entry evidence whose
clean-copy install cost is deliberately outside the rapid gate. Its scenarios are
credential-free, carry `periodic`, and are run with
`UV_OFFLINE=1 make test-entry-environment-regression`, which writes
`.reports/test-entry-environment.xml` and enforces a 180-second per-scenario duration
budget. Owner/reason/expiry waivers live in `scripts/check_test_durations.py`; an expiry
requires a deliberate renewal. `make test-assets` collects the periodic selectors to
validate their central claims without running their process bodies. The distinct
`agent-entry-environment-regression.yml` CI job runs the target for declared
entry-environment path changes, daily, and manually; it does not change the rapid
workflow's status identity or assert branch-protection configuration.

`make test-live` selects six bounded canaries: three short public-entry prefixes and
three directly seeded late-node cases. The late-node cases prove only their focused
node/provider/store/gate semantics and explicitly do not prove the public entry,
predecessor lifecycle, production recipe, or full pipeline. Reports use
`report_schema_version=1` / `metrics_schema=evidence-v1` with typed metric status and
structural evidence basis. An explicitly selected live lane fails preflight when its
environment is incomplete; it never silently skips.

The full-real selector is retained at
`tests/scenarios_suspended/test_evh_024_release_acceptance.py`. It has no Make target, CI
workflow, active evidence claim, or published execution command. Its local README links
to the diagnostic issue; only a new approved change that first establishes its
less-than-ten-second deterministic loop may reactivate it.

CI follows the same authority split: `agent-tests.yml` runs deterministic gates on pull
requests and pushes. The six-case `agent-live-evaluation.yml` is manual-only while the
current measured lane has open failures; schedule is restored only after all six pass
and preserve the aggregate margin. Subjective quality thresholds remain reported until
a reviewed later change promotes a stable baseline.

The accepted 2026-07-17 full-real proof survives cleanup of gitignored raw reports as
the minimal redacted committed attestation in
[`release-attestation-2026-07-17.json`](release-attestation-2026-07-17.json). It proves
one isolated accepted run, not a current release result, provider distribution, or a
general quality threshold.

Every live or release defect follows the [regression-descent policy](regression-descent.md):
record a redacted discovery, classify its risk and lowest stable seam, add the smallest
red-before-green deterministic regression when it is replayable, and retain an explicit
provider-only live rationale when it is not. A successful demo or single full-real run
never replaces the lower test assets or proves distributional quality by itself.

## Runtime Verification Boundary

`make test-viability` verifies reflected async `ToolRuntime` injection and ordinary
asyncio cancellation through a nested LangGraph without private Gateway cancellation
state.

The runtime substrate and fixed fixture graph are verified with zero-API tests: the trusted
`RuntimeAdapter`, `GraphHost` with isolated checkpoint namespaces, the node-agent bridge
with budgets/policy, the reflected `infra_probe` tool, configuration materialization
(`configure.py`), the source-loading preparation core (`prepare.py`) and Docker override,
readiness diagnostics (`doctor.py`), and file-backed SQLite lifecycle recovery across a
real subprocess restart (`make test-durability`), and event-loop blocking checks
(`make test-blocking-io`). The topology snapshot is generated with
`uv run python scripts/render_topology.py`.
