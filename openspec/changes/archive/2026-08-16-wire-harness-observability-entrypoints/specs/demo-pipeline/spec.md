> req: DPL-004

## MODIFIED Requirements

### Requirement: CLI real demo validates and explains prerequisite readiness

`deep_research_harness/scripts/demo_real.py` SHALL retain `--question`, non-blank-
question validation, and shared typed lifecycle presentation. Its default real path
SHALL require one valid explicit `--profile` label that resolves to a ready local
Gateway profile, create a public Gateway thread for a non-scripted question, and
submit each explicit user turn through the configured `deep-research` Agent's public
run-stream interface. It SHALL not require local `DEERFLOW_DEMO_MODEL` or
`TAVILY_API_KEY` values, construct an all-real recipe/executor, or use a local Bundle
lifecycle transport on that Gateway-backed path; model and web credentials remain owned
by the launched Gateway profile.

The Gateway-backed CLI SHALL not derive a Run/control identity from the demo process,
a checkpoint, retained-session record, path, or timestamp, and SHALL not accept a
recipe, executor, checkpoint, graph route, Bundle id, run id, thread id, or caller-
selected Gateway identity as command input. It MAY retain the Gateway-created thread id
only for explicit follow-up turns during the current process. `--scripted` without an
explicit embedded-smoke selection SHALL fail before profile/Gateway thread creation:
its automatic policy is trusted runtime context and cannot be sent as a public user
turn. It SHALL not replace that failure with a fixed question, invented follow-up, or
direct Deep Research lifecycle action.

If profile/Gateway preflight fails, the public stream cannot start, or the Gateway turn
ends without a validated typed Deep Research lifecycle result, the CLI SHALL present
the bounded startup/transport outcome and SHALL NOT render synthetic research
completion.

The existing direct graph composition MAY remain only behind an explicit embedded-
smoke mode. That mode alone SHALL retain the current local model/Tavily preflight and
all-real recipe/executor construction, and its output SHALL identify itself as
embedded smoke without Gateway history, Console, trace-correlation, StreamBridge, or
custom-event-forwarding claims. (`DPL-004`)

#### Scenario: Real demo entry follows the canonical root
- **WHEN** an operator starts `deep_research_harness/scripts/demo_real.py` with a ready
  selected profile and no embedded-smoke selection
- **THEN** its request, follow-up turns, live display, and typed lifecycle result use
  the configured public Gateway path without constructing an embedded all-real
  executor or local lifecycle transport

#### Scenario: Gateway readiness replaces local provider readiness
- **WHEN** the selected Gateway profile is healthy and its entry/logging/history
  prerequisites pass while the observer process has no local model or Tavily key
- **THEN** the default real CLI may start because provider credentials belong to the
  Gateway process rather than the observer

#### Scenario: Gateway CLI requires a selected profile
- **WHEN** an operator omits `--profile` or provides an invalid/unready label
- **THEN** the command exits before a health, thread, or stream request and reports
  only the safe profile corrective action

#### Scenario: Gateway CLI does not fabricate the scripted policy
- **WHEN** an operator passes `--scripted` without selecting embedded smoke
- **THEN** the command exits before profile/Gateway thread creation, reports that
  automatic policy is embedded-smoke-only, and sends no fixed question, synthetic
  answer, lifecycle action, or Gateway request

#### Scenario: Real demo cannot claim synthetic completion
- **WHEN** the configured Gateway observer cannot start or its turn returns no
  validated typed Deep Research lifecycle result
- **THEN** the command exits nonzero without reporting completed research or
  constructing a local completion from stream end, retained data, or assistant prose

#### Scenario: Embedded smoke remains honestly scoped
- **WHEN** a developer explicitly selects the direct graph smoke route
- **THEN** that mode applies the existing local provider preflight, identifies itself
  as embedded smoke, and does not claim Gateway run history, Console data, trace
  correlation, SSE liveness, or custom-event forwarding
