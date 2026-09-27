# Deep Research Testing And Evaluation

This reference explains test selection and evidence posture for contributors and
operators. Exact selectors and `TestEvidenceClaim` records remain in the central
test-owned registry; this document is not the enumerable catalog or a runtime behavior
authority. For code-change routing, begin with [`../AGENTS.md`](../AGENTS.md) and its
lowest responsible test seam.

## Test Command Route

Run commands from `deep_research_harness/`. During an ordinary edit, run the smallest relevant target
first, then use `UV_OFFLINE=1 make verify` as the complete deterministic gate.

The pytest lanes (`test`, `test-fast`, `test-integration`, `test-workflow`) run
in parallel by default (`-n 4`; parallel safety reviewed in
`_backlog/_done/_closed_plans/CLS-053-test-regression-speedup.md` §L2). Serial is opt-out:
`make test-fast PYTEST_XDIST=` (empty). The test-required runtime extras
(textual, python-dotenv, ruamel.yaml) live in the `dev` dependency group, so
pytest targets run plain `uv run pytest` without `--extra` flags.

| Goal | Command |
| --- | --- |
| Format and lint | `make format`, `make lint` |
| Complete deterministic gate | `UV_OFFLINE=1 make verify` |
| Pytest-only union of deterministic selections | `make test` |
| Fast contract/domain/engine/unit/graph/evaluation selection | `make test-fast` |
| HITL profile parsing and lifecycle slice | `make test-intake` |
| Retained-summary/event-journal slice | `make test-retained-observation` |
| Ledger and work-unit controller slice | `make test-work-unit` |
| Strict msgpack checkpoint compatibility | `make test-strict-checkpoint` |
| Validate the `test-fast` JUnit duration report | `make test-duration-policy` |
| Reference fast-lane collection/setup/call benchmark | `make benchmark-fast` |
| Run only tests touched by the working-tree diff (local iteration) | `make test-changed` |
| Generate the ignored local node-prompt review catalog | `make prompt-dump` |
| Validate an existing local node-prompt review catalog without writing | `make prompt-dump-check` |
| Deterministic integration/blocking-I/O correctness | `make test-integration` |
| Deterministic real-loop workflow conformance | `make test-workflow` |
| Maintained low-frequency clean-copy entry regression | `UV_OFFLINE=1 make test-entry-environment-regression` |
| Viability, durability, or blocking-I/O slices | `make test-viability`, `make test-durability`, `make test-blocking-io` |
| Asset governance | `make test-assets` |
| Credentialed bounded live canaries | `make test-live` |

## Test Directory Taxonomy

Top-level test directories under `deep_research_harness/tests/`:

| Directory | Meaning |
| --- | --- |
| `unit/` | Deterministic unit-style contracts for a single module or seam. Not import-isolated: some files reuse scenario/asset helpers. |
| `domain/`, `engine/`, `graph/` | Deterministic contracts for the named layer (domain models, engine gates/kernels, graph composition/routing). |
| `contract/` | Cross-cutting governance and meta contracts (lane selection, verification gate, structure, evidence, documentation integrity). |
| `assets/` | Test-owned support library: data plus validators (incidents, evidence claims, node conformance, lane expressions) imported by tests and `make test-assets`; contains no collected test and no pytest fixtures. |
| `fixtures/` | Shared **helper modules** (scenario recipes, scripted tools, fake models); despite the name it contains no `@pytest.fixture` declarations. |
| `scenarios/` | Reusable scenario manifests (stable id, risk, entrypoint, expected outcome). |
| `scenarios_periodic/` | Scheduled periodic workflow evidence, excluded from the fast/integration lanes. |
| `scenarios_suspended/` | Retained suspended release-acceptance material; collectable but excluded by its `requires_llm`/`release_e2e` markers. |
| `integration/`, `blocking_io/` | Deterministic integration and event-loop/blocking-I/O lanes. |
| `live/` | Credentialed live canaries (`requires_llm`), never part of the deterministic gate. |
| `eval/` | Evaluation metrics, corpora, and adversarial checks. |
| `mutations/` | Declarative mutation registry for the delivery lanes: each entry removes one guarded behaviour so `make mutation-check` can require the named selector to go red. Contains no collected test. |

