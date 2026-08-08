> req: WOU-001, WOU-003, WOU-004, WOU-005, WOU-006, WOU-009, WOU-011

## ADDED Requirements

### Requirement: Work-unit stores use one runtime-bound Run Bundle reference

Work-unit, evidence, and content stores SHALL resolve every durable path from one
runtime-bound Run Bundle reference. They SHALL not accept a `research_id`, bundle
directory, caller-supplied root, session record, or checkpoint locator as an alternate
identity/path input. They SHALL preserve contained-write, atomic publication, locking,
and per-Run isolation guarantees, and SHALL fail closed when their selected Bundle is
unavailable. (`WOU-011`)

#### Scenario: Caller cannot redirect evidence outside the selected Bundle
- **WHEN** a work-unit operation receives a valid WorkSpec alongside an attempted path or legacy identity override
- **THEN** validation rejects the override before any artifact write and the operation remains contained in its bound Bundle

## RENAMED Requirements

- FROM: `### Requirement: Per-research cross-process serialization prevents duplicate or partial publication`
- TO: `### Requirement: Per-Run-Bundle cross-process serialization prevents duplicate or partial publication`
- FROM: `### Requirement: Work-unit and content roots use the canonical bundle locator`
- TO: `### Requirement: Work-unit and content paths resolve through a runtime-bound Bundle reference`
- FROM: `### Requirement: Ledger and checkpoint crash windows reconcile idempotently`
- TO: `### Requirement: Ledger and Bundle-State crash windows reconcile idempotently`

## MODIFIED Requirements

### Requirement: Per-Run-Bundle cross-process serialization prevents duplicate or partial publication

The work-unit store SHALL serialize evidence publication by the selected runtime-bound
Run Bundle, using a contained Bundle-local ledger lock and no legacy research identity,
session binding, external checkpoint namespace, or caller-supplied root. It SHALL retain
the existing bounded lock timeout, atomic complete-ledger publication, compare-and-set
one-winner guarantee per logical work, cancellation-safe off-event-loop filesystem I/O,
and closed redacted storage-error/result-code pairing. Different Bundles SHALL not share
a global mutation lock. Scope-level lifecycle admission may serialize Run creation but
shall not replace Bundle-local evidence publication serialization. A deleted or
unavailable Bundle SHALL return the lifecycle unavailable outcome and SHALL not create a
replacement ledger or recover it from external State. (`WOU-006`)

#### Scenario: Independent processes race one Bundle's candidate
- **WHEN** two store instances concurrently submit candidates for the same logical work in one available Bundle
- **THEN** at most one complete Bundle-local ledger record becomes authoritative, the other caller observes the existing winner/conflict, and no partial ledger line is visible

#### Scenario: Bundle loss prevents evidence replacement
- **WHEN** the selected Bundle becomes unavailable before ledger publication or lock acquisition
- **THEN** the operation reports unavailable, creates no replacement root or ledger, and does not consult an external checkpoint/session record

#### Scenario: Storage outage does not block cancellation
- **WHEN** Bundle evidence storage readiness fails while an available Run is suspended at a cancellable HITL boundary
- **THEN** cancellation follows its Bundle-local control path without constructing the work-unit store or exposing ledger authority to the cancelling node

### Requirement: Work-unit and content paths resolve through a runtime-bound Bundle reference

The work-unit projection, storage probe, deterministic Bundle helpers, and `ContentRef`
validation SHALL derive research and attempt roots only from the selected runtime-bound
Run Bundle reference plus controller-assigned work and attempt ids. They SHALL reject a
malformed/foreign Bundle reference, root mismatch, symlink/path escape, or an artifact
belonging to another Bundle. A physical root is private to the lifecycle/store boundary;
it is not checkpointed, projected, accepted from a caller, or derived from
`research_id`. This changes no work, attempt, ledger, or lifecycle identity. (`WOU-009`)

#### Scenario: Attempt content follows one selected Bundle
- **WHEN** a Wave0 work attempt runs for one available Bundle
- **THEN** its spec, result, cache, evidence ledger, diagnostics probe, and `ContentRef` all remain under that one Bundle's private contained root

#### Scenario: Bundle mismatch fails containment
- **WHEN** a candidate or stored reference targets another Bundle through a path or legacy identity override
- **THEN** validation rejects it before ledger publication or content-reference acceptance

### Requirement: Ledger and Bundle-State crash windows reconcile idempotently

Submit SHALL treat the validated Bundle-local ledger as evidence truth and the selected
Bundle-local `ResearchState` as control truth without claiming a distributed
transaction. The last durable State write may predate execution of the current bounded
phase step; controller allocation shall therefore remain deterministic from that State,
and replay SHALL reconcile regenerated work/attempt identities against the contained
ledger before redispatch. A matching ledger record may repair a missing Bundle-local
accepted reference without a second append; a submitted reference without a matching
valid ledger, broken chain, duplicate logical-work record, or mutated accepted artifact
SHALL fail closed with the existing redacted storage outcome. No external checkpoint,
session, or cache may supply a missing State or ledger record. (`WOU-005`)

#### Scenario: Crash occurs after contained ledger publication
- **WHEN** fault injection stops execution after the atomic contained ledger publish and before the Bundle-local State update
- **THEN** replay finds the same record, performs no second append, and publishes the missing submitted status only in that Bundle

### Requirement: Controller-assigned immutable work contracts preserve identity and spec integrity

The existing frozen, versioned work/attempt/candidate/submission contracts and their
controller-assigned generation, phase, work, attempt, role, and spec-hash invariants
remain unchanged. Their Run association SHALL come only from the runtime-bound selected
Bundle context; no work-unit contract, caller, worker, or candidate may supply or
override `research_id`, a Bundle directory, a session reference, or an external
checkpoint identity. (`WOU-001`)

#### Scenario: Work contract cannot redirect its Run
- **WHEN** a valid-looking WorkSpec or CandidateResult includes a legacy Run identity or
  path override
- **THEN** validation rejects the value before a store resolves its selected Bundle

### Requirement: Deterministic submit validation fails closed before evidence acceptance

The existing stable-order submit validation, schema/hash/source/reference checks, and
redacted failure categories remain unchanged. Persisted content references SHALL use
only the canonical relative form produced from the selected runtime-bound Bundle
reference plus controller-assigned work and attempt ids. They SHALL not persist
`workspace/deep-research/<research_id>/...`, an external checkpoint locator, or a
caller-selected root as authority. (`WOU-003`)

#### Scenario: Legacy content reference is rejected before ledger mutation
- **WHEN** a candidate presents a reference derived from `research_id` or an old
  workspace root instead of the selected Bundle reference
- **THEN** submit fails closed before evidence acceptance or State mutation

### Requirement: The controller submit path is the sole accepted-evidence writer

The controller-owned submit path SHALL retain its existing atomic hash-chained
accepted-record, one-winner, and redaction guarantees, but its ledger SHALL be resolved
only inside the selected available Run Bundle. An external checkpoint, session record,
or `research_id` path SHALL not select, recreate, or reconcile that ledger. (`WOU-004`)

#### Scenario: External record cannot supply a missing ledger
- **WHEN** a selected Bundle is unavailable while an old session/checkpoint record still
  names an evidence ledger
- **THEN** submit returns the typed unavailable outcome and creates no replacement ledger
