# research-demo-tui Specification

> req: RED-001, RED-002, RED-003, RED-004, RED-005, RED-006, RED-007, RED-008

## Purpose

Provide a bounded, standalone Textual visualization of the Deep Research lifecycle
without implying production Terminal Workbench, Web UI, Gateway, or generic
human-input integration.
## Requirements

### Requirement: Standalone TUI demo traverses fake and real lifecycle modes through the shared experience

The Textual demo SHALL use one owned `DemoAdapter` and the shared
`ResearchRunExperience` Module. Default mode SHALL obtain its all-real recipe,
demo-local bridge, and graph executor from the same shared demo runtime composition
boundary used by the real CLI; it SHALL not dispatch without that executor into the
existing full-fake fallback. `--fake` SHALL retain the existing full-fake behavior
without a model, Tavily, Gateway, root configuration, or network. Both modes SHALL retain
graph-owned free-text HITL-1, explicit graph cancellation, and a truthful selected-mode
label. Current HITL2 is an autonomous graph continuation, not an advertised choice.

The TUI SHALL render `Ready`, `Working`, `AwaitingInput`, `Terminal`, and `Fault`
`RunUpdate` values. Its question view SHALL show only the focused composer after
preflight passes. It SHALL disable re-entry while a shared `Working` update is active
and retain a contained fixed safe fault view for unexpected UI failures. It SHALL show
only whitelisted run-update fields, semantic prompt text, safe diagnostic references,
and graph-owned advertised choices when another specified interaction exists; it SHALL
not display raw payloads, exception/configuration text, environment values, client
objects, or machine brief JSON.

The tracker SHALL use only the shared verified returned trace delta and actual
observed activity. It SHALL not infer stage from start/resume, option presence,
request shape, or a private phase list; it SHALL not claim streaming or node-internal
progress without a real observed event. A missing all-real executor or absent
graph-backed final-delivery evidence SHALL leave the TUI in its bounded fault or
non-completed terminal state; it SHALL not display completed research. (`RED-001`)

#### Scenario: User completes the deterministic fake visual path
- **WHEN** a user launches `--fake`, submits a question and HITL-1 response
- **THEN** the shell visibly identifies fake mode and completes without credentials,
  network, or a HITL2 choice control while every UI state came from shared `RunUpdate`
  values

#### Scenario: User starts the all-real visual path
- **WHEN** a user launches default mode with a supported model key and `TAVILY_API_KEY`
- **THEN** it passes shared preflight, starts the all-real recipe, and presents a
  returned bootstrap-plus-HITL-1 state as an `AwaitingInput` scope prompt

#### Scenario: Real TUI cannot use a full-fake completion
- **WHEN** the default real TUI cannot obtain its all-real graph composition
- **THEN** it shows the bounded startup fault and does not report completed research

#### Scenario: Processing does not fabricate node progress
- **WHEN** a lifecycle call is unresolved
- **THEN** re-entry is disabled, local elapsed waiting may advance, and tracker phases
  do not change until a shared observed event or returned trace proves it

#### Scenario: Startup presents one action
- **WHEN** either mode passes preflight and reaches question entry
- **THEN** only the focused research composer is actionable

#### Scenario: Unexpected lifecycle error stays inside the TUI
- **WHEN** an unexpected UI or adapter exception escapes normal shared fault projection
- **THEN** the application remains open with a fixed bounded safe fault view

### Requirement: Demo remains bounded and explicitly non-product

The demo SHALL launch from `deep_research_harness/` through the canonical
`make demo-tui` and `make demo-tui-fake` targets. It retains its existing real/fake
preflight, explicit non-product boundary, deterministic fake-pilot coverage, and
no-upstream-change constraint. Real mode loads `deep_research_harness/.env` when
present; fake mode remains credential-free. It SHALL project the shared Bundle
lifecycle result and never treat retained demo output as a recoverable session.
(`RED-002`)

#### Scenario: Demo TUI uses the renamed environment file
- **WHEN** real demo TUI mode starts from the downstream module
- **THEN** it reads only `deep_research_harness/.env` when present and does not require
  an old-root compatibility directory

### Requirement: TUI owns no independent lifecycle state inference

The TUI SHALL not decide whether a pending request is HITL-1 or HITL-2 from action,
mode, option count, trace, or local stage state. It SHALL not construct a human
response envelope or lifecycle call id itself. It may retain visual focus and widget
state, but its lifecycle state and next action SHALL come exclusively from
`ResearchRunExperience`. (`RED-003`)

