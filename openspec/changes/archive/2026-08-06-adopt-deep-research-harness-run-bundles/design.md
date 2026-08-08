## Context

See [proposal.md](proposal.md) for motivation and the approved scope. The current
runtime couples a conversation-derived `research_id` to an application-selected
bundle directory and an external graph checkpoint. `runtime/research.py` derives the
identity, creates the bundle locator, selects a checkpoint namespace, and projects
both facts through public results. `runtime/graph_host.py` compiles lifecycle actions
with the configured external checkpointer. The retained-session, lifecycle-binding,
and session-operations stack then records, locates, and authorizes that external
state. Content stores receive both `research_id` and `bundle_directory`.

Those verified current facts produce several durable authorities for one Run. They
cannot represent the approved model in `CONTEXT.md` and ADR-0028, where a Run Bundle
contains the State, evidence, and content for one Deep Research Run and can be
deleted independently. The target is therefore an authority migration, not a text
rename.

The structural root is also a repository contract: `project-structure.toml`, the
generated module-guide locator, Docker/profile configuration, tests, scripts, and
documentation enumerate `deerflow_research/`. The project directory changes to
`deep_research_harness/`; the Python distribution, import namespace, and public tool
do not.

## Goals / Non-Goals

**Goals:**

- Make one Run Bundle the sole durable authority for one Deep Research Run's State,
  evidence, and content.
- Establish one runtime-owned lifecycle boundary for Bundle creation, scoped
  discovery, State mutation, refinement admission, and typed control outcomes.
- Enforce at most one active Bundle in a trusted outer-conversation scope while
  allowing any number of retained ended Bundles.
- Make Bundle loss truthful and final for that Run, including during active work.
- Move the downstream filesystem root atomically across all governed structural
  consumers without renaming the Python/distribution/public-tool identities.
- Give every projection the same typed `bundle_id` result and preserve zero-API,
  lowest-responsible deterministic evidence.

**Non-Goals:**

- Preserve or auto-migrate a deleted Bundle through session manifests, bindings,
  external checkpoints, logs, caches, or a replacement State.
- Add a durable cross-conversation Run registry, active-Bundle pointer, index, or
  session authority.
- Change upstream `backend/` or `frontend/`, introduce a new host API, or make DeerFlow
  import the downstream package.
- Rename `deerflow-deep-research`, `deerflow_deep_research`, or `deep_research`.
- Conflate Cognitive Evaluation Run Bundles with Deep Research Runs, their storage,
  discovery, controls, or retention.
- Change node model roles, model/tool policy, or evaluation workflow semantics.

## Decisions

### 1. Use a runtime-owned Run Bundle lifecycle module as the one control boundary

The target runtime will expose one deep module whose public interface accepts trusted
conversation scope plus typed action input and returns a typed Bundle lifecycle
result. It owns the following operations:

- create and atomically publish a fresh Bundle;
- validate a supplied Current Bundle Handle;
- discover an available Bundle from directories and Bundle-local State in the trusted
  scope when the handle is absent;
- read State, admit a refinement, and perform lifecycle control; and
- produce the only typed outcome consumed by tool, graph, CLI, TUI, workbench, and
  retained-inspection adapters.

The module is the owner because it is where trusted host context, filesystem I/O,
persistence, and lifecycle actions meet. `domain/` will define the stable typed
identity, State/result contracts, and pure validation, but will not select roots or
authorize context. Node and presentation adapters receive a bound Bundle context or
typed result only; they do not receive a lifecycle root, construct a path, derive an
identity, select a checkpointer, or keep an active-Run cache.

The implementation may split this module into focused internal stores/adapters, but
only this interface can mutate lifecycle State or resolve a Run for a control action.
A scope-level synchronization primitive is permitted to serialize create/refinement
admission. It is coordination only, not a persisted Run record, discovery source, or
second lifecycle authority.

**Alternative considered:** retain `ResearchActionHandler` as the authority and add
Bundle fields around its external checkpoint. This would preserve the old identity and
checkpoint split, leaving deletion/recovery semantics false. It is rejected.

### 2. Make `bundle_id` the one Run identity and keep the handle transient

Starting a new Run creates a fresh opaque `bundle_id`. The identifier names the Bundle
directory, Run, and public control target while that Bundle is available. It MUST NOT
be derived from user, conversation, message, checkpoint, or request text. The concrete
encoding, length, and directory spelling remain internal details as long as opacity,
freshness, containment, and validation are preserved.

