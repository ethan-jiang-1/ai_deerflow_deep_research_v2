# deep-research-wave0-worker-failure-classification Specification

> req: WFC-001

## Purpose

Classify real Wave0 worker failures with closed redacted categories while preserving
the existing controller, retry, ledger, and lifecycle authorities.
## Requirements
### Requirement: Wave0 worker failures have a closed controller-owned classification

The Deep Research runtime SHALL classify each terminal real Wave0 work attempt as
exactly one closed value: `agent_invocation`, `tool_execution`, `structured_output`,
`submission_validation`, or `unknown`.  Only trusted controller/runtime code SHALL
derive that value from existing safe node-agent result facts, Wave0 parser/repair
outcomes, or deterministic submission validation.  A model, tool, worker artifact,
exception string, or caller payload SHALL NOT select or extend the classification.

#### Scenario: A bridge failure remains classified without its exception
- **WHEN** a real Wave0 node-agent result is non-successful or the bridge returns an
  existing safe provider/tool failure problem
- **THEN** the terminal attempt receives the corresponding closed invocation or tool
  class and no exception text is retained

#### Scenario: A malformed result is classified at the parse boundary
- **WHEN** Wave0 cannot parse a successful worker result and the bounded repair result
  is also unusable
- **THEN** the terminal attempt is classified `structured_output` and follows the
  existing retry policy

#### Scenario: A deterministic submission rejection is classified separately
- **WHEN** a Wave0 candidate fails deterministic submission validation
- **THEN** the terminal attempt is classified `submission_validation` without changing
  validator precedence, ledger authority, or retry/gate routing

#### Scenario: An unmapped local failure is honest
- **WHEN** a trusted controller boundary catches a failure with no recognized safe map
- **THEN** it classifies the attempt as `unknown` and does not serialize the failure
  message or type

### Requirement: Exhausted-work aggregation is derived from persisted attempts

For one Wave0 work id, the controller SHALL derive an exhaustion aggregate from the
checkpointed terminal `AttemptRef` history: the shared per-attempt class when every
failed attempt has that class, otherwise the separate closed aggregate `mixed`.  The
aggregate SHALL NOT be written as an attempt class, chosen from the latest attempt, or
used to change the existing `research.blocked` terminal route code.

#### Scenario: Retry history produces a mixed aggregate
- **WHEN** one persisted attempt is `agent_invocation` and a later retry is
  `structured_output` for the same work id
- **THEN** their attempt events retain their individual classes and the exhausted-work
  aggregate is exactly `mixed`
