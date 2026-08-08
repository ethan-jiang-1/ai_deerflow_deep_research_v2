> req: REG-012, REG-013

## ADDED Requirements

### Requirement: Pending interrupt projection never creates a second control authority

The LangGraph pending interrupt task remains the sole authority for the currently
awaited human request. A lifecycle projection may expose a bounded pending-input
view derived from that task for presentation, but the view SHALL not be written into
ResearchState, a bundle status file, a second checkpoint, an event journal, or a
UI-local phase cursor. Its request id, phase, generation, and mode must agree with
the one pending interrupt and the existing human-input artifact before a caller can
present or answer it.

The checkpointed phase remains the sole committed phase fact even when it lags the
pending interrupt because interruption occurs before node_update. Trace, status,
and terminal projection SHALL report that distinction rather than silently
rewriting phase or treating the legal suspension as corrupt. (REG-012)

#### Scenario: First interruption has two non-conflicting facts
- **WHEN** HITL-1 interrupts while bootstrap is the latest completed checkpoint
  phase
- **THEN** bootstrap remains the committed phase, HITL-1 is the pending
  interaction, and no new ResearchState field or bundle phase/status file is
  introduced to make those facts appear identical

### Requirement: Terminal incidents remain compact, safe, and status-visible

When a node or runtime source directly classifies a causal failure that leads to a
blocked terminal outcome, ResearchState MAY retain one bounded latest-incident
projection containing only a closed safe category, known phase, certainty, opaque
diagnostic reference, and schema version. Its writer, reader, reducer, size bound,
and compatibility default SHALL be declared explicitly. The projection SHALL be
monotonic for its terminal result and surfaced by status without reading a separate
diagnostic or state file.

The compact incident is explanatory metadata, not a route, phase cursor, pending
request, evidence record, or replacement for raw diagnostics. It SHALL never
contain exception message/body, stack trace, user text, provider response, URL,
credential, host path, sandbox handle, or arbitrary error dictionary. (REG-013)

#### Scenario: Blocked status keeps a safe cause after restart
- **WHEN** a classified real HITL-1 model configuration failure routes to blocked
  and the checkpoint provider is reopened in a fresh process
- **THEN** status reports the same compact category and opaque diagnostic reference
  together with the terminal lifecycle result, without re-running a node or
  recovering raw exception data
