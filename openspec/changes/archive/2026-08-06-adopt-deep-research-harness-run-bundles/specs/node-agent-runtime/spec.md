> req: NOA-007, NOA-008, NOA-014

## ADDED Requirements

### Requirement: Node-agent execution receives bound Bundle context without lifecycle authority

The runtime-owned node-agent bridge SHALL receive only ephemeral, runtime-bound context
for the selected Run Bundle. It MAY use contained artifact/evidence interfaces granted
by the parent graph, but SHALL not derive `bundle_id`, construct a Bundle path, select a
checkpoint, persist lifecycle State, or make a Bundle available/unavailable decision.
The parent Bundle lifecycle/graph control boundary remains the sole owner of those
facts. (`NOA-014`)

#### Scenario: Agent-facing context cannot redirect a Run Bundle
- **WHEN** a model/tool-facing node-agent request includes path-like or identity-like content
- **THEN** the bridge treats it as untrusted data and no Bundle selection, State write, or lifecycle action changes

## MODIFIED Requirements

### Requirement: Node-agent failures retain a closed causal category for the parent graph

The existing bounded provider classification, redaction, cancellation, and graph-owned
failure-routing guarantees remain unchanged. The direct runtime dependency declaration
for `httpx>=0.28,<0.29` and `openai>=2.45,<3`, with matching lock metadata, SHALL live
under `deep_research_harness/`; the project-structure import policy continues to admit
those namespaces only for the raw-binding bridge. This root migration SHALL not make a
node-agent bridge a Bundle selector, State writer, checkpoint authority, or recovery
path. (`NOA-007`, `NOA-008`, `PRS-002`)

#### Scenario: Node-agent dependency metadata follows the Harness root
- **WHEN** structural validation checks the direct bridge dependencies after the move
- **THEN** it finds their declaration and lock metadata beneath
  `deep_research_harness/` without widening node-agent lifecycle authority
