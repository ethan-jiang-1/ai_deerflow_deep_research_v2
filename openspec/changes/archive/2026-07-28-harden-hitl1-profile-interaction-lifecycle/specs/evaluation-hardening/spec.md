> req: EVH-014

## ADDED Requirements

### Requirement: HITL1 interaction lifecycle acceptance has independent evidence claims

Test-owned evidence SHALL register two distinct collected central claims for the
HITL1 profile-interaction lifecycle: one scripted real-node/fake-capabilities claim
covering confirmation, source-constrained revision, question, and ambiguity; and one
different claim covering exhausted semantic failure fallback. Both claims SHALL assert
the deterministic owner boundary, correlated lifecycle outcome, preserved/updated
proposal state as applicable, and the human-visible control/feedback outcome. They
SHALL NOT claim live model quality, research-result quality, capability migration, or
an aggregate pytest count as lifecycle acceptance evidence. (`EVH-014`)

#### Scenario: Success and fallback journeys have separate collected proof
- **WHEN** lifecycle evidence is collected for this change
- **THEN** two unique central selectors independently prove the accepted interaction
  journey and the exhausted fallback journey at the real HITL1 node seam

#### Scenario: Fake capabilities do not become quality evidence
- **WHEN** either lifecycle claim runs with scripted fake capability results
- **THEN** its recorded authenticity is limited to deterministic real-node/fake-capability
  lifecycle behavior and does not assert live model or research quality
