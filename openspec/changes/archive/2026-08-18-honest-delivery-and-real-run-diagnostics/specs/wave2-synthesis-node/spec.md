## MODIFIED Requirements

### Requirement: Gate validates finding references

The real Wave2 gate SHALL validate that every finding reference is backed by an
accepted submission. Dangling or unbacked references SHALL fail. It SHALL
additionally consume the typed preview derived from validated synthesis output,
write the bounded searchable gap ids to the existing gate-owned `unresolved_gaps`
control field, and route `evidence_needed` when that projection is non-empty and
repair budget remains. A later successful synthesis with no searchable gap SHALL
clear the projection and route `pass`. Repeated unresolved semantic gaps SHALL use
the existing gate budget/fatigue contract: while budget remains they route
`evidence_needed`, and at budget exhaustion the gate SHALL declare
`degraded_pass_on_exhaustion` so the first exhaustion degrades to a bounded honest
`pass` (`degraded=true`, same route label as `pass`) that leaves
`unresolved_gaps` intact for downstream disclosure; a repeated exhaustion of the
same phase after that degradation SHALL route `exhausted` to the typed blocked
terminal exactly as before. (`WSN-004`)

#### Scenario: Dangling reference fails gate
- **WHEN** a finding references a source not in accepted submissions
- **THEN** the gate routes repair

#### Scenario: Searchable gap routes targeted evidence
- **WHEN** validated Wave2 output produces a typed preview with one or more searchable gap ids
- **THEN** the real gate records only those ids in `unresolved_gaps` and routes `evidence_needed`

#### Scenario: No searchable gap clears prior projection
- **WHEN** a later validated Wave2 output contains no `search_required=true` gap
- **THEN** the real gate clears `unresolved_gaps` and routes `pass`

#### Scenario: Repeated searchable gap exhausts convergence budget
- **WHEN** targeted evidence returns through synthesis but the same searchable gap remains after the Wave2 repair budget is spent
- **THEN** the first exhausted evaluation degrades to the honest `pass` route, and
  the next exhausted evaluation of the same gaps routes `exhausted` so the graph
  reaches the typed blocked terminal

#### Scenario: Fabricated checkpoint gap cannot route
- **WHEN** checkpoint input contains an unvalidated gap body or id that is absent from the current typed Wave2 gate preview
- **THEN** the real gate ignores it as routing authority

#### Scenario: First budget exhaustion degrades honestly instead of blocking
- **WHEN** the wave2 gate exhausts its evidence budget with only searchable-gap
  failures remaining and the phase has not degraded before
- **THEN** the gate passes degraded with the normal `pass` route label,
  `unresolved_gaps` still names the unresolved searchable gap ids, and no blocked
  terminal or incident is produced

#### Scenario: Repeated exhaustion after degradation blocks
- **WHEN** wave2 synthesis is re-evaluated at exhausted budget after the phase
  already produced an exhaustion-degraded pass and searchable gaps remain
- **THEN** the gate routes `exhausted` to the typed blocked terminal with the
  existing incident semantics
