## MODIFIED Requirements

### Requirement: Demo progress display uses shared verified run updates

Demo scripts SHALL render phase progress only from a shared verified returned trace
delta and labels supplied by the run experience. They MAY preserve repeated logical
phase visits. A suspended marker SHALL identify `pending_input.pending_phase`, not
`control.phase`, because `control.phase` is the last committed checkpoint fact. No
demo script shall hardcode a phase sequence, infer current phase from action or
request options, or update a tracker before a valid returned event/result proves it.

The shared display map SHALL cover the complete closed `RunTraceEntry` set, including
the presentation-only trace steps `hitl1_auto_profile` and `hitl2_auto_proceed` with
safe display labels and descriptions. A returned trace that includes a
presentation-only step SHALL render without a crash and SHALL identify that step as an
automatic-policy step rather than a logical phase.

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

#### Scenario: Presentation-only trace step renders without crashing
- **WHEN** a returned trace delta includes `hitl1_auto_profile` or
  `hitl2_auto_proceed`
- **THEN** each demo adapter renders that step from the shared display map with an
  automatic-policy label and does not raise or invent a logical phase

#### Scenario: Fake demo shows phases that actually executed
- **WHEN** `make demo --scripted` runs the fake lifecycle
- **THEN** it renders the actual trace order before, during, and after its HITL1
  interaction without inventing an HITL2 prompt

#### Scenario: Autonomous update is not rendered as a menu
- **WHEN** the shared update represents a policy-led HITL2 continuation
- **THEN** neither adapter renders `proceed`, `repair`, `rerun`, or another internal
  route as an input menu
