> req: NOA-011

## ADDED Requirements

### Requirement: Runtime execution admits capability posture before model-visible work

For a request carrying a validated `NodeAgentCapabilityRef`, the runtime node-agent
bridge SHALL receive the renderer's validated capability projection and compare its
closed tool posture with the request window and the selected `ExecutionPolicy` before
constructing a model-visible agent. A `forbidden` posture SHALL require
`tools_enabled=false`, no request call requirement, and no model-visible tool. A
`required` posture SHALL require `tools_enabled=true`, `minimum_tool_calls >= 1`, a
non-empty request call limit, and a non-empty capability name set contained by
`ExecutionPolicy.allowed_tool_names`. The bridge SHALL expose only the intersection
of that set with configured actual tools; at least one permitted actual tool is
required, but Wave0's alternative retrieval names do not require every configured
provider. Existing middleware remains the owner of path, sandbox, budget,
cancellation, and dispatch enforcement. An unknown capability, empty permitted-tool
intersection, forbidden visible tool, or posture/window disagreement SHALL fail before
`build_node_agent` or tool dispatch. The bridge SHALL NOT interpret capability policy
as a graph route, state write, retry, or arbitrary full-system-prompt override.
(`NOA-011`)

#### Scenario: Required tool posture is mechanically aligned
- **WHEN** a migrated `wave0/worker` request declares the required retrieval
  capability and the trusted runtime supplies one matching allowed alternative
- **THEN** the bridge binds that tool under its existing policy and records the
  bounded call window without exposing another configured tool outside the capability
  intersection

#### Scenario: Tool disagreement fails closed
- **WHEN** a migrated capability forbids tools, has no permitted configured tool, or
  disagrees with its request window or `ExecutionPolicy`
- **THEN** the bridge returns the existing typed non-success result without a model
  invocation, tool dispatch, new retry, or graph action

#### Scenario: Wave2 does not inherit HITL1 tool posture
- **WHEN** a mixed real recipe resolves `wave2_synthesis`
- **THEN** both synthesis catalog cases use the dedicated zero-tool policy and no
  model-visible tool, independent of HITL1's bridge or budget
