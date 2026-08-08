## ADDED Requirements

### Requirement: Phase execution policies are named and independently bounded

The runtime SHALL bind each distinct direct model-calling phase to a named
`ExecutionPolicy` whose model-call, token, tool, and wall-time bounds are explicit.
Topic planning SHALL use a policy distinct from HITL1 with zero tool authority, one
model call per invocation, and a 60-second wall-time ceiling. A policy timeout SHALL
continue to return the existing safe `provider.timeout` result shape; policy
separation SHALL not alter cancellation handling or grant retry authority to the
bridge.

#### Scenario: Topic planning no longer inherits the HITL1 wall-time budget
- **WHEN** real HITL1 and real topic planning are assembled in one recipe
- **THEN** they receive distinct named policies and a topic-planning invocation can
  run until its own 60-second ceiling without changing HITL1's configured bound

#### Scenario: A phase budget expiry remains classified
- **WHEN** a phase invocation exhausts its wall-time budget
- **THEN** the bridge returns a safe non-success result with the bounded timeout
  classification and no raw exception text for the owning phase to handle
