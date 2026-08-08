## Context

Phase 2 stores an owner-only binding and can read a durable checkpoint, but deliberately
does not reconstruct a `TrustedRuntimeEnvelope` or expose operations. Existing lifecycle
handlers derive namespace, sandbox capability, and graph context from the current outer
thread. A later local session command therefore needs a new authority boundary, not a
manifest-backed shortcut.

The current `RuntimeAdapter` can adapt only an active `ToolRuntime`; DeerFlow exposes no
public historical `ToolRuntime` or historical `thread_data` resolver. It does expose
scope-addressed `get_paths()` and `SandboxProvider.acquire_async(thread_id, user_id=...)`
facilities for the Gateway runtime, while the existing standalone `DemoAdapter` owns a
fixed local `LocalSandbox` and contained roots directly. This change therefore resolves a
historical envelope from an already trusted current operation access plus a verified
private binding; it never fabricates a historical runtime object or reads an outer
conversation history.

There are two further constraints that the prior proposal left implicit. The existing
standalone demo uses a same-process memory provider, so it cannot honestly advertise a
restart operation unless its operation-enabled local profile supplies a stable file-SQLite
provider. Also, the checkpoint does not record the graph implementation map: reopening a
full-fake checkpoint with an all-real recipe (or the reverse) would be semantic drift even
if its namespace and provider matched.

## Goals / Non-Goals

**Goals**

- Discover only bounded sessions owned by the authenticated local principal through a
  private owner index, never by scanning retained bundle directories.
- Reopen a selected durable session through private binding plus authoritative
  checkpoint verification, then dispatch the existing lifecycle behavior safely.
- Give local CLI/TUI one shared safe projection for session list, current status, and
  allowed operation results, including a validated owner-visible pending-input view when
  a response can actually be submitted.

**Non-Goals**

- No `backend/`, `frontend/`, Gateway endpoint, Web workbench, production CLI, MCP,
  ACP, public skill, multi-user sharing, existing-session provider migration, retention
  redesign, or artifact-body viewer. A new configured local profile may select file
  SQLite before it starts a session.
- No caller-selected user, outer thread, namespace, path, provider, phase, pending
  request, or reconstructed sandbox. A caller may submit only raw answer text plus an
  expected opaque request id; the broker treats neither as authority. No binding/manifest
  as graph control state.
- No bare CLI/TUI process invents a principal, AppConfig, or sandbox. The local demo
  adapter may create a single configured local operation access; production access remains
  runtime-owned and this change adds no Gateway surface.
- No automatic migration or owner-index backfill for phase-2 binding records, no
  checkpoint-row deletion as part of bundle retention, and no attempt to resume a binding
  whose durable provider or recipe compatibility cannot be independently verified.

## Decisions

### A broker owns discovery and operation authorization

`ResearchSessionOperationBroker` is runtime-owned. It receives a trusted current
principal/runtime access capability, never raw CLI authority. Binding publication stages
private metadata, and only a successfully retained bundle activates an owner-and-profile
scoped private index containing opaque binding references. Discovery starts from that
index, then validates each selected entry against the current principal, profile,
provider, and recipe; it never scans retained bundle directories to discover operations.
Unknown, foreign, corrupt, non-durable, and provider-drift records produce the same
bounded unavailable/denied shape, with no enumeration hint.

The owner-index directory name is derived internally from the trusted principal and a
stable profile identifier carried only by `SessionOperationAccess`; it is subject to the
same no-follow, bounded, atomic, and lock-order rules as the binding files. It is not a
public index or a second lifecycle authority. Existing
`RunSessionStore.list_sessions()` and `inspect()` remain separate legacy observation
commands; legacy bundles are never backfilled into the owner index and never become
broker-operable by inference.

Phase-2 version-1 bindings and any binding missing an owner-index membership or recipe
compatibility value remain valid only for the old read-only verifier/inspection path. The
broker projects them as unavailable rather than guessing a profile or rewriting private
metadata.

Each owner/profile index retains at most `MAX_RETAINED_BUNDLES` (currently 20) active
references. Activation first runs the bounded retention reconciliation; if a safe cleanup
cannot make room, activation fails closed and the new bundle remains inspection-only.
While holding the retained-root lease, cleanup may remove an undiscoverable staged record
only when no validated retained manifest refers to it. Discovery itself never creates,
repairs, or prunes index state.

### Binding activation follows retained-bundle publication

The publisher stages a newly validated binding without an active owner/profile index,
publishes the retained bundle and its ordinary observation records, and activates the
index only after bundle publication succeeds. A failed bundle publication leaves at most
an undiscoverable staged record; it never creates an operation entry. A failed index
activation leaves the bundle inspection-only and its manifest projects binding operations
as unavailable. A later record-bearing publication may retry activation, but it never
guesses or backfills a phase-2 record.

There is deliberately no cross-file transaction between private binding metadata and the
public manifest. The broker trusts only an active index plus verified binding/checkpoint;
the manifest remains a conservative observation. This ordering makes each partial failure
fail closed instead of exposing a discoverable session without a retained bundle.

