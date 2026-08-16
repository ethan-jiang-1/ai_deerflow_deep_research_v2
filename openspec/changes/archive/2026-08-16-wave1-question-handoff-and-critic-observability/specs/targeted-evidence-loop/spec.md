> req: TEL-007

## Purpose

Close the wrapper red line that makes any routed gap work fail with
`work_unit_gate_view_inconsistent` before the targeted evidence node can run.

## ADDED Requirements

### Requirement: Targeted evidence node conforms to the work-unit gate-view protocol

The real targeted_evidence node SHALL return the reconciled `WorkUnitGateView` under
the reserved key on every visit. A visit with a non-empty gap projection SHALL
return the view built by its existing shared work-unit component; a gap-less visit
SHALL return the canonical empty drained view (no planned work, nothing to
reconcile) because the shared component's plan bound requires at least one intent.
It SHALL NOT derive routing authority from gap presence or absence, SHALL NOT
raise `work_unit_gate_view_inconsistent` for a visit routed with a non-empty or an
empty `unresolved_gaps` projection, and SHALL NOT build a view that claims planned
or accepted work for a gap-less visit. The reserved key SHALL follow the existing
work-unit kernel contract: the wrapper pops and type-checks it, and it SHALL never be
a `ResearchState` field or reach checkpoint serialization.

#### Scenario: A gap visit returns the reconciled view
- **WHEN** the Wave2 gate routes `evidence_needed` with non-empty `unresolved_gaps`
- **THEN** the targeted_evidence node returns the component-built `WorkUnitGateView` under the reserved key and the wrapper admits it without raising `work_unit_gate_view_inconsistent`

#### Scenario: An empty-gap visit returns a drained view
- **WHEN** targeted_evidence runs with an empty gap projection
- **THEN** the node returns the canonical empty drained `WorkUnitGateView` with no planned work and the wrapper admits it without raising `work_unit_gate_view_inconsistent`

#### Scenario: The reserved key never becomes checkpoint state
- **WHEN** the wrapper extracts the reserved key from the targeted_evidence result
- **THEN** the view is injected only into the in-memory gate mapping and is omitted from the final state update, matching the existing work-unit kernel contract
