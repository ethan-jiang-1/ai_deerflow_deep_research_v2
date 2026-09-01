# research-cli-onboarding Specification

> req: REC-001, REC-002, REC-003, REC-004, REC-005, REC-006, REC-007, REC-008

## Purpose

Provide a first-run-friendly standalone all-real Deep Research CLI with explicit
input, graph-owned human checkpoints, truthful lifecycle visibility, and bounded
failure guidance without changing the production DeerFlow CLI, Gateway, Web UI, or
Terminal Workbench.
## Requirements

### Requirement: Real CLI establishes a prepared user journey before dispatch

The standalone `demo_real.py` interactive command SHALL obtain a successful shared
`ReadinessReport` before prompting for a research question, constructing a start
message, or calling a model. A passing report SHALL explain the bounded graph-owned
journey, that an inspectable local bundle appears only after a validated research id,
and that inspection does not promise cross-process execution recovery. A failed report
SHALL identify the missing or invalid local prerequisite, why it is needed, an
actionable next step, and any safe diagnostic reference without asking for a research
question or presenting an inspect command.

After preflight, the CLI SHALL choose or confirm a non-blank research question and
then answer each `AwaitingInput` update until a `Terminal` or `Fault` update is
returned. Current graph-produced `AwaitingInput` updates belong to HITL1 and MAY repeat
for its bounded follow-up flow; a verified HITL2 visit SHALL not create another CLI
prompt. Supplying `--question` SHALL bypass only question entry and visibly confirm
a bounded control-character-safe representation while preserving the original value
for start. Blank `--question` SHALL fail before graph construction. `--scripted`
SHALL remain a credentialed, non-interactive real route that uses the graph's
documented automatic policy, reads no stdin, and renders the same shared `RunUpdate`
semantics. EOF or interrupt at a CLI-owned prompt SHALL exit cleanly without
dispatching the next action or printing a traceback.

The CLI SHALL submit only `Start`, `Answer`, `Cancel`, or `Status` intent to
`ResearchRunExperience`. It SHALL NOT parse `Command`, `ToolMessage`, `human_input`
artifact, raw control JSON, pending phase, or graph response correlation. (`REC-001`)

#### Scenario: Preflight succeeds before a first question
- **WHEN** a user runs `make demo-real` with usable local real-demo prerequisites
- **THEN** the CLI first confirms what will be checked and that an inspectable bundle
  appears only after a run reference, then asks for a research question before
  dispatching start

#### Scenario: Missing prerequisite is explained before question entry
- **WHEN** a user runs `make demo-real` without a required model or web-tool prerequisite
- **THEN** the CLI stops at preflight with a specific safe setup explanation and next action, creates no research run or bundle, and does not ask the user to retry an unexplained lifecycle result

#### Scenario: Explicit question preserves automation
- **WHEN** a user runs `make demo-real` with an explicit non-blank `--question`
- **THEN** the CLI does not prompt for a question, safely confirms it after preflight, and sends the original value only through shared `Start` intent

#### Scenario: Blank explicit question is refused
- **WHEN** a user supplies a blank or whitespace-only `--question`
- **THEN** the CLI exits before graph construction with a concise input error and does not silently substitute a sample question

#### Scenario: Scripted route has no stdin dependency
- **WHEN** automation runs `demo_real.py --scripted` with complete real credentials
- **THEN** it completes shared preflight, prints its documented default or explicit question and automatic policy, reads no stdin, and renders the terminal or fault update returned through `ResearchRunExperience`

#### Scenario: Scripted route honors an explicit question
- **WHEN** automation runs `demo_real.py --scripted --question "Compare storage costs"`
- **THEN** it reads no stdin, safely confirms that explicit question, and uses it as the initial start message rather than silently replacing it with the scripted default

#### Scenario: Graph-owned HITL requests may repeat
- **WHEN** an HITL1 response yields a bounded follow-up request
- **THEN** the CLI renders that returned request through `RunUpdate` and does not assume a fixed number of HITL1 resumes or prompts

#### Scenario: Autonomous HITL2 adds no CLI answer round
- **WHEN** the verified run trace advances through HITL2 after Wave2 passes
- **THEN** the CLI may render that progress but reads no additional answer and displays
  no internal route menu

### Requirement: Real CLI renders shared truthful run updates and failures

The real CLI SHALL render only `RunUpdate` values from `ResearchRunExperience`.
Before an unresolved dispatch it MAY show the shared `Working` action and elapsed
local time. It SHALL render completed phase progress only from a verified returned
trace delta, including repeat visits, and SHALL never infer a phase from action,
input mode, option count, or a local fixed sequence. A pending HITL1 prompt SHALL
display its shared semantic guidance, advertised typed inputs/controls, and validation
feedback. A verified HITL2 trace visit without pending input SHALL render only as
autonomous progress and SHALL NOT expose graph routes as user choices.

