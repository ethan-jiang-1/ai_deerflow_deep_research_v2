> req: NOA-015

## ADDED Requirements

### Requirement: Node-agent budget stops expose one closed diagnostic subreason

The runtime node-agent bridge SHALL map each known budget stop to one closed
budget-stop reason defined by `run-event-journal`: `request_content_unestimable`,
`model_call_limit`, `token_admission`, `per_call_output_cap`,
`total_token_budget`, `tool_calls_per_response`, `parallel_tool_calls`,
`total_tool_calls`, `bridge_wall_time`, or `unknown`. It SHALL carry only that safe
reason through a private per-invocation recording projection to the existing Event
Journal producer. It SHALL NOT expose middleware detail, exception text, request
content, model output, tool body, provider payload, credential, or endpoint through
the normalized result or Journal.

The bridge SHALL preserve the existing `NodeFinishReason`, normalized
`RunFailureCode`, provider-timeout origin, cancellation behavior, recovery ownership,
and parent graph result; it SHALL NOT add this attribution to `NodeProblem` or make it
part of a graph-facing node result contract. A budget-stop reason is diagnostic
attribution only; it SHALL NOT grant the bridge retry, route, checkpoint,
Bundle-selection, or lifecycle authority. (`NOA-015`)

#### Scenario: Middleware budget boundaries map to a closed reason
- **WHEN** a model-call, token-admission, output-cap, total-token, or tool-call bound
  stops a node-agent invocation
- **THEN** the existing safe result category remains unchanged and the Journal producer
  receives the matching allowed budget-stop reason with no raw middleware detail

#### Scenario: Bridge wall time remains a timeout with bounded attribution
- **WHEN** the bridge's existing wall-time deadline expires
- **THEN** its existing timeout category and origin remain unchanged while the Journal
  can retain only `bridge_wall_time` as the associated budget-stop reason

#### Scenario: A non-budget result cannot gain a budget reason
- **WHEN** a node-agent invocation succeeds, is cancelled, fails provider recovery, or
  fails another policy or structured-output boundary
- **THEN** it retains the existing normalized behavior and no budget-stop reason is
  published unless the bridge has a known budget stop
