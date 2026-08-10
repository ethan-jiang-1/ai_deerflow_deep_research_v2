# work-unit-kernel Specification

> req: WOU-001, WOU-002, WOU-003, WOU-004, WOU-005, WOU-006, WOU-007, WOU-008, WOU-009, WOU-010, WOU-011

## Purpose
The shared work-unit kernel beneath Wave0/Wave1 fixture nodes: immutable controller-assigned work/attempt contracts, bounded `Send`, deterministic file validation, one hash-chained JSONL ledger writer, crash reconciliation, and the shared drain/gate view.
## Requirements

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

### Requirement: Typed bounded batches reduce candidates without losing or replacing winners

Checkpointed parent `ResearchState` SHALL use typed work-unit fields for immutable spec
metadata, terminal/aggregate work status, batch and id cursors, bounded attempt history,
and accepted submission refs. A separate typed, size-bounded child state SHALL own the
current replay unit's pending work, in-flight attempts, and candidate fan-in. Because the
current Wave child is manually invoked, those transient channels SHALL use explicit
`checkpointer=False`; after a crash they SHALL be reconstructed deterministically from
the last parent checkpoint and reconciled against the ledger before redispatch.

The child state SHALL have exactly sorted `planned_work_ids` (max 32), sorted
`pending_work_ids` (max 32), `batch_cursor`, `in_flight_by_attempt_id` (max 16),
`candidates_by_attempt_id` (max 16), and `terminal_updates_by_attempt_id` (max 64).
An `AttemptTerminalUpdate` SHALL contain only attempt id, terminal status, UTC terminal
timestamp, terminal code, and optional ordered closed validation codes.
Terminal code `validation_failed` SHALL require a non-empty validation-code tuple in the
closed registry order; every other terminal code SHALL require that tuple to be empty.
In-flight, candidate, and terminal-update reducers SHALL treat identical keyed values as
idempotent and different values as conflicts. The sole deferred submit node SHALL run
after current workers, process sorted attempt keys, accumulate terminal updates, and
clear only the in-flight/candidate maps with LangGraph `Overwrite({})` before refill; it
SHALL NOT write the aggregated candidate map back through its reducer or clear terminal
updates before the child returns.

The child SHALL compile with `checkpointer=False` and SHALL be invoked with internal
`recursion_limit=128`, sufficient for 32 work items at concurrency 1. Public/root config
SHALL NOT select or lower that internal limit.

The phase-local work-unit component SHALL select pending work in stable order and emit no
more LangGraph `Send` calls than its construction-time concurrency limit. The
Wave0 and Wave1 fixtures SHALL use exactly 3; generic construction SHALL accept only
`1..16`; the limit SHALL NOT be a caller-supplied authority field. Work SHALL be ordered
by ordinal/zero-padded id. `batch_cursor` SHALL be the zero-based next-undispatched index,
allocation SHALL select the next slice of at most the limit and advance by the emitted
count before dispatch, and worker completion SHALL NOT move the cursor.

`work_specs_by_id` SHALL be keyed by logical work id. `attempts_by_id` and the retained
compatibility field `work_status_by_id` SHALL both be keyed by attempt id.
`active_attempt_by_work_id` SHALL map each logical work to at most one non-terminal
attempt. Retry SHALL append a new attempt/status entry and SHALL NOT replace or downgrade
an old terminal entry. Compact map values SHALL omit identity derivable from their
validated keys: `WorkSpecRef` contains only worker role and spec hash; `AttemptRef`
contains only lifecycle timestamps and terminal code; and
`terminal_failures_by_attempt_id` values contain only failure code and detail hash.
Classification SHALL be derived from the existing closed `FailureCode` registry when the
gate view is built and SHALL NOT be duplicated in checkpoint state. Attempt work id/
ordinal and spec hash SHALL be recovered from the attempt id plus `work_specs_by_id`,
never duplicated in the value.
`detail_hash` SHALL be the standard `h_<base64url-no-padding>` SHA256 of exact canonical
JSON object `{"terminal_code": <enum>, "validation_codes": [<ordered enums>]}` prefixed
by exact ASCII-plus-NUL domain `deerflow-deep-research:terminal-failure-detail:v1\0`.
Non-validation terminals SHALL use an empty validation-code list; free-form worker/model
text SHALL never enter that hash or the checkpoint.
The canonical first-spec path SHALL be derived from the trusted research id and work id
as attempt `a00`'s `work-spec.json` through `domain/bundle.py`; it SHALL NOT be persisted
inside `WorkSpecRef`. Retry spec paths SHALL likewise derive from their attempt ids.

