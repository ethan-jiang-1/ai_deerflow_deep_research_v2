> req: LDO-001, LDO-002, LDO-003, LDO-004, LDO-005, LDO-006, LDO-007, LDO-008

## ADDED Requirements

### Requirement: Versioned trace frames project committed boundaries with honest active visits

The observation surface SHALL project each committed or suspended boundary, and
each non-committed failed segment, as one immutable versioned `TraceFrame` whose
closed field set is: `schema_version`, `bundle_id`, `frame_sequence`, `visit_id`,
`generation`, `node`, `outcome`, `route`, `next_nodes`, `changed_field_names`,
work/attempt/model/tool counts, existing safe budget facts,
`node_agent_context_count`, opaque `node_context_collection_ref`,
`context_quality`, wrapper-measured `duration_ms`, `failure_category`, terminal
disposition, pending-input projection, and `observation_quality`
(`complete | degraded | unavailable`) with a bounded gap reason. A frame with a
commit SHALL be identified by its checkpoint identity; a failure without a
checkpoint SHALL be identified by its failure event sequence; `visit_id` SHALL
correlate segments and SHALL NOT be a uniqueness key. Frames SHALL NOT embed raw
State values, generalized `input_summary`/`output_delta`, raw model/tool
payloads, or host paths. A `TracePage` SHALL carry at most one
`ActiveVisitProjection` whose state is `running`, `committing`, or `uncertain`;
only a checkpoint commit or a determined non-committed failure SHALL produce a
frame. Incremental reads SHALL use an opaque versioned `TraceReadCursor`
covering both checkpoint position and journal high watermark. Live reads of a
verified Bundle and full replay SHALL produce equivalent frames and ordering;
the projector SHALL NOT launch a graph, scan the workspace for a handle, or
accept a caller-chosen State path. (`LDO-001`, `LDO-002`)

#### Scenario: Replay and incremental live reads agree
- **WHEN** a Journal-complete Bundle is read once as full replay and once as
  incremental live reads separated by a restart on the opaque cursor
- **THEN** both reads expose the same frames, ordering, and terminal disposition

#### Scenario: A journal-completed event before commit is not a frame
- **WHEN** a node body records completed but the wrapper or gate fails before a
  checkpoint commit exists
- **THEN** the projector yields a failed frame identified by the failure event
  sequence and never a completed boundary frame

#### Scenario: Unmatched started yields an uncertain active projection
- **WHEN** a journal holds a started node fact with no matching outcome, no
  checkpoint, and no live execution evidence
- **THEN** the page carries `ActiveVisitProjection(uncertain)` and no frame is
  fabricated for it

#### Scenario: Degraded journal keeps checkpoint boundary skeletons
- **WHEN** journal events are missing, malformed, or evicted for a committed
  boundary
- **THEN** the boundary frame persists from checkpoint identity with
  duration/inner facts marked unavailable and `observation_quality=degraded`,
  and no success fact is inferred to fill the gap

#### Scenario: Isolation between concurrent bundles
- **WHEN** two Bundles interleave journal writes and a projector reads one
  verified Bundle
- **THEN** no frame, sequence, or phase from the other Bundle appears, and the
  cursor consumes only the selected Bundle

#### Scenario: Privacy sentinels stay out of default frames
- **WHEN** sentinels for question/profile/evidence/messages/paths are planted in
  checkpoint State
- **THEN** default frames and pages contain none of them; only
  `changed_field_names` and closed facts appear

### Requirement: Invocation duration is measured, never derived from checkpoint spacing

The node wrapper SHALL measure each actual invocation segment with a monotonic
clock and persist the bounded `duration_ms` on the segment's finalized outcome
fact. Human wait, operator inspect time, and pause intervals SHALL NOT be
included in any segment duration, and adjacent checkpoint timestamps SHALL NOT
be presented as node duration. (`LDO-003`)

#### Scenario: Long operator pause does not inflate duration
- **WHEN** a run is suspended at HITL and resumed after an artificial long wait
- **THEN** each recorded segment `duration_ms` reflects only its active
  invocation, and no field labels checkpoint timestamp deltas as duration

### Requirement: Finalized node facts get elevated bounded-retention priority

Within the existing `MAX_EVENT_RECORDS` bound, finalized node outcome facts
(completed/suspended/failed with their segment facts) SHALL be retained with
higher eviction priority than ordinary start and model/tool success facts while
admission, terminal, validation, failure, retry, and exhaustion anchors keep
their existing protection. When capacity still forces drops, the manifest and
`TracePage` SHALL disclose the dropped interval and count, and the affected
frames SHALL be marked degraded. (`LDO-004`)

