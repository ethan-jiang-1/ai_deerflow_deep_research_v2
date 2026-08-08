## ADDED Requirements

### Requirement: Provider timeout diagnostics retain a closed observed origin

For each admitted provider timeout that the runtime bridge positively identifies as
either its own expired wall-time budget or the supported `openai.APITimeoutError`
branch, the bridge SHALL attach respectively only `bridge_wall_time_budget` or
`provider_sdk_timeout` to that typed `ProviderObservation`. The origin SHALL be absent
when neither cause was positively observed, including the separately handled
`httpx.TimeoutException`, a bare inner `TimeoutError`, and legacy/generic `no_response`
results; it SHALL not be inferred from category, timing, service label, or endpoint
authority. It SHALL contain no raw exception text, provider body, prompt, credential,
full URL, host path, or request payload. The existing provider failure category,
response observation, cancellation behavior, and retry eligibility SHALL remain
unchanged. (`NOA-001`)

#### Scenario: Bridge wall-time is not reported as an SDK timeout
- **WHEN** the bridge wall-time budget expires while a provider request is admitted
- **THEN** the typed provider timeout retains the closed bridge-budget origin and no
  raw exception detail

#### Scenario: SDK timeout remains distinguishable
- **WHEN** an admitted provider request raises the supported provider-SDK timeout
- **THEN** the typed provider timeout retains the distinct closed SDK-timeout origin
  while preserving the existing safe no-response observation

#### Scenario: Legacy or generic no-response does not invent an origin
- **WHEN** a legacy projected provider observation has no bridge-supplied timeout origin
- **THEN** downstream projection preserves the origin as absent and does not infer one
  from category, timestamp, service label, or endpoint authority

#### Scenario: Transport timeout does not claim an SDK origin
- **WHEN** the separately handled `httpx.TimeoutException` produces the existing
  admitted `provider.timeout` result
- **THEN** its origin remains absent while its existing category, safe no-response
  observation, and retry eligibility remain unchanged
