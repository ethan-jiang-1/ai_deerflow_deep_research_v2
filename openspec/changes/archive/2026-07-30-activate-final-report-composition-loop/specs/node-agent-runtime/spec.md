> req: NOA-013

## ADDED Requirements

### Requirement: Final report composition uses an independently bounded zero-tool bridge

The runtime SHALL assemble the final-delivery composer through a named dedicated
zero-tool execution policy with explicit one-invocation, token, result-size, and
wall-time bounds. Policy, provider, timeout, cancellation, and structured-output
failure SHALL retain the runtime's existing closed non-success result and SHALL not
grant retry, publication, route, or lifecycle authority to the bridge. (`NOA-013`)

#### Scenario: Composer cannot inherit another node's tool posture
- **WHEN** a real final-delivery recipe resolves its composer bridge
- **THEN** it receives its dedicated forbidden-tool policy and a failure produces no
  model-owned retry, artifact, route, or terminal result
