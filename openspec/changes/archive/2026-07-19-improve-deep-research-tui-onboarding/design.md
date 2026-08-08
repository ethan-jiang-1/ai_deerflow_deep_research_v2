## Context

`agent/scripts/demo_tui.py` currently mounts its welcome panel, full 11-phase tracker, empty `RichLog`, composer, and disabled cancel button together. It has only `question`, `hitl1`, `hitl2`, and `terminal` stages, so its first render does not distinguish onboarding from lifecycle observation. The current UI also writes raw lifecycle payloads to the visible log even when the user only needs to answer the next question.

The TUI and `demo_real.py` both build their all-real recipe through `agent/scripts/_demo_core.py`. `ResearchGraphRecipe.create()` accepts a `node_agent_bridge_factory`; the runtime constructs that factory with a trusted envelope and execution policy, and passes an explicit zero-tool resolver for HITL-1/topic planning. Wave workers use the factory's default resolver. The existing `RuntimeNodeAgentBridge._default_tools_resolver()` falls back to global `get_app_config()` whenever `DemoAppConfig.tools` is empty. Supplying a Tavily `ToolConfig` to the shim alone is not sufficient: the upstream Tavily `web_search_tool` and `web_fetch_tool` also read global `get_app_config()` for their client credentials.

Textual background workers exit the application by default when their coroutine raises. The current handlers await `run_deep_research()` inline, so the new presentation design needs an explicit worker failure policy as well as a processing-state policy. The installed Tavily client provides `AsyncTavilyClient` with explicit async context-manager cleanup, so a demo-local wrapper can avoid both synchronous event-loop blocking and unbounded client lifetime.

`run_deep_research()` awaits a complete graph `ainvoke()` before projecting a `DeepResearchControlResult`. The returned `execution_trace` is therefore authoritative only at lifecycle-call boundaries; the current TUI cannot observe individual nodes while a start or resume call is in flight.

This remains an agent-owned standalone demo. `agent/src/`, `backend/`, and `frontend/` are outside the change. No configuration field changes, next-agent-build action, or Gateway restart are introduced; the demo reads its process environment only when it starts.

## Goals / Non-Goals

**Goals:**

- Make the first screen communicate one action: enter a research question and submit it.
- Reveal lifecycle detail in proportion to the current stage without changing graph, checkpoint, HITL, or cancellation authority.
- Make a fully deterministic Textual route available through `--fake` and `make demo-tui-fake`.
- Make the all-real CLI and TUI obtain only the demo-local Tavily tools they require, without relying on a root `config.yaml` tool entry.
- Preserve truthful checkpoint-driven phase display and deterministic, zero-API tests at the TUI and demo-core seams.

**Non-Goals:**

- No `astream_events`, polling loop, callback bridge, or claim of node-internal live progress.
- No structured HITL form, new terminal product surface, Gateway/Web/IM integration, second graph, checkpoint schema, or persistent authority.
- No generic configurable web-provider catalog, modification of upstream Tavily tools, global `AppConfig` mutation, or credential persistence.
- No changes under `agent/src/`, `backend/`, or `frontend/`.

## Decisions

### 1. One TUI stage controller owns visibility, not lifecycle state

`DeepResearchDemoTUI` will retain lifecycle identifiers, pending request data, and the latest projected result only as presentation state. A single stage-transition helper will set widget visibility, prompt copy, input enabled state, focus, and cancel availability together; it will not infer or write graph state.

The display contract is:

| Stage | Visible surface | Input and controls |
| --- | --- | --- |
| `question` | Product title, one short instruction, and the prefilled example composer | Composer enabled; tracker, lifecycle log, and cancel absent from layout |
| `starting` | Bounded "starting research" status only | Composer disabled; no fabricated phase progress and no cancel action |
| `hitl1` | Clear free-text scope prompt, examples, and a concise lifecycle status | Composer and explicit cancel enabled; full tracker remains hidden |
| `processing` | Full checkpoint-driven tracker, lifecycle status/log, and a bounded running indicator | Composer and cancel disabled while the lifecycle call is unresolved |
| `hitl2` | Typed decision prompt, advertised choices, lifecycle log, and a compact tracker | Composer and explicit cancel enabled |
| `terminal` | Final tracker state and concise terminal summary | Composer and cancel disabled |

Widgets will remain mounted and be shown or removed from layout using Textual display/style state rather than being repeatedly mounted and removed. This keeps dimensions stable, preserves selector-based tests, and avoids focus races. The user-facing log will contain bounded status/summary messages rather than raw control/HITL JSON; the existing typed `HumanMessage` construction and advertised-decision validation remain unchanged.

Alternative: retain every panel at all stages and only replace its contents. Rejected because the empty log and pending-only tracker compete with the sole onboarding action. Alternative: put the interaction into select boxes/forms. Rejected because the existing free-text HITL contract carries richer research scope and needs no new schema.

### 2. Fake and real modes share the same TUI module and stage transitions

The TUI entry point will parse `--fake`. Without the flag it remains all-real and validates prerequisites before constructing the application. With the flag it builds the existing `mode="fake"` recipe, skips all credential checks, and follows the same stage controller, input routing, cancellation path, and terminal projection as real mode. The header will accurately label the selected mode so the fake flow cannot be mistaken for real research.

