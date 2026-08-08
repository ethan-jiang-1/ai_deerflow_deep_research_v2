## MODIFIED Requirements

### Requirement: One runtime Module owns lifecycle-to-presentation interpretation

The agent project SHALL provide one runtime-owned `ResearchRunExperience` Module and
frozen domain contracts for the standalone Deep Research run experience. Its public
Interface SHALL be `preflight()` returning `ReadinessReport` and
`handle(RunIntent, observer=None)` returning `RunUpdate`. `RunIntent` SHALL be a
closed set of `Start`, `Answer`, `SelectControl`, `Cancel`, and `Status`. `Answer`
SHALL carry only the correlated text, advertised action, or advertised option response
shape of the current prompt. `RunUpdate` SHALL be a closed set of `Ready`, `Working`,
`AwaitingInput`, `Terminal`, and `Fault` with only safe serializable values.

The Module SHALL own lifecycle transport invocation, `Command`/`ToolMessage`/artifact
parsing, control/request correlation, fresh response construction, ordered trace
validation, phase projection, safe prompt construction, failure classification, and
diagnostic publication. It SHALL preserve ordinary `CancelledError` propagation.
CLI and TUI SHALL be presentation adapters: they may render `RunUpdate` and submit
`RunIntent` but SHALL NOT decode a lifecycle wire result, infer a HITL phase, compare
trace prefixes, construct a graph response envelope, or own a retry budget.

The Module is process-local run presentation, not a durable Session abstraction. It
SHALL expose the lifecycle durability truth and SHALL NOT create a session directory,
phase cursor, checkpoint state copy, or alternative graph authority. The existing
research bundle is the future session root, not this Module's state store. (`RER-001`)

#### Scenario: Both entry points receive the same pending prompt
- **WHEN** equivalent CLI and TUI adapters handle one returned HITL-1 or HITL-2 lifecycle result
- **THEN** both receive the same `AwaitingInput` phase, request id, safe prompt, options, and next action through `RunUpdate` without either adapter inspecting `Command`, `ToolMessage`, artifact JSON, action, or option count

#### Scenario: Unknown wire data fails at the shared seam
- **WHEN** a lifecycle result is malformed, has an unknown closed enum, has a divergent trace, or has inconsistent control/artifact correlation
- **THEN** `ResearchRunExperience` returns a safe `Fault` with a stable protocol category and no adapter is allowed to guess a continuation

### Requirement: Public lifecycle projection distinguishes committed state from pending input

`DeepResearchControlResult` SHALL retain phase as the last committed checkpoint
logical phase. For a suspended lifecycle it SHALL additionally expose an optional
`pending_input` projection with its own schema version, request id, pending phase,
generation, and input mode. The projection SHALL be derived only from the one
validated `PendingResearchInterrupt`, SHALL omit suspension cursor, path, raw context,
exception data, and arbitrary state, and SHALL be available on suspended status
results as well as suspended `Command` results.

The existing `human_input` artifact remains the full graph-owned prompt transport.
`ResearchRunExperience` SHALL require the projection and artifact to agree on request
id, generation, pending phase, and mode before it presents `AwaitingInput`. It SHALL
present a HITL1 `CHOICE` prompt only as the explicit bounded supported-language option
set and submit only its current advertised option through the correlated response
shape. The pending projection SHALL NOT be written into `ResearchState`, treated as a
second checkpoint, or used to override graph transition authority. (`RER-002`)

#### Scenario: First real HITL-1 suspension is presented correctly
- **WHEN** real HITL-1 interrupts before its `node_update` and the checkpoint phase is `bootstrap` while `PendingResearchInterrupt.pending_phase` is `hitl1`
- **THEN** the control result preserves checkpoint phase `bootstrap`, projects `pending_input.pending_phase` `hitl1`, and the shared experience presents an `AwaitingInput` HITL-1 prompt rather than a generic retry or inconsistent-result failure

#### Scenario: HITL1 language choice is rendered and correlated
- **WHEN** a real HITL-1 interrupt is an explicit supported-language choice
- **THEN** the shared experience renders exactly its typed language options and submits only the selected current option with the pending request id

#### Scenario: Suspended status remains interpretable
- **WHEN** status reads a suspended run whose committed phase predates its pending interrupt
- **THEN** it reports both the committed phase and the pending-input projection so a caller can accurately explain completed work and the input currently awaited
