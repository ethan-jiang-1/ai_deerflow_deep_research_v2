> req: WFO-002

## MODIFIED Requirements

### Requirement: Workflow outcome evidence is complete for every discovered model owner

The deterministic workflow evidence inventory SHALL syntax-discover every production
graph-node package that invokes `run_agent`. Each discovered owner SHALL declare its
applicable closed outcome classes, the corresponding Bundle-local Event Journal process facts, and
collected scripted-real-node evidence at its phase seam, plus a collected lifecycle or
work-controller projection assertion. The evidence SHALL prove that a known non-success
outcome reaches the shared Journal with its safe phase/attempt correlation and existing
closed classification, while its existing recovery and terminal authority are unchanged.
The inventory SHALL fail when an owner, applicable outcome class, journal fact,
selector, or projection assertion is missing or stale.

#### Scenario: A new run-agent owner cannot bypass outcome coverage
- **WHEN** production source adds a graph-node package that invokes `run_agent`
- **THEN** deterministic governance fails until that owner has a declared outcome and
  journal-coverage entry with collected evidence

#### Scenario: A success-only workflow case is insufficient
- **WHEN** an owner has a scripted successful workflow case but no assertion for one
  of its declared non-success outcome classes
- **THEN** the outcome coverage validator rejects the owner rather than accepting
  success-path evidence as failure-path conformance

#### Scenario: A terminal projection cannot replace journal evidence
- **WHEN** a discovered model owner has a collected terminal or work-controller
  projection assertion but no correlated Event Journal assertion for a declared
  non-success outcome
- **THEN** deterministic governance rejects the coverage entry even though the
  lifecycle projection itself is present