`terminal_failures_by_attempt_id` SHALL be the bounded current gate projection, not the
terminal-history authority. It SHALL contain at most one summary per logical work for the
selected highest terminal unaccepted attempt; an accepted work has none. The controller
SHALL publish the complete validated mapping with replacement semantics when a retry
changes that selection. The replaced attempt SHALL remain immutable in `attempts_by_id`
and `work_status_by_id`, so this derived projection update SHALL NOT erase terminal
history or count as silent eviction.

Compact refs/summaries SHALL be validated by frozen extra-forbid Pydantic models, but
checkpoint channels SHALL persist their `model_dump(mode="json")` plain mappings rather
than opaque model instances. Reducers and checkpoint loading SHALL accept model/mapping
input, validate and normalize it through the same model, and use that exact JSON-mode
representation for size accounting, replay equality, and checkpoint output.

The active parent window SHALL contain at most 32 logical works, 64 attempts, 32 terminal
failure summaries, and 64 accepted record hashes. Canonical JSON for exactly the parent
work-unit fields SHALL be at most 40,960 bytes. The budget object SHALL contain exactly
`pending_work_ids`, `batch_cursor`, `next_work_ordinal`,
`next_attempt_ordinal_by_work_id`, `work_specs_by_id`, `attempts_by_id`,
`work_status_by_id`, `active_attempt_by_work_id`,
`terminal_failures_by_attempt_id`, and `accepted_submission_refs` under sorted-key compact
JSON; none may be omitted from the size calculation. The existing 65,536-byte whole-
state limit SHALL still apply. Exceeding a collection, work-block, or whole-state bound
SHALL fail closed without truncation or silent eviction. A maximum-shape golden fixture
SHALL prove the independent-field 32/64/32/64 work-block upper envelope fits its budget.
A separate legal all-terminal fixture at the same four collection maxima, with empty
pending/active maps, SHALL fit the whole-state bound when combined with a maximum-length
single-byte ASCII request text. Other request/control combinations SHALL remain subject
to the unchanged whole-state failure rather than receiving a larger request allowance.

Compatibility is one-way for upgrade: the current reader SHALL load version-2
checkpoints with absent compatible fields defaulted, while an older reader MAY reject a
newly written payload containing added fields. Rollback SHALL fail closed and require a
fresh research run; it SHALL NOT claim that old code ignores new fields.

Candidate fan-in SHALL reduce by `(work_id, attempt_id)`, normalize stable order, treat
same-hash replay as idempotent, reject different-hash replay as a conflict, and preserve
terminal monotonicity. A terminal attempt SHALL have at most one winner and SHALL NOT be
downgraded to pending or running by a stale branch.

Controller materialization and `SUBMIT` operations SHALL each be writer-authorized
against their applicable current/preview state, then one pure cross-field validator SHALL
check the final parent projection across spec ref, attempt ref, status, active mapping,
selected failure, and accepted ref before the node returns. Worker/model output SHALL
never be accepted as a parent-state delta. Parent reducers SHALL enforce keyed replay and
terminal monotonicity on that coalesced projection; they SHALL NOT infer missing internal
child transitions from a single status field.

#### Scenario: Three workers finish in arbitrary scheduler order
- **WHEN** three fixture workers are dispatched in one bounded batch and complete in any order
- **THEN** all three candidates are retained exactly once, normalized by stable work/attempt identity, submitted at most once each, and no candidate is lost at fan-in

#### Scenario: Two branches claim different winners for one attempt
- **WHEN** concurrent branches return different candidate hashes for the same work and attempt identity
- **THEN** the reducer raises a typed conflict, publishes no accepted winner for that attempt, and does not use last-write-wins behavior

#### Scenario: Retry preserves terminal attempt history
- **WHEN** a failed attempt is retried for the same immutable work
- **THEN** the old attempt/status entry remains terminal, a fresh attempt id is appended and becomes the sole active attempt for the work, and no reducer rewrites history

#### Scenario: Accepted work needs a quality repair
- **WHEN** a gate requests revised evidence after the logical work already has a valid accepted record
- **THEN** planning allocates a new logical work id and leaves the accepted work/record immutable rather than creating a sibling attempt

#### Scenario: Maximum parent work window remains serializable
- **WHEN** the compact parent budget fixture independently maximizes every declared work field and a separate legal all-terminal state reaches 32 logical works, 64 attempts, 32 selected failures, and 64 accepted hashes
- **THEN** the pessimistic work-block encoding is at most 40,960 bytes and the legal full checkpoint with maximum-length single-byte ASCII request is at most 65,536 bytes without truncation

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

