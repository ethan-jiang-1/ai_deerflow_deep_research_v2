# research-demo-tui Specification

> req: RED-001, RED-002, RED-003, RED-004, RED-005, RED-006, RED-007, RED-008, RED-009, RED-010, RED-011, RED-012, RED-013, RED-014, RED-015, RED-016, RED-017

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

### Requirement: Journal-derived live narration binds the session's exact Bundle

During a dispatched run, the demo TUI's journal-derived live narration (progress
lines, rolling event feed, and last model-call state) SHALL read only the exact
Bundle that the session's shared updates identify by Bundle id. It SHALL NOT
select a narration source by scanning the workspace for the most recently updated
active or suspended Bundle. Until the session's updates identify a Bundle, live
narration SHALL degrade to the static working presentation and SHALL NOT read any
other Bundle's journal. A suspended node visit SHALL be narrated as awaiting
recovery, never as completed or failed. The startup attach candidate listing
keeps its bounded recency ordering; selecting a candidate is an exact bind.
(`RED-012`)

#### Scenario: Narration never shows another Bundle's facts
- **WHEN** two active or suspended Bundles coexist in the workspace and the
  session's updates identify one of them
- **THEN** live narration exposes only the identified Bundle's sequence, phase,
  and facts, and never the other Bundle's events

#### Scenario: Unbound narration stays static
- **WHEN** a dispatch is running and the session's updates have not yet
  identified a Bundle id
- **THEN** the TUI shows the static working presentation and reads no Bundle
  journal through a latest-activity scan

#### Scenario: A suspended visit is narrated as awaiting recovery
- **WHEN** the bound journal contains a node attempt whose outcome is `suspended`
- **THEN** live narration names that phase as suspended/awaiting recovery and
  does not count it as completed or failed

### Requirement: Canonical launcher entry reaches the debugger workbench

The repository SHALL ship an executable `run/tui-workflow-debugger.sh` that
resolves the harness root from any working directory without dependency
sync/install and without Bundle discovery or lifecycle logic. With no arguments
it SHALL start the debugger TUI composition chooser; `--fixture` and
`--embedded` SHALL pre-select the composition; `--attach <bundle_id>` and
`--replay <bundle_id>` SHALL carry explicit intent that the TUI and lifecycle
still validate; `--help` SHALL print usage and the equivalent Make commands;
unknown flags SHALL exit non-zero with usage. The launcher SHALL NOT scan the
workspace, select a latest Bundle, read checkpoints, or acquire leases.
(`RED-013`)

#### Scenario: Explicit intents reach the validated workbench
- **WHEN** an operator runs the launcher with `--fixture`, `--embedded`,
  `--attach <id>`, or `--replay <id>` from an arbitrary cwd
- **THEN** the debugger workbench starts with the requested composition or
  intent, and every Bundle reference is validated by the lifecycle before use

#### Scenario: Unknown flags fail without starting the TUI
- **WHEN** the launcher receives an unknown flag
- **THEN** it prints usage and exits non-zero without starting a session

### Requirement: Workbench opens with three entries and a Node Context pane