The outer conversation can retain a `Current Bundle Handle` containing that id. It is
a convenience for the next control or refinement, not durable lifecycle authority. A
handler validates it by opening the scoped Bundle and reading its State; a stale or
foreign handle cannot establish a Run. If no handle is available, the lifecycle module
scans only Bundle directories under the trusted conversation scope and reads their
Bundle-local State. It selects exactly one active Bundle. Missing, malformed,
unavailable, or ambiguous candidates fail closed with a typed result; discovery never
falls back to a global scan, a session index, binding, external checkpoint, or cache.

The trusted scope may map to a private containment bucket derived only from the trusted
runtime envelope. That bucket is neither a Run identity nor an active pointer: it may
contain Bundle directories and their local State, but no scope manifest, registry,
index, session binding, or replacement State. `bundle_id` remains the only public,
directory, and Run identity.

For a duplicate delivery of one start command, only the already-published Bundle's
own State may carry any idempotency correlation needed to reproject the same result.
No correlation record may become a cross-Bundle registry. A distinct start is admitted
only when scoped discovery finds no active Bundle; ended Bundles do not block it.

**Alternative considered:** use a conversation-derived id as both directory and
checkpoint key. It prevents independent fresh Runs and treats a conversation as a
durable Run. It is rejected.

### 3. Store all lifecycle State inside the selected Bundle

Every durable fact needed to determine a Deep Research Run's lifecycle, pending
interaction, refinement round, admitted refinement, terminal disposition, and legal
control action belongs in that Bundle's State. The graph/checkpoint adapter for Deep
Research must persist its recoverable lifecycle snapshot under the selected Bundle;
the exact internal checkpoint representation is not public behavior. A generic
external checkpointer may not be read as lifecycle authority, selected as a fallback,
or used to create replacement State for a missing Bundle.

Bundle State is authoritative only while its containing Bundle is available. A
non-terminal State, including a suspended State awaiting user input, means active. A
terminal current refinement round means ended. Bundle loss is not written as a
terminal State because there is no authoritative State location left to write it.

Existing graph and node code can retain graph-local transient values during an
invocation, but it must route every durable lifecycle write through the selected
Bundle State writer. Blocking file I/O remains off the async event loop. The writer
uses contained paths, version/atomic-write semantics, and serialization appropriate
to the existing storage contract; those mechanics are implementation choices that
must preserve the requirements in the new capability spec.

**Alternative considered:** retain an external LangGraph checkpoint as the source of
truth and mirror a summary into the Bundle. This turns the Bundle into a projection
and permits forbidden recovery after deletion. It is rejected.

### 4. Publish a Bundle atomically and contain all content beneath it

Fresh-start admission runs under scope coordination:

1. Inspect the trusted scope for an existing active Bundle.
2. When none exists, allocate a fresh opaque `bundle_id` and a private staging
   location below the trusted Run storage boundary.
3. Create initial Bundle-local State and the required initial content roots in that
   staging location.
4. Validate containment and atomically publish the finished Bundle directory.
5. Return the typed result and transient Current Bundle Handle only after publication.

A discoverable Bundle therefore cannot exist without initial State/content, and a
partial staging directory cannot be selected by discovery. Content stores receive a
runtime-bound Bundle reference rather than `(research_id, bundle_directory)` or a
caller-supplied path. They keep their existing atomicity, lock, and containment
guarantees, but resolve all artifact paths from that reference. The internal child
layout remains encapsulated by the lifecycle/store boundary.

**Alternative considered:** create a public directory first and allow later actions to
fill State/content. A crash can then create an apparently valid but unauthorizable
Run. It is rejected.

### 5. Model active, ended, refinement, and one-active admission from Bundle State

The lifecycle module derives activity from the selected Bundle's State rather than a
conversation-level status flag. At most one State in a trusted conversation scope may
be non-terminal. A completed/blocked/cancelled/refinement-terminal Bundle remains
inspectable and does not prevent a fresh Run. An explicit refinement of an available
ended Bundle starts a later refinement round in the same Bundle and retains prior
materials for inspection only when no different Bundle is active in that scope.

The public actions are deliberately distinct:

- `resume` is only a correlated `AcceptedHumanResponse` to the current Bundle-local
  pending interaction. It cannot be used as a generic refinement and cannot reactivate
  an ended Bundle.
