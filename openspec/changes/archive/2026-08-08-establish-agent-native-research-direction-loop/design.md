## Context

See `proposal.md` for motivation and the six delta specs for required behavior. Six
verified current facts shape the implementation:

- the installed public skill and dedicated Agent already use DeerFlow's supported
  composition path, but their Markdown describes wire actions rather than a follow-up
  decision workflow; full `SKILL.md` content is automatically injected only by explicit
  slash activation, while an ordinary turn is told to call `read_file`, which the
  dedicated Agent does not currently expose. The requested ordinary natural-language
  UX therefore needs the existing `file:read` group rather than a copied prompt or
  slash-only workaround;
- Bundle-local State has one `admitted_refinement` slot, but admission currently
  replaces that slot, no production active-graph path consumes it, and ended
  refinement does not start graph execution;
- the accepted profile artifact contains `scope_boundaries` and `custom_notes`, while
  topic planning reads only short graph-State projections and therefore omits both;
- the two topic-planning capability resources are runtime-loaded and zero-tool, but
  most reusable planning method still lives in Python prompt assembly; and
- the installed LangGraph `aupdate_state` implementation executes the selected graph
  node's checkpoint writers rather than its node body. A zero-API local probe composed
  from the production `StateGraph` topology, reducers, and rerun writer/edge with fixture
  adapters for external dependencies observed that a deterministic update supplied as
  `as_node="rerun"` creates the pending `topic_planning` task. That proves neither a
  Bundle-contained SQLite terminal snapshot nor the lifecycle two-record transition,
  both of which remain Phase 0 feasibility obligations; and
- `UV_OFFLINE=1 make test-assets` currently fails because 13 approved requirement ids
  used by `@impl` declarations are absent from their main-spec checker-recognized
  `> req:` source. The active deltas temporarily declare `DRH-005` and `TOP-008`, so
  the in-change red output lists the remaining 11; all 13 main-spec declarations still
  require repair before archive.

The implementation remains downstream under `deep_research_harness/`. It may consume
the existing public `deerflow.*` skill/agent interfaces in integration tests, but it
does not edit `backend/` or `frontend/`, add a public action, or make a generic DeerFlow
checkpoint authoritative for a Deep Research Run.

## Goals / Non-Goals

**Goals:**

- deliver one end-to-end, same-Bundle direction loop behind the existing five-action
  public interface;
- make the lifecycle/graph module deep: callers submit one bounded refinement and
  receive one typed result while crash consistency, writer ordering, rerun preparation,
  and truthful projection remain internal;
- give accepted profile notes and one current-round refinement a canonical bounded path
  into topic planning;
- make public controller and topic-planning Markdown real cognitive programs while
  preserving deterministic admission; and
- make later implementation conditional on small, explicit Go/No-Go evidence gates.

**Non-Goals:**

- a refinement queue, semantic merge, supersede UI, unlimited direction history, or
  cross-Bundle direction transfer;
- a generic `Note` domain object or sixth lifecycle action;
- mid-node interruption, immediate mutation beneath a running graph writer, or a new
  scheduler/background worker;
- migration of the other node capabilities, changes to their tools/memory/subagents,
  or broad prompt cleanup;
- consolidation of the evidence registry, removal of existing behavioral tests, a
  credentialed full-real release run, or a quality threshold based on one live run.

## Decisions

### 1. One change advances through five gated phases

The change remains one review/archive unit, but implementation does not begin every
surface at once. Each phase has a bounded exit condition. A No-Go leaves later tasks
unchecked and causes the design/specs to be revised inside this change; it does not
silently open several compensating changes.

