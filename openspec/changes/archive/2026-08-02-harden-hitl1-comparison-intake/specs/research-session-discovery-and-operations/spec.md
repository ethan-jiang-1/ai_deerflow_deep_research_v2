## MODIFIED Requirements

### Requirement: Operations retain checkpoint and pending-interrupt authority

`open` and `status` SHALL be read-only. `resume` and `cancel` SHALL revalidate the
authoritative checkpoint through the official provider and invoke only the existing
lifecycle handlers with a trusted resolved envelope. For a reopened resume, the broker
SHALL derive the pending request and its bounded display view from the latest checkpoint
interrupt, compare the caller's expected opaque request id, validate the submitted
typed response against that request, and pass only a brokered response to the handler.
Text retains its existing raw-answer validation; an action or option response SHALL be
accepted only when its action or option id is advertised by that exact current pending
request. The handler SHALL repeat the request-id, response-kind, and
pending-interrupt checks while its namespace lock is held before graph invocation. A
manifest, binding, caller phase, binding cursor, or caller request id SHALL NOT be
treated as lifecycle authority. Local broker resume and cancel SHALL hold the same
retained-root dispatch lease as normal local lifecycle dispatch from binding resolution
through completion. Lease acquisition SHALL be bounded to at most 30 seconds and
contention SHALL fail before provider, sandbox, or graph work. (`RDO-003`)

#### Scenario: Stale response remains rejected after session reopen
- **WHEN** a reopened session receives a response not correlated with its latest checkpointed pending interrupt
- **THEN** resume rejects it without checkpoint mutation or graph-node invocation

#### Scenario: Retained current language option resumes through the verifier
- **WHEN** an authorized retained-session caller selects the Chinese option projected by the current HITL1 language request
- **THEN** the broker forwards that exact correlated `OPTION` response under lock and HITL1 remains the owner of profile mutation and routing

#### Scenario: Retained stale language option is rejected
- **WHEN** a caller submits a language option that is absent from the latest retained pending request
- **THEN** the broker returns its existing unavailable/invalid result without invoking the graph or mutating the checkpoint