- `refine` requires bounded refinement text. It may name an available `bundle_id`; when
  it does not, the lifecycle module uses the valid Current Bundle Handle or exactly one
  active Bundle found by scoped discovery. Selecting an ended Bundle for another round
  requires an explicit id, so an ambiguous set of retained ended Bundles cannot be
  guessed.
- A refinement may arrive while the selected Bundle is active, awaiting input, or
  ended. While input is pending, it is a later admitted refinement and does not replace
  the required response. For an ended selected Bundle, admission first checks that no
  different Bundle is active. A conflict returns the current legal continuation rather
  than queueing a second active Run.

The module validates the target and stores an admitted refinement in Bundle State or a
Bundle-contained control record. It does not rewrite an in-flight State writer or race
an active graph update. The graph consumes the admitted refinement only at an explicit
safe, durable control point and then records the resulting transition in the same
Bundle. The concrete queue/sequence encoding is internal; the required ordering is:
accepted input is durable before it is consumed, and the old writer cannot be partially
overwritten by the new input.

**Alternative considered:** make every refinement a new Bundle. It loses the user's
continuous research object and gives one conversation multiple active targets. It is
rejected.

### 6. Treat loss as unavailable and retire external session authority

Every lifecycle action validates Bundle availability before it reads or writes State,
content, or a graph checkpoint. If the Bundle disappears, becomes unreadable, or fails
integrity checks, the module returns a closed typed unavailable outcome and stops
further persistence for that Run. An active invocation detects loss at its next
authoritative store/checkpoint boundary and cannot recreate the directory or publish
replacement State.

`run_session`, lifecycle-binding, session-operation, session-workbench, and legacy
migration surfaces will be removed or rebuilt as non-authoritative inspection adapters.
No durable external binding, owner index, broker verification, session reference, or
checkpoint namespace may select, authorize, resume, or recover a Run. Retained logs,
diagnostics, audits, and historical manifests can disclose only permitted observation
facts and must not contradict the unavailable result. The change intentionally does
not migrate old lifecycle state into new Bundles; implementation may offer
operator-readable migration diagnostics only if they remain observation-only.

**Alternative considered:** retain the old binding as a fallback for missing Bundles.
That makes an external record a recovery authority and violates deletion semantics.
It is rejected.

### 7. Use one typed result and bounded projections at every entry surface

The public tool, graph bridge, CLI, TUI, workbench, and retained inspection surfaces
will consume a shared typed lifecycle result. It carries a bounded Bundle identity
when disclosure is valid, lifecycle/availability outcome, any legal action state, and
a truthful next action. A human projection explains the outcome and legal next action;
an AI-facing projection exposes bounded machine facts without prose parsing. Neither
surface exposes host paths, checkpoint keys, raw exceptions, or enough detail to
cross conversation boundaries.

Public actions are `start`, `resume`, `status`, `cancel`, and `refine`; their target
identity is `bundle_id`, never `research_id` or `session_ref`. Status and cancel
validate the same Bundle authority. `resume` consumes only a correlated pending response;
`refine` carries bounded refinement text and follows the target rules above. A completed
Bundle may be explicitly selected for another round only when it is available in trusted
scope and no different Bundle is active. Adapters cannot invent a new active Run, infer
State from report files, or resolve an unavailable Run from old records.

**Alternative considered:** translate old session/research identities separately per
adapter. This would leave multiple public control vocabularies and duplicate control
logic. It is rejected.

### 8. Keep Cognitive Evaluation Bundles deliberately separate

Cognitive Evaluation has its own Run Workspace/Bundle and must continue to be
created, stored, discovered, and retained independently. Deep Research scoped
discovery never scans evaluation paths; evaluation code never supplies a Deep Research
Bundle as lifecycle state. The migration audits shared naming and root configurations
so the structural move cannot accidentally make the two domains discover each other.

**Alternative considered:** reuse the generic name "Run Bundle" as a discovery
protocol across both systems. Shared vocabulary does not imply shared lifecycle
authority, so this is rejected.

### 9. Move the filesystem root through the structural authority, not a global replace

The implementation will rename the project directory to `deep_research_harness/` and
first update `project-structure.toml`, its owning delta, and the generated locator.
It will then migrate every governed path consumer: Makefiles, Docker mounts, profile
scripts, fixtures, tests, docs, public skill/SOUL, import-boundary checks, and
automation. Historical archived plans/ADRs remain historical facts unless a reference
would make an active command or contract wrong. The Python `src/deerflow_deep_research`
and `src_fake/deerflow_deep_research_fixtures` paths remain package roots under the
new structural root.