| Phase | Smallest deliverable | Go condition | No-Go response |
| --- | --- | --- | --- |
| 0. Establish a trustworthy start | Repair only the 13 missing approved `> req:` declarations; prove that the dedicated Agent can be provisioned only when the existing effective `file:read` group has a usable `read_file`; prove the committed controller is available on its ordinary non-slash DeerFlow path; compose the production `StateGraph` topology, reducers, and rerun writer/edge with fixture adapters for external dependencies, then prove a Bundle-contained terminal graph checkpoint can accept the typed full-rerun update through `aupdate_state(..., as_node="rerun")` and re-enter `topic_planning` without another Bundle or external API call; and prove the existing POSIX storage foundation can serialize independent contenders at a validated scope directory and Bundle root, release a cancelled waiter or dead holder, and reject root replacement without creating a lifecycle record. | `UV_OFFLINE=1 make test-assets` is green; configuration tests prove the exact Agent/preflight/rollback boundary; the loader test observes the committed skill in the real ordinary loading sequence; the graph feasibility test observes the same `bundle_id`, next generation, production topology/reducers/writer, no downstream cognitive work before Bundle-State commit, and the `topic_planning` route after it; and the coordination probe proves the required descriptor/liveness behavior. | Stop before State/result/Markdown expansion. Record the exact unsupported public interface, unapproved privilege, storage primitive, or graph transition as an unchecked task and revise this design; do not introduce an external checkpoint, copied loader, slash-only test masquerading as ordinary UX, second Run, lifecycle registry, or all-real provider call as a graph-API substitute. |
| 1. Make admission truthful | Add bounded pending/current-round refinement facts, ceiling-bounded private replay receipts, idempotent replay, no-overwrite conflict, the strict text-bearing and textless `refine` forms, compatible State reads, shared Bundle-local admission coordination, and typed public result projection. | Reducer and lifecycle matrices pass for a literal pre-change State mapping with no write-on-read, pending/current/retained-receipt replay, same-key mismatch conflict, different-second conflict, terminal-continuation form rejection outside its State predicate, every exhausted-terminal projection, independent-instance CAS including HITL1 profile materialization, process reopen, pending-response separation, ceiling, unavailable target, and redaction. | Do not connect graph work or advertise richer skill behavior. Resolve the State owner or result contract first. |
| 2. Make one same-Bundle round real | Add crash-consistent graph preparation, existing full-rerun reuse, a single execution owner, ended-Bundle lazy start, terminal-boundary consumption for an active Bundle, and one explicit no-text continuation of an already pending terminal direction. A post-CAS textless retry is only a matching queued-task recovery, never a new active admission. | Partial graph and restart tests prove one prepared token, one generation increment, one continuation owner, retained evidence, stale-writer rejection, no downstream work before the State commit, exact post-CAS queued-task recovery, actual `topic_planning` progress, and no external recovery. | Keep the direction pending and the public result honest. Do not compensate with last-write-wins, a second Bundle, a session broker, or a claimed application. |
| 3. Complete the agent-native vertical slice | Expand the one public `SKILL.md`, slim SOUL, read the canonical profile, pass notes/current-round refinement into topic planning, and move the reusable planning/repair method into the two existing capability resources. | Actual loader, scripted lead handoff, final-prompt capture, zero-tool bridge, parser/materializer, and one end-to-end direction-effect workflow all pass. | Revert only the unproved stage within the change and preserve the deterministic lifecycle closure; do not migrate other nodes. |
| 4. Calibrate and close | Add bounded versioned controller/topic-planning evaluation cases, run deterministic gates, record plan/closeout findings, and document claim limits. | All required deterministic gates pass; every actionable review finding is an ordinary completed task; supplemental evaluation records execution separately from cognitive review. | Leave the affected task open and do not archive. A missing credential or inconclusive cognitive run is recorded as limited evidence, not converted into deterministic failure or pass. |

This ordering spends early effort only on current blockers and feasibility. Phase 0 can
invalidate the proposed graph technique before the domain/result and Markdown surfaces
grow.

### 2. Freeze three domain meanings; do not model a generic note

The Deep Research product glossary is updated with the following separation:

| Meaning | Canonical term | Lifecycle path | Durable owner |
| --- | --- | --- | --- |
| Bounded context accepted during Research Confirmation | Accepted Profile Note | accepted profile materialization | canonical profile artifact referenced by Bundle State |
| Answer to the one current human subject | Correlated Research Response | `resume` | pending request/message correlation in Bundle-local State |
| Independent adjustment to the same Run | Run Refinement | `refine` | pending/current-round refinement facts in Bundle-local State |

Words such as "note", "remember", "adjust", or "fix" are raw user language, not
domain discriminators. The lead agent may classify them only with the visible pending
subject and current lifecycle facts; ambiguity results in clarification before a tool
call. `custom_notes` and `scope_boundaries` remain profile content. A Run Refinement
does not rewrite `profile.json`, and a Correlated Research Response cannot smuggle in a
second lifecycle effect. After Research Confirmation, a request to persist or mutate a
profile note has no hidden lifecycle path: the controller makes no lifecycle call and
does not promise a `profile.json` write. It may ask whether the user instead intends a
bounded same-Run direction; only a clear independent direction then follows the normal
`refine` path.

Alternative considered: add a `note` action and inbox. Rejected because it would leave
the effect owner undefined, duplicate `resume`/`refine`, and create another durable
message authority.

### 3. Keep one pending slot and one current-round refinement

Bundle-local State remains the sole lifecycle authority. The compatible State extension
retains the existing pending slot and adds only enough bounded data to distinguish
trusted replay and the current round:

| Semantic field | Meaning | Writer |
| --- | --- | --- |
| pending refinement | bounded text, a runtime-owned operation key, and a private canonical digest, or a legacy text-only pending value | Bundle lifecycle only |
| current-round refinement | bounded text, the trusted operation key and private canonical digest that admitted it, committed round/generation, and deterministic transition token | Bundle lifecycle only |
| applied-refinement replay receipts | at most the current full-rerun generation ceiling of private operation-key/digest/round/generation receipts, with no direction text | Bundle lifecycle only |
| refinement round / generation | existing monotonic authorities | lifecycle and existing rerun controller under their current reducer rules |

The operation key comes from trusted delivery context. The reflected tool uses the
current `tool_call_id`; other adapters must derive a key from an operation record they
own. No public argument may provide it. The canonical text digest is used only inside
the lifecycle module to verify reuse of one operation key and to keep a legacy
text-only pending value effect-free. It is not an idempotency key for a later trusted
operation. The current record retains both private values so a post-application
delivery of the same operation can be proven a replay rather than create another round;
neither value is projected. The current production composition pins the full-rerun
ceiling at two. The rerun module exposes one internal pure capacity predicate that takes
that trusted bound; a single immutable rerun policy is selected by runtime composition
and passed to lifecycle admission/receipt validation, the shared compiler, and the rerun
node dependencies. It is neither a public tool argument nor an Agent/model choice. The
alternate test bound at or below the existing public generation ceiling may exercise the
lifecycle boundary to prove allowed/rejected capacity decisions, but an alternate bound
above that ceiling may exercise only the pure compiler/direct-node seam. It SHALL NOT
drive a public result, work-unit contract, Bundle State/checkpoint, lifecycle, or full
graph continuation until a later change widens every affected public/runtime contract.
Every permitted alternate composition binds the same policy to all of its participating
components. A fixed private receipt is retained
for each committed legal operation through that capacity, so a replay remains
recognizable after the current-round text has been superseded. A receipt contains only
operation key, digest, applied round, and generation; it is not direction text or a
user-visible history. Changing the production ceiling or exposing an operator override
requires a later change to revise the rerun-owned policy, receipt bound, compatibility
story, and state/replay evidence together.

