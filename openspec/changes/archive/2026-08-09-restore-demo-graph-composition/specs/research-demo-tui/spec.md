## MODIFIED Requirements

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
- **THEN** it passes shared preflight, obtains the all-real executor from the shared
  demo runtime, starts the all-real recipe, and presents a returned bootstrap-plus-HITL-1
  state as an `AwaitingInput` scope prompt

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
