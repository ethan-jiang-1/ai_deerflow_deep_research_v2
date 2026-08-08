## ADDED Requirements

### Requirement: Real model workflow coverage proves failure-outcome conformance

The deterministic workflow-conformance suite SHALL maintain a syntax-discovered
inventory of every production graph-node package that invokes `run_agent`. In
addition to success-path workflow evidence, each owner SHALL have executable
scripted-real-node cases for every declared applicable non-success outcome and an
assertion at the owning lifecycle or work-controller projection seam. Inventory and
test-asset governance SHALL fail closed on a missing owner, missing declared class,
uncollected selector, stale mapping, or a success-only substitute.

#### Scenario: A missing timeout case is detected for topic planning
- **WHEN** topic planning remains a discovered run-agent owner but its declared
  provider-timeout outcome case is removed or uncollected
- **THEN** deterministic workflow governance fails with the owner and missing
  outcome class before a change can claim complete workflow coverage

#### Scenario: An empty detector cannot pass as enforcement
- **WHEN** the outcome inventory is evaluated against an empty, relocated, or
  mis-scoped production-node root
- **THEN** a focused detector smoke test fails with the known missing owner rather
  than accepting an empty inventory
