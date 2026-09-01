> req: REC-001, REC-002, REC-003, REC-004, REC-005, REC-006, REC-007, REC-008

## MODIFIED Requirements

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
