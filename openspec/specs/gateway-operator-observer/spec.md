# gateway-operator-observer Specification

> req: GOO-001, GOO-002, GOO-003

## Purpose

Provide a bounded local operator path that starts and observes configured DeerFlow
Gateway turns without turning transport, presentation, or physical logs into Deep
Research execution, history, or lifecycle authority.

## Requirements

### Requirement: Gateway observer uses only the configured public entry and stream

The observer SHALL use the selected ready local profile and DeerFlow's public thread
creation and thread-run streaming interfaces at the profile-launched direct local
Gateway `http://127.0.0.1:8001`. It SHALL address the configured `deep-research`
Agent through the public request field, submit only the operator's explicit entered
text or a value from a currently displayed selected control, and consume the returned
public SSE stream. A non-scripted start SHALL create a fresh Gateway thread; only a
later explicit follow-up in the same observer process may use that returned opaque
thread id. It SHALL NOT construct an embedded graph, call `DemoLifecycleTransport`,
select a local Bundle, read a private Gateway journal/store, poll graph State, or
derive a thread, Run, Bundle, trace, checkpoint, or lifecycle identity from a path or
timestamp. It SHALL NOT accept a caller-supplied origin or use the Nginx/proxy `:2026`
endpoint. (`GOO-001`)

The observer MAY retain for its process only the Gateway-created opaque thread id,
public SSE metadata run correlation, the public response-header trace correlation, and
an existing safe Bundle/diagnostic reference supplied by an approved Deep Research
event or validated reflected-tool result. It SHALL exclude credentials, headers, tool
arguments, non-Deep-Research tool results, request/model/provider internals, full
URLs, host paths other than the profile launcher's explicitly permitted local log path,
private store data, and caller-forged correlation. (`GOO-001`)

#### Scenario: Real observation enters through the configured Agent
- **WHEN** an operator starts a supported real CLI or TUI turn with a ready local
  profile
- **THEN** the observer creates/uses a public Gateway thread, streams the turn with
  `assistant_id=deep-research` at `127.0.0.1:8001`, and constructs no embedded graph
  or local lifecycle transport

#### Scenario: Proxy or caller-selected origin is not an observer target
- **WHEN** a caller supplies a Gateway URL or the Nginx `:2026` endpoint is available
- **THEN** the observer does not use that value and targets only the ready
  profile-launched local Gateway at `127.0.0.1:8001`

#### Scenario: Explicit follow-up creates only another public turn
- **WHEN** the shared typed experience asks for user input and the operator supplies
  one explicit answer, direction, or currently advertised control value
- **THEN** the adapter sends exactly that value as the next public turn on the same
  process-retained Gateway thread and does not directly choose or invoke a Deep
  Research lifecycle action

#### Scenario: New research starts with a fresh public thread
- **WHEN** an operator explicitly starts a new non-scripted research request after a
  prior observer turn exists in the same process
- **THEN** the observer creates a new public Gateway thread for the new request and
  does not use, delete, or derive identity from the prior thread

#### Scenario: Non-text local control is not converted into a Gateway turn
- **WHEN** a Gateway-default entry receives a scripted runtime context or local
  cancel/status/refine control that has no operator-entered text
- **THEN** it fails before a new Gateway turn request, creates no new thread or stream
  request, submits no invented user message, and does not invoke a Deep Research
  lifecycle action directly

#### Scenario: Missing or forged correlation is not used
- **WHEN** stream input lacks metadata or a caller supplies a run, thread, Bundle,
  trace, path, or checkpoint value outside the Gateway response
- **THEN** the observer omits that value and does not use it to select, recover, or
  control a Run or Bundle

### Requirement: Structured stream projection preserves typed lifecycle authority

The observer SHALL parse SSE through a structured client and accept only bounded
records from `metadata`, `messages-tuple`, `custom`, `error`, `end`, heartbeat, and
explicit gap events. From `messages-tuple`, it MAY render safe public assistant text
and MAY admit only a returned `deep_research` tool result that validates against the
existing typed lifecycle result contract. It SHALL ignore tool arguments, other tool
results, raw model/provider payloads, and unknown records.

Before a configured-Gateway integration contract has proved nested forwarding, an
otherwise valid `deep_research.progress.v1` payload received on DeerFlow's public SSE
`custom` channel SHALL remain a withheld validation candidate. It MAY be observed only
by focused deterministic evidence or the bounded forwarding proof and SHALL NOT reach a
real CLI/TUI presentation callback. After
`add-deerflow-native-live-event-projection` has archived and that proof succeeds, the
observer SHALL render only the predecessor-approved fields from later candidates that
pass the same validation. It SHALL not persist, replay, acknowledge, deduplicate,
retry, or re-emit either the proof record or an observed event.