### Reconstruct from current DeerFlow services, never from a stored envelope

The broker receives a `SessionOperationAccess` created only by `RuntimeAdapter` from an
active trusted runtime or by the fixed local demo-profile adapter. The access carries the
current principal, AppConfig, operation run identity, and progress emitter; it contains no
caller-selected historical scope. After owner-index and binding validation,
`TrustedSessionRuntimeResolver` uses the binding's private outer-thread lookup key with
the current principal through factories carried by the access. A runtime-originated access
uses public `get_paths()` and, only for graph work, public
`SandboxProvider.acquire_async(thread_id, user_id=...)`. A local-profile access uses the
same fixed contained-root and `LocalSandbox` factories its adapter used to start the run;
those factories are profile-owned and do not accept binding/CLI paths or sandbox ids. The
resolver then builds a new runtime-only envelope with the verified historical thread,
current AppConfig, and current operation run identity. It does not construct a historical
`ToolRuntime`, fetch historical `thread_data`, reuse a stored sandbox id, or take any host
path, AppConfig, sandbox, or provider connection from storage.

`open`/`status` use the phase-2 read-only verifier and do not initialize a sandbox.
`resume`/`cancel` call existing handlers through the resolved envelope and revalidate
the current checkpoint/pending interrupt inside the lifecycle handler's namespace lock
immediately before dispatch. A reopened `resume` accepts raw answer text only after the
broker has read the current interrupt; it compares the caller's expected opaque request
id, validates mode/options against that interrupt, and creates an internal brokered
response. Its message id is deterministically derived from the verified binding reference,
current request id, and submitted value so an identical retry remains idempotent without
persisting an answer. Manifest and binding data never supply an answer, phase, cursor, or
request id.

### Recipe compatibility is a validation gate, never a route

Each `SessionOperationAccess` is created for one immutable, profile-owned
`ResearchGraphRecipe` and carries a versioned recipe-compatibility fingerprint. At a
record-bearing bind, the private binding records that fingerprint alongside its existing
scope/provider facts. Before a broker opens a checkpoint or constructs a historical
envelope, it compares the access fingerprint with the stored value. The fingerprint
canonically covers the registered logical topology, explicit implementation map, research
state schema, and resume-protocol version. A mismatch or missing value is unavailable.

The binding fingerprint does not select a recipe, node, phase, or route. The profile has
already selected the only recipe it is allowed to execute; the binding is merely a
fail-closed compatibility check. This prevents a local fake/real mode switch or code
protocol change from reinterpreting an existing checkpoint.

The operation-enabled local demo profile uses a stable file-SQLite path beneath its
owner-only retained root. Its adapter constructs the same profile-owned recipe on a fresh
process and therefore can pass the provider and recipe checks. Same-process demo sessions
remain honestly non-operable after restart. A profile may be selected through the existing
controlled local-profile setup, but a session command does not accept an arbitrary recipe
or implementation map.

### Local mutations share the retained-root dispatch lease

`RunSessionStore.dispatch_lock()` is the established owner-only cross-process retained-root
lease. The local profile adapter already takes it around normal start/resume/cancel
dispatch; this change requires broker `resume` and `cancel` to take the same lease from
binding resolution through handler completion and session publication. That prevents a
fresh local process from consuming the same HITL beside an in-process demo dispatch.
`list`, `open`, and `status` remain lock-free reads and never initialize a sandbox.

Mutation acquisition uses the same lock file but has a bounded retry window (at most 30
seconds); contention returns a redacted busy/unavailable projection before provider,
sandbox, or graph work. The normal local lifecycle adapter adopts that bounded acquisition
too, so it cannot indefinitely wait behind a stale-but-live local operation.

This lease is deliberately local-profile scope, not a claim that the process-local
`GraphHost` locks coordinate Gateway workers. A future Gateway/workbench surface needs an
upstream-compatible distributed mutation boundary before it can reuse these operations.

### Local command shape keeps answers out of process arguments

`make -C agent demo-sessions` retains the legacy read-only `list`, `inspect`, and
`cleanup` commands. It gains profile-mediated `discover`, `open <session_ref>`,
`status <session_ref>`, `cancel <session_ref>`, and
`resume <session_ref> --request-id <opaque_id>` commands. The operation commands first
construct their fixed current-profile `SessionOperationAccess`; no command argument can
select a user, profile, provider, path, recipe, or implementation map.

`open`/`status` may print the validated bounded pending-input view. `resume` reads the
raw answer from an interactive terminal or standard input after the caller supplies the
opaque expected request id; it never accepts the answer as a command-line argument,
prints it, writes it to a manifest/trace/diagnostic, or dispatches on EOF. The broker
re-reads the checkpoint and treats the request id only as a stale-view comparison, not as
authority. The TUI follows the same broker API and keeps the request id in its view model,
not a parallel lifecycle controller.

### Retention revokes operation discovery before deleting a bundle