#### Scenario: Phase lag cannot produce different TUI behavior
- **WHEN** the shared Module receives a suspended result with committed `bootstrap` and pending HITL-1
- **THEN** the TUI shows the same scope prompt as the CLI and does not classify it from the fact that the preceding action was start

### Requirement: TUI makes safe failure and cancellation status visible

The TUI SHALL render a fault or terminal outcome with its safe category, known phase,
next action, retryability, durability truth, and diagnostic reference when available.
It SHALL distinguish local interruption from graph-confirmed cancellation and shall
not call a local stop a cancelled research run. (`RED-004`)

#### Scenario: Unexpected lifecycle failure remains explainable
- **WHEN** a lifecycle transport or shared run experience returns a fault
- **THEN** the application remains open with a bounded explanation and diagnostic reference instead of only a generic red terminal state

### Requirement: TUI exposes shared run inspection truth without local path inference

The local TUI SHALL use an adapter-injected broker's projections for discovered-session
status and operations instead of keeping a parallel lifecycle/session controller. It MAY
render the broker's validated bounded pending-input view for an authorized session, and
SHALL render unavailable or denied operations without raw scope, path, provider, or
checkpoint data. It SHALL not select or reconstruct a recipe for a stored session; the
profile-owned broker determines whether the session is compatible. It retains the safe
legacy inspect reference and may offer only broker-backed discover/open/status/cancel or
resume controls; it keeps the expected opaque request id in its safe view model and passes
raw answer text only to the broker. (`RED-005`)

#### Scenario: TUI shows the same paused-run reference as CLI
- **WHEN** the shared run experience projects a retained HITL-1 or HITL-2 session
- **THEN** the TUI presents the same reference and inspectability truth as the CLI without decoding a lifecycle `Command`

#### Scenario: TUI shows an unavailable operation without a recovery claim
- **WHEN** the broker denies or cannot resolve a selected session
- **THEN** the TUI renders only the bounded unavailable state and does not offer a
  fabricated resume path

### Requirement: Demo TUI consumes shared typed intake actions and safe run updates

The standalone demo TUI SHALL render HITL1 proposal/progress/feedback and an explicit
acceptance control only from shared `PromptView` facts. It SHALL dispatch the same typed
`AnswerRun` action or text response as the CLI, without parsing raw interrupt context,
constructing a human-input envelope, or inferring lifecycle state. Its returned-only
waiting and terminal presentation SHALL consume the existing safe shared run updates.
(`RED-006`)

#### Scenario: TUI action is not a magic text answer
- **WHEN** a shared prompt advertises `accept_suggestion`
- **THEN** the TUI emits the typed action intent rather than a text value and hides the
  control when the shared prompt no longer advertises it

### Requirement: TUI renders shared workflow-failure outcomes without inference

For every terminal or fault update carrying a workflow incident, the demo TUI SHALL
render only the shared safe category, phase, bounded recovery disposition, diagnostic
reference, durability truth, and legal next action. It SHALL not replace a known
incident with generic blocked text, infer a retry from elapsed time, or present an
inspection reference as a recovery control.

#### Scenario: A provider timeout is distinguishable from generic blocking
- **WHEN** the shared run update carries a terminal topic-planning timeout incident
- **THEN** the TUI shows the timeout category and phase from that update alongside
  the one legal action and does not offer an inferred resume or local retry

### Requirement: Demo TUI submits visible controls without text aliases

The standalone demo TUI SHALL render shared `VisibleControl` values and submit their
control ids through `SelectControlRun`. Its input field SHALL forward ordinary HITL1
text unchanged for semantic intake. It SHALL not recognize an acceptance phrase,
construct an action id, or inspect raw prompt context. (`RED-007`)

#### Scenario: TUI control has no text equivalent
- **WHEN** a shared prompt exposes the current-proposal control
- **THEN** pressing its button submits that control id while entering a natural
  confirmation remains ordinary text

### Requirement: Demo TUI projects the shared Bundle lifecycle contract without local inference

The demo TUI SHALL render the same typed Bundle lifecycle outcome, bounded `bundle_id`,
and legal controls as the shared run experience. It SHALL remain a non-product demo and
shall not derive state from a session reference, path, report, external checkpoint, or
fixture-local cache. (`RED-008`)

#### Scenario: Demo TUI does not treat retained output as a resumable Run
- **WHEN** a demo retains output for a Bundle that is no longer available
- **THEN** it renders the shared unavailable observation and submits no resume/control action for that Bundle
