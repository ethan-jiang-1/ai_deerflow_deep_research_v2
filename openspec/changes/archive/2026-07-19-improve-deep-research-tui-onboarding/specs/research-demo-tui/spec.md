> req: RED-001, RED-002

## MODIFIED Requirements

### Requirement: Standalone TUI demo traverses fake and real lifecycle modes

The agent project SHALL provide a Textual demo entry that invokes the existing reflected-tool lifecycle dispatch with a retained process-local memory host and test-owned trusted runtime envelope. By default it SHALL construct the all-real implementation mode (`ALL_REAL_MODES`) through `ResearchGraphRecipe.create()` and the demo-local node-agent bridge factory. With `--fake`, it SHALL construct the existing full-fake recipe without constructing a node-agent bridge or requiring model, Tavily, Gateway, root configuration, or network access. The TUI SHALL own exactly one `DemoAdapter` and build its selected recipe from that adapter; it SHALL NOT accept a prebuilt recipe capturing a different adapter. Both modes SHALL use the same stage controller, free-text HITL-1 response, typed advertised HITL-2 decision, explicit lifecycle cancel path, and terminal projection; the visible mode label SHALL not misrepresent fake execution as real research.

The TUI SHALL make `question` a single-action screen containing only a title, short research-question instruction, and enabled composer. At this stage the tracker, lifecycle log, and cancel control SHALL be absent from layout. It SHALL use bounded `starting` and `processing` states that disable re-entry while a lifecycle call is unresolved. Start, resume, and explicit cancel work SHALL run in one exclusive Textual lifecycle-worker group with `exit_on_error=False`; a cancel dispatch SHALL disable its trigger before it begins. Unexpected exceptions SHALL be projected as a fixed redacted terminal failure, while worker cancellation during application teardown SHALL not be represented as a research completion or failure. User-visible lifecycle status, terminal summary, and error surfaces SHALL render only stable whitelisted result fields. Stage copy and HITL-1 examples SHALL be static; the only fields displayed from a pending HITL request SHALL be its request id and advertised HITL-2 option values. The TUI SHALL NOT render raw exception strings, raw control/HITL payloads, environment values, or client representations. At HITL-1 it SHALL show a concise free-text scope prompt and examples while the full tracker remains hidden. At processing it SHALL reveal the full tracker and lifecycle log. At HITL-2 it SHALL retain a compact tracker alongside the typed decision prompt and advertised choices. At terminal it SHALL show the final tracker and concise result summary with input disabled. The tracker SHALL be derived from `execution_trace` in each returned `DeepResearchControlResult`, rendered as a Rich table with ✓/⏸/● markers for completed/suspended/active phases; it SHALL NOT mark node-internal progress, append guessed phases, or imply streaming while a lifecycle call is in flight. The demo SHALL NOT introduce a second graph, checkpoint schema, fixture authority, or research artifact. (`RED-001`)

#### Scenario: User completes the deterministic fake visual path
- **WHEN** a user launches the TUI with `--fake`, submits a research request and HITL-1 response, then selects the advertised `proceed` decision
- **THEN** the UI shows both request ids, follows the same staged interaction flow as real mode, visibly identifies full-fake mode, and reaches the existing completed terminal result without credentials or network access

#### Scenario: TUI owns fake-mode temporary resources
- **WHEN** a deterministic pilot launches and unmounts the TUI in fake mode
- **THEN** the same owned `DemoAdapter` supplies the recipe and is closed exactly once without leaking a separately constructed test adapter

#### Scenario: User starts the all-real visual path
- **WHEN** a user launches the default TUI with one supported model credential and `TAVILY_API_KEY`, then submits a research request
- **THEN** it builds the all-real recipe through the validated factory, begins the lifecycle with `action="start"`, and displays returned checkpoint progress only after the control result is available

#### Scenario: User cancels a suspended lifecycle
- **WHEN** the demo has a pending HITL request and the user invokes the explicit cancel action
- **THEN** the same lifecycle handler reaches the durable cancelled terminal without interpreting UI interruption as a user answer

#### Scenario: Real mode refuses incomplete prerequisites
- **WHEN** the default TUI starts without a non-blank supported model credential or without a non-blank `TAVILY_API_KEY`
- **THEN** it exits before building the graph with a clear error that identifies the missing model-key group or Tavily key

#### Scenario: Startup presents one action
- **WHEN** either TUI mode reaches the initial `question` stage
- **THEN** the tracker, lifecycle log, and cancel control consume no layout space, and the focused composer is the only actionable research control

#### Scenario: Processing does not fabricate node progress
- **WHEN** a start or resume lifecycle call is unresolved
- **THEN** the TUI disables composer and cancel re-entry, shows only a bounded running state, and does not change tracker phases until that call returns a control result

#### Scenario: Unexpected lifecycle error stays inside the TUI
- **WHEN** an unexpected exception escapes a start or resume lifecycle call
- **THEN** the Textual application remains running, displays the fixed redacted terminal failure through the normal stage controller, and does not expose a sentinel credential, raw exception text, or raw exception configuration

### Requirement: Demo remains bounded and explicitly non-product

The demo SHALL launch through `make -C agent demo-tui` for all-real mode and `make -C agent demo-tui-fake` for full-fake mode, using the agent-only Textual optional dependency. Real targets SHALL use `LOCAL_ENV_ARG` to load `agent/.env` when present while also accepting explicitly exported credentials, and require non-blank values for one of `DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY` plus `TAVILY_API_KEY`; the fake target SHALL omit `LOCAL_ENV_ARG` and require neither credential. Deterministic Textual pilot tests SHALL exercise the visual flow using fake mode and shall not call a model or web API. Documentation SHALL state that the shell is not DeerFlow Terminal Workbench, Web UI, Gateway, or generic human-input integration, distinguish fake from real prerequisites, and state that tracker updates are lifecycle-result-driven rather than streaming. No files under `backend/` or `frontend/` SHALL change. (`RED-002`)

#### Scenario: Unsupported decision is refused locally
- **WHEN** a user enters a HITL-2 value that is not in the request's advertised options
- **THEN** the UI retains the pending request, displays a bounded validation error, and does not invoke resume or mutate the checkpoint

#### Scenario: Phase progress updates at lifecycle boundaries
- **WHEN** the TUI completes a `run_deep_research()` call
- **THEN** the phase progress panel updates from the returned `DeepResearchControlResult.execution_trace` and labels a returned suspension distinctly

#### Scenario: Fake target starts without product configuration
- **WHEN** `make -C agent demo-tui-fake` runs in the locked agent environment without root `config.yaml`, model credentials, `TAVILY_API_KEY`, Gateway, or network access
- **THEN** the Textual application starts and the lifecycle can complete using only deterministic local dependencies
