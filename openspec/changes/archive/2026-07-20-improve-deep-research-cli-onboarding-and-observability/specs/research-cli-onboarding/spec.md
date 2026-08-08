> req: REC-001, REC-002, REC-003

## MODIFIED Requirements

### Requirement: Real CLI establishes a prepared user journey before dispatch

The standalone demo_real.py interactive command SHALL obtain a successful shared
ReadinessReport before prompting for a research question, constructing a start
message, or calling a model. A passing report SHALL explain the bounded
graph-owned journey and the standalone demo's temporary/non-resumable durability.
A failed report SHALL identify the missing or invalid local prerequisite, why it is
needed, an actionable next step, and any safe diagnostic reference without asking
for a research question.

After preflight, the CLI SHALL choose or confirm a non-blank research question and
then answer each AwaitingInput update until a Terminal or Fault update is returned.
Supplying --question SHALL bypass only question entry and visibly confirm a bounded
control-character-safe representation while preserving the original value for
start. Blank --question SHALL fail before graph construction. --scripted SHALL
remain a credentialed, non-interactive real route that uses the graph's documented
automatic policy, reads no stdin, and renders the same shared RunUpdate semantics.
EOF or interrupt at a CLI-owned prompt SHALL exit cleanly without dispatching the
next action or printing a traceback.

The CLI SHALL submit only Start, Answer, Cancel, or Status intent to
ResearchRunExperience. It SHALL NOT parse Command, ToolMessage, human_input
artifact, raw control JSON, pending phase, or graph response correlation. (REC-001)

#### Scenario: Preflight succeeds before a first question
- **WHEN** a user runs make demo-real with usable local real-demo prerequisites
- **THEN** the CLI first confirms what will be checked and that the demo is
  temporary, then asks for a research question before dispatching start

#### Scenario: Missing prerequisite is explained before question entry
- **WHEN** a user runs make demo-real without a required model or web-tool
  prerequisite
- **THEN** the CLI stops at preflight with a specific safe setup explanation and
  next action, creates no research run, and does not ask the user to retry an
  unexplained lifecycle result

#### Scenario: Explicit question preserves automation
- **WHEN** a user runs make demo-real with an explicit non-blank --question
- **THEN** the CLI does not prompt for a question, safely confirms it after
  preflight, and sends the original value only through shared Start intent

#### Scenario: Scripted route has no stdin dependency
- **WHEN** automation runs demo_real.py --scripted with complete real credentials
- **THEN** it completes shared preflight, prints its documented default or explicit
  question and automatic policy, reads no stdin, and renders the terminal or fault
  update returned through ResearchRunExperience

### Requirement: Real CLI renders shared truthful run updates and failures

The real CLI SHALL render only RunUpdate values from ResearchRunExperience. Before
an unresolved dispatch it MAY show the shared Working action and elapsed local time.
It SHALL render completed phase progress only from a verified returned trace delta,
including repeat visits, and SHALL never infer a phase from action, input mode,
option count, or a local fixed sequence. A pending prompt SHALL display its shared
semantic HITL-1/HITL-2 guidance, graph-owned choices, and validation feedback.

For every terminal or fault outcome the CLI SHALL show what happened, the known
phase when available, the safe category/reason level, concrete next action,
retryability or non-retryability, durability truth, and opaque diagnostic reference
when available. It SHALL not stringify dictionaries, exceptions, arbitrary fields,
machine context, credentials, paths, provider bodies, raw model output, or a
terminal-control sequence. It SHALL not display a generic retry-only outcome.

Ctrl-C while a lifecycle action is unresolved SHALL propagate as a local
interruption, close local resources, and not claim that the graph was cancelled.
An explicit shared Cancel result may be displayed only after the graph confirms it.
(REC-002)

#### Scenario: Valid bootstrap-plus-HITL-1 suspension is actionable
- **WHEN** start returns a suspended result whose committed phase is bootstrap and
  whose pending input is HITL-1
- **THEN** the CLI renders completed initialization, a semantic scope prompt, and
  the next answer action rather than rejecting the result or saying only retry

#### Scenario: Blocked run has a useful safe explanation
- **WHEN** a run ends blocked after a classified model, tool, provider, storage, or
  graph failure
- **THEN** the CLI names the safe category and phase, tells the user what to check
  or whether it is not retryable, prints its diagnostic reference, and never leaks
  the underlying raw failure content

#### Scenario: Returned-only waiting is honest
- **WHEN** a dispatch is unresolved and no stream event is available
- **THEN** the CLI shows only local elapsed waiting for the lifecycle result and
  does not update a phase tracker, percentage, or fabricated model/web activity

## ADDED Requirements

### Requirement: Real CLI exposes bounded standalone diagnostics and durability

The CLI SHALL label the all-real entry as a standalone demo, state whether its
current run is same-process or restart-durable when that fact is known, and never
promise recovery after the demo process exits. On a diagnosable failure it SHALL
show a safe opaque reference and documented relative diagnostic-record location.
The CLI SHALL distinguish a preflight failure that created no research record from
a failure in an existing research run. It SHALL not claim that the local record is
a durable product session or report workspace. (REC-003)

#### Scenario: User can retain a safe support reference
- **WHEN** a standalone run fails after its lifecycle begins
- **THEN** the CLI prints an opaque diagnostic reference and bounded local record
  location that an operator can inspect without revealing raw runtime data
