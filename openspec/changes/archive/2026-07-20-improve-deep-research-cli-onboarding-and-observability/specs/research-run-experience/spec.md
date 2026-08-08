> req: RER-001, RER-002, RER-003, RER-004, RER-005

## ADDED Requirements

### Requirement: One runtime Module owns lifecycle-to-presentation interpretation

The agent project SHALL provide one runtime-owned ResearchRunExperience Module and
frozen domain contracts for the standalone Deep Research run experience. Its public
Interface SHALL be preflight() returning ReadinessReport and handle(RunIntent,
observer=None) returning RunUpdate. RunIntent SHALL be a closed set of Start,
Answer, Cancel, and Status. RunUpdate SHALL be a closed set of Ready, Working,
AwaitingInput, Terminal, and Fault with only safe serializable values.

The Module SHALL own lifecycle transport invocation, Command/ToolMessage/artifact
parsing, control/request correlation, fresh response construction, ordered trace
validation, phase projection, safe prompt construction, failure classification,
and diagnostic publication. It SHALL preserve ordinary CancelledError propagation.
CLI and TUI SHALL be presentation adapters: they may render RunUpdate and submit
RunIntent but SHALL NOT decode a lifecycle wire result, infer a HITL phase, compare
trace prefixes, construct a graph response envelope, or own a retry budget.

The Module is process-local run presentation, not a durable Session abstraction.
It SHALL expose the lifecycle durability truth and SHALL NOT create a session
directory, phase cursor, checkpoint state copy, or alternative graph authority.
The existing research bundle is the future session root, not this Module's state
store. (RER-001)

#### Scenario: Both entry points receive the same pending prompt
- **WHEN** equivalent CLI and TUI adapters handle one returned HITL-1 or HITL-2
  lifecycle result
- **THEN** both receive the same AwaitingInput phase, request id, safe prompt,
  options, and next action through RunUpdate without either adapter inspecting
  Command, ToolMessage, artifact JSON, action, or option count

#### Scenario: Unknown wire data fails at the shared seam
- **WHEN** a lifecycle result is malformed, has an unknown closed enum, has a
  divergent trace, or has inconsistent control/artifact correlation
- **THEN** ResearchRunExperience returns a safe Fault with a stable protocol
  category and no adapter is allowed to guess a continuation

### Requirement: Public lifecycle projection distinguishes committed state from pending input

DeepResearchControlResult SHALL retain phase as the last committed checkpoint
logical phase. For a suspended lifecycle it SHALL additionally expose an optional
pending_input projection with its own schema version, request id, pending_phase,
generation, and input mode. The projection SHALL be derived only from the one
validated PendingResearchInterrupt, SHALL omit suspension cursor, path, raw
context, exception data, and arbitrary state, and SHALL be available on suspended
status results as well as suspended Command results.

The existing human_input artifact remains the full graph-owned prompt transport.
ResearchRunExperience SHALL require the projection and artifact to agree on
request id, generation, pending phase, and mode before it presents AwaitingInput.
The pending projection SHALL NOT be written into ResearchState, treated as a
second checkpoint, or used to override graph transition authority. (RER-002)

#### Scenario: First real HITL-1 suspension is presented correctly
- **WHEN** real HITL-1 interrupts before its node_update and the checkpoint phase
  is bootstrap while PendingResearchInterrupt.pending_phase is hitl1
- **THEN** the control result preserves checkpoint phase bootstrap, projects
  pending_input.pending_phase hitl1, and the shared experience presents an
  AwaitingInput HITL-1 prompt rather than a generic retry or inconsistent-result
  failure

#### Scenario: Suspended status remains interpretable
- **WHEN** status reads a suspended run whose committed phase predates its pending
  interrupt
- **THEN** it reports both the committed phase and the pending-input projection so
  a caller can accurately explain completed work and the input currently awaited

### Requirement: Failures are safe, categorized, and diagnosable

The runtime SHALL classify failures at their source into a closed run-failure
registry covering configuration, provider authentication/unavailability/timeout,
tool availability/execution, input, persistence, checkpoint, graph-blocked,
protocol, local interruption, and internal-unexpected failures. A user-visible
Fault or terminal outcome SHALL identify the safe category, known phase when
available, certainty, a concrete next action, retryability, and an opaque
diagnostic reference when a record exists. It SHALL never print only "retry".

