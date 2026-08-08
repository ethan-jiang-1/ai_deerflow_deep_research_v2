> req: WSN-007

## ADDED Requirements

### Requirement: Wave2 synthesis uses only accepted evidence in its selected Run Bundle

Wave2 SHALL obtain accepted evidence, synthesis State, gaps, and materialized content
only through the selected runtime-bound Run Bundle interfaces. It SHALL not derive a
research identity, use an external checkpoint/session as a content source, or write
synthesis artifacts outside that Bundle. Bundle loss SHALL prevent further synthesis
materialization for that Run. (`WSN-007`)

#### Scenario: Synthesis cannot materialize into a replacement root
- **WHEN** the selected Bundle becomes unavailable after a synthesis candidate is produced
- **THEN** Wave2 does not publish that candidate to a new directory or external lifecycle store
