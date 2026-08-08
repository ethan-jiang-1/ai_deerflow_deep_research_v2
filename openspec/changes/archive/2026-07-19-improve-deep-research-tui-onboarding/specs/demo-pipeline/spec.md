> req: DPL-001, DPL-002, DPL-003, DPL-004, DPL-005

## MODIFIED Requirements

### Requirement: Shared demo core module provides infrastructure and local web tools for all demo scripts

The agent project SHALL provide `agent/scripts/_demo_core.py` containing: `DemoAdapter` (custom `RuntimeAdapter` with temporary workspace/upload/output directories and `WorkUnitStore` factory), synthetic tool-call construction helpers (`_tool_call`, `_runtime` accepting an optional `context` parameter, `_suspension`), `PHASE_META` mapping all 11 logical node names to Chinese labels and descriptions, `ALL_REAL_MODES` constant, `build_demo_recipe()` factory (fake/real), `build_demo_host()` factory, `create_hitl_response()` helper, a real-demo prerequisite guard, and `display_phase_progress(phases, *, suspended_at)` for human-readable phase output. `DemoAdapter.close()` SHALL be idempotent. CLI entry points SHALL close their owned adapter in `try`/`finally`; the TUI SHALL use one private one-shot cleanup helper from both `on_unmount()` and an idempotent `main()` `finally` guard around `app.run()`, invoking the owned adapter's `close()` at most once. The prerequisite guard and `DemoAppConfig` model selection SHALL use the same non-blank credential predicate for the supported model variables and `TAVILY_API_KEY`. The module SHALL also provide a demo-local node-agent bridge factory that preserves an explicitly supplied tools resolver and otherwise returns only `web_search` and `web_fetch` Tavily tools whose names are allowed by the execution policy. Each bridge `run_agent()` resolution SHALL create a fresh pair of async tools with one run-local approved-URL set. The tools SHALL obtain `TAVILY_API_KEY` from demo-process environment closure state, use `AsyncTavilyClient` within an async context manager for each provider request, and release that client before returning. `web_search` SHALL return at most five normalized results and add their exact URLs to the run-local set; `web_fetch` SHALL reject every URL outside that set and bound returned extracted content. Because fetch provenance requires search, a policy that allows `web_fetch` but not `web_search` SHALL fail as no usable demo-local tool set rather than receive a dead fetch tool. The tools SHALL NOT read or mutate global DeerFlow `AppConfig`, SHALL not expose credentials in tool errors, and SHALL keep provider work off the async event loop. A dedicated `demo-real` extra SHALL directly declare a compatible `tavily-python` dependency for these real-demo imports, the tool factory SHALL import that SDK lazily, and `agent/uv.lock` SHALL lock that declaration. The module SHALL be importable by all demo scripts in the same directory without `sys.path` manipulation beyond what `make` targets already provide. (`DPL-001`)

#### Scenario: CLI fake demo imports from shared core
- **WHEN** `make demo` runs `demo.py` which imports `DemoAdapter`, `_tool_call`, `_runtime`, `_suspension`, `PHASE_META`, `build_demo_recipe`, `build_demo_host`, and `create_hitl_response` from `_demo_core`
- **THEN** all imports resolve and the lifecycle completes with phase progress displayed

#### Scenario: CLI real demo imports local web-tool support from shared core
- **WHEN** `make demo-real` runs `demo_real.py` with valid real-demo prerequisites
- **THEN** it imports the shared adapter, recipe/host factories, response helper, and prerequisite guard, constructs the all-real recipe, and starts without requiring a global tool configuration entry

#### Scenario: Demo adapter cleanup survives lifecycle failure
- **WHEN** a CLI or TUI lifecycle call raises unexpectedly or its UI unmounts during teardown
- **THEN** its owned `DemoAdapter` is closed once through an idempotent cleanup path without masking the original failure

#### Scenario: Demo-local resolver follows execution policy
- **WHEN** the real recipe builds a worker bridge under a policy allowing `web_search` and `web_fetch`
- **THEN** the resolver supplies only those locally constructed tool names and does not call global `get_app_config()`

#### Scenario: Demo-local fetch requires same-run search provenance
- **WHEN** a worker calls `web_fetch` with a URL that its own `web_search` has not returned
- **THEN** the tool returns a bounded provenance-denial result without making an extraction request or exposing the Tavily credential

#### Scenario: Fetch-only policy fails closed
- **WHEN** a worker policy allows `web_fetch` but not `web_search`
- **THEN** the resolver raises the typed unavailable-tools configuration failure instead of exposing a fetch tool that cannot satisfy its provenance contract

#### Scenario: Async Tavily clients are not retained by the bridge
- **WHEN** a demo-local search or fetch tool completes or raises
- **THEN** its `AsyncTavilyClient` context is closed before the result or bounded error is returned, while the next `run_agent()` receives a new tool pair and approved-URL set

#### Scenario: Real demo SDK dependency is declared directly
- **WHEN** the agent project's `demo-real` extra is resolved from its lockfile
- **THEN** it contains a compatible direct `tavily-python` declaration required by the lazily imported demo-local tool factory rather than relying only on a harness transitive dependency

#### Scenario: Phase meta covers all 11 logical nodes
- **WHEN** `PHASE_META` is inspected
- **THEN** it contains entries for every key in `deerflow_deep_research.graph.topology.LOGICAL_NODES`

### Requirement: Recipe factory supports fake and real implementation modes

`build_demo_recipe(*, mode, work_unit_store_factory)` SHALL return a `ResearchGraphRecipe` created via `ResearchGraphRecipe.create()`. When `mode="fake"`, it SHALL pass no `implementation_modes` and no node-agent bridge factory, defaulting all nodes to fake. When `mode="real"`, it SHALL pass `ALL_REAL_MODES`, the work-unit store factory, and the demo-local node-agent bridge factory that delegates model execution to `RuntimeNodeAgentBridge` while preserving explicit zero-tool resolvers. The factory SHALL NOT bypass `create()` validation or construct the recipe dataclass manually. (`DPL-003`)

