## ADDED Requirements

### Requirement: Known invocation failures remain phase-owned lifecycle facts

When a direct real phase terminally blocks after a known normalized invocation
failure, its checkpoint update SHALL retain a compact `latest_incident` carrying the
same safe category, phase, certainty, safe diagnostic reference, and bounded
recovery facts when observed. When a worker phase fails, its work-unit controller
SHALL retain the corresponding closed attempt/aggregate facts and no node may create
a competing terminal authority. Generic `research.blocked` remains a route outcome,
not a replacement for a known incident.

#### Scenario: Topic planning blocks after exhausted provider recovery
- **WHEN** topic planning exhausts its declared provider-recovery bound
- **THEN** the blocked checkpoint retains a provider terminal incident with the
  topic-planning phase and the route remains the existing terminal blocked route

#### Scenario: Worker exhaustion does not create a second controller
- **WHEN** a Wave worker produces a classified invocation failure and its existing
  controller exhausts permitted work attempts
- **THEN** the controller-derived work outcome supplies the terminal diagnosis and
  the worker does not independently advance, resume, or rewrite graph control state
