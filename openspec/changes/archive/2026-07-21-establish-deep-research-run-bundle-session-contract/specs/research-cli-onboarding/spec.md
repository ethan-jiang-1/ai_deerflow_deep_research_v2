> req: REC-001, REC-004

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
returned. Supplying `--question` SHALL bypass only question entry and visibly confirm
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
- **WHEN** a HITL-1 response yields a follow-up request or a HITL-2 decision routes through rerun/repair and later returns another HITL request
- **THEN** the CLI renders that returned request through `RunUpdate` and does not assume a fixed number of resumes or prompts

## ADDED Requirements

### Requirement: Real CLI exposes a safe run reference and local inspection path

After the first record-bearing validated lifecycle result identifies a research run,
the standalone CLI SHALL present its opaque run reference, inspectability truth, and the exact local
inspection command `make -C agent demo-sessions DEMO_ARGS="inspect <research_id>"`.
It SHALL not print a raw host path, temporary directory, checkpoint namespace,
credential, or arbitrary diagnostic content. On terminal/local interruption it SHALL
state whether the retained bundle remains inspectable and shall not claim that
inspection resumes execution.

The CLI SHALL render this information only from shared run updates or a bounded
session-inspection result; it SHALL not parse lifecycle wire values or construct a
filesystem path itself. EOF or `KeyboardInterrupt` at a paused CLI-owned prompt SHALL
render at most a local interruption message and this exact inspect command; it SHALL
not publish a lifecycle transition, promise resume, or claim anything newer than the
last verified returned state. (`REC-004`)

#### Scenario: First HITL gives a developer an inspectable handle
- **WHEN** real CLI start returns the first bootstrap-plus-HITL-1 suspension
- **THEN** the user sees the semantic scope prompt and a safe run reference with an explicit inspect path, without raw workspace details or a promise of resume
