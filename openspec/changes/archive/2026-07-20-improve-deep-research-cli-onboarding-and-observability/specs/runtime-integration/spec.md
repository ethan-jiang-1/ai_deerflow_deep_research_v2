> req: RUI-007

## ADDED Requirements

### Requirement: Reflected lifecycle results project pending interaction separately from checkpoint phase

The reflected Deep Research lifecycle SHALL preserve DeepResearchControlResult.phase
as the last committed checkpoint phase. A suspended result SHALL additionally carry a
bounded pending_input projection derived from the validated
PendingResearchInterrupt. The projection SHALL include only its own schema version,
request id, pending phase, generation, and input mode. It SHALL not include a
suspension cursor, a host path, raw prompt context, exception text, arbitrary
checkpoint data, or caller authority.

The same suspended status read SHALL include pending_input so a client can explain
the current required action without inferring it from phase. A suspended Command
shall retain its existing human_input artifact as the graph-owned full request.
Projection shall fail closed when the checkpoint says suspended without exactly one
valid interrupt, or terminal with any interrupt. It SHALL not alter the checkpoint,
insert pending state into ResearchState, or change resume/cancel authority.
(RUI-007)

#### Scenario: Phase lag is projected instead of overwritten
- **WHEN** a real HITL node interrupts before a node transition commits and the
  checkpoint phase remains bootstrap
- **THEN** the lifecycle result keeps phase bootstrap and carries
  pending_input.pending_phase hitl1 from the interrupt descriptor

#### Scenario: Status can identify the requested action
- **WHEN** status reads the same suspended run after its original Command delivery
- **THEN** it returns the bounded pending-input projection without invoking a node,
  changing a checkpoint, or exposing the full prompt context
