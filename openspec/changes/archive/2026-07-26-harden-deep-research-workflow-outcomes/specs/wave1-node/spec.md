## ADDED Requirements

### Requirement: Wave1 retains classified invocation causes through work-unit failure

Wave1 SHALL normalize every non-successful worker or repair invocation before it
reaches the existing work-unit controller. It SHALL retain the applicable closed
worker category and safe provider observation when known, and it SHALL leave retry,
aggregation, gate routing, and terminal projection with the existing controller.

#### Scenario: A Wave1 repair invocation fails with a known provider error
- **WHEN** a Wave1 structured-output repair invocation returns a safe non-success
  provider result
- **THEN** the worker emits a classified work-attempt failure preserving that safe
  cause rather than a generic `wave1_worker_repair_failed` error