Unknown exceptions SHALL become internal-unexpected and SHALL NOT be mislabelled as
checkpoint-inconsistent. A graph route such as gate_blocked may remain the terminal
route but SHALL retain its safe causal incident where one is directly known. A
terminal checkpoint MAY carry only compact safe incident metadata needed by a
later status read; it SHALL not carry raw exception text, credentials, provider
content, user text, URLs, paths, stack traces, or diagnostic payloads.

The standalone demo SHALL publish one bounded redacted diagnostic record outside
its disposable temporary workspace when a record is warranted. The record shall
contain only an opaque reference, time, action/phase, closed category, certainty,
and a non-reversible fingerprint. It SHALL have a documented relative location
and retention rule, and it SHALL explicitly distinguish preflight failure before a
research record exists from failure inside an existing run. (RER-003)

#### Scenario: Model configuration failure is actionable without leaking configuration
- **WHEN** the real brief cannot start because no usable model configuration is
  available
- **THEN** the user sees that model configuration is missing, why it is required,
  the next configuration action, and a diagnostic reference; no key name value,
  path, exception body, provider request, or raw stack is displayed

#### Scenario: Unknown implementation failure is not falsified
- **WHEN** an unrecognized exception escapes a lifecycle source
- **THEN** the outcome category is internal-unexpected with unknown certainty and
  a safe support action, not checkpoint-inconsistent or a false provider diagnosis

### Requirement: First-run prompts and waiting states explain user intent truthfully

The shared run experience SHALL perform non-network preflight before an interactive
question is collected or graph construction begins. It SHALL report the selected
real/fake mode, model and web-tool readiness, local environment problems, and the
temporary/non-resumable nature of the standalone demo in bounded user language.

HITL-1 presentation SHALL decode only the recognized versioned research-brief
context into goal, proposed scope, missing information, supported values, and a
concise answer example. Malformed or unknown context SHALL use a safe generic
scope request and SHALL not print machine JSON. HITL-2 presentation SHALL render
the graph-owned advertised decisions with a bounded explanation of each
consequence while leaving all decision validation to the graph.

Working state SHALL show the dispatch action, elapsed local time, and actual
observed activity only. With no stream writer it SHALL identify delivery as
returned_only and say it is waiting for the lifecycle result. It SHALL not emit a
percentage, infer a node phase, or claim model/web progress before a valid returned
event or result proves it. (RER-004)

#### Scenario: Missing prerequisite stops before the user supplies a question
- **WHEN** a real standalone demo lacks a required model or web-search prerequisite
- **THEN** preflight identifies the missing prerequisite, its purpose, and the next
  action before the question prompt, model request, or graph construction

#### Scenario: HITL-1 is not a truncated machine object
- **WHEN** a valid versioned HITL-1 brief is returned
- **THEN** the user sees a semantic research-scope prompt with the known proposed
  values and missing fields rather than a truncated JSON line or an internal
  lifecycle/gate label

#### Scenario: Waiting makes no false progress claim
- **WHEN** a lifecycle dispatch has begun but no graph event or result has been
  observed
- **THEN** the entry point shows only elapsed local waiting and does not advance
  its pipeline tracker or claim that any graph node completed

### Requirement: Verification protects the production-shaped first interaction

The change SHALL include deterministic tests at the run-experience Interface and a
SCRIPTED_REAL_WORKFLOW using the real bootstrap, real HITL-1, interrupt,
checkpointer, and reflected lifecycle projection with replayed external
dependencies. It SHALL cover first HITL-1 suspension, HITL-1 follow-up, HITL-2,
status, trace repetition/divergence, malformed wire values, source failure
categories, redaction, diagnostic records, cancellation outcome distinction, and
CLI/TUI shared adapter fixtures.

A stubbed top-level lifecycle result may supplement adapter tests but SHALL NOT be
the only proof of the first real suspension. Credentialed provider/tool acceptance
is supplemental live evidence and SHALL preserve only redacted category/reference
data. (RER-005)

#### Scenario: A favorable stub cannot hide the phase-lag regression
- **WHEN** a test suite exercises the standalone first interaction
- **THEN** at least one deterministic collected test reaches the production
  interrupt projection with checkpoint phase bootstrap and pending phase hitl1,
  so a fixture that manually sets phase hitl1 cannot be the sole regression proof
