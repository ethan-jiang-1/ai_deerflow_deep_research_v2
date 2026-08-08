> req: NOA-007

## ADDED Requirements

### Requirement: Node-agent failures retain a closed causal category for the parent graph

RuntimeNodeAgentBridge SHALL translate model resolver, tool resolver, agent
construction/invocation, provider timeout, policy stop, and structured-output
failure into a typed, bounded NodeProblem before returning control to a graph node.
NodeProblem SHALL contain only a closed run-failure category, direct-or-unknown
certainty, safe operation/phase attribution, and an optional opaque diagnostic
reference. It SHALL not contain raw exception strings, provider bodies, credentials,
paths, user input, tool output, or model output.

CancelledError SHALL continue to propagate. Graph nodes SHALL receive enough typed
information to choose their existing route and publish a safe compact terminal
incident when appropriate; they SHALL not need to catch all exceptions and erase
the causal category. Unknown exceptions SHALL map to internal-unexpected, not an
invented checkpoint inconsistency. (NOA-007)

#### Scenario: Configuration error reaches a node without raw exception text
- **WHEN** the bridge cannot resolve a configured model for a real HITL-1 brief
- **THEN** HITL-1 receives a typed configuration.model_missing problem, may route
  to its declared blocked path, and a later lifecycle result can explain that safe
  category without exposing the resolver exception

#### Scenario: Cancellation remains cancellation
- **WHEN** the outer lifecycle task is cancelled while a child agent is active
- **THEN** CancelledError propagates after child cleanup and no failure category is
  published as a successful, blocked, or graph-cancelled result
