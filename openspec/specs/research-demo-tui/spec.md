# research-demo-tui Specification

> req: RED-001, RED-002, RED-003, RED-004, RED-005, RED-006, RED-007, RED-008, RED-009, RED-010, RED-011

## Purpose

Provide a bounded, standalone Textual visualization of the Deep Research lifecycle
without implying production Terminal Workbench, Web UI, Gateway, or generic
human-input integration.
## Requirements

### Requirement: Standalone TUI demo traverses fixture-graph and all-real lifecycle modes through the shared experience

The Textual demo SHALL use one shared `ResearchRunExperience` presentation contract
in every supported mode. Default real mode SHALL require one valid explicit `--profile`
label that resolves to a ready local Gateway profile and obtain lifecycle results and
live transport observations through the public Gateway adapter; it SHALL not construct
`DemoAdapter`, `DemoLifecycleTransport`, an all-real recipe, or a local graph executor.
`--fixture` SHALL retain the existing fixed fixture graph without a model, Tavily,
Gateway, root configuration, or network. An explicit embedded-smoke mode MAY retain the
current local all-real recipe/executor, but it SHALL be visibly labelled embedded smoke
and SHALL retain the local model/Tavily preflight without any Gateway observability
claim.

Gateway real mode SHALL submit the question and each explicit follow-up as public turns
to the configured `deep-research` Agent. It MAY retain only the Gateway-created thread
id for the current TUI process and SHALL not directly select a Bundle or Deep Research
lifecycle action. Gateway mode SHALL forward only entered text or a value from a
currently displayed selected control. It SHALL not render or dispatch the local cancel
button, and closing or interrupting the local TUI SHALL not claim that the Gateway Run
was cancelled. Fixture and embedded-smoke modes retain graph-owned free-text HITL-1 and
explicit graph cancellation.

The TUI SHALL render `Ready`, `Working`, `AwaitingInput`, `Terminal`, and `Fault`
`RunUpdate` values plus bounded Gateway transport observations. Its question view SHALL
show only the focused composer after the selected mode's preflight passes. It SHALL
disable re-entry while a shared `Working` update or public Gateway turn is active and
retain a contained fixed safe fault view for unexpected UI failures. It SHALL show only
whitelisted run-update fields, approved progress-event fields, safe assistant text,
semantic prompt text, safe diagnostic references, and graph-owned advertised choices.
It SHALL not display raw SSE payloads, tool arguments, non-Deep-Research tool results,
exception/configuration text, environment values, client objects, or machine brief JSON.

The tracker SHALL use only shared verified returned trace facts and actual approved
Gateway progress events. It SHALL not infer stage from request submission, stream end,
option presence, request shape, heartbeat, gap, or a private phase list; it SHALL not
claim node-internal progress without a received approved event. Missing Gateway
readiness, absent/invalid reflected lifecycle result, or missing embedded graph-backed
final-delivery evidence SHALL leave the TUI in its bounded fault or non-completed state
and SHALL not display completed research. (`RED-001`)

#### Scenario: User completes the deterministic fixture-graph visual path
- **WHEN** a user launches `--fixture`, submits a question and HITL-1 response
- **THEN** the shell visibly identifies fixture-graph mode and completes without
  credentials, network, or a HITL2 choice control while every UI lifecycle state came
  from shared `RunUpdate` values

#### Scenario: User starts the all-real visual path
- **WHEN** a user launches default real mode with a selected ready local Gateway
  profile
- **THEN** it passes profile/Gateway preflight, creates a public Gateway thread for
  the configured `deep-research` Agent, and constructs no local all-real graph runtime

#### Scenario: Gateway TUI requires a selected profile
- **WHEN** a user launches default real mode without `--profile` or with an invalid or
  unready profile label
- **THEN** the TUI remains in its bounded preflight fault state and makes no health,
  thread, or stream request

#### Scenario: Gateway real TUI does not require local provider credentials
- **WHEN** the selected Gateway profile is ready but the TUI process has no local
  `DEERFLOW_DEMO_MODEL` or `TAVILY_API_KEY`
- **THEN** default real mode may start because those provider prerequisites belong to
  the Gateway, while embedded-smoke mode still requires them