For every terminal or fault outcome the CLI SHALL show what happened, the known
phase when available, the safe category/reason level, concrete next action,
retryability or non-retryability, durability truth, and opaque diagnostic reference
when available. It SHALL not stringify dictionaries, exceptions, arbitrary fields,
machine context, credentials, paths, provider bodies, raw model output, or a
terminal-control sequence. It SHALL not display a generic retry-only outcome.

Ctrl-C while a lifecycle action is unresolved SHALL propagate as a local
interruption, close local resources, and not claim that the graph was cancelled. An
explicit shared `Cancel` result may be displayed only after the graph confirms it.
(`REC-002`)

#### Scenario: Valid bootstrap-plus-HITL-1 suspension is actionable
- **WHEN** start returns a suspended result whose committed phase is `bootstrap` and whose pending input is HITL-1
- **THEN** the CLI renders completed initialization, a semantic scope prompt, and the next answer action rather than rejecting the result or saying only retry

#### Scenario: Blocked run has a useful safe explanation
- **WHEN** a run ends blocked after a classified model, tool, provider, storage, or graph failure
- **THEN** the CLI names the safe category and phase, tells the user what to check or whether it is not retryable, prints its diagnostic reference, and never leaks the underlying raw failure content

#### Scenario: Returned-only waiting is honest
- **WHEN** a dispatch is unresolved and no stream event is available
- **THEN** the CLI shows only local elapsed waiting for the lifecycle result and does not update a phase tracker, percentage, or fabricated model/web activity

#### Scenario: Repeated phase progress is preserved
- **WHEN** a returned trace extends a prior trace with another `wave2_synthesis` visit after a rerun
- **THEN** the CLI renders that returned repeated visit once as new progress and does not infer any phase that was absent from the verified returned suffix

#### Scenario: Local interruption does not claim durable cancellation
- **WHEN** the user presses Ctrl-C while the CLI is awaiting a lifecycle action
- **THEN** it closes local resources and exits as an interrupted local process without issuing a graph `Cancel` or claiming the research was durably cancelled

#### Scenario: Internal HITL2 route is not rendered as a choice
- **WHEN** a shared update reports an autonomous HITL2 visit with no pending request
- **THEN** the CLI renders no prompt, route options, or Answer action for that visit

### Requirement: Real CLI exposes bounded standalone diagnostics and durability

The standalone CLI SHALL label the active local profile's durability truth and remain
explicitly non-product. Same-process sessions SHALL not promise recovery after process
exit. A configured operation-enabled file-SQLite profile MAY direct an owner to the
bounded profile-mediated session commands, but SHALL not claim Gateway, Web, multi-user,
or generic product-session recovery. Failures continue to expose only safe opaque
diagnostic references and relative local record locations.

The local session-workbench entry SHALL run only against the configured durable local
profile and SHALL state that it is a standalone terminal operator surface rather than a
Gateway, Web, upstream terminal, or generic recovery client. (`REC-003`)

#### Scenario: User can retain a safe support reference
- **WHEN** a standalone run fails after its lifecycle begins
- **THEN** the CLI prints an opaque diagnostic reference and bounded local record location that an operator can inspect without revealing raw runtime data

#### Scenario: Durable local operation is not advertised as product recovery
- **WHEN** a record-bearing run uses the configured restart-durable local profile
- **THEN** the CLI may state the bounded local session-operation command while still
  identifying the surface as a standalone local demo rather than a Gateway or workbench

#### Scenario: Workbench startup remains local-profile-bound
- **WHEN** an owner launches the local session workbench
- **THEN** it reports only the configured local profile's durable availability and does
  not claim that a Gateway, Web, or production terminal session was opened

### Requirement: Real CLI exposes a safe run reference and local inspection path

The real CLI SHALL expose only the shared bounded `bundle_id` from a lifecycle result as
a selected Run reference. It may offer supported contained Bundle inspection through the
same trusted-scope lifecycle/inspection boundary, but SHALL not display or accept a
session reference, `research_id`, raw path, provider key, checkpoint namespace, or
retained-manifest locator. A deleted, unavailable, foreign, or ambiguous Bundle SHALL
produce truthful bounded guidance and SHALL not offer resume/recovery through a local
path. (`REC-004`)

#### Scenario: CLI inspection cannot reconstruct a lost Run
- **WHEN** a user requests inspection for a deleted Bundle whose historical diagnostic remains
- **THEN** the CLI reports the bounded unavailable outcome and performs no graph, provider, or content recovery

### Requirement: Real CLI makes profile confirmation and run state actionable

The real standalone CLI SHALL render the shared HITL1 proposal, recognized fields, missing fields including `must_answer`, rejection feedback, remaining accepted-answer and rejection-retry budgets, and visible advertised `accept_suggestion` action. It SHALL offer a stable complete JSON example and SHALL not imply that a vague sentence accepts a proposal.

During returned-only waiting the CLI SHALL render bounded recurring local state including run reference when known, elapsed time, last committed phase, and the fact that it is waiting for a lifecycle return rather than observing background execution. Every terminal outcome SHALL render its outcome, phase, safe diagnostic reference/category when known, durability-specific recovery truth, and exact inspection command. (`REC-005`)