The root move is a structural contract migration and must be completed atomically in
the change's final tree. The architecture registry is the enumerated source of truth;
the generated guide block is rendered from it rather than hand-edited.

**Alternative considered:** leave a permanent `deerflow_research` compatibility
directory or symlink. It would preserve two structural roots and make agents/tools
ambiguous. It is rejected unless a separate approved compatibility change owns a
specific external consumer.

### 10. Preserve EVH-024 through one Bundle-bound public execution path

EVH-024 remains the one selected full-real release proof. Its fixed Chinese request,
model-led HITL1 proposal, natural-language confirmation, canonical Python source set,
Chinese report, and citation assertions do not change. The migration changes only the
authority it executes and observes: the release runner calls the ordinary trusted
public control entry, carries the returned opaque `bundle_id` only through trusted
control context, and reads lifecycle, report, citation, and containment facts from the
selected available Run Bundle.

This change closes the deterministic authority migration, not the provider-dependent
success of a credentialed execution. The manually selected full-real success acceptance
is deferred to `_backlog/plans/evh-024-release-acceptance-diagnosis.md`, which must
first establish a fast red-capable diagnostic loop. No later release attempt may be
presented as proof for this change unless it is separately authorized and succeeds.

The runtime-owned Bundle boundary starts and continues the real graph at the selected
Bundle. It does not compile a release-only external GraphHost, derive a `research_id`,
select a generic checkpoint namespace, or reconstruct report facts from a workspace
path. The release runner remains an observer/test driver: it may submit the declared
human responses and fail a release attempt, but it cannot create a second controller,
write lifecycle State, or infer terminal success from a non-Bundle artifact.

**Alternative considered:** keep the legacy release runner as a temporary
session/checkpoint compatibility path. That would leave the only full-real public-entry
proof validating a retired authority model, so it is rejected.

## Authority Map

| Fact / operation | Target direct owner | Allowed projections | Explicitly not authoritative |
| --- | --- | --- | --- |
| Fresh Bundle ID and published root | Runtime-owned Bundle lifecycle module | Typed lifecycle result, transient Current Bundle Handle | Derived `research_id`, caller path, session record |
| Run existence, activity, round, pending input, admitted refinement | Bundle-local Research State | Status/control result, retained inspection view | Outer conversation, external checkpoint, logs, cache |
| Evidence and content | Contained stores beneath the selected Bundle | Artifact/content view | Report path, session manifest, adapter-local cache |
| Trusted conversation scope | Existing trusted runtime envelope/context boundary | Scoped locator input to lifecycle module | Caller-provided user/thread strings, Bundle contents |
| One-active admission | Lifecycle module plus non-durable scope coordination and scoped State scan | Typed conflict/continuation outcome | Durable active pointer, registry, owner index |
| Bundle availability | Filesystem plus lifecycle module validation | Typed unavailable outcome, diagnostics | External checkpoint/binding/session recovery |
| Human/AI-visible outcome | Typed lifecycle result | Tool/CLI/TUI/workbench/SOUL/skill text | Any presentation text or diagnostic |
| EVH-024 release execution/result observation | Runtime-owned Bundle execution boundary and contained report/citation artifacts | Bounded release attempt/report | Release runner, external GraphHost snapshot, workspace-derived path |

## State and Control Flow

```text
trusted outer conversation scope
            |
            v
  Current Bundle Handle (optional, transient)
            |
            v
runtime-owned Bundle lifecycle module
  validate handle | scoped Bundle discovery | scope coordination
            |
            v
one selected Run Bundle
  Bundle-local Research State + evidence + content
            |
            v
typed lifecycle result -> tool / graph / CLI / TUI / workbench
```

For a fresh start, the module publishes an initialized Bundle before it returns a
result. For a control or refinement, it resolves the Bundle first, verifies
availability/State, and only then reads or mutates it. For a missing handle, it scans
the trusted scope. For loss at any point, it stops using that Run and returns the
unavailable outcome. No arrow in this flow is an external checkpoint/session fallback.

## Impact Matrix and Implementation Routing