### Requirement: Attempt retry, expiry, cancellation, and crash recovery are one-way

Attempt statuses SHALL be one-way across `pending | running | submitted | failed |
timed_out | cancelled`. Once terminal, an attempt SHALL NOT return to pending or running.
A repair/retry after `failed` or `timed_out` SHALL create a new controller-assigned
attempt id and ordinal for the same immutable work spec. `cancelled` and `superseded`
attempts SHALL never authorize retry. The first version SHALL fail closed on a candidate
from any expired, cancelled, or superseded attempt and SHALL NOT implement a late-submit
winner.

The only state changes SHALL be `pending -> running`, `pending -> cancelled`, and
`running -> submitted | failed | timed_out | cancelled`. Reapplying the same status with
identical timestamps and terminal code SHALL be idempotent. Any same-status detail
mismatch, direct `pending -> submitted|failed|timed_out`, transition out of a terminal
status, mutation of immutable identity/spec/created-at fields, or replacement that is not
the validated next lifecycle version SHALL be a conflict. A legal transition publishes a
new frozen `Attempt` value for the same key with only its permitted lifecycle fields
advanced. Retry SHALL append a fresh attempt and SHALL preserve every prior terminal
entry.

Those adjacency rules SHALL govern kernel transition operations. The manually invoked
child is one atomic parent node, so a validated parent update MAY coalesce multiple legal
internal transitions and first project a new attempt as terminal, or project an existing
non-terminal attempt at its later terminal state. Before return, the cross-field parent-
projection validator SHALL prove the attempt timestamps/code/status, active-map removal,
failure selection, and accepted ref are mutually consistent. This allowance SHALL NOT
permit reopening/replacing a checkpointed terminal attempt or bypassing the internal
transition tests.

Terminal codes SHALL be the closed set
`accepted | worker_failed | validation_failed | candidate_conflict |
deadline_exceeded | expired | cancelled | superseded` with these
status mappings: submitted uses only `accepted`; failed uses
`worker_failed | validation_failed | candidate_conflict`; timed out
uses `deadline_exceeded | expired`; cancelled uses `cancelled | superseded`.
Pending/running attempts SHALL have null terminal timestamp/code; terminal attempts SHALL
have both. `created_at` SHALL always be present, `started_at` SHALL be present after
running, and direct pending-to-cancelled MAY keep `started_at` null.
All timestamps SHALL be timezone-aware UTC with monotonic ordering:
`created_at <= started_at <= terminal_at` when started,
`created_at <= terminal_at` for direct cancellation, and `expires_at > created_at` when
set. `expired` SHALL require `terminal_at >= expires_at`; submit SHALL reject a candidate
when the injected current UTC time is greater than or equal to `expires_at`.

Replay SHALL skip work already proven submitted by a valid accepted ledger record.
Non-terminal work interrupted before acceptance MAY execute again with the same active
attempt when replaying the same graph step; after explicit failure or timeout, further
execution requires a new retry attempt. Cancellation SHALL propagate, SHALL never be
converted into worker success, and SHALL not authorize retry. A superseded attempt SHALL
remain closed because a sibling accepted record is authoritative.

#### Scenario: Failed work is retried
- **WHEN** an attempt reaches failed or timed-out status and repair schedules the logical work again
- **THEN** the controller preserves the original spec hash, allocates a strictly newer attempt id, and refuses any later candidate from the old attempt

#### Scenario: Crash recovery distinguishes accepted and unaccepted attempts
- **WHEN** a process restarts with one attempt present in the accepted ledger and another attempt without an accepted record
- **THEN** the accepted attempt is skipped idempotently while the non-terminal unaccepted attempt may be re-executed without creating a second winner

#### Scenario: Cancellation or expiry races a late candidate
- **WHEN** an attempt is cancelled, timed out, expired, or superseded before its candidate is submitted
- **THEN** the late candidate is rejected and no ledger record is added for that attempt; failed/timed-out work may continue only through a fresh retry, while cancelled/superseded work cannot be redispatched

#### Scenario: Terminal transition is replayed exactly
- **WHEN** replay applies the same terminal status, timestamp, and terminal code to an existing attempt
- **THEN** the reducer treats it as an idempotent no-op, while any changed terminal detail or attempted reopening is rejected as a conflict

### Requirement: Generic phase drain gates on empty pending and in-flight work

