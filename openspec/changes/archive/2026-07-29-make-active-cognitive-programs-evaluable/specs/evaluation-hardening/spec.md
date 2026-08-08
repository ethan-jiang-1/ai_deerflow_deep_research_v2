> req: EVH-017

## ADDED Requirements

### Requirement: Cognitive-program evidence uses explicit proof classification

Every active-branch ledger evidence link SHALL classify its referenced existing or new
central claim as `cognitive-program`, `deterministic-guardrail`, `wiring`, or
`obsolete-duplicate` before consolidation. The ledger SHALL retain exact branch
identity, source seam, and proof role. Every row SHALL retain distinct deterministic
composition, feedback-disposition, and guardrail/admission proof roles plus an
evaluation disposition. An `obsolete-duplicate` link SHALL remain reviewable but
SHALL NOT close a required proof role, justify test deletion, or be inferred from an
aggregate outcome.

#### Scenario: Existing proof is classified
- **WHEN** a direct branch's evidence is reviewed
- **THEN** its class, proof role, branch identity, and any required judgment-evaluation
  disposition are explicit