| Area | Current responsibility to replace or audit | Target responsibility | Required evidence |
| --- | --- | --- | --- |
| Public tool/control | `tool.py`, `domain/lifecycle.py`, `runtime/research.py` expose/derive `research_id`; `resume` is the only post-start action that consumes user input. | Typed `bundle_id` controls, transient Current Bundle Handle projection, correlated `resume`, and separate bounded `refine`. | Public lifecycle/replay/action-separation tests. |
| State/checkpoint | `runtime/research.py`, `domain/state.py`, `runtime/graph_host.py`, `runtime/checkpoint.py` use external checkpoint/state. | Bundle-local State/checkpoint adapter only. | State persistence, transition, and loss tests. |
| Bundle/content | `domain/bundle.py`, bootstrap/request/work-unit stores receive identity/path pairs. | Bound Bundle reference and contained stores. | Atomic publication and containment tests. |
| Session stack | run-session, binding, operations, workbench authorize/locate from retained records. | Removed or observation-only adapters over Bundle facts. | Discovery/control/no-recovery regression tests. |
| Nodes | bootstrap, HITL, agent runtime, planning, Wave1/Wave2 carry old identity/path/checkpoint assumptions. | Consume bound Bundle context only. | Focused node/store tests plus audit assertions. |
| Presentation | CLI, TUI, demo, workbench, skill/SOUL have old vocabulary/control state. | Shared typed Bundle lifecycle outcome. | Contract and transcript tests. |
| Structure/config | registry, Docker, profiles, scripts, docs, prompt-review workspace, fixtures enumerate old root. | One `deep_research_harness/` root. | Architecture, configuration, mount, prompt-catalog, and import-boundary tests. |
| Evaluation | evidence assets encode old lifecycle/path assumptions, including the legacy EVH-024 session/checkpoint runner. | Deterministic scenarios cover new authority and loss; EVH-024 retains its one real public-entry proof by observing its selected Bundle; evaluation Bundles stay separate. | Requirement/evidence registry checks, release control-plane tests, and selected full-real acceptance. |

## Accepted-Contract Migration Coverage

This is an apply-admission map, not a second behavioral authority. It records where
accepted wording currently carries the old root or a competing Run authority so the
implementation sequence cannot silently leave a contradictory contract behind.

| Legacy contract family | Accepted requirement groups to reconcile | Target reading rule | Direct proof |
| --- | --- | --- | --- |
| Physical downstream root | `PRS-001/004/005/006/011/014/015`, `DEC-001/003`, `DPL-001/004/005/007`, `LCP-001/002`, `FSI-001`, `NPC-002`, `DRC-002/006`, `RED-002`, `FCO-001`, `REC-005/006`, `EVH-005/010`, `NOA-007`, `HIN-005` | `deep_research_harness/` is the one current filesystem root; package/distribution/public-tool names stay unchanged; historical archives remain factual only. | Architecture, configuration/mount, prompt-review, path-scan, and module-command tests. |
| Public Run identity and action vocabulary | `RUI-001/002/003/006/007/008/009`, `REG-003/004/005/006/012/016`, `RER-001/002/003/006/007/009`, `REC-004/005/006`, `RWB-001/002/006/007` | `bundle_id` is the only Run/directory/public-control identity; `resume` is correlated response only; `refine` has bounded text and needs an explicit id to reactivate an ended Bundle. | Tool schema/replay, action-separation, CLI/TUI/workbench contract tests. |
| Bundle-contained durable authority | `REG-004/005/006/007/009/010/011/012/013/014/016`, `BON-001/002/004/006`, `HIN-001/002/004/005`, `TOP-008`, `WON-009`, `WSN-007`, `NOA-014` | Bundle-local State owns lifecycle and pending/refinement facts; contained ledger/evidence/content retain their direct authority within that Bundle; external checkpoints cannot recover a Run. | Atomic publication, state reload, safe-point, loss, node-context, and containment tests. |
| Work/evidence path authority | `WOU-001/003/004/005/006/009`, `REG-009/010`, `RSV-001/002/003` | Stores receive a runtime-bound Bundle reference and never a caller path, `research_id`, checkpoint locator, or session reference. | Store containment, ledger replay, artifact-view, and Bundle-loss tests. |
| Retained observation and local operations | `RUS-001/002/003/004/006`, `RES-001/002/003/004`, `RDO-001/002/003/004/005/006`, `RWB-003/005`, `RER-006`, `RSV-004` | Logs, diagnostics, retained manifests, and workbench timelines may observe but never select, authorize, resume, or reconstruct a Bundle. | No-external-recovery, deletion, observation-redaction, and local-operation tests. |
| Evaluation-domain separation | `CES-001..008`, `PRS-015`, `EVH-025` | Evaluation Workspaces/Bundles remain outside Deep Research scope discovery and cannot restore a lost Deep Research Run. | Cross-domain negative discovery case and structural registry check. |

