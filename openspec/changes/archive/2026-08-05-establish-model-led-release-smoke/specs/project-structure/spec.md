> req: PRS-016

## ADDED Requirements

### Requirement: Research Confirmation has one registered downstream domain surface

The Research Confirmation deterministic admission boundary and its focused domain
tests SHALL occupy registered paths under the existing Deep Research downstream
domain and test roots. The structure registry and generated module locator SHALL
remain synchronized with those paths, preserve the existing ownership-layer import
direction, and introduce no `backend/` or `frontend/` path. (`PRS-016`)

#### Scenario: The confirmation boundary remains a pure registered domain module
- **WHEN** architecture governance validates the registered project structure after
  the Research Confirmation capability is added
- **THEN** it finds the registered downstream module and focused tests, rejects an
  unregistered or upstream placement, and preserves the existing domain-to-graph and
  domain-to-runtime dependency boundary
