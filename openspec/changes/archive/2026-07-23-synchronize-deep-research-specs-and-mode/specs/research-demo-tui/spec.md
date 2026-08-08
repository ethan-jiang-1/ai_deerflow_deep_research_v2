## MODIFIED Requirements

### Requirement: Standalone TUI demo traverses fake and real lifecycle modes through the shared experience

The Textual demo SHALL use one owned `DemoAdapter` and the shared
`ResearchRunExperience` Module. Default mode SHALL construct the all-real recipe
with the demo-local bridge; `--fake` SHALL construct the full-fake recipe without a
model, Tavily, Gateway, root configuration, or network. Both modes SHALL retain
graph-owned free-text HITL-1, advertised HITL-2 decisions, explicit graph
cancellation, and a truthful selected-mode label derived from the returned
`DeepResearchControlResult`: default mode is `all_real`, and `--fake` is
`full_fake`. The TUI SHALL not infer this label from its local mode flag, trace, or
phase list.

The TUI SHALL render `Ready`, `Working`, `AwaitingInput`, `Terminal`, and `Fault`
`RunUpdate` values. Its question view SHALL show only the focused composer after
preflight passes. It SHALL disable re-entry while a shared `Working` update is
active and retain a contained fixed safe fault view for unexpected UI failures. It
SHALL show only whitelisted run-update fields, semantic prompt text, safe diagnostic
references, and graph-owned advertised choices; it SHALL not display raw payloads,
exception/configuration text, environment values, client objects, or machine brief
JSON.

The tracker SHALL use only the shared verified returned trace delta and actual
observed activity. It SHALL not infer stage from start/resume, option presence,
request shape, or a private phase list; it SHALL not claim streaming or node-internal
progress without a real observed event. (`RED-001`)

#### Scenario: User completes the deterministic fake visual path
- **WHEN** a user launches `--fake`, submits a question and HITL-1 response, then selects `proceed`
- **THEN** the shell visibly identifies `full_fake` and completes without credentials or network while every UI state comes from shared `RunUpdate` values

#### Scenario: User starts the all-real visual path
- **WHEN** a user launches default mode with a supported model key and `TAVILY_API_KEY`
- **THEN** it passes shared preflight, starts the all-real recipe, presents a returned bootstrap-plus-HITL-1 state as an `AwaitingInput` scope prompt, and visibly identifies `all_real`

#### Scenario: Processing does not fabricate node progress
- **WHEN** a lifecycle call is unresolved
- **THEN** re-entry is disabled, local elapsed waiting may advance, and tracker phases do not change until a shared observed event or returned trace proves it

#### Scenario: Startup presents one action
- **WHEN** either mode passes preflight and reaches question entry
- **THEN** only the focused research composer is actionable

#### Scenario: Unexpected lifecycle error stays inside the TUI
- **WHEN** an unexpected UI or adapter exception escapes normal shared fault projection
- **THEN** the application remains open with a fixed bounded safe fault view