Admission for the text-bearing direction form under shared Bundle-local State
coordination and a revision compare-and-swap follows this closed table:

| Existing fact | Incoming operation | Result |
| --- | --- | --- |
| same operation key and same digest is pending, current-round, or in a retained replay receipt | replay | no write; return the submitted-operation `refinement_pending` or `refinement_applied` code and the post-call Bundle refinement projection |
| same operation key but a different digest is pending, current-round, or in a retained replay receipt | trusted-operation mismatch | no write; return `refinement_conflict` as the submitted-operation code and preserve the first direction and Bundle projection |
| legacy text-only pending value has the same digest | compatibility replay | no write; return `refinement_pending` and the existing pending Bundle projection because the prior operation key is unavailable |
| a pending refinement exists under a different operation key | competing refinement, including identical text | no write; return `refinement_conflict` and the unchanged Bundle projection |
| no pending refinement, whether or not a current round or receipt has the same digest, and generation permits another round | valid new operation | persist one pending refinement; retain any current-round record; return `refinement_pending` and `pending` or `applied_with_pending` from the Bundle projection |
| no future generation is legal | valid text | no admission; return the existing bounded rerun-exhausted/blocked outcome |
| target is unavailable or requires an explicit ended id | any | preserve the existing unavailable/explicit-target behavior |

`refine` also has one deliberately non-overlapping continuation form. Its
`refinement` field is omitted or JSON `null` (never a blank string), and its `bundle_id`
is mandatory. The tool schema rejects an omitted-text call without that id; the lifecycle accepts the
explicit form only after reading the selected Bundle under its transition exclusion: it
must be available, terminal, and
hold one pending direction. The form asks to continue that already durable direction;
it supplies no direction text, receives no public operation key/digest, writes no new
admission or profile field, and uses the pending record's existing trusted identity and
round token. It may take the ordinary ended-Bundle preparation/commit path, including
preparation-token reconciliation, only when capacity and the one-active rule also hold.
It is rejected with the existing bounded invalid-transition or unavailable/active-Bundle
outcome without State or graph mutation when the explicit target is active or suspended,
has no pending direction, is unavailable, or cannot legally begin another round. A
text-bearing request remains a direction submission: it never becomes a
continuation merely because its text resembles the pending direction.

The continuation form is a user-visible control, not an automatic recovery. The public
skill proposes it only after the user explicitly asks to continue the queued direction
and only with the `bundle_id` from a current typed Bundle result. It neither recovers
hidden text from conversation/profile content nor follows a terminal result on its own.
For a same-call race, a continuation that read the pending record may report
`refinement_applied` only after it commits or observes that exact record's committed
token; a later fresh no-text request after the pending record is gone is an invalid
transition, never a claim that an unrelated current round was its effect.

Only the current applied refinement retains direction text as structured State; earlier
directions remain observable only through their already-produced rounds and artifacts.
The bounded private receipts preserve one trusted operation's replay identity, not
direction content or a user-visible history, so this does not create an unbounded
history contract. A later operation may intentionally repeat the same text once no
direction is pending; it is still subject to generation capacity. The current compatible
Bundle-State version accepts the literal complete mapping written before this change,
including existing text-only `admitted_refinement` values, without rewriting the file or
revision merely to read it; every new optional field defaults absent on that read.
Unknown keys and an incompatible schema still fail closed.

Alternative considered: bounded FIFO. Rejected for the first slice because ordering,
coalescing, cancellation, capacity, and user-visible queue controls multiply the
interface before one direction is proven effective. Alternative considered: visible
supersede. Rejected because it requires a new human decision and audit history. Silent
last-write-wins is not an alternative.

### 4. The MVP safe point is the terminal boundary of the current round

For this change, a legal refinement boundary is deliberately narrower than every graph
superstep:

- an available ended Bundle is already at the boundary and may begin its explicitly
  targeted next round immediately;
- an active graph reaches an automatic refinement boundary only after its current graph
  invocation commits a `COMPLETED` terminal snapshot and Bundle progress has been
  synchronized;
- a suspended graph is not at the boundary. Its current human subject remains visible
  and correlated until `resume` resolves it and the current round later becomes
  terminal.

`STOPPED`, `CANCELLED`, and `BLOCKED` are terminal but are not automatic refinement
boundaries. They retain a pending direction without consuming or discarding it. A later
explicit selected textless continuation `refine` may proceed with that exact stored
direction, while a text-bearing `refine` is still subject to ordinary
admission/conflict rules. This prevents a user stop/cancel, or a failed current round,
from silently restarting research while retaining the direction as an honest bounded
fact.

This means an active refinement can wait for the current round to finish. The typed
result says pending; the public skill must not promise immediate replanning. This is the
lowest-risk first semantics that can reuse the current public invocation model without
adding a control node before every cognitive phase.

Alternative considered: inspect the pending slot between every graph node. Rejected
because it would spread lifecycle reads and conditional edges across the topology and
make every node know refinement control. Alternative considered: interrupt a running
node. Rejected because it cannot preserve current writer and external-call semantics.