#### Scenario: A typical short run keeps every finalized node fact
- **WHEN** a fixture run produces more than the bound in total events
- **THEN** all finalized node facts of the retained boundaries survive, protected
  anchors survive, and the dropped interval/count is disclosed

### Requirement: Node context snapshots capture the exact initial invocation envelope before any provider call

For each admitted bridge/node-agent invocation under a local debugger
composition, the runtime SHALL durably persist one versioned, immutable,
Bundle-private `NodeContextSnapshot` after cognitive-program rendering and
model/tool/policy admission resolve but before `agent.ainvoke` or the first
provider call. The snapshot's closed field set is: exact rendered initial
system policy and initial human message; captured bytes and content hashes of
the base `runtime_policy.md` and the selected capability body; bounded
`NodeExecutionRequest` facts; safe model/profile label; requested and enforced
tool names/posture; the full `ExecutionBudget`; safe structured-output schema
identity/version; virtual workspace/attempt/read/write roots and mount manifest;
source artifact refs; exact Bundle, node, attempt, node-agent ordinal, and
invocation/correlation identity; and capture quality/schema. Multiple
`run_agent` invocations per node (worker, critic, repair) each persist their own
snapshot; snapshots SHALL NOT be overwritten or evicted while the debug Bundle
is usable, and same-id/same-hash replay SHALL be idempotent while
same-id/different-hash SHALL be a typed conflict. Snapshots SHALL be managed as
Bundle-private sensitive content, excluded from default cards, logs, and the
Gateway, and SHALL NOT capture AppConfig, outer identity, host paths, handles,
credentials, chain-of-thought, raw checkpoint/State, or internal provider call
message histories. A write-only, composition-injected, exact-Bundle-bound
recorder protocol SHALL be the only write surface; the bridge SHALL NOT receive
Bundle roots, paths, or a generic writer. When capture, store, or correlation
fails — or the single-Bundle size/count bound is exhausted — the invocation
SHALL fail closed with a typed reason before the first provider call, proven by
a provider spy observing zero calls. Parent visit/segment correlation SHALL be
explicitly supplied by the wrapper/controller, never inferred from node name,
phase, or current State, and a durable collection index SHALL map each segment
to its ordered context refs so eviction of journal events cannot orphan a
retained snapshot. Bounded model/tool call counts and safe outcome facts SHALL
persist as separate per-invocation activity facts, distinct from context
counts. (`LDO-005`)

#### Scenario: Snapshot precedes the first provider call
- **WHEN** a fixture or embedded debugger invocation enters a fresh agent
- **THEN** the provider spy observes zero calls before the snapshot is durably
  committed, and the captured initial messages, runtime MD bytes/hashes,
  request, enforced tools/budget, and mount roots are typed-value equal to the
  renderer/bridge inputs

#### Scenario: Capture failure means zero provider calls
- **WHEN** snapshot write or correlation fails for an admitted invocation
- **THEN** the invocation fails closed with a typed reason before any provider
  call, and no unexplained invocation exists

#### Scenario: Multiple invocations and multiple provider calls stay distinct
- **WHEN** one node performs several `run_agent` invocations and one invocation
  performs several provider calls
- **THEN** each invocation has its own unique context ref, provider-call counts
  grow independently, exactly one initial snapshot exists per invocation, and
  raw per-call histories are marked `NOT_RETAINED`

#### Scenario: Source drift never rewrites captured history
- **WHEN** the current capability or base resource changes after capture
- **THEN** old snapshot bytes and hashes are unchanged, the inspector reports
  `DRIFT` while still serving captured bytes, and a legacy Bundle without
  snapshots reports `CONTEXT_NOT_CAPTURED` instead of reconstruction

#### Scenario: Capacity exhaustion refuses the new invocation, keeps old contexts
- **WHEN** a new invocation's snapshot exceeds the single-record or per-Bundle
  bound
- **THEN** a typed capacity failure is raised before the first provider call and
  all previously retained snapshots remain readable

#### Scenario: Eviction cannot orphan contexts
- **WHEN** journal events are evicted around retained snapshots
- **THEN** the durable collection index still maps every retained context to its
  exact segment, and multi-segment HITL visits never merge

### Requirement: Typed inspectors expose context, curated source, and coverage truth