#### Scenario: A first-time user can see every required intake field
- **WHEN** real HITL1 returns its first prompt
- **THEN** CLI shows the proposal, `must_answer`, accepted/missing fields, a visible acceptance action, and a complete JSON example

#### Scenario: A completed background-looking call is not misrepresented
- **WHEN** a retained same-process run has already returned a terminal result
- **THEN** CLI prints the terminal receipt and says the retained bundle is inspectable but not proof of a live or cross-process-resumable run

#### Scenario: CLI never echoes unsafe diagnosis data
- **WHEN** a diagnostic fixture contains exception text, a secret, path, or raw answer
- **THEN** terminal and inspect guidance omit those values while retaining safe category and opaque reference

### Requirement: Real CLI reports provider diagnostics and honest fresh-start guidance

The real CLI and TUI SHALL retain the existing redacted provider-diagnostic category,
phase, bounded recovery-observation, diagnostic-reference, and legal-next-action
guarantees. A current Deep Research lifecycle projection SHALL use the shared typed
Bundle result: an inspect action is permitted only for an available selected Bundle and
never for a retained session reference or a diagnostic alone. For the `fresh_start`
legal action, the static `make demo-real` command SHALL be labelled as a distinct fresh
run from `deep_research_harness/`; it SHALL not promise resume or recovery of an
unavailable Bundle. (`REC-006`)

#### Scenario: Provider diagnosis cannot make a deleted Bundle inspectable
- **WHEN** a provider-diagnostic observation remains after its Bundle has been deleted
- **THEN** the CLI may render the safe observation but suppresses inspection/control and
  directs the user only to the typed legal next action

### Requirement: Real CLI renders direct-phase workflow incidents without collapsing them

The standalone real CLI SHALL render a terminal direct-phase workflow incident using
only the shared run update's safe category, phase, observed recovery disposition,
diagnostic reference, durability truth, and legal next action. It SHALL distinguish a
known provider timeout/unavailable incident from generic blocked, structured-output
exhaustion, and unknown local failure without displaying raw provider or exception
content.

#### Scenario: BUG-010 is reported as a bounded topic-planning timeout
- **WHEN** real topic planning exhausts its configured provider-recovery policy
- **THEN** the CLI identifies `provider.timeout` and `topic_planning`, reports the
  observed bounded recovery, prints only the legal next action, and preserves a safe
  diagnostic reference rather than saying only that research was blocked

### Requirement: Real CLI makes natural proposal interaction and fallback controls discoverable

The real standalone CLI SHALL render the shared proposal and bounded feedback in normal
human language. A user may submit ordinary confirmation, revision, question, or
clarification text; the CLI SHALL not require a JSON object or hidden acceptance phrase
for those intents. It SHALL render each shared visible control with a stable number and
submit the selected number as `SelectControlRun`, never as an action id or magic text.
On semantic failure it SHALL state the non-terminal condition, retain the proposal, and
render the current-proposal fallback control. (`REC-007`)

#### Scenario: First-time confirmation needs no protocol knowledge
- **WHEN** a user sees the initial complete proposal
- **THEN** the CLI explains that they can confirm, revise, or ask a question in normal
  language and also shows `1. Start with the current proposal`

#### Scenario: Semantic failure stays actionable
- **WHEN** semantic intake cannot interpret or reach its provider for a reply
- **THEN** CLI shows bounded feedback and the same numbered current-proposal control
  instead of JSON-only recovery or a terminal input error

### Requirement: Retained-diagnostic command is executable and read-only

Whenever CLI or TUI renders an available Bundle inspection action, it SHALL render the
documented command shape executable from `deep_research_harness/`:
`make demo-sessions DEMO_ARGS="inspect <bundle-id>"`. The command remains explicitly
read-only and may show only the existing safe diagnostic/timing observations. It SHALL
not accept a session reference, imply retry, resume, cross-process continuation, or
provider conclusion; an unavailable Bundle suppresses the command even when an
external diagnostic remains. (`REC-005`, `REC-006`)

#### Scenario: Rendered inspection command uses Bundle identity
- **WHEN** an authorized available terminal Bundle has a correlated retained diagnostic
- **THEN** the displayed command uses its bounded `bundle_id`, runs from
  `deep_research_harness/`, and returns only a read-only observation

### Requirement: Real CLI uses one Bundle lifecycle vocabulary and truthful loss guidance

The real CLI SHALL consume the shared typed Bundle lifecycle result for start, status,
control, refinement, and inspection. It SHALL display the bounded `bundle_id` where
appropriate and explain active, awaiting-input, ended, and unavailable outcomes with
their legal next action. It SHALL not display or require `research_id`, session
references, checkpoint names, or host paths, and it SHALL not claim that a deleted
Bundle can resume. (`REC-008`)

#### Scenario: CLI reports a deleted Run without false resume guidance
- **WHEN** a CLI action targets a Bundle that was externally deleted
- **THEN** it reports the typed unavailable outcome and guides the user to a fresh independent Run or permitted observation only
