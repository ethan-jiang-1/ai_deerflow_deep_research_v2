> req: RDO-006

## ADDED Requirements

### Requirement: Broker binds visible controls under its existing lock

The authorized local session broker SHALL project typed visible controls from the
current pending request and accept a generic control id in its resume seam. Under its
existing namespace lock it SHALL resolve the control only against that current pending
request and its advertised action ids, then pass the resulting typed response through
the existing generic verifier. It SHALL deny stale, unknown, or unadvertised controls
without graph mutation. (`RDO-006`)

#### Scenario: Reopened stale control remains unavailable
- **WHEN** a workbench submits a previously displayed control after another response
  changed the pending request
- **THEN** the broker returns its bounded unavailable result and does not invoke a
  graph node