Directory placement is a convention, not an evidence authority: exact selection and
evidence semantics remain in the owning spec and executable test-owned assets.

## Deterministic Network Boundary

Every deterministic test runs under the autouse `_deny_public_network` fixture in
`tests/conftest.py`, which blocks non-loopback socket connects. A test that must reach
a real provider belongs in `tests/live/` and carries the `requires_llm` marker; the
retained `release_e2e` marker is the only other escape. A deterministic test that
incidentally needs network fails loudly with `deterministic test network denied`.

## Fixtures Directory Is Helpers

`tests/fixtures/` contains shared helper modules (scenario recipes, scripted tools,
fake model classes) — not `@pytest.fixture` declarations. Look for reusable pytest
fixtures inside the test files that use them, not in this directory.

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

## Test Hygiene

Tests preserve runtime invariants without changing production execution topology
(borrowed from the framework's own test guidance):

- synchronize on explicit signals (events, wait-for predicates, bounded polling)
  instead of sleep thresholds — a timing-based assertion is a flake with a deadline;
- release every blocked worker before the test ends, so a hung double never leaks
  into the next case;
- restore every process-global patch in teardown;
- never rewire production topology (routing, policy, step order) to make a test pass;
- label scripted/synthetic inputs as scripted/synthetic in the assertion and in the
  evidence claim — a fixture run must never read as real evidence;
- read credentials only from named environment variables, and never download
  external material silently inside a test.

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
and its lifecycle or work-controller projection. `scripts/checks/check_test_assets.py` rejects
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

The runtime-control digests in `evals/control/cases/*.json` pin each case to the exact
source files it declares (prompts and domain modules). When a pinned source file
changes, run `make control-digests-check` to see the drift and re-pin deliberately with
`uv run python scripts/checks/regenerate_control_digests.py` once the change is reviewed; the
deterministic gate (`test-fast`) enforces the pin, so a stale digest turns the eval
contracts red until re-pinned.

## Deterministic And Live Lanes

Selection is intentionally non-overlapping. The rapid gate is `make test-fast`,
`make test-integration`, and `make test-workflow`; `make test` is their pytest-only
union and excludes `requires_llm`, `release_e2e`, and `periodic`. `make verify` is the
canonical complete rapid deterministic gate for this application and composes exactly
`lock-check lint test-assets test-fast test-integration test-workflow`; it runs from
this directory, is offline-capable via `UV_OFFLINE=1 make verify`, and leaves
`.reports/test-fast.xml` for the separate CI/local `make test-duration-policy` check.

The asset gate (`make test-assets`, part of `verify`) enforces a **suite-level case
budget** in addition to coverage: each lane (fast / integration / workflow / live /
periodic) and the deterministic total must stay under the limits declared in
`scripts/checks/check_test_assets.py::CASE_BUDGETS` / `DETERMINISTIC_TOTAL_BUDGET`. Adding
tests beyond a budget without a current `CaseBudgetWaiver` (reason + owner +
expiry) turns the gate red, so test-count growth is an explicit reviewed decision
rather than silent accumulation. Budget baselines are the 2026-08-22 measured counts
plus headroom; raise a budget deliberately (or add a waiver) when a bounded,
evidence-backed addition needs the room, and re-run `make test-assets`.

For local iteration, `make test-changed` runs only the test files touched by the
working-tree diff (plus `--last-failed` for the previously failing set, or a custom
`--base` ref via `make test-changed ARGS="--last-failed --base HEAD~1"`). It is a
local convenience outside the deterministic gate: the gate always runs the full lane
selection, so narrowing local runs never weakens CI evidence.
Project-level planning and closeout governance for OpenSpec changes runs as an
independent repository-root column and is never part of this Makefile gate; this
application does not read, import, execute, or link that column.
Requirement impact metadata is maintained beside the existing evidence policy in
`tests/assets/requirement_evidence.py`. Prepare the project with `make install` and run
the rapid gate offline as `UV_OFFLINE=1 make verify`.

`tests/scenarios_periodic/` holds maintained deterministic public-entry evidence whose
clean-copy install cost is deliberately outside the rapid gate. Its scenarios are
credential-free, carry `periodic`, and are run with
`UV_OFFLINE=1 make test-entry-environment-regression`, which writes
`.reports/test-entry-environment.xml` and enforces a 180-second per-scenario duration
budget. Owner/reason/expiry waivers live in `scripts/checks/check_test_durations.py`; an expiry
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
[`release-attestation-2026-07-17.json`](evidence/release-attestation-2026-07-17.json). It proves
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

## Interactive TUI Journey Harness

Import-time tests and per-link unit tests cannot see defects that live in *how the
TUI script executes as `__main__`*. Three operator-reported failures in a row were
invisible to the suite:

- the launcher never enabled `src_fixtures`, so the fixture graph failed to import
  and the app rendered a generic presentation fault (pytest injects that path via
  `pythonpath`, so every test passed);
- the C4b debug methods were defined at module level and bound to the class *after*
  the `if __name__ == "__main__": main()` guard, so a real launch blocked inside
  `main()` before the bindings ran and the first composer submit raised
  `AttributeError`;
- the submit router kept treating a live debug session as "not started", so a
  second Enter tried to open another session and was refused as `busy`.

`scripts/tui_journey_probe.py` (target: `make tui-journey`) closes that gap. It
executes the real script as `__main__` with `PYTHONPATH` stripped, replaces
`App.run` with a headless stand-in, and drives the [runbook-030](runbooks/runbook-030-debugger.md)
debugger ladder with per-step semantic assertions — Ready, Start Step landing on the
HITL1 prompt, answering, empty-Enter stepping, mid-ladder `/detach`, the retained-bundle
`busy` refusal, `/cancel` recovery, a fresh session, the ladder to `terminal`,
`/context`, and final `/detach`. It prints a step transcript, runs in about five
seconds, and exits non-zero at the first failing step with both panes captured.

**Operator-experience suite.** `scripts/tui_experience_suite.py` (`make tui-experiences`)
drives fifteen independent end-to-end operator journeys — first screen, HITL request
display, stepping, continuous run, pause semantics, observation panes, help and palette,
the recovery chain, attach, read-only replay, degraded layout, observation honesty,
harness anatomy, debuggable-object inventory, and captured-context drill-down — each in
its own app and Bundle root at a realistic terminal size, printing one PASS/FAIL line per
journey. `make debugger-proof` runs the whole debugger evidence chain (driver matrix, entry
contract, workbench tests, journey harness, experience suite) in one command.

**Rule of use:** an agent must run this harness before handing any TUI path to a
human operator, and the same assertion runs inside `make verify`
(`tests/integration/test_debugger_entry.py`). A leftover active debug bundle (a
session interrupted mid-ladder) is recovered with `make tui-journey
JOURNEY_ARGS="--cancel-active"`, which abandons it so a fresh Start Step is admitted.

Two assertion styles are mandatory, because a "green" harness that omits them can
still hand an operator a broken screen:

- **Realistic dwell.** Every checkpoint waits at least 1.3 s and then re-asserts the
  operator-facing state. Assertions that complete faster than the UI's own timers
  prove nothing: the workbench once showed the shared one-second "已收到，正在处理…"
  hint instead of the HITL prompt, and only a post-dwell assertion catches it.
- **Layout visibility.** `tests/integration/test_demo_tui.py` runs the workbench at
  80×24, 100×30 and 120×45 and asserts every operator pane has a real region inside
  the screen, the log keeps readable height, and the composer is usable and focused.
  Reading widget text is not the same as the operator being able to see the tool.

**Boundary:** the harness drives the application, CLI wiring, `__main__` execution
order, session routing, and lifecycle admission headlessly. It does not exercise the
real terminal driver or literal keystrokes; those remain a human/terminal concern.