#### Scenario: Gateway TUI does not invent a cancellation turn
- **WHEN** a Gateway-real TUI displays a pending input
- **THEN** it does not render or dispatch the local cancel button; an operator may only
  send cancellation by entering an explicit user turn for the configured Agent, and a
  window close or interrupt claims no Gateway cancellation

#### Scenario: Real TUI cannot use a synthetic completion
- **WHEN** the Gateway turn ends without a validated typed Deep Research lifecycle
  result
- **THEN** the TUI shows a bounded unknown/fault outcome and does not report completed
  research from assistant prose, elapsed time, or the SSE `end` record

#### Scenario: Processing does not fabricate node progress
- **WHEN** a lifecycle call or Gateway turn is unresolved
- **THEN** re-entry is disabled, local elapsed waiting may advance, and tracker phases
  do not change until a shared returned fact or approved received progress event proves
  them

#### Scenario: Startup presents one action
- **WHEN** any supported mode passes its applicable preflight and reaches question
  entry
- **THEN** only the focused research composer is actionable

#### Scenario: Embedded real mode remains smoke-only
- **WHEN** a developer explicitly selects embedded-smoke mode
- **THEN** the TUI identifies the direct local graph route and makes no claim about
  Gateway run history, Console data, trace correlation, SSE liveness, or nested custom
  event forwarding

#### Scenario: Unexpected lifecycle error stays inside the TUI
- **WHEN** an unexpected UI, Gateway adapter, or lifecycle projection exception escapes
  normal shared fault projection
- **THEN** the application remains open with a fixed bounded safe fault view

### Requirement: Demo remains bounded and explicitly non-product

The demo SHALL launch from `deep_research_harness/` through the canonical
`make demo-tui` and `make demo-tui-fixture` targets. It retains its existing all-real/
fixture preflight, explicit non-product boundary, deterministic fixture-graph coverage,
and no-upstream-change constraint. Real mode loads `deep_research_harness/.env` when
present; fixture mode remains credential-free. It SHALL project the shared Bundle
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

### Requirement: Demo TUI answers advertised CHOICE prompts with typed options

The standalone demo TUI in fixture and embedded-smoke modes SHALL render the
options of the current advertised HITL1 CHOICE prompt and submit a user's
selection as the shared typed option answer carrying that advertised option id
for the prompt's current request. It SHALL NOT submit a text-kind answer for a
prompt whose shared contract requires an option, and SHALL NOT invent an option
id, construct a response envelope, or admit the answer itself — legality remains
with the shared run experience. Ordinary TEXT-mode HITL1 prompts SHALL keep
forwarding free text unchanged for semantic intake, and non-language CHOICE
prompts SHALL keep forwarding composer text to the shared graph-owned
validation unchanged. (`RED-009`)

#### Scenario: User selects an advertised language option
- **WHEN** a HITL1 CHOICE prompt advertises language options and the user selects one
- **THEN** the demo TUI submits the typed option answer carrying that advertised
  option id, and the shared run experience accepts it without the
  language-answer rejection reserved for text-kind answers

#### Scenario: Composer entry during a HITL1 CHOICE prompt
- **WHEN** a HITL1 CHOICE prompt is current and the user submits composer text
- **THEN** an exact match of one advertised option id is submitted as the typed
  option answer for that advertised id, while any other text is not dispatched
  as a text-kind answer and fabricates no option id, leaving the prompt awaiting
  a real selection

#### Scenario: TEXT prompts keep free-text semantic intake
- **WHEN** the current HITL1 prompt is TEXT mode and the user submits free text
- **THEN** the demo TUI forwards it unchanged as the shared text answer for
  semantic intake, exactly as before this requirement

### Requirement: Demo TUI provides an explicit zero-human-input auto entry

The standalone demo TUI SHALL offer an explicit auto entry for embedded-smoke
mode: once the local preflight passes, it SHALL dispatch one fixed research
start carrying the graph-owned scripted policy intent (`StartRun` with the
fixed question, `scripted=True`, and no declared `profile_intent`) without any
composer input, and SHALL reach a terminal outcome with zero human typing,
while rendering the shared run updates. The auto flag
SHALL be accepted only for embedded-smoke mode: the command line SHALL reject
the flag in other modes, and fixture and Gateway observer modes SHALL keep
their interactive behavior unchanged. The TUI SHALL NOT construct a profile,
answer HITL1 or HITL2 itself, or alter the graph-owned scripted policy — it
only submits the start and projects the shared lifecycle result. (`RED-010`)

