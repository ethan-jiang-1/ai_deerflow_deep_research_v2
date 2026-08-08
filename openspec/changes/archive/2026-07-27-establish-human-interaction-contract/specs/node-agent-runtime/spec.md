> req: NOA-009

## ADDED Requirements

### Requirement: Semantic-intake invocations remain bounded zero-tool node work

The existing runtime node-agent bridge SHALL execute HITL1 semantic-intake requests as
independent zero-tool structured requests under the trusted HITL1 policy. The bridge
SHALL make at most one model call for each request and SHALL not interpret candidates,
retry, route, write checkpoint state, or grant action authority. HITL1 owns the
cross-request three-call semantic budget and recovery. (`NOA-009`)

#### Scenario: Semantic intake cannot receive tools
- **WHEN** HITL1 sends a semantic-intake request after a human reply
- **THEN** the trusted bridge receives `tools_enabled=false` and no tool policy or
  graph action is available to that invocation