### 5. Prepare the rerun idempotently before publishing application

Bundle State and the Bundle-contained graph checkpoint are separate durable files, so a
single filesystem transaction cannot honestly cover both. The current State-store lock
is instance-local and cannot coordinate separately constructed stores or processes.
The existing `WorkUnitStore` already proves the local POSIX foundation needed here:
no-follow descriptors, advisory `flock`, off-loop/cancellation-aware acquisition, and
fresh descriptor-versus-path liveness comparison. Phase 0 proves that the same foundation
also supports the required scope-directory and Bundle-root use on the supported runtime
filesystem before lifecycle work begins.

The lifecycle/graph module then adds a small coordination adapter that contains no
lifecycle facts and is usable by independent runtime instances. It has three distinct,
non-authoritative exclusions:

- a short trusted-scope-directory exclusion, used only to serialize fresh Bundle
  publication with an ended Bundle's terminal-to-active refinement commit; it stores no
  scope record, pointer, manifest, or lock file in the scope bucket;
- a short Bundle transition exclusion for every published Bundle State
  read/validate/reducer/write sequence, including admission, RequestBundleStore/HITL1
  profile materialization's resulting `profile_ref` projection, response consumption,
  cancellation/terminal updates, graph-progress projection, checkpoint preparation, and
  Bundle-State CAS; and
- a Bundle execution exclusion held across each selected-Bundle `ainvoke` and any
  immediate terminal-boundary continuation owned by that invocation.

The execution exclusion does not block the transition exclusion, so an active Run can
still admit one pending direction while graph work runs. Every graph entry (`start`,
`resume`, an authorized refinement continuation, and its exact post-CAS queued-task
recovery) uses the execution exclusion;
contenders re-read the selected checkpoint after acquiring it and run only an actually
pending graph task. Acquisition and release stay off the event loop; cancellation while
waiting leaves no State/checkpoint write, and process death releases the advisory
descriptor. After acquiring either Bundle exclusion and immediately before each State
write, checkpoint update, or graph invocation, the adapter reopens the selected Bundle
through its validated no-follow path and compares its device/inode identity. Removal or
replacement is `unavailable`, never a reason to recreate a root or reuse a detached
descriptor. The only nested order is scope then transition for an ended reactivation;
no path holds a transition exclusion while waiting for execution. The module exposes one
committed Bundle fact through this internal two-record protocol:

For an already-published Bundle, no lifecycle State writer or RequestBundleStore/HITL1
permitted State reduction bypasses the transition exclusion. HITL1 retains only its
existing profile/interaction field authority; the coordinator makes its read/reduce/write
sequence re-read and reapply that permitted reducer after a lawful concurrent direction
admission rather than granting the node lifecycle authority. The existing revision field
remains the in-lock stale-write fence and a defensive compatibility check; it is not
relied on as a cross-process mutex. Read-only
`status` takes no exclusion and returns one durable snapshot without reconciliation.
Fresh Bundle staging/publish remains under the scope exclusion before a Bundle root
exists. This keeps a concurrent `resume`, `cancel`, terminal projection, or admission
from replacing another State writer while retaining the separate execution exclusion for
long graph work.

1. For an ended target, acquire the trusted-scope exclusion first, verify no other
   Bundle is active in that scope, then acquire its transition exclusion. For an active
   target, acquire only the transition exclusion. Read the pending refinement, Bundle
   revision, and terminal graph snapshot; verify the legal boundary and generation
   ceiling, and derive a deterministic round token from Bundle id, target generation,
   and the pending operation/digest. A terminal textless continuation is authorized
   solely by this read of the existing pending record; it has no substitute direction,
   operation identity, or admission write of its own.
2. Compute one typed full-rerun update through a pure deterministic compiler extracted
   from and shared with the existing rerun node's planner/materializer. Its only inputs
   are the terminal graph snapshot and the committed candidate's bounded
   `run_refinement` source, token, and direction. It forces `full` scope and reuses the
   existing generation ceiling, invalidation, and route rules; it has no checkpoint,
   Bundle-State, model, tool, provider, or artifact side effect. It is internal to the
   lifecycle/graph module, cannot be called by a public adapter, and is not a second
   route authority.
3. Prepare the graph only by submitting that exact compiler output to the compiled
   production graph's `aupdate_state(..., as_node="rerun")` checkpoint-update path.
   That writes through the production rerun writer and conditional edge, but does not
   execute the rerun node wrapper or any downstream node. Preparation records the round
   token and current-round refinement as graph data for the later continuation, but it
   MUST NOT invoke `rerun`, `topic_planning`, or any other node; call a model, tool, or
   provider; or publish topics, artifacts, or a graph-progress projection before
   Bundle-State commit. Phase 0 proves this specific no-downstream-work boundary with a
   Bundle-contained SQLite checkpoint rather than assuming that a checkpoint API is
   inert.
4. Still under those exclusions, compare-and-swap Bundle State from pending to
   current-round applied using the same token and target generation. For an ended target,
   this is the sole terminal-to-active commit while the scope exclusion is held. The
   committed current-round token is the one continuation authorization; no separate
   controller or durable lifecycle record is introduced. Until this Bundle-State commit
