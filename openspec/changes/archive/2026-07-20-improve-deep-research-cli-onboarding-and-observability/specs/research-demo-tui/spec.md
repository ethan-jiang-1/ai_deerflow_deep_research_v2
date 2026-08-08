> req: RED-001, RED-002, RED-003, RED-004

## MODIFIED Requirements

### Requirement: Standalone TUI demo traverses fake and real lifecycle modes through the shared experience

The Textual demo SHALL use one owned DemoAdapter and the shared
ResearchRunExperience Module. Default mode SHALL construct the all-real recipe with
the demo-local bridge; --fake SHALL construct the full-fake recipe without a model,
Tavily, Gateway, root configuration, or network. Both modes SHALL retain
graph-owned free-text HITL-1, advertised HITL-2 decisions, explicit graph
cancellation, and a truthful selected-mode label.

The TUI SHALL render Ready, Working, AwaitingInput, Terminal, and Fault RunUpdate
values. Its question view SHALL show only the focused composer after preflight
passes. It SHALL disable re-entry while a shared Working update is active and
retain a contained fixed safe fault view for unexpected UI failures. It SHALL show
only whitelisted run-update fields, semantic prompt text, safe diagnostic
references, and graph-owned advertised choices; it SHALL not display raw payloads,
exception/configuration text, environment values, client objects, or machine
brief JSON.

The tracker SHALL use only the shared verified returned trace delta and actual
observed activity. It SHALL not infer stage from start/resume, option presence,
request shape, or a private phase list; it SHALL not claim streaming or
node-internal progress without a real observed event. (RED-001)

#### Scenario: User completes the deterministic fake visual path
- **WHEN** a user launches --fake, submits a question and HITL-1 response, then
  selects proceed
- **THEN** the shell visibly identifies fake mode and completes without
  credentials or network while every UI state came from shared RunUpdate values

#### Scenario: User starts the all-real visual path
- **WHEN** a user launches default mode with a supported model key and
  TAVILY_API_KEY
- **THEN** it passes shared preflight, starts the all-real recipe, and presents a
  returned bootstrap-plus-HITL-1 state as an AwaitingInput scope prompt

#### Scenario: Processing does not fabricate node progress
- **WHEN** a lifecycle call is unresolved
- **THEN** re-entry is disabled, local elapsed waiting may advance, and tracker
  phases do not change until a shared observed event or returned trace proves it

### Requirement: Demo remains bounded and explicitly non-product

The demo SHALL launch as real mode through make -C agent demo-tui and fake mode
through make -C agent demo-tui-fake, using the agent-only Textual dependency. Real
mode requires shared preflight for one non-blank supported model credential plus
TAVILY_API_KEY and loads agent/.env when present; fake mode uses a corresponding
credential-free preflight. Deterministic pilots SHALL exercise fake mode without a
model or web request. Documentation SHALL distinguish the two modes, state that
updates are lifecycle-result-driven, and explain that the demo is not a durable
product session or workbench. No backend or frontend files change. (RED-002)

#### Scenario: Fake target starts without product configuration
- **WHEN** make -C agent demo-tui-fake runs without root config, credentials,
  Gateway, or network
- **THEN** shared fake preflight and the lifecycle complete with only deterministic
  local dependencies

## ADDED Requirements

### Requirement: TUI owns no independent lifecycle state inference

The TUI SHALL not decide whether a pending request is HITL-1 or HITL-2 from action,
mode, option count, trace, or local stage state. It SHALL not construct a human
response envelope or lifecycle call id itself. It may retain visual focus and
widget state, but its lifecycle state and next action SHALL come exclusively from
ResearchRunExperience. (RED-003)

#### Scenario: Phase lag cannot produce different TUI behavior
- **WHEN** the shared Module receives a suspended result with committed bootstrap
  and pending HITL-1
- **THEN** the TUI shows the same scope prompt as the CLI and does not classify it
  from the fact that the preceding action was start

### Requirement: TUI makes safe failure and cancellation status visible

The TUI SHALL render a fault or terminal outcome with its safe category, known
phase, next action, retryability, durability truth, and diagnostic reference when
available. It SHALL distinguish local interruption from graph-confirmed
cancellation and shall not call a local stop a cancelled research run. (RED-004)

#### Scenario: Unexpected lifecycle failure remains explainable
- **WHEN** a lifecycle transport or shared run experience returns a fault
- **THEN** the application remains open with a bounded explanation and diagnostic
  reference instead of only a generic red terminal state