The work-unit kernel SHALL expose one deterministic phase drain predicate shared by
Wave0, Wave1, targeted evidence, and rerun consumers. A phase SHALL NOT invoke its gate
while any logical work remains pending or any attempt remains in flight. Terminal
failed, timed-out, or cancelled attempts MAY make the queue structurally drained, but
their typed failures SHALL remain available to gate rules; drain SHALL never imply gate
pass or evidence coverage. Wave0 and Wave1 gate definitions SHALL include one shared
deterministic work-completion rule ahead of their fixture rule. It SHALL verify structural
drain, terminal status, and the bounded pure accepted-coverage view produced by the
controller's immediately preceding ledger reconciliation for every planned work item,
and map typed submission failures to the existing closed gate failure registry. The rule
SHALL perform no filesystem I/O. A fixture
`pass` SHALL NOT override missing, failed, conflicting, unaccepted, or invalid work.

The frozen ephemeral `WorkUnitGateView` SHALL contain only `drained`, sorted
`planned_work_ids`, `terminal_attempt_by_work_id`,
`accepted_record_by_work_id`, and ordered bounded failure summaries, each collection
limited to 32 entries. It SHALL contain no scope, artifact path, candidate body, ledger
record, cursor, phase, route, fixture counter, or host/virtual path and SHALL never be
checkpointed.
For one work it SHALL select the accepted attempt when present, otherwise the highest
terminal attempt ordinal, and SHALL include at most one matching failure summary ordered
by work id.
Each ephemeral `WorkUnitGateFailure` SHALL contain exactly work id, attempt id, failure
code, classification derived from that code, and detail hash. It SHALL be constructed
from the keyed compact parent failure but SHALL be a separate non-checkpointed type so
identity carried by the parent map key is not lost in the ordered tuple.

Because an accepted record hash alone does not encode its logical work id, the reconciler
SHALL return the typed view to a declaring Wave node under exact reserved mapping key
`__work_unit_gate_view__`. `_node_wrapper` SHALL copy the result, pop and type-check the
view before reducer preview, reject that key from every non-`WORK_UNIT_CONTROLLER` node,
inject it only into the in-memory gate mapping, and omit it from the final state update.
The reserved key SHALL not be a `ResearchState` field and SHALL never reach LangGraph
reduction or checkpoint serialization.

View validation SHALL have two explicit stages. Before child return, while reconciled
records and the exact child plan are still available, a pure component validator SHALL
prove that `planned_work_ids` exactly equals the child plan, each accepted
`work_id -> record_hash` pair matches the reconciled `SubmissionRecord` work/attempt/hash
association, terminal selection is canonical, and the view agrees with the complete final
parent projection. After reserved-key extraction, a separate wrapper validator SHALL
prove only what the reducer preview can establish: planned ids are sorted/unique, belong
to the previewed current-phase spec map, and exactly key the terminal map; each
terminal attempt exists, derives the mapped work id, and has a terminal preview status;
each accepted work selects a submitted attempt whose hash is present in previewed
`accepted_submission_refs`, while an unaccepted work does not select submitted; and each
selected failure matches `terminal_failures_by_attempt_id`. The wrapper SHALL NOT claim
to reconstruct record-to-work association from accepted hashes. Either mismatch SHALL
raise `work_unit_gate_view_inconsistent` before fixture/business gate evaluation and
SHALL NOT be converted into a repairable work failure.

For a declaring Wave node, `_node_wrapper` SHALL construct the gate input by shallow-
copying the input checkpoint and previewing exactly `work_specs_by_id`, `attempts_by_id`,
`work_status_by_id`, `active_attempt_by_work_id`,
`terminal_failures_by_attempt_id`, and `accepted_submission_refs` through their explicit
domain reducers. It SHALL NOT inspect LangGraph channel internals, mutate the input or
node delta, preview phase/route/trace/cursors/gate fields, or return the merged preview as
the node update. The node delta and gate update SHALL have disjoint keys; overlap SHALL
fail as `node_gate_write_conflict`, and LangGraph SHALL apply each returned reducer delta
exactly once.

The deterministic submit projection SHALL map validation detail to the compact parent
failure exactly once. For a validation failure, it SHALL select the first code in the
closed collect-all precedence as primary, hash the complete ordered validation-code tuple
into `detail_hash`, and map `work_spec_missing -> MISSING_WORK_SPEC`;
`identity_mismatch | spec_hash_mismatch -> IDENTITY_MISMATCH`;
`schema_version_unsupported -> SCHEMA_VERSION_UNSUPPORTED`;
`result_contract_unsupported | invalid_output_schema | path_not_canonical |
path_not_contained | artifact_missing | artifact_empty | source_ref_invalid ->
INVALID_OUTPUT_SCHEMA`; `content_hash_mismatch | candidate_hash_mismatch ->
CONTENT_HASH_MISMATCH`; and `candidate_conflict -> WORK_FAILED`. Non-validation terminal
codes SHALL map at the same boundary as follows: `worker_failed | candidate_conflict ->
WORK_FAILED`, `deadline_exceeded | expired -> WORK_TIMED_OUT`, and `cancelled |
superseded -> WORK_CANCELLED`. Submitted/accepted attempts SHALL have no failure summary.
`WorkUnitCompletionRule` SHALL consume the already mapped `FailureCode` and SHALL NOT
repeat or reinterpret this mapping.

