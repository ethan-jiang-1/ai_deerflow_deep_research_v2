> req: REG-014

## ADDED Requirements

### Requirement: Run-session records remain derived lifecycle projections

Run-session manifests and lifecycle traces SHALL be written only from record-bearing
validated lifecycle/checkpoint facts and SHALL never be read by graph nodes, reducers,
lifecycle transition validation, pending-interrupt correlation, or evidence gates.
They SHALL not add a `ResearchState` phase, pending request, route, or checkpoint
authority. A retained bundle may be inspected after process exit even when the
underlying provider honestly reports same-process-only durability. A session store MAY
create only `manifest.json` and `diagnostics/` for a full-fake run whose graph has not
materialized content; it SHALL not fabricate bootstrap/request, work, evidence,
synthesis, review, or final artifacts.

#### Scenario: Inspecting a retained bundle cannot advance a graph
- **WHEN** a developer reads a manifest or lifecycle trace for a suspended run
- **THEN** no checkpoint mutation, node invocation, pending-interrupt consumption, or route evaluation occurs

#### Scenario: Session metadata does not impersonate bootstrap output
- **WHEN** full-fake session observation creates an inspectable root after the first
  record-bearing returned lifecycle result
- **THEN** the root contains only session metadata/diagnostics and graph routing does
  not treat it as a bootstrap marker or research content artifact