The debugger workbench first screen SHALL present three explicit entries — New
Run (Start Step or Start Run over a validated question draft), Attach (bounded
lifecycle-verified candidates with busy/read-only versus takeover postures),
and Replay (read-only) — normalized so buttons, command palette actions, and
slash commands produce the same typed adapter action. The workbench SHALL
present a Node Context pane listing the selected frame's node-agent invocations
from the C3 context inspector with the fixed coverage strip, and SHALL consume
`OperatorWorkspaceReader` typed pages in the Files pane. No pane SHALL scan the
workspace for a latest bundle, rebuild prompts, or expose host paths.
The workbench SHALL always state the current session posture and the next legal
composer action, and after a detach, a cancel, or a refused start it SHALL state
an explicit no-session posture instead of the previous session's posture. It
SHALL declare the minimum terminal size it supports and report that minimum to
the operator; on a smaller terminal it SHALL state the limitation and keep the
three entries, the composer, and the log usable. Opening the Node Context or
Files pane SHALL not clip pane content or reduce the log below a readable
height.
The workbench SHALL state, for the current posture, what the session is waiting for
(including the pending human request's own title, guidance, and advertised options)
and which actions are legal at that moment; it SHALL expose both start compositions -
Start Step and Start Run over one validated question draft - and the driver's pause
request, and SHALL offer a capability listing that names every workbench action.
The workbench SHALL also offer an exploration surface for the harness it drives: it
SHALL report the composition it runs (recipe identity and per-node kinds), the trusted
workspace roots, and the readable projections it exposes; it SHALL inventory every
Bundle the workspace offers as a debug target with its lifecycle status and attach
posture, and SHALL show one selected Bundle's internals including its frames and its
typed work-unit records; and for a captured node-agent invocation it SHALL show the
content the model was given and allowed - the request objective, the initial policy and
human message, the base-policy and capability layers with their identities and hashes,
the requested versus enforced tools, the budget, and the mount/root facts - with raw
provider histories labelled NOT RETAINED. Every entry that takes a Bundle id SHALL list
bounded candidates rather than answering with a bare usage line.
(`RED-014`)

#### Scenario: Three entries are explicit and equivalently reachable
- **WHEN** an operator triggers New Run, Attach, or Replay by button or by
  slash command
- **THEN** both paths normalize to the same typed adapter action and produce
  the same update or typed denial

#### Scenario: Node Context pane discloses coverage honestly
- **WHEN** an operator opens the context pane for a frame with captured
  invocations
- **THEN** invocations list from the C3 context store with the coverage strip
  (INITIAL CAPTURED, RUNTIME ENFORCED, ACTIVITY BOUNDED, OUTCOME
  OBSERVED/UNAVAILABLE, FILES CURRENT) and raw provider histories marked
  NOT RETAINED

#### Scenario: The workbench never shows a stale session state
- **WHEN** an operator detaches, cancels, or is refused a start because another
  bundle is active
- **THEN** the workbench states an explicit no-session posture with the legal
  next actions instead of the previous posture

#### Scenario: Panes never starve the log or clip
- **WHEN** an operator opens the Node Context or Files pane
- **THEN** the pane shows its content and the log retains a readable height

#### Scenario: A small terminal degrades honestly
- **WHEN** the terminal is smaller than the declared supported minimum
- **THEN** the workbench reports that minimum and the limitation, keeps the
  entries and the composer usable, and clips no content

#### Scenario: A HITL stop says what it asks and what may follow
- **WHEN** a session stops at a human-input request
- **THEN** the workbench states the request's own title, guidance, mode and
  advertised options together with the actions legal at that posture

#### Scenario: Both start compositions and pause are reachable
- **WHEN** an operator supplies one validated question draft
- **THEN** Start Step and Start Run are both reachable over that draft, and a
  running session can request a pause at its next committed boundary

#### Scenario: The debugger exposes what it is debugging
- **WHEN** an operator asks the workbench for its own anatomy or for the available
  debug targets
- **THEN** it reports the composition and readable projections, and lists each Bundle
  with its status and attach posture plus one selected Bundle's frames and work units

#### Scenario: A captured invocation shows what the model was given and allowed
- **WHEN** an operator drills into one captured node-agent invocation
- **THEN** the workbench shows that invocation's objective, initial policy and human
  message, layer identities and hashes, requested versus enforced tools, budget and
  mounts, with raw provider histories labelled NOT RETAINED

### Requirement: Operator shell escape at the workbench

The debugger workbench SHALL let the operator run a bounded one-shot shell command
from the composer by prefixing it with `!`, at any posture, without the line being
consumed as a research answer or a debug command. The command SHALL run
non-interactively with the operator's own privileges — the escape grants no new
authority — under a runtime bound that terminates an overrun command, with captured
output bounded in size and truncation stated. Its working directory SHALL anchor to
the live session's Bundle directory when a session is open, else to the workspace
bundle root. The output SHALL be rendered verbatim in the log, labelled as
operator-invoked content with the command and the working directory; it is not a
workbench projection, and no graph state, admission decision, route, or tool
authority is derived from it. The capability SHALL be listed by `/help`.

#### Scenario: Inspecting the filesystem at a paused boundary
- **WHEN** the workbench is paused at any boundary and the operator submits a
  `!`-prefixed command
- **THEN** the command runs with the anchored working directory and its bounded
  output appears in the log as operator-invoked content, while the pending HITL
  request stays open

#### Scenario: A runaway command is bounded
- **WHEN** the command exceeds the runtime bound
- **THEN** the escape terminates it, states the timeout, and the workbench stays
  responsive

#### Scenario: The escape is not graph authority
- **WHEN** any shell escape runs
- **THEN** no admission, tool, route, or graph state changes because of it, and the
  rendered output is presented as operator-invoked content rather than a projection

### Requirement: Operator side-chat at the workbench

The debugger workbench SHALL let the operator converse with a chat model from the
composer by prefixing the line with `?` (or the full-width `？`), at any posture.
A side-chat turn SHALL NOT be consumed as a research answer or a debug command,
SHALL NOT consume a pending HITL request or its revision rounds, and SHALL NOT
change any graph state, admission decision, route, or tool authority. The
conversation SHALL use the operator's own chat model with the same read-only
workspace tools as the recon chat, and its output SHALL render in the log as
operator-invoked content while the debug posture pane keeps ownership of the
posture display. The capability SHALL be listed by `/help`.

#### Scenario: Conversing at a HITL stop without consuming the round
- **WHEN** the workbench is waiting at a HITL request and the operator submits a
  `?`-prefixed line
- **THEN** the chat model answers in the log, the pending HITL request stays open
  with its revision rounds untouched, and the next unprefixed line is still the
  formal answer

#### Scenario: The side chat holds no graph authority
- **WHEN** any side-chat turn runs
- **THEN** no admission, tool, route, or graph state changes because of it, and the
  rendered output is presented as operator-invoked content rather than a projection

### Requirement: The debugger workbench renders HITL stops as a typed conversation, never as machine JSON

At a HITL stop the debugger workbench SHALL render the pending request's typed prompt
card when the session projection carries one — the node's heading, goal summary,
proposed dimensions, missing fields, remaining accepted-answer rounds, and localized
guidance — together with the request's own title, mode, and advertised options. It
SHALL NOT print the request's raw machine context payload. When the projection carries
no prompt card, the workbench SHALL state the title, mode, and a bounded
unparsed-context note instead of the raw payload.

When the session projection carries the node's last feedback for the pending
conversation, the workbench SHALL render it as the node's visible reply. After an
operator answer is consumed and the session re-stops at the same node's HITL request,
the workbench SHALL state that the answer was consumed but not accepted, including the
remaining accepted-answer rounds when the card carries them.

A plain-text submit in the debugger SHALL clear the composer, so a repeated Enter
cannot resubmit the same text as another answer or as an unintended advance. The HITL
card and the capability listing SHALL name the fastest legal confirm input and the
single-field revision format. (`RED-015`)

#### Scenario: A HITL stop shows the card, not the payload
- **WHEN** a debug session stops at a HITL request whose projection carries a parsed
  prompt card
- **THEN** the workbench renders the card's goal, proposed dimensions, missing fields,
  remaining rounds, and guidance, and the raw context JSON appears nowhere in the log

#### Scenario: The node's reply is visible
- **WHEN** the projection carries the node's last feedback after a consumed answer
- **THEN** the workbench renders that feedback message as the node's reply together
  with the consumption outcome and remaining rounds when known

#### Scenario: An unparsed context degrades honestly
- **WHEN** a HITL request's projection carries no prompt card
- **THEN** the workbench states the request's title and mode with a bounded
  unparsed-context note and prints no raw machine payload

#### Scenario: A repeated Enter cannot double-consume
- **WHEN** the operator submits plain text in the debugger and presses Enter again
- **THEN** the composer no longer holds the submitted text, and the second Enter
  produces no second answer submission and no unintended node advance beyond the
  documented empty-submit behavior for the current posture

#### Scenario: The fastest path out is advertised
- **WHEN** the workbench shows a HITL card or its capability listing
- **THEN** the fastest legal confirm input and the single-field revision format are
  named in operator-readable text

### Requirement: The workbench exposes node rerun and states every policy auto-answer

The debugger workbench SHALL expose the node-rerun entry at a stopped boundary as a
slash command listed by `/help`, with a visible cost note that the embedded
composition re-bills the real model call. When the drive policy auto-answers a hitl1
request, the workbench SHALL state each auto-answer in the log as operator-policy
content, and a policy stop SHALL render the node's reply and remaining rounds exactly
like a human-facing HITL card. (`RED-016`)

#### Scenario: Rerun is reachable and honest about cost
- **WHEN** the operator reruns the last committed node at a boundary
- **THEN** the log states the rerun, its node, and — in embedded compositions — that
  the model call is billed again

#### Scenario: Auto-answers are never silent
- **WHEN** the drive policy answers a hitl1 request
- **THEN** the log states that the answer came from the drive policy, and a policy
  stop renders the standard HITL conversation card for the human

### Requirement: The workbench answers where-am-I, what-is-this-field, and watch requests

The debugger workbench SHALL provide three bounded introspection entries, listed by
`/help`: `/bt` states the walked node path from the session's durable trace (grouping
consecutive revisits, marking the node currently awaited, if any); `/state [field]`
renders one typed State field's bounded value, or the field-name list when no field is
given, and rejects unknown names with a typed line; `/watch [field]` and
`/unwatch <field>` manage the session's watch set against the same typed field
allowlist. When a drive stops on a watch hit, the workbench SHALL state which watched
fields changed. (`RED-017`)

#### Scenario: The walked path is answerable at any stop
- **WHEN** the operator enters `/bt` at any session posture
- **THEN** the workbench renders the walked node path with revisit counts and the
  current position, derived from the session's durable trace

#### Scenario: A single field is answerable without machine JSON
- **WHEN** the operator enters `/state <field>` for a typed State field
- **THEN** the workbench renders that field's bounded value, and an unknown field
  name renders a typed rejection instead of any payload

#### Scenario: A watch hit is stated, never silent
- **WHEN** a drive stops because a watched field changed
- **THEN** the workbench names the changed fields in the log
