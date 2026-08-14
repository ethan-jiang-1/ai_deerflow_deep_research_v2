> req: NOA-005

## MODIFIED Requirements

### Requirement: Results, progress, failure, and cancellation are normalized

The adapter SHALL validate structured model output and project stable redacted
progress events through the supported stream-writer API. Malformed output SHALL fail;
outer `CancelledError` SHALL propagate after child/provider cleanup and SHALL not
leave background work running.

The optional endpoint-authority observation SHALL derive only from the exact selected
model configuration's `base_url` field. It SHALL normalize only a safe HTTP(S)
authority and SHALL emit no observation for a missing, malformed,
credential-bearing, conflicting, or retired-alias value. `openai_api_base` and
`api_base` are retired observation aliases: their presence, whether alone or
alongside `base_url`, SHALL not select a model, change provider behavior, alter
lifecycle or retry policy, or cause model-object reflection. The observation remains
a projection only and SHALL not reveal a path, query, fragment, credential, raw
configuration, or endpoint authority beyond the existing safe normalization contract.

#### Scenario: Valid result and progress are projected
- **WHEN** a fake agent emits progress and a result matching the node output schema
- **THEN** the parent receives stable progress records and one validated normalized
  result without raw secrets or source bodies

#### Scenario: Cancellation cannot become success
- **WHEN** the outer task is cancelled while a fake embedded agent has child work in
  flight
- **THEN** child work is cancelled and awaited, cleanup completes, and no successful
  result is emitted

#### Scenario: Selected base URL produces a safe observation
- **WHEN** the exact selected model configuration contains a safe normalizable
  `base_url`
- **THEN** the node-agent result may carry only its normalized endpoint authority and
  no model, provider, retry, route, or lifecycle decision changes

#### Scenario: Retired alias produces no endpoint observation
- **WHEN** the selected model configuration contains `openai_api_base` or `api_base`,
  whether or not it also contains `base_url`
- **THEN** the result contains no endpoint-authority observation and the alias does
  not affect model creation, provider selection, or lifecycle behavior

#### Scenario: Unsafe base URL fails closed as an observation
- **WHEN** the selected `base_url` is malformed, contains userinfo, conflicts with a
  retired alias, or cannot normalize to a safe authority
- **THEN** the result contains no endpoint-authority observation and does not expose
  the rejected value or create another configuration reader
