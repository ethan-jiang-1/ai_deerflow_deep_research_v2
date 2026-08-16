> req: RED-001

## MODIFIED Requirements

### Requirement: Standalone TUI demo traverses fixture-graph and all-real lifecycle modes through the shared experience

The Textual demo SHALL use one shared `ResearchRunExperience` presentation contract
in every supported mode. Default real mode SHALL require one valid explicit `--profile`
label that resolves to a ready local Gateway profile and obtain lifecycle results and
live transport observations through the public Gateway adapter; it SHALL not construct `DemoAdapter`,
`DemoLifecycleTransport`, an all-real recipe, or a local graph executor. `--fixture`
SHALL retain the existing fixed fixture graph without a model, Tavily, Gateway, root
configuration, or network. An explicit embedded-smoke mode MAY retain the current
local all-real recipe/executor, but it SHALL be visibly labelled embedded smoke and
SHALL retain the local model/Tavily preflight without any Gateway observability claim.

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
retain a contained fixed safe fault view for unexpected UI failures. It SHALL show
only whitelisted run-update fields, approved progress-event fields, safe assistant
text, semantic prompt text, safe diagnostic references, and graph-owned advertised
choices. It SHALL not display raw SSE payloads, tool arguments, non-Deep-Research tool
results, exception/configuration text, environment values, client objects, or machine
brief JSON.

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