`make demo-tui` and the real CLI targets will use the existing Makefile `LOCAL_ENV_ARG`: it supplies `--env-file .env` only when that file exists, otherwise preserving explicitly exported process credentials. `make demo-tui-fake` will select the existing `operations` and `demo-tui` extras, pass `--fake`, and omit `LOCAL_ENV_ARG`; it must start with no model credential, Tavily key, network service, or root configuration file. All demo targets will forward `DEMO_ARGS` consistently.

Alternative: create a second fake TUI script. Rejected because it duplicates lifecycle presentation and allows mode-specific UI behavior to drift. Alternative: make fake the default. Rejected because the existing `demo-tui` command is the documented real-mode entry; an explicit flag preserves that contract.

### 3. Each demo entry owns and closes exactly one adapter

`DeepResearchDemoTUI` will accept an explicit `mode: Literal["fake", "real"]` and create exactly one `DemoAdapter`; it will build the selected recipe from that adapter's work-unit-store factory. It will not accept a prebuilt recipe that could capture a second adapter. `on_unmount()` and `main()`'s `try`/`finally` guard around `app.run()` will both call one private one-shot TUI cleanup helper, which invokes the owned adapter's idempotent `close()` at most once. This covers normal unmount and abnormal application exit without double-cleaning temporary state.

The fake/real CLI entry points will similarly enclose adapter use in `try`/`finally`. Focused Textual tests will choose `mode="fake"` and temporarily patch the imported lifecycle runner only for delayed/error behavior, relying on fixture restoration rather than injecting an externally owned recipe. This keeps the adapter, envelope, temporary directories, host, and recipe on one ownership chain.

Alternative: retain `_recipe` injection for tests. Rejected because the current test helper constructs a separate `DemoAdapter` whose temporary directory is never owned or closed by the TUI instance. A direct mode selection is both smaller and representative of the user-facing route.

### 4. Demo-local bridge factory closes over Tavily credentials

`_demo_core.py` will provide a small bridge-factory adapter compatible with the existing `node_agent_bridge_factory(envelope=..., policy=..., tools_resolver=...)` seam. If the runtime passes a resolver explicitly, the adapter will preserve it; this keeps HITL-1/topic planning zero-tool. Otherwise it will supply a demo-local resolver that:

1. reads `TAVILY_API_KEY` only from the launched demo process;
2. constructs a fresh pair of asynchronous `web_search` and `web_fetch` `BaseTool` instances for each `RuntimeNodeAgentBridge.run_agent()` call, so their closure state belongs to exactly one bounded agent run;
3. creates an `AsyncTavilyClient` inside `async with` for each provider call and closes it before the tool result is returned;
4. caps search output at five normalized `{title, url, snippet}` records and fetch output at the existing bounded extracted-content shape;
5. records the exact search-result URLs in that run's tool closure and rejects `web_fetch` URLs that were not returned by its `web_search`; and
6. filters those tools against `ExecutionPolicy.allowed_tool_names`, exposing `web_fetch` only when `web_search` is also eligible because fetch provenance depends on that search; and
7. raises the existing typed configuration failure when a non-empty worker policy has no usable tool set, including a fetch-only policy.

The tools will not import or call `get_app_config()`. The key remains in process-local trusted closure state, never in graph state, checkpoints, log text, model-facing prompts, or a committed file. Provider exceptions and fetch-provenance denials return bounded, key-free tool errors to the agent; they never stringify a client object or its configuration.

Because the demo-local factory uses the Tavily SDK, `agent/pyproject.toml` will add a dedicated `demo-real` extra with a compatible `tavily-python` floor. `demo-real*` and real `demo-tui` commands will select that extra in addition to their current extras; fake CLI and fake TUI commands will not. The SDK import will remain lazy behind the real tool factory. `agent/uv.lock` will be regenerated and checked. The existing `make install` and credential-free canonical verification composition remains `operations` + `demo-tui`: real commands select their own extra, and deterministic tests replace the lazy SDK import boundary with a stub. This makes the demo's package interface independent of `deerflow-harness` retaining Tavily as a transitive dependency without expanding the fake commands' direct extra selection; the current harness lock may still install Tavily transitively.

`build_demo_recipe(mode="real", ...)` will use this adapter while continuing to call `ResearchGraphRecipe.create()` with `ALL_REAL_MODES`; fake mode will continue to omit implementation modes and any bridge. Both `demo_real.py` and the real TUI will use one pure prerequisite helper that accepts only non-blank credential values and reports missing model credentials separately from a missing `TAVILY_API_KEY` before graph construction. `DemoAppConfig` will use the same non-blank predicate when choosing its model configuration, so preflight and model construction cannot disagree.

Alternative: populate `DemoAppConfig.tools` and use `_default_tools_resolver`. Rejected because the upstream Tavily wrappers independently consult global configuration and would still fail without a matching root `config.yaml`. Alternative: mutate global config for the demo. Rejected because it makes a standalone command depend on process-global state and risks affecting unrelated DeerFlow callers. Alternative: modify upstream Tavily tools. Rejected by the downstream ownership boundary.

