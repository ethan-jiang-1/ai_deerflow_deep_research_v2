> req: DPL-001, DPL-002

## MODIFIED Requirements

### Requirement: Shared demo core provides infrastructure, lifecycle transport, and prerequisite checks

The agent project SHALL provide `agent/scripts/_demo_core.py` with a demo adapter,
recipe and host factories, idempotent cleanup, a shared lifecycle transport adapter,
and non-network preflight primitives for all demo scripts. The preflight and
`DemoAppConfig` SHALL share non-blank validation for one supported model key plus
`TAVILY_API_KEY`. Real recipes SHALL resolve fresh, policy-filtered Tavily
`web_search`/`web_fetch` tool pairs. Fetch requires same-run search provenance;
clients close before return; credentials never enter state, prompts, errors,
`RunUpdate`, or diagnostic records; global DeerFlow tool configuration is unused;
and the direct `demo-real` extra declares compatible `tavily-python`.

The demo core SHALL not become the owner of lifecycle presentation semantics. It
may satisfy the runtime Module's narrow transport seam, but `Command` parsing,
pending-phase interpretation, trace validation, prompt rendering, and failure
classification belong to `ResearchRunExperience`.

The credential-free `make demo` route SHALL keep its full-fake, zero-model,
zero-web-request boundary and SHALL automatically consume its configured HITL2
fixture route after the required HITL1 scope response. It SHALL not ask the user to
choose an internal route or claim fixture progress is research output. (`DPL-001`)

#### Scenario: Default fake demo needs no second decision
- **WHEN** an interactive `make demo` receives a valid HITL1 scope response
- **THEN** it completes the fake lifecycle without printing an HITL2 choice prompt or
  reading another user response

#### Scenario: Fixture routes remain testable without human input
- **WHEN** a deterministic fake fixture selects a non-default existing HITL2 route
- **THEN** the graph takes that route without presenting its internal route identifier
  as a user choice

### Requirement: Demo progress display uses shared verified run updates

Demo scripts SHALL render phase progress only from a shared verified returned trace
delta and labels supplied by the run experience. They MAY preserve repeated logical
phase visits. A suspended marker SHALL identify `pending_input.pending_phase`, not
`control.phase`, because `control.phase` is the last committed checkpoint fact. No
demo script shall hardcode a phase sequence, infer current phase from action or
request options, or update a tracker before a valid returned event/result proves it.

For a shared `PromptView` in `choice` mode from a separately specified graph
interaction, standalone demo adapters SHALL distinguish the canonical option ID from
its bounded human-readable consequence and submit only the advertised ID through
`AnswerRun`; they SHALL NOT parse rendered text as graph-control protocol. Current
HITL2 produces no such prompt. When `ResearchRunExperience` re-presents an unchanged
choice prompt with `rejection_category=choice_input_invalid`, adapters SHALL show
fixed safe feedback and the same choices without echoing rejected input, inferring
progress, changing the request ID, or constructing a lifecycle result. (`DPL-002`)

#### Scenario: First HITL phase is not confused with checkpoint phase
- **WHEN** a suspended run has execution trace `bootstrap`, checkpoint phase
  `bootstrap`, and pending-input phase `hitl1`
- **THEN** a demo marks bootstrap as completed and renders HITL-1 as the current
  requested interaction without treating the result as inconsistent

#### Scenario: Fake demo shows phases that actually executed
- **WHEN** `make demo --scripted` runs the fake lifecycle
- **THEN** it renders the actual trace order before, during, and after its HITL1
  interaction without inventing an HITL2 prompt

#### Scenario: Autonomous update is not rendered as a menu
- **WHEN** the shared update represents a policy-led HITL2 continuation
- **THEN** neither adapter renders `proceed`, `repair`, `rerun`, or another internal
  route as an input menu