succeeds, public projection remains the preceding terminal State with its pending
direction, even if the internal graph preparation is durable. That State's legal next
action is explicit selected `refine` only while capacity permits it; otherwise it is
`start`, while the pending fact remains inspectable. Its textless continuation predicate
stays at the lifecycle boundary, and `status` remains a read-only observation that never
becomes a hidden reconciliation trigger.
5. Release the scope and transition exclusions. If the eligible `COMPLETED` terminal
   projection that discovered the pending direction already owns the execution
   exclusion, it re-reads the selected checkpoint and runs the matching queued task
   under that existing owner; it does not re-acquire its own execution exclusion.
   Otherwise acquire the Bundle's execution exclusion, then re-read the selected
   checkpoint and committed State/token. Only a pending graph task for the matching
   current round may enter `ainvoke`. A competing continuation observes the completed
   or otherwise owned task after it acquires this exclusion and does not invoke it again.
   Each later graph-progress projection reacquires the transition exclusion and may
   update State only when its Bundle identity, generation, round token, and
   active/terminal State are still authorized; a stale, mismatched, or terminal-losing
   snapshot makes no State write. After a CAS-before-continuation crash, an explicit
   selected textless retry may enter this execution step only when Bundle State has no
   pending human or later direction and its current token exactly matches the sole
   queued `topic_planning` task in the Bundle-contained checkpoint. It does not enter
   admission, prepare another update, or make ordinary active/suspended textless calls
   legal.

Crash reconciliation is token-based and idempotent:

- a crash before graph preparation leaves only pending State;
- a crash after graph preparation but before Bundle commit finds the matching token and
  completes the same CAS without preparing another generation. A later text-bearing
  `refine` first reconciles that pending operation before considering its incoming
  direction: the same trusted operation receives `refinement_applied`; a different
  operation receives `refinement_conflict` while the post-reconciliation Bundle
  projection is `applied`. Recovery ends that incoming admission attempt rather than
  falling through to the ordinary no-pending admission row in the same call. A qualified
  textless terminal continuation may likewise reconcile only that already-read pending
  record and returns `refinement_applied` only for its exact committed token; it cannot
  enter ordinary admission. The different text-bearing operation may make a separate
  later `refine` call once the originally pending slot is clear;
- a crash after Bundle commit but before graph continuation observes the applied token,
  acquires the execution exclusion, and continues the already-prepared graph on replay
  of the graph-owning action. An explicit selected textless retry is such an action only
  when the current State/token and its one queued `topic_planning` task match exactly;
  and
- a crash during continuation releases the execution exclusion with process death; a
  later authorized graph-owning action re-reads the selected checkpoint and uses the
  graph's existing bounded node/provider recovery semantics. This can never create a
  second refinement round or allow a stale projection to publish it; and
- a mismatched token, generation, Bundle identity, or stale revision fails closed and
  cannot be projected back into Bundle State.

`status` remains read-only and never performs reconciliation or graph work. The selected
text-bearing `refine` path may reconcile its own pending prepared transition; the
qualified textless terminal form may reconcile only the existing pending record it
selected; and its explicit post-CAS retry may continue only a matching current-token
queued task. An already-committed current-round graph-owning continuation may continue
it. A generic checkpoint, session record, conversation memory, or diagnostic never may.

The final projection of an active graph and an arriving `refine` may race at the
eligible `COMPLETED` terminal boundary. Both re-evaluate the selected Bundle under the
transition exclusion: the final projection preserves an already-admitted pending
direction and, while retaining its execution ownership, prepares and continues that one
round; a direction admitted just after terminal projection follows the ended-Bundle path.
Exactly one path may prepare/CAS the token; the execution exclusion then serializes its
continuation. A `STOPPED`, `CANCELLED`, or `BLOCKED` projection instead preserves the
pending fact without preparation or continuation until a later explicit selected
textless continuation request.

The external seam stays small: `BundleControl` asks the lifecycle/graph module to admit
or continue a refinement and receives a `BundleControlResult`. The graph-checkpoint
preparation helpers are internal seams used by focused tests, not public adapter
interfaces.

### 5.1 The requested ordinary controller route uses the existing `file:read` group

The requested UX is ordinary natural-language control through DeerFlow's Markdown
workflow, not a requirement for users to prefix every request with
`/deep-research-controller`. This change therefore selects the existing `file:read`
group route. The normal DeerFlow prompt lists a matching skill and directs the lead
agent to load its `SKILL.md`; full content is automatically injected only for an
explicit slash activation. The dedicated Agent currently has only
`deep-research-control`, so it has `deep_research` but not `read_file`. Its `skills`
list is an allowlist, not a preload mechanism.

The committed dedicated-Agent template and authenticated Agent API fixture will use the
ordered groups `[deep-research-control, file:read]`. `file:read` remains wholly owned by
the effective DeerFlow configuration. The downstream fragment MUST NOT define, merge,
repair, delete, or rename that group or any tool assigned to it. This deliberately
exposes every tool assigned to the configured group (the repository example currently
places `ls`, `read_file`, `glob`, and `grep` there), not a path-only reader. The Agent
may use those tools under DeerFlow's existing sandbox/path policy, but the workflow and
result contract do not claim exclusive tool isolation or a narrower filesystem boundary.

