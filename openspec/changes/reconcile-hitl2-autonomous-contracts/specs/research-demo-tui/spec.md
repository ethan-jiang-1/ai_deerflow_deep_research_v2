> req: RED-001, RED-002, RED-003, RED-004, RED-005, RED-006, RED-007, RED-008, RED-009, RED-010, RED-011

## MODIFIED Requirements

### Requirement: TUI owns no independent lifecycle state inference

The TUI SHALL consume a pending request's typed phase and subject from
`ResearchRunExperience` rather than deciding them from action, mode, option count,
trace, or local stage state. The current graph-owned pending human-input producer is
HITL1. A verified HITL2 trace visit without a pending request SHALL be rendered only as
autonomous progress and SHALL NOT become a prompt. The TUI SHALL not construct a human
response envelope or lifecycle call id itself. It may retain visual focus and widget
state, but its lifecycle state and next action SHALL come exclusively from
`ResearchRunExperience`. (`RED-003`)

#### Scenario: Phase lag cannot produce different TUI behavior
- **WHEN** the shared Module receives a suspended result with committed `bootstrap` and pending HITL-1
- **THEN** the TUI shows the same scope prompt as the CLI and does not classify it from the fact that the preceding action was start

#### Scenario: HITL2 progress is not a pending prompt
- **WHEN** a shared update contains a verified HITL2 trace visit and no pending input
- **THEN** the TUI may show that phase as progress but offers no Answer control, route
  options, or inferred resume action

### Requirement: TUI exposes shared run inspection truth without local path inference

The local TUI SHALL use an adapter-injected broker's projections for discovered-session
status and operations instead of keeping a parallel lifecycle/session controller. It MAY
render the broker's validated bounded pending-input view for an authorized session, and
SHALL render unavailable or denied operations without raw scope, path, provider, or
checkpoint data. It SHALL not select or reconstruct a recipe for a stored session; the
profile-owned broker determines whether the session is compatible. It retains the safe
legacy inspect reference and may offer only broker-backed discover/open/status/cancel or
resume controls; when a current HITL1 request is pending, it keeps the expected opaque
request id in its safe view model and passes raw answer text only to the broker. A
session at or after HITL2 with no typed pending request SHALL NOT be presented as an
HITL2 answer session. (`RED-005`)

#### Scenario: TUI shows the same paused-run reference as CLI
- **WHEN** the shared run experience projects a retained HITL-1 session
- **THEN** the TUI presents the same reference and inspectability truth as the CLI without decoding a lifecycle `Command`

#### Scenario: TUI shows an unavailable operation without a recovery claim
- **WHEN** the broker denies or cannot resolve a selected session
- **THEN** the TUI renders only the bounded unavailable state and does not offer a
  fabricated resume path

#### Scenario: HITL2 phase does not fabricate an answer session
- **WHEN** an inspected run has reached HITL2 but its typed Bundle-local State has no
  pending human request
- **THEN** the TUI exposes only the broker's legal status/continuation projection and
  does not create an HITL2 prompt, expected request id, or answer submission

### Requirement: Demo TUI answers advertised CHOICE prompts with typed options

The standalone demo TUI in fixture and embedded-smoke modes SHALL render the
options of the current advertised HITL1 CHOICE prompt and submit a user's
selection as the shared typed option answer carrying that advertised option id
for the prompt's current request. It SHALL NOT submit a text-kind answer for a
prompt whose shared contract requires an option, and SHALL NOT invent an option
id, construct a response envelope, or admit the answer itself — legality remains
with the shared run experience. Ordinary TEXT-mode HITL1 prompts SHALL keep
forwarding free text unchanged for semantic intake. The TUI SHALL NOT synthesize a
CHOICE prompt from HITL2 route labels or treat those labels as advertised user options.
(`RED-009`)

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

#### Scenario: Internal HITL2 routes never become TUI options
- **WHEN** an autonomous HITL2 visit selects or records an internal graph route
- **THEN** the TUI renders no CHOICE prompt and submits no option answer for that route