Cleanup treats a binding/index entry as the capability to discover and operate a retained
session. While holding the existing root and per-bundle liveness locks, it validates the
manifest's opaque binding reference and asks the private binding store to revoke the
matching binding and remove its owner-index entry before deleting the bundle. If revocation
fails, cleanup leaves the bundle intact and reports a bounded skip. If later bundle deletion
fails, it updates the manifest's bounded binding-operation projection to unavailable; the
remaining bundle is safely inspection-only because its operation binding has already been
revoked. Generic checkpoint rows are not deleted in this change.

### Operation matrix remains explicit

| Operation | Authority and provider/checkpoint check | Sandbox | Mutation |
|---|---|---|---|
| `list` | private owner index, current principal, provider and recipe fingerprint; no checkpoint read | no | no |
| `open`, `status` | selected binding plus recipe guard and read-only checkpoint verifier | no | no |
| `resume` | selected binding plus provider/recipe guard, retained-root dispatch lease, latest pending interrupt, then handler-lock revalidation | yes, only after those checks | existing graph handler |
| `cancel` | selected binding plus provider/recipe guard, retained-root dispatch lease, current checkpoint, then handler-lock revalidation | no | existing graph handler |

The broker returns a typed safe projection, not an executable graph or checkpoint.
Manifest/trace/artifact refs remain observations.

### Discovery is bounded and content-free

The shared projection includes opaque session/binding refs, retention, durability,
availability, bounded lifecycle facts, and whitelisted relative artifact references.
For an authorized selected suspended session it may additionally include the existing
bounded `HumanInputRequest` display fields derived from the authoritative pending
interrupt: request id, phase, mode, title, context, and advertised options. This is the
only prompt-shaped data exposed and is necessary for a local owner to answer; it is never
read from a manifest or treated as checkpoint control state. Projections never recursively
enumerate bundle content or return host paths, raw checkpoint data, provider details,
diagnostics bodies, artifact bodies, or raw answers.

## Risks / Trade-offs

- [Resolver crosses a tenant boundary] -> owner index and binding validation compare the
  trusted current principal before paths, namespace, or sandbox resolution; use
  indistinguishable denials.
- [Read-only operation initializes a sandbox] -> test resolver call counts and keep
  verifier outside sandbox-capable paths.
- [Resume bypasses HITL correlation] -> derive the display and internal response from the
  latest checkpointed interrupt, compare the expected request id, and validate again in
  the existing handler while its namespace lock is held.
- [Discovery silently scans foreign bundles] -> make the owner index the only broker
  discovery source; preserve legacy inspection as an explicitly separate observation
  surface.
- [A compatible namespace runs an incompatible graph] -> bind and compare a
  profile-owned recipe fingerprint before any checkpoint operation; never use the stored
  value to select a recipe.
- [Cleanup leaves an operation capability behind] -> revoke matching binding/index before
  deletion under the established retained-root and liveness locks; a revocation failure
  skips cleanup.
- [Publication exposes an operation before its retained bundle] -> stage binding metadata,
  publish the bundle, then activate the owner/profile index; partial publications are
  inspection-only.
- [One local profile discovers another's sessions] -> derive the private index from both
  trusted principal and stable profile identity, then reject mismatched profile/provider/
  recipe before opening any session resource.
- [Two local processes consume one interrupt] -> route every local mutation, including
  broker resume/cancel, through the same retained-root dispatch lease.
- [Artifact discovery leaks data] -> fixed reference whitelist, containment checks, and
  sentinel scans; report viewing remains phase 4.

## Migration Plan

1. Add pure operation/discovery contracts, versioned owner-index/recipe binding metadata,
   and deterministic fail-closed tests.
2. Implement resolver and broker around existing binding/verifier/handlers, including
   brokered resume correlation, handler-lock revalidation, and the shared local dispatch
   lease.
3. Reconcile retention by revoking bindings/index entries before eligible bundle deletion.
4. Adapt the durable local-profile CLI/TUI to an injected broker projection; preserve
   separate legacy inspect commands.
5. Add file-SQLite subprocess, authorization, and no-extra-node evidence; run full
   deterministic verification. Rollback removes new commands without altering existing
   checkpoints, bindings, or bundles.

## Verified Integration Boundary

`RuntimeAdapter` is intentionally current-runtime-only. The harness exposes no public
historical `ToolRuntime` or `thread_data` lookup, so this design does not require either.
Runtime-originated operation access uses public scope-addressed path and sandbox-provider
APIs after a private binding proves the historical thread belongs to its principal. The
standalone profile access uses only its already-owned contained-root and local-sandbox
factories, never raw storage values. The implementation must retain deterministic tests
for both factories proving that historical scope is impossible to select before binding
validation, and must report bounded unavailability when the selected trusted factory
cannot satisfy the validated scope.

The current standalone `DemoAdapter` selects a memory provider and is therefore an
explicit negative case for restart operations. The implementation must add an
operation-enabled, profile-owned file-SQLite adapter path and prove it in a subprocess;
otherwise its sessions remain listable/inspectable but the broker reports them
unavailable. The implementation must also prove that a recipe mismatch is rejected before
opening a provider or constructing a sandbox.
