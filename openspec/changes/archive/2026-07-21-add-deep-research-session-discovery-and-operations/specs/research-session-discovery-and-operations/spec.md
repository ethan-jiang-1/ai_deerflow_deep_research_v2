> req: RDO-001, RDO-002, RDO-003, RDO-004

## ADDED Requirements

### Requirement: Authorized local discovery projects bounded owned sessions

The runtime SHALL provide a local discovery broker that returns only bounded session
projections authorized for the current trusted principal. It SHALL discover selected
opaque binding references from a private owner-and-profile index that activates only after
retained-bundle publication, validate each binding against the current principal, profile,
provider, and profile-owned recipe fingerprint, and never enumerate raw bundle directories
or another principal/profile's sessions. Existing legacy inspection remains a separate
observation surface; the broker SHALL NOT infer, backfill, or operate a phase-2/legacy
binding that lacks current owner-index membership and recipe compatibility. The index
SHALL retain no more than the configured retained-session bound, and discovery SHALL never
create, repair, or prune it. (`RDO-001`)

#### Scenario: Foreign and unknown sessions are indistinguishable
- **WHEN** discovery or open receives a foreign, unknown, or corrupt opaque reference
- **THEN** it returns the same bounded unavailable or denied projection without a path,
  owner, provider, or existence hint

### Requirement: Trusted runtime resolution precedes a cross-session operation

The broker SHALL receive a `SessionOperationAccess` created by a trusted runtime adapter
or fixed local profile adapter, not by CLI/TUI arguments. After private owner-index and
binding validation, its resolver SHALL obtain contained historical paths and, only when
needed, a sandbox through factories owned by the access. Runtime-originated access SHALL
use public DeerFlow scope-addressed APIs with the verified bound thread and current trusted
principal; local-profile access SHALL use only its fixed contained-root/local-sandbox
factories. It SHALL validate recipe compatibility before opening a provider or constructing
an envelope/sandbox. It SHALL not synthesize a historical `ToolRuntime` or take AppConfig,
host paths, provider connection, sandbox id, user, thread, recipe, or implementation map
from a manifest or caller input. A binding alone SHALL NOT construct a
`TrustedRuntimeEnvelope`. (`RDO-002`)

#### Scenario: Read-only open does not initialize a sandbox
- **WHEN** an authorized principal opens or reads status for a durable session
- **THEN** it uses the read-only verifier and does not initialize a parent sandbox or
  construct graph invocation capabilities

### Requirement: Operations retain checkpoint and pending-interrupt authority

`open` and `status` SHALL be read-only. `resume` and `cancel` SHALL revalidate the
authoritative checkpoint through the official provider and invoke only the existing
lifecycle handlers with a trusted resolved envelope. For a reopened resume, the broker
SHALL derive the pending request and its bounded display view from the latest checkpoint
interrupt, compare the caller's expected opaque request id, validate submitted raw answer
text against that request, and pass only a brokered response to the handler. The handler
SHALL repeat the request-id and pending-interrupt check while its namespace lock is held
before graph invocation. A manifest, binding, caller phase, binding cursor, or caller
request id SHALL NOT be treated as lifecycle authority. Local broker resume and cancel
SHALL hold the same retained-root dispatch lease as normal local lifecycle dispatch from
binding resolution through completion. Lease acquisition SHALL be bounded to at most 30
seconds and contention SHALL fail before provider, sandbox, or graph work. (`RDO-003`)

#### Scenario: Stale response remains rejected after session reopen
- **WHEN** a reopened session receives a response not correlated with its latest
  checkpointed pending interrupt
- **THEN** resume rejects it without checkpoint mutation or graph-node invocation

### Requirement: Discovery and operation outputs fail closed and remain redacted

All discovery and operation outputs SHALL fail closed for unavailable, non-durable,
stale, provider-drifted, malformed, or unauthorized sessions. They SHALL expose only
opaque references, bounded lifecycle/availability facts, and whitelisted contained
artifact references. For an authorized selected suspended session, they MAY expose the
validated bounded `HumanInputRequest` display fields derived from the authoritative
pending interrupt so the owner can answer it. They SHALL never expose raw scope,
provider, host path, checkpoint payload, unvalidated prompt data, raw answer, diagnostic
body, or artifact body. (`RDO-004`)

#### Scenario: Recipe mismatch fails before provider access
- **WHEN** a selected binding's stored recipe fingerprint does not match the authorized
  operation access's fixed recipe
- **THEN** the broker returns bounded unavailability without opening a provider,
  resolving historical paths, or acquiring a sandbox

#### Scenario: Provider drift cannot become a discovery fallback
- **WHEN** the current provider fingerprint differs from a session binding
- **THEN** the operation reports bounded unavailability without probing another provider
  or reading session content
