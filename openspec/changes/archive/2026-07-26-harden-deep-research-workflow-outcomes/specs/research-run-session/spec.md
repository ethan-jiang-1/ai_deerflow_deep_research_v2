## ADDED Requirements

### Requirement: Retained session diagnostics project classified workflow outcomes

For a record-bearing terminal lifecycle result, the retained session/event journal
SHALL project the checkpointed terminal incident or controller-derived worker failure
category, phase, safe diagnostic reference, and bounded recovery chronology when
available. The journal SHALL retain no raw exception, provider body, or prompt text,
and session inspection SHALL remain read-only rather than becoming a retry or resume
controller.

#### Scenario: A direct provider failure is inspectable without raw provider data
- **WHEN** a terminal topic-planning provider failure creates a retained run bundle
- **THEN** its session diagnostics contain the safe category, phase, diagnostic
  reference, and observed recovery disposition but not the raw timeout exception or
  provider response

#### Scenario: Inspection cannot alter a classified outcome
- **WHEN** an operator inspects a retained terminal session with workflow failure
  facts
- **THEN** inspection returns only the derived observation and cannot start a retry,
  resume the graph, or change the terminal incident