#### Scenario: Fake recipe has no node-agent bridge requirement
- **WHEN** `build_demo_recipe(mode="fake", ...)` is called
- **THEN** the returned recipe has `requires_node_agent_bridge=False`

#### Scenario: Real recipe requires the demo-local bridge
- **WHEN** `build_demo_recipe(mode="real", ...)` is called with a valid `work_unit_store_factory`
- **THEN** the returned recipe has `requires_node_agent_bridge=True`, `requires_bootstrap_bundle=True`, and a bridge factory that can resolve demo-local policy-filtered web tools

#### Scenario: Real recipe validates dependency chain
- **WHEN** `build_demo_recipe(mode="real", ...)` is called
- **THEN** `ResearchGraphRecipe.create()` validates the all-real dependency chain and raises `ValueError` only if a real factory is unavailable

### Requirement: CLI real demo is an independent script with complete prerequisite validation

The agent project SHALL provide `agent/scripts/demo_real.py` as an independent CLI entry point for all-real research. Before building its recipe, it SHALL validate non-blank values for both one known model API key (`DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY`) and `TAVILY_API_KEY`, and report each missing prerequisite clearly. It SHALL display phase progress from the `execution_trace` field in each `DeepResearchControlResult`, support `--question` and `--scripted` arguments, and in `--scripted` mode pass `non_interactive_policy={"auto_profile": True, "auto_proceed": True}` via the `_runtime` helper's `context` parameter. `DemoAppConfig` SHALL auto-detect the same non-blank model keys and build the corresponding `ModelConfig` (DeepSeek → `PatchedChatDeepSeek`, Anthropic → `ChatAnthropic`, OpenAI → `ChatOpenAI`). (`DPL-004`)

#### Scenario: Real demo rejects missing model credentials
- **WHEN** `demo_real.py` is launched without a non-blank value for any of `DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY`
- **THEN** it prints a clear error listing the supported model environment variables and exits with non-zero status before building the graph

#### Scenario: Real demo rejects a missing Tavily key
- **WHEN** `demo_real.py` is launched with a non-blank supported model credential but without a non-blank `TAVILY_API_KEY`
- **THEN** it prints a clear Tavily prerequisite error and exits with non-zero status before building the graph

#### Scenario: Real demo starts with complete credentials
- **WHEN** `demo_real.py` is launched with non-blank `DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY` and `TAVILY_API_KEY`
- **THEN** it auto-detects the available model config, constructs the all-real recipe, and begins the lifecycle with `action="start"`

#### Scenario: Scripted real demo passes non-interactive policy
- **WHEN** `demo_real.py --scripted` is launched with complete real-demo credentials
- **THEN** the runtime context includes `non_interactive_policy` with `auto_profile=True` and `auto_proceed=True`, allowing the lifecycle to pass HITL-1 and HITL-2 without stdin prompts

### Requirement: Makefile provides targets for all demo variants

The `agent/Makefile` SHALL provide `demo` (unchanged, fake CLI), `demo-scripted` (unchanged, fake CLI non-interactive), `demo-real`, `demo-real-scripted`, `demo-tui`, and `demo-tui-fake`. The `demo-real*` and `demo-tui` targets SHALL use the existing conditional `LOCAL_ENV_ARG`, so `agent/.env` is loaded when present and explicitly exported credentials work when it is absent; they SHALL select the `demo-real` extra containing the direct Tavily SDK dependency. `demo-tui-fake` SHALL pass `--fake`, select the `operations` and `demo-tui` extras but not `demo-real`, and SHALL omit `LOCAL_ENV_ARG`. The unchanged fake CLI targets SHALL not select `demo-real`. The existing `make install` and canonical deterministic verification composition SHALL remain `operations` plus `demo-tui`; deterministic tests SHALL stub the lazy Tavily SDK boundary rather than require `demo-real`. Every target SHALL forward `DEMO_ARGS`. No files under `backend/` or `frontend/` SHALL be modified. (`DPL-005`)

#### Scenario: make demo runs fake pipeline
- **WHEN** `make demo` is invoked
- **THEN** it executes `uv run --extra operations python scripts/demo.py $(DEMO_ARGS)` and the fake lifecycle completes

#### Scenario: make demo-real runs real pipeline
- **WHEN** `make demo-real` is invoked with complete real-demo credentials
- **THEN** it executes `uv run $(LOCAL_ENV_ARG) --extra operations --extra demo-real python scripts/demo_real.py $(DEMO_ARGS)` and real nodes are selected whether credentials came from `agent/.env` or the process environment

#### Scenario: make demo-tui runs real TUI
- **WHEN** `make demo-tui` is invoked
- **THEN** it executes `uv run $(LOCAL_ENV_ARG) --extra operations --extra demo-real --extra demo-tui python scripts/demo_tui.py $(DEMO_ARGS)` and the TUI validates complete real-demo prerequisites before starting

#### Scenario: make demo-tui-fake runs without credentials
- **WHEN** `make demo-tui-fake` is invoked in an environment without model or Tavily credentials
- **THEN** it executes the TUI with `--fake`, without selecting `demo-real` or loading `.env`, and starts the full-fake lifecycle

#### Scenario: canonical deterministic installation excludes real-demo dependencies
- **WHEN** `make install` and `UV_OFFLINE=1 make verify` prepare the canonical deterministic agent environment
- **THEN** they continue to select only `operations` and `demo-tui`, while deterministic demo-core tests replace the lazy Tavily SDK import boundary and do not require the `demo-real` extra