Before downstream configuration creates or replaces its dedicated-Agent files, reports
that route ready, or presents the authenticated provisioning fixture as ready, it performs
one pure effective-config preflight. It requires one unambiguous `file:read` group and
a tool assigned to that group whose resolved public tool name is `read_file`. It records
only a redacted prerequisite failure; it does not probe arbitrary files or construct a
new sandbox. A missing group, a missing or misbound `read_file`, or ambiguous group/tool
definition leaves the dedicated entry route `not_ready`, makes no Agent file mutation,
and never falls back to a control-only Agent, copied Markdown, or slash-only UX. Public
skill/control-group materialization and the global `deep_research` tool remain separately
assessed and usable according to their existing contracts. The authenticated fixture has
the same two-group shape and is not a reduced fallback; its use remains contingent on a
passing prerequisite check.

The public skill MUST NOT add `allowed-tools` frontmatter as a way to narrow this
surface. DeerFlow applies that field while composing the tool policy for every Agent
that loads the public skill; it is not a dedicated-Agent-only capability restriction.
The dedicated Agent's group list, the existing sandbox policy, strict lifecycle schema,
and runtime admission are the relevant deterministic enforcers.

The ordinary-route proof starts from a non-slash user turn. With normal discovery, the
first relevant AIMessage calls `read_file` on the canonical public `SKILL.md`; its
ToolMessage must match the committed digest, and DeerFlow captures a durable
`skill_context` reference. The later AIMessage in that same lead-agent run issues one
exclusive `deep_research` call with no sibling tool. The full Markdown body remains in
the actual tool exchange; after compaction `skill_context` is a reference/reminder, not
a second durable copy, so a later use must re-read the file. If DeerFlow deferred skill
discovery is enabled, `describe_skill` may precede that read, but it never substitutes
for it or for the later exclusive call. A slash-only activation, direct system-prompt
copy, or prewritten lifecycle call cannot discharge this proof.

Alternative considered: explicit slash activation. Rejected because it would abandon the
ordinary-language UX this change exists to establish. Alternative considered: an upstream
preload or skill-path-only reader. It could reduce the broader read surface, but requires
an upstream contract and is outside this downstream-only change.

### 6. Reuse the existing rerun node with a distinct direction source

One pure rerun-update compiler is shared by the existing rerun node and the
Bundle-bound checkpoint preparation. For `rerun_source=run_refinement`, its bounded
input is the round token and current-round refinement; it forces `full` scope, applies
the existing generation/invalidation checks, and yields the existing route to
`topic_planning`. Preparation supplies that exact typed update to the compiled graph as
`as_node="rerun"`; only after Bundle-State commit does normal graph invocation run the
queued node. It does not manufacture or persist a `hitl2_rerun_payload`, because that
payload means a different human decision.

The current-round refinement is assignment data only. It cannot choose scope, route,
topic ids, paths, or artifacts. The existing full-rerun materializer remains the deep
module for those effects.

Alternative considered: bypass rerun and invoke topic planning directly. Rejected
because it would duplicate generation, invalidation, evidence-retention, gate-reset,
and route semantics in the runtime adapter.

### 7. Read profile notes from the canonical artifact, not more short fields

`profile_ref` remains the pointer stored in Bundle/graph State. The request-bundle
module gains one read operation that accepts that already-selected reference, performs
contained nonblocking file access, parses the canonical `ResearchProfile`, and verifies
schema and content hash. Topic planning declares the existing request-bundle
capability and uses this operation; it never accepts a path.

The deterministic `PlannerAssignment` contains:

- the canonical profile dimensions, including `scope_boundaries` and `custom_notes`;
- the existing request text and coverage fallback;
- the current round's applied refinement, if any; and
- explicit labels that make profile/refinement text research data, not tool or control
  instructions.

Required short State fields are compared with the canonical profile where they remain
needed for routing/compatibility. A missing, hash-invalid, cross-Bundle, schema-invalid,
or contradictory canonical profile fails before model invocation. We do not add notes
as another short checkpoint projection, because that would create a second content
authority and continue the drift that caused this defect.

Alternative considered: add `custom_notes` and `scope_boundaries` to every State model
and prompt. Rejected because it duplicates canonical content and expands every consumer
before one real downstream use is proven.

### 8. Markdown owns method; Python owns trusted projection and admission

The existing two topic-planning capability resources remain the only runtime cognitive
program ids. They are expanded as follows:

- initial capability: decomposition procedure, direction/profile precedence, coverage,
  non-overlap, scope/exclusion construction, self-check, and zero-tool uncertainty
  behavior;
- repair capability: preserve the identical assignment, interpret the draft as data,
  repair only supplied validation failures, self-check, and add no evidence or scope.

Python constructs and bounds `PlannerAssignment`, selects the capability, serializes the
expected output schema, enforces the invocation/recovery ceiling, and calls the existing
parser/materializer. It no longer duplicates the reusable decomposition method in the
objective string. `workflow.md` remains a reader interface and is not loaded at runtime.

The public controller follows the same ownership pattern. One focused `SKILL.md`
contains qualification, the intent/subject decision procedure, target rules, examples,
edge cases, exclusive-call behavior, and typed-result explanation. SOUL contains only
stable identity and honesty posture. Tool schema, trusted runtime, and Bundle lifecycle
remain deterministic authority. The first version stays in one skill file; supporting
resources are added only if the actual loader test and an approved token budget show the
file has become unmaintainable.

Alternative considered: encode the intent classifier in Python. Rejected because the
decision is semantic and would produce an expanding keyword program while still not
teaching the actual DeerFlow lead agent. Alternative considered: put the full decision
table in SOUL and skill. Rejected as duplicate cognitive authority.

### 9. Typed results are the only explanation source