### 5. Processing state is honest about the available observability

Before each `start`, `resume`, or explicit `cancel` call, the TUI will transition to `starting` or `processing`, disable re-entry, render the applicable bounded status, and dispatch the async lifecycle work through one exclusive Textual worker in a dedicated lifecycle group. Cancellation uses that same group and disables its trigger before dispatch, so it cannot race with another lifecycle action or block the event handler. That worker SHALL use `exit_on_error=False`; its body catches unexpected exceptions, projects a fixed redacted terminal failure through the normal stage controller, and re-raises `CancelledError` so application teardown does not look like a completed or failed research action. User-visible status, terminal summary, and error rendering will be a whitelist of stable lifecycle fields (`code`, `status`, `phase`, request ids, and terminal reason where present). Stage copy and HITL-1 examples are static; the only data displayed from a pending request are its request id and its advertised HITL-2 option values. The TUI SHALL not display raw exception strings, raw control/HITL payloads, environment values, or client representations. When a call returns, it will update the tracker from the returned `execution_trace` and transition to HITL-1, HITL-2, or terminal. An unresolved call has no active-node marker and does not append guessed phases; it only states that the lifecycle is running.

The tracker remains derived from projected control results and may batch multiple completed nodes after a resume. It will not poll checkpoints or consume the bridge's internal progress emitter. This preserves the one controller and ensures the UI never represents a phase that the graph has not reported.

Alternative: immediately mark the next expected node active. Rejected because retries, gates, and routing make that prediction untrustworthy. Alternative: add streaming to the graph tool. Rejected because it would widen the runtime contract beyond this agent-owned presentation change.

### 6. Tests exercise presentation and tool seams without external services

Focused Textual pilots will instantiate the explicit fake mode and verify: startup layout excludes tracker/log/cancel; the happy path reveals the appropriate staged surfaces; invalid HITL-2 choices do not resume; explicit cancellation stays a lifecycle action; terminal state disables input; and no-key fake launch is permitted. A delayed scripted lifecycle test will hold a call in `processing` long enough to assert disabled controls and the absence of fabricated trace progress. A separate injected lifecycle failure will prove that an unexpected exception reaches the redacted terminal state without terminating the Textual application.

Demo-core unit tests will replace the lazy Tavily SDK import boundary with a stub async client and use environment patches to verify prerequisite diagnostics, the two locally named tools, policy filtering, per-call cleanup, search-result URL provenance enforcement, and that the resolver does not use global config. This preserves the canonical `operations` + `demo-tui` deterministic environment without relying on a harness transitive SDK install. They will retain fake/real recipe validation coverage. Every new deterministic selector will receive a central `TestEvidenceClaim` at its lowest responsible seam before the canonical asset check runs. Real credentials and network access are excluded from this change's deterministic acceptance; a manually selected real run remains a separate operator check.

## Risks / Trade-offs

- [Risk] A full real resume remains visually quiet until it returns. → The processing indicator makes the wait explicit and the tracker updates only from the next authoritative control result; streaming is deferred rather than simulated.
- [Risk] A user may try to cancel while a graph call is in flight. → Disable cancel during `starting`/`processing`; retain the existing explicit cancel action only at a graph-owned HITL suspension.
- [Risk] Tavily provider behavior can fail after valid preflight. → Preflight validates non-blank credential presence only; bounded key-free tool errors flow through the graph, and unexpected lifecycle-worker errors remain visible in terminal summary instead of exiting the TUI.
- [Risk] A model could request an arbitrary extraction URL. → `web_fetch` accepts only exact URLs returned by the same bounded agent run's `web_search`; provenance rejection is covered deterministically.
- [Risk] Tool closures or UI failure handling can accidentally leak a secret through diagnostics. → Do not serialize the client or key, redact configuration errors to variable names, render only whitelisted lifecycle fields plus a fixed unexpected-failure message, and cover tool/UI error paths with sentinel credentials.
- [Risk] Textual visibility changes can break narrow terminals. → Keep widgets mounted, use bounded heights and display state, and cover stage layout with pilot tests rather than terminal-size-specific assumptions.

## Migration Plan

1. Add focused failing unit and Textual pilot tests for the new stage matrix, adapter ownership/cleanup, fake entry path, real preflight, and local tool resolver.
2. Implement the demo-core bridge factory/prerequisite helper and wire it through `ResearchGraphRecipe.create()` without changing runtime or graph code.
3. Implement explicit TUI mode/adapter ownership, the stage controller, and `--fake` parsing; add the Make target and update agent documentation for both modes and their prerequisites.
4. Run the focused unit/integration tests, `cd agent && make lint`, required agent governance/verification targets, and strict OpenSpec validation; confirm no protected upstream path changed.

Rollback removes the agent-owned bridge adapter, fake target, stage presentation changes, tests, and documentation. There is no data migration, configuration mutation, checkpoint conversion, or process restart to reverse.

## Open Questions

None. Per-node streaming and broader web-provider selection are intentionally deferred rather than hidden behind this demo interface.