#### Scenario: Auto entry dispatches a fixed scripted start after preflight
- **WHEN** embedded-smoke mode is launched with the auto flag and the local preflight passes
- **THEN** the TUI dispatches one `StartRun` carrying the fixed question, `scripted=True`, and no `profile_intent`, and reaches a terminal outcome with zero human input

#### Scenario: Auto flag is rejected outside embedded-smoke mode
- **WHEN** the auto flag is used without embedded-smoke mode
- **THEN** the command line rejects the combination at argument parsing, and fixture or Gateway observer mode retains its interactive behavior

#### Scenario: Scripted run passes HITL1 and HITL2 as graph-owned phases
- **WHEN** the auto entry starts a scripted run
- **THEN** HITL1 and HITL2 pass as graph-owned policy phases without a human-facing input prompt, and the terminal outcome comes from the shared lifecycle result

### Requirement: Demo TUI projects the shared Bundle lifecycle contract without local inference

The demo TUI SHALL render the same typed Bundle lifecycle outcome, bounded `bundle_id`,
and legal controls as the shared run experience. It SHALL remain a non-product demo and
shall not derive state from a session reference, path, report, external checkpoint, or
fixture-local cache. (`RED-008`)

#### Scenario: Demo TUI does not treat retained output as a resumable Run
- **WHEN** a demo retains output for a Bundle that is no longer available
- **THEN** it renders the shared unavailable observation and submits no resume/control action for that Bundle

### Requirement: Credential-free TUI uses the fixed fixture graph

The credential-free standalone TUI SHALL use the same fixture catalog, fixed fixture
recipe, graph executor, shared Bundle lifecycle result, and truthful `fixture`
composition fact as the credential-free CLI. It SHALL remain a non-product
visualization, require no model, Gateway, network, or real-demo configuration, and
shall not construct a no-graph lifecycle or infer completed research from local UI
state. (`RED-001`, `RED-002`, `RED-008`)

#### Scenario: Credential-free TUI starts a fixture-backed Run
- **WHEN** an operator starts the named credential-free TUI route in a prepared
  checkout with fixture source available to that child process
- **THEN** its shared updates originate from the fixture graph and Bundle-local State
  identifies `implementation_mode=fixture`

#### Scenario: Credential-free TUI lacks its fixture executor
- **WHEN** the TUI cannot construct its fixed fixture executor
- **THEN** it presents the bounded startup fault and does not create a State record or
  render completed research

### Requirement: The TUI offers attach projection for recoverable bundles

On startup, when the demo TUI's workspace contains recoverable bundles whose
projected legal next action is RESUME, the TUI SHALL present an attach
projection listing those bundles (bounded to the most recent, with the recorded
phase summary), and SHALL let the operator choose to continue, inspect, or
discard toward a fresh run. The projection is presentation only: it SHALL NOT
decide recovery semantics, SHALL NOT construct any human response, and SHALL
route the operator's choice through the existing lifecycle actions. When no
recoverable bundle exists, startup behavior SHALL be unchanged. (`RED-011`)

#### Scenario: Startup presents a recoverable bundle for attach
- **WHEN** the TUI starts and the workspace contains a suspended bundle whose
  projected legal next action is RESUME
- **THEN** the TUI presents the bundle (bounded list, phase summary) with
  continue / inspect / discard choices, and startup without operator choice
  does not itself mutate the bundle

#### Scenario: Continue routes through lifecycle, not TUI authority
- **WHEN** the operator chooses continue for a projected bundle
- **THEN** the TUI issues the choice through the existing lifecycle resume
  path, and the run continues from its durable checkpoint without the TUI
  constructing any response or route

#### Scenario: No recoverable bundle leaves startup unchanged
- **WHEN** the TUI starts with no bundle projecting RESUME
- **THEN** startup proceeds exactly as before with no attach projection