The context inspector SHALL accept only a lifecycle-verified Bundle ref plus an
opaque context-collection/ref/cursor, and SHALL return paginated bounded
invocation summaries and a per-invocation `NodeContextView` whose fields are
labeled `MODEL_VISIBLE`, `RUNTIME_ENFORCED`, or `DEVELOPER_ONLY`, with a fixed
coverage projection: initial context `CAPTURED`, runtime posture `ENFORCED`,
inner activity `BOUNDED | DEGRADED`, outcome `OBSERVED | UNAVAILABLE`, and
workspace files `CURRENT`. Inner provider request/response message histories
SHALL be presented as `NOT_RETAINED` and never reconstructed from the initial
snapshot, candidate, or State. A curated source reader SHALL accept only node
registry or validated capability identity and SHALL present current
`runtime_policy.md`, the exact capability resource, and the node's
`workflow.md` as non-runtime developer projection with
`MATCH | DRIFT | CURRENT_SOURCE_UNAVAILABLE` status; package source SHALL NOT
mount into the research sandbox and no caller-selected source path SHALL be
readable. A deterministic node SHALL report zero node-agent invocations rather
than a fabricated prompt. (`LDO-006`)

#### Scenario: Coverage strip discloses every layer honestly
- **WHEN** an inspector view is opened for an invocation with bounded activity
  and an unavailable terminal outcome
- **THEN** the view labels initial context CAPTURED, posture ENFORCED, activity
  BOUNDED, outcome UNAVAILABLE, files CURRENT, and marks raw provider histories
  NOT_RETAINED

#### Scenario: Curated source stays non-runtime and bounded
- **WHEN** a developer guide view is opened and when an arbitrary source path is
  requested
- **THEN** the guide renders current `workflow.md` marked NOT MODEL VISIBLE with
  drift status, and the arbitrary path request is typed-denied

### Requirement: Operator workspace reading is bounded, policy-labeled, and composition-injected

The `OperatorWorkspaceReader` SHALL be constructed only by composition with
trusted mounted roots and an access policy; list and preview calls SHALL accept
only relative paths or lifecycle-verified Bundle/content refs, and SHALL return
typed bounded `WorkspacePage`/`FilePreview` results or restricted/unavailable
denials without absolute host paths. The reader SHALL enumerate all
composition-injected virtual mounts with effective read/write/attempt roots,
label entries `MODEL_READ`, `MODEL_WRITE`, `OPERATOR_ONLY`, or `RESTRICTED`,
keep current files labeled `CURRENT` versus captured refs labeled
`CAPTURED_AT_NODE_AGENT_INVOCATION`, verify immutable hashes when present, and
never claim a whole-workspace point-in-time snapshot. Path escape, absolute
paths, symlink traversal, foreign trusted scopes, raw checkpoint/State,
credentials, and non-contract binaries SHALL be typed-denied. Path selection
SHALL never bind a Bundle, infer lifecycle, or grant driving. (`LDO-007`)

#### Scenario: Tree and command reads agree under one interface
- **WHEN** an operator lists and previews operator-visible content through the
  reader
- **THEN** identical requests return identical results regardless of caller,
  with relative paths and policy labels only

#### Scenario: Escapes and private scopes are denied without leakage
- **WHEN** requests use `..`, absolute paths, symlink escapes, or target private
  State, checkpoint, secret, or foreign-scope content
- **THEN** the reader returns typed restricted/unavailable denials with no host
  path or content leakage, and the current session's binding, cursor, and
  control state are unchanged

#### Scenario: CURRENT and CAPTURED time semantics stay distinct
- **WHEN** a workspace file changes after an invocation captured its ref/hash
- **THEN** the reader shows the changed file as CURRENT, the captured ref/hash
  still verifies against the captured bytes, and no full-snapshot claim is made

### Requirement: Adapters consume typed observation views and the read-side spike retires

Presentation adapters SHALL consume only the typed interfaces of this capability
(`TracePage`, `NodeContextPage`/`NodeContextView`/`NodeSourceView`,
`WorkspacePage`/`FilePreview`) and SHALL NOT render or rebuild prompts, load
package resources, compile graphs, open checkpoint databases, resolve arbitrary
paths, or scan for bundles. The `scripts/experiments/tui_trace.py` spike SHALL
be replaced by formal interface tests and deleted or reduced to a thin adapter
that knows no SQLite, recipe, or serde detail. (`LDO-008`)

#### Scenario: The spike no longer exists as a contract
- **WHEN** the repository is searched for the former spike entry point and its
  direct SQLite/recipe access
- **THEN** formal interface tests own the coverage and the former spike path is
  gone or reduced to a typed thin adapter