`BundleControlResult` gains two deliberately separate refinement facts. Its existing
`code` reports the outcome for the submitted action only: `refinement_pending` means
that a text-bearing operation is durably pending (including a pending replay),
`refinement_applied` means that a text-bearing operation has a committed round (including
a retained-receipt replay), or that a qualified textless continuation committed or
observed the exact pending record it selected, and `refinement_conflict` means that a
text-bearing operation acquired no lifecycle effect. A conflict code never means the
selected Bundle lacks an applied or pending first direction. A no-text request outside
its terminal-pending predicate returns the existing invalid-transition outcome rather
than being reclassified as a direction conflict.

Every available selected-Bundle result carries a compatible bounded `refinement`
projection derived only from Bundle-local State; unavailable results omit it. Its
`disposition` is exactly one of `none`, `pending`, `applied`, or
`applied_with_pending`. The last form is required because one current applied direction
and one later pending direction are independently legal facts. Its `current_round` is
present only for `applied` and `applied_with_pending`, and is validated with the existing
top-level generation and State monotonicity rules. This projection reports the Bundle
after any lawful admission or reconciliation, not the submitted operation. It contains
no text, digest, operation key, replay receipt, round token, path, or checkpoint fact.

The resulting matrix is closed: a new or replayed pending operation returns
`refinement_pending` with `pending` or `applied_with_pending`; a committed or retained
applied operation returns `refinement_applied` with the current Bundle projection; an
ordinary conflict returns `refinement_conflict` with the untouched projection; and the
post-preparation competitor returns `refinement_conflict` with `applied`. `status`
returns its existing read-only code and any one of the four Bundle dispositions. Existing
unavailable, suspended, terminal, and legal-next-action rules continue to validate the
complete result shape.

Legal next action is derived from direct State and the same trusted immutable rerun
policy that admits a round:

- pending plus a human subject: `resume`;
- pending in an active Bundle without a human subject: `status`;
- pending or applied-with-pending in a terminal Bundle with legal remaining capacity:
  `refine`, because only an explicit selected textless continuation may
  reconcile/continue its pending next round and `status` remains read-only;
- terminal `none` or `applied` with legal remaining capacity: `refine`, but only a
  text-bearing direction form can propose a next round;
- every terminal Bundle where that policy permits no future full rerun: `start`;
  pending facts remain inspectable, but either continuation or a new direction returns
  the owned exhausted/blocked outcome rather than an endlessly advertised retry;
- applied or applied-with-pending work that is active: `status`, or `resume` only when
  the selected Bundle itself exposes a correlated subject;
- conflict: the action legal for the post-call Bundle projection, not a claim that the
  submitted operation applied; and
- unavailable: `start`.

The skill and Agent may explain these fields but cannot turn pending into applied,
conflict into replacement, or unavailable into recovery.

### 10. Evidence follows the real handoff, not file presence

The implementation uses the existing evidence semantics and does not add a new registry
system. Each claim stops at the lowest responsible seam:

| Claim | Required evidence | Explicit claim limit |
| --- | --- | --- |
| Requirement ids are recognized | checker regression plus `UV_OFFLINE=1 make test-assets` | no broader metadata cleanup |
| Public workflow is really composed | effective-config/preflight and configure/rollback tests, then actual DeerFlow loading with the committed content digest and ordinary `read_file` then later-turn handoff | does not prove model judgment or narrow the configured full `file:read` surface |
| One selected action completes the lead/tool/result loop | scripted real lead middleware/tool handoff with typed fake lifecycle outcome after the real selected loading sequence | action selection is scripted |
| Direction cannot overwrite and survives restart | reducer/lifecycle/concurrency/reopen tests through the lifecycle interface | does not prove graph effect |
| Direction starts one same-Bundle round | partial graph, crash-point, stale-writer, ended and active-terminal integration tests | does not prove planning quality |
| Notes/direction reach the cognitive program | final composed prompt capture plus real capability loader/bridge and materializer tests | proves handoff, not semantic compliance |
| Controller/planner make good judgments | versioned bounded Cognitive Evaluation cases with separate execution and review records | supplemental; no single-run release threshold |

The current public replay that prewrites tool calls remains wiring evidence and is
renamed/reclassified accordingly. It is not deleted merely to reduce counts. New
controller cases cover new request, correlated answer, mid-suspension direction,
status, explicit stop, ambiguous criticism, active conflict, ended target, unavailable
Bundle, and mixed answer/direction. Topic-planning cases cover canonical notes,
direction contrast, adversarial control text, and repair without scope expansion.

### 11. Phase 0 fixes declarations, not the evidence architecture

The requirement checker already defines `> req:` as its explicit approved-id source.
Phase 0 repaired the original 13 missing ids in their owning main-spec declarations and
added a known regression fixture. During final mandatory-gate verification, an exact
source regression identified a further 23 pre-existing registry-owned header omissions
that prevent the same verifier from completing. The authorized 7.2a repair adds only
those owning-header declarations and source assertions. Neither repair makes the parser
scrape arbitrary requirement prose, adds a second registry, changes evidence semantics,
or triages the 363 claims. That broader audit remains outside this change.

## Control Ownership