Heartbeat SHALL mean only that the transport delivered liveness. A gap, disconnect,
duplicate, reordering, absent custom event, malformed payload, or replay boundary SHALL
remain a transport condition. Gateway `end` SHALL mean only that the outer turn ended;
it SHALL NOT by itself mean that Deep Research completed, failed, cancelled, resumed,
retried, or remains active. Only the existing validated typed lifecycle result may
produce those lifecycle presentations. (`GOO-002`)

#### Scenario: Valid reflected result enters the shared typed experience
- **WHEN** one public `messages-tuple` record contains a returned `deep_research` tool
  result that satisfies the existing lifecycle schema
- **THEN** the Gateway transport returns that typed result to the shared experience
  without retaining raw tool arguments or creating another lifecycle interpretation

#### Scenario: Assistant text is presentation only
- **WHEN** the configured Agent emits public assistant text during a Gateway turn
- **THEN** the CLI/TUI may display the bounded text, but neither the text nor the
  renderer may select a Bundle, authorize an action, or prove a Deep Research outcome

#### Scenario: Verified custom event is rendered as a projection
- **WHEN** the predecessor is archived and the configured-Gateway contract receives
  one valid `deep_research.progress.v1` payload on the public `custom` channel
- **THEN** the observer renders only its approved safe fields without persisting,
  acknowledging, re-emitting, or using it to decide a lifecycle outcome

#### Scenario: Unproven custom delivery is withheld from an entrypoint
- **WHEN** deterministic stream evidence receives a valid
  `deep_research.progress.v1` candidate before the configured-Gateway forwarding proof
  has succeeded
- **THEN** the candidate may establish only decoder/proof evidence and does not reach
  a real CLI/TUI presentation callback or decide a lifecycle outcome

#### Scenario: Heartbeat and gap remain transport facts
- **WHEN** the observer receives a heartbeat, explicit gap, duplicate, reordered
  record, or reconnect boundary
- **THEN** it displays only the applicable bounded transport condition and issues no
  Deep Research retry, resume, cancel, or recovery action

#### Scenario: Gateway end cannot manufacture research completion
- **WHEN** the stream ends without one validated typed Deep Research lifecycle result
- **THEN** the presentation reports the Gateway turn as ended with Deep Research
  outcome unknown and does not report completed research

### Requirement: Profile-owned capture preserves DeerFlow logging boundaries

A project-owned local profile that advertises Gateway observation SHALL preflight
restart-scoped trace-correlated JSON logging, durable supported run-history storage,
public Deep Research entry readiness, and Gateway health before the observer starts or
claims Gateway/Console history. It SHALL NOT patch configuration or fall back to an
ephemeral history backend while retaining that claim.

The profile launcher SHALL tee the launched unchanged Gateway stack's existing
`stderr` bytes to one process-scoped rotating log family below
`deep_research_harness/.deep-research-demo-runs/logs/`, a sibling of the sandbox-mapped
`workspace/`, while retaining normal `stderr`. It SHALL create the log directory and
files with owner-only permissions, print the invocation's absolute base log path before
provider work, isolate concurrent launches, bound each process log and total retained
inactive logs, and never delete an active process file.

The capture remains a deployment artifact. It SHALL NOT be a Bundle artifact, Deep
Research event format, replay source, Run selector, recovery input, lifecycle API, or
replacement for Gateway SSE/history. Capture creation, write, rotation, or retention
failure SHALL leave normal `stderr`, the Gateway process, and every Deep Research
execution/lifecycle fact unchanged. (`GOO-003`)

#### Scenario: Ready profile exposes a bounded local log location
- **WHEN** a valid local observer profile launches the unchanged Gateway stack
- **THEN** it prints that process's absolute owner-only base log path before provider
  work, continues the same normal `stderr` stream, and stores no log beneath a Bundle
  or sandbox workspace

#### Scenario: Profile cannot claim history without durable prerequisites
- **WHEN** the selected profile lacks trace-correlated JSON logging, durable supported
  run history, public Deep Research entry readiness, or a healthy Gateway
- **THEN** preflight fails before an observer turn, reports only the safe corrective
  profile action, and neither rewrites configuration nor creates a Run

#### Scenario: Capture failure cannot affect research execution
- **WHEN** local capture is unavailable, fails, or reaches its retention bound while
  the Gateway is running
- **THEN** capture reports only its bounded local condition and leaves Gateway
  `stderr` plus every Deep Research execution and lifecycle fact unchanged