#### Scenario: Pending or running work blocks phase gate
- **WHEN** either `pending_work_ids` or active in-flight attempts are non-empty after a batch
- **THEN** the component schedules the next bounded batch or waits for fan-in and does not invoke the phase gate

#### Scenario: Terminal batch reaches gate without inventing success
- **WHEN** pending and in-flight collections are empty after all attempts become terminal
- **THEN** the phase may invoke its gate against a reducer-previewed post-work state, and the gate sees the current batch's accepted refs plus terminal failures rather than stale input or drain alone

#### Scenario: Ephemeral gate view diverges from the returned state delta
- **WHEN** a controller result's reserved view names a missing terminal attempt, accepted hash, planned work, or selected failure relative to the reducer preview
- **THEN** the wrapper raises `work_unit_gate_view_inconsistent` before gate rules or state reduction, the reserved key is never checkpointed, and the reflected tool returns redacted `checkpoint_inconsistent`

#### Scenario: Fixture pass cannot override failed submit
- **WHEN** a Wave fixture route is `pass` but one planned work item lacks a valid accepted record or carries a terminal submit-validation failure
- **THEN** the shared work-completion rule returns a typed hard or repairable failure, the collect-all gate does not pass, and the fixture rule cannot suppress that failure

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

### Requirement: Work-unit terminal projection carries diagnosis without control authority

The shared work-unit component SHALL preserve one closed controller-owned worker failure
classification for each failed Wave0 attempt through its terminal update, checkpoint
projection, retry/exhaustion observation, and terminal incident input.  The
classification SHALL be additive diagnosis only: it SHALL NOT alter attempt identity,
status transition validity, retry eligibility, submission validation, ledger commit,
gate failure code/classification, or lifecycle route.  Legacy terminal updates lacking
the field SHALL remain readable as classification unavailable. (`WOU-010`)

#### Scenario: Categorized failure retries as before
- **WHEN** a classified failed attempt has remaining Wave0 retry budget
- **THEN** the component allocates the same next attempt and gate behavior it would
  have allocated before classification was added

#### Scenario: Category cannot forge control state
- **WHEN** a caller supplies an unknown/free-form worker category or a category that
  conflicts with the trusted terminal update
- **THEN** contract validation rejects it before checkpoint or event publication and
no ledger or gate authority changes

#### Scenario: Only typed validation rejection becomes a validation attempt
- **WHEN** the lower submission seam raises its frozen closed-code validation exception
- **THEN** the component creates its existing `validation_failed` terminal attempt with
  `submission_validation`, while any other submission/storage exception propagates
  unchanged

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

### Requirement: Shared submit validation records a distinct post-candidate Journal fact

When the shared work-unit component receives a candidate that reached its deterministic
submit-validation boundary, it SHALL record the boundary as a correlated
`post_candidate` Event Journal validation fact. A rejected candidate SHALL retain only
the existing canonical submission-validation code collection; a successful submission
SHALL retain no post-candidate rejection fact. The component SHALL not label this
boundary as `initial` or `repair`, because those stages remain reserved for the
worker-local candidate validation observations.

This fact is a Bundle-local diagnostic projection only. It SHALL not change candidate
validation, attempt status, failure category, retry eligibility, ledger commit, gate
evaluation, checkpoint state, route, terminal disposition, or lifecycle action. The
component SHALL continue to propagate only its existing frozen typed validation
rejection through the existing controller path. (`WOU-012`)

#### Scenario: Rejected submitted candidate retains its own validation stage
- **WHEN** a Wave0 or Wave1 candidate reaches the shared submit validator and receives
  canonical validation codes
- **THEN** the correlated Journal records one `post_candidate` validation fact with
  those codes while the existing attempt remains a `submission_validation` failure

#### Scenario: Accepted candidate does not fabricate a later failure
- **WHEN** a candidate passes shared submit validation and is committed through the
  existing ledger path
- **THEN** no `post_candidate` rejection fact is recorded and the existing submit and
  terminal projections remain unchanged
