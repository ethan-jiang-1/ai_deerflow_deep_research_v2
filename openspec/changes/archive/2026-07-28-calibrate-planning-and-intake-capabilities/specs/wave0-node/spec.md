> req: WAN-007

## ADDED Requirements

### Requirement: Wave0 source intake has bounded retrieval and honest degradation evidence

The existing Wave0 source-intake and repair capabilities SHALL retain distinct
deterministic real-node evidence. A normal worker SHALL use only its existing
permitted retrieval policy, make at least one and at most three tool calls, and submit
only contract-valid source candidates through the existing validator/controller/ledger
path. A source-floor or retrieval shortfall SHALL retain the existing failed or
degraded outcome and SHALL not be represented as fetched or accepted coverage. Repair
SHALL expose no model-visible tool and SHALL not invent a URL, title, source metadata,
or fact absent from its bounded draft and retained observations. (`WAN-007`)

#### Scenario: Bounded retrieval admits only validated sources
- **WHEN** a scripted real Wave0 worker completes permitted retrieval calls within its
  1--3 bound
- **THEN** the existing validation and ledger owners admit only canonical,
  contract-valid candidates and the model receives no ledger or route authority

#### Scenario: Retrieval shortfall remains honest
- **WHEN** the scripted worker misses its retrieval/source-floor condition or its
  repair draft lacks a source field
- **THEN** the existing controller records only its legal failed or degraded outcome
  and no fabricated fetched source or accepted coverage is produced