## Risks / Trade-offs

- [Large structural move produces stale paths in scripts, docs, mounts, or test
  fixtures] -> Freeze a current-HEAD path inventory, update the architecture registry
  first, retain a mechanically checked old-root detector, and run structural/config
  tests before the full gate.
- [A compatibility shim quietly recreates external lifecycle authority] -> Keep
  compatibility limited to package/import/tool names; make all legacy session and
  checkpoint reads observation-only and add deletion/no-recovery tests.
- [Concurrent control creates two active Bundles or overwrites State] -> Serialize
  scoped admission, use atomic publish/State writes, reject ended-Bundle
  reactivation while another Bundle is active, and test concurrent starts, refinements,
  pending-input separation, and restart/discovery paths deterministically.
- [Bundle deletion during execution leaves a partial writer or false terminal state]
  -> Revalidate at authoritative write/checkpoint boundaries, fail closed, and assert
  no replacement directory/State is produced.
- [The new module becomes a broad service with duplicate helpers] -> Keep the public
  interface limited to Bundle lifecycle operations and leave domain validation,
  content writes, and projections in their existing owners.
- [Adapter changes diverge in wording or machine semantics] -> Use one typed result,
  test all adapters against it, and prohibit path/checkpoint/session inference.
- [Cognitive Evaluation storage accidentally enters Deep Research discovery] -> Keep
  separate roots/types and add cross-domain negative discovery tests.
- [No automatic migration leaves old retained Runs unavailable] -> This is intentional
  and explicit. Preserve only bounded read-only diagnostics; a new Run is the legal
  recovery.

## Migration Plan

1. Re-run the `research_id`, `bundle_directory`, old-root, external-checkpoint, and
   session-authority impact inventory at the apply HEAD. Classify every hit as
   lifecycle authority, bound-content consumer, projection, structural consumer,
   historical archive, or unaffected.
2. Add focused red tests for the approved behavioral matrix: fresh opaque Bundle,
   one-active admission, transient-handle continuation, absent-handle discovery,
   safe refinement, ended-Bundle reactivation, loss/no recovery, isolation, and
   shared projections.
3. Introduce the typed Bundle identity/State/result contracts and runtime lifecycle
   module. Migrate creation, scoped discovery, Bundle-local persistence, and safe
   control before removing legacy interfaces.
4. Bind graph/node/content writers to the selected Bundle and remove their ability to
   derive identities, receive arbitrary paths, or select external lifecycle
   checkpoints. Keep their existing contained-write semantics.
5. Replace or retire session/binding/index/broker authority. Convert only valid
   retained records into observations, and add negative tests proving they cannot
   recover a missing Bundle.
6. Migrate tool, graph bridge, CLI, TUI, demo, workbench, SOUL, and public skill to
   the shared typed result and `bundle_id` vocabulary.
7. Rename the structural root and update the registry, generated locator, governed
   configuration/mount/profile consumers, docs, fixtures, and tests in the same final
   tree. Do not retain a second root without separate approval.
8. Update requirement/evidence assets, run focused tests after each behavioral
   slice, then run the complete deterministic gate and strict governance validation.

**Rollback:** before the change is released, revert the implementation as one scoped
change rather than maintaining parallel lifecycle authorities. After a Bundle is
deleted, rollback cannot and must not restore that Run from old external state. A
post-release rollback requires a separately approved compatibility plan if external
consumers need a temporary filesystem-root bridge.

## Open Questions

- The opaque `bundle_id` encoding and exact Bundle-internal child layout can be chosen
  during implementation, provided they do not change freshness, opacity, containment,
  scoped discovery, or deletion requirements.
- The concrete file-backed checkpoint/state adapter and scope-lock primitive can be
  selected during implementation, provided State remains entirely Bundle-local,
  blocking I/O stays off the event loop, and neither mechanism creates a durable
  external lifecycle authority.
- The exact closed result-code names for unavailable, ambiguous, and active-conflict
  outcomes can be aligned with existing typed enums during implementation; their
  distinct observable meanings and legal next actions are fixed by the specs.