| Surface | Owning transition or predicate | Typed input/output | Writer/evaluator | Recovery and terminal owner | Deterministic proof |
| --- | --- | --- | --- | --- | --- |
| Controller Markdown loading | Lead-agent relevance decision plus the configured skill loader sequence | ordinary user turn -> optional `describe_skill`, canonical `read_file`, durable reference, later lifecycle candidate | effective config owns group/tool definition; configure preflight and dedicated-Agent template own route availability | missing/misbound group leaves the entry route not-ready; no synthetic preload or reduced Agent | configure/provisioning matrix and actual non-slash loader sequence |
| Follow-up selection | DeerFlow lead turn proposes one tool or clarification | user turn + visible typed subject -> tool candidate | skill is advisory; tool schema/runtime admits | lead clarification is one turn; runtime denial is final for that call | selected-route loader and scripted later-turn handoff |
| Refinement admission | Bundle lifecycle CAS table | bounded refinement + trusted operation key -> typed disposition | lifecycle writer only | only the same operation replays; a different operation conflicts while the pending slot is occupied | reducer, concurrent lifecycle, reopen |
| Terminal pending continuation | lifecycle terminal-pending predicate | explicit bundle id + omitted refinement + stored pending direction -> ordinary round transition or bounded denial | lifecycle writer only | only a user-requested explicit selected form can continue that exact pending record; it cannot add/recover text or mutate a profile | tool-schema/state, terminal-workflow, and controller-handoff tests |
| Round preparation and continuation | terminal-boundary predicate, deterministic round token, selected checkpoint pending-task predicate, and scope-versus-ended-reactivation predicate | pending refinement + terminal Bundle/graph facts -> typed full-rerun update -> one owned graph continuation | shared pure rerun compiler evaluates; no-fact scope/transition exclusions prepare and commit; production graph's `as_node="rerun"` writer/edge prepares; execution exclusion owns `ainvoke` | token reconciliation plus checkpoint/root re-read; mismatches, cancellation, root loss, or a completed task fail closed | crash-point partial graph, execution-contention, root-loss, start/reactivation, and stale-writer tests |
| Topic candidate | `rerun -> topic_planning -> next|exhausted` | `PlannerAssignment` -> `TopicPlan` candidate | capability is advisory; parser/materializer admits; planner writes registry | existing bounded provider recovery or one structured repair, then blocked | prompt capture, bridge, parser/materializer, real-node scripted tests |
| Result explanation | result-shape validator | Bundle State -> `BundleControlResult` | lifecycle projection owns fields | no prose retry/recovery | result matrix and scripted final response |

## Risks / Trade-offs

- [A terminal-only active safe point can delay a user's direction] -> Project pending
  honestly, preserve the current human subject, and use evaluation/transcript evidence
  before considering a future finer-grained boundary.
- [A terminal pending direction could otherwise require the user to reproduce hidden
  text] -> Reuse `refine`'s explicit selected textless continuation form only under the
  terminal-pending State predicate, retain text-bearing conflict/replay semantics, and
  prove that no automatic or implicit continuation is possible.
- [Two durable records cannot be committed in one filesystem transaction] -> Use a
  deterministic round token, checkpoint-only preparation, no-fact scope/Bundle
  transition/execution exclusions built on the existing POSIX storage foundation, one
  shared pure rerun-update compiler, production rerun writer/edge, Bundle-State CAS,
  root revalidation, token-fenced projection, and crash-point/execution-contention
  reconciliation tests; never use status or an external store as recovery.
- [The controller skill is indexed but cannot be read on an ordinary turn] -> The
  selected `file:read` route exposes the configured full read group, so preflight its
  group/tool binding, materialize no reduced fallback Agent, and prove the real
  sequence; do not let slash activation or copied Markdown stand in for it.
- [A richer skill may increase prompt cost or still classify poorly] -> Keep one focused
  workflow under the actual loader limit, measure digest/tokens/cost/latency, and use
  repeated cognitive cases without making one result a release threshold.
- [Accepted profile text can contain instruction-like content] -> Delimit it as research
  data, keep tools forbidden, and enforce all candidate effects through the existing
  parser/materializer and State writers.
- [Reading canonical profile adds local I/O to a model node] -> Put blocking reads behind
  the existing request-bundle module and off the async event loop; verify containment,
  size, schema, and hash before invocation.
- [Compatible optional State fields can hide stale assumptions] -> Add explicit old-State
  fixtures and missing-field defaults, while incompatible versions remain unavailable.
- [One change still spans several modules] -> Preserve one causal owner, phase gates, and
  the small public interfaces above; stop at the first failed Go condition rather than
  widening scope.

## Migration Plan

1. Complete Phase 0 without changing production lifecycle behavior. The requirement-id
   declarations, dedicated-Agent `file:read` preflight/template, and loader/graph
   feasibility tests are independently revertible; rollback leaves the operator-owned
   `file:read` group untouched.
2. Add optional bounded refinement/result projections with old-State and old-no-
   refinement fixtures. Do not rewrite retained Bundles during configure or startup.
3. Enable graph application only after its deterministic admission and crash tests are
   green. Rollback before any applied round leaves old Bundles readable; rollback after
   an applied round retains ordinary prior/new generation artifacts but older code may
   inspect the Bundle only if it accepts the compatible optional fields.
4. Install the expanded skill/SOUL and topic capability content through the existing
   idempotent configure path. Rollback restores the prior committed content; it does not
   mutate Bundle State or authenticated Agent ownership.
5. Add evaluation cases last. They create new isolated local evaluation Bundles and do
   not migrate production Runs.

No database migration, upstream deployment, or background service rollout is required.
Before archive, verify the actual selected-change boundary and all ordinary tasks; do
not describe a supplemental cognitive evaluation as deterministic closeout evidence.
