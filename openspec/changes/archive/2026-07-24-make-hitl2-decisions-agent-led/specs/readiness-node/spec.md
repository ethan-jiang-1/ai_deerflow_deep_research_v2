> req: REA-001, REA-005

## MODIFIED Requirements

### Requirement: Hard checks verify citation availability, provenance, and HITL2 consumption

The readiness node SHALL run deterministic hard checks on pre-existing state: accepted
submissions are non-empty (`check_citation_availability`) and all refs are canonical
submission-ledger hashes (`check_provenance`). It SHALL NOT require a consumed HITL2
request: an autonomous HITL2 continuation is neither missing evidence nor missing user
authority. Failures SHALL be collected as `HardRuleFailure` tuples. Structural evidence
or provenance failures SHALL route to `exhausted` with `BLOCKED` terminal status.

#### Scenario: Autonomous continuation is not a readiness failure
- **WHEN** accepted evidence and provenance are valid but no HITL2 request was consumed
- **THEN** readiness does not produce `hitl2_not_consumed` and may continue to its
  critic and normal route determination
