## Context

The completed run-bundle, binding, and discovery/operation changes establish the
local session boundary in layers:

- `RunSessionStore` owns contained retained-bundle observations and bounded lifecycle
  trace data.
- `SessionLifecycleBindingStore` plus the current provider verifier prove that a
  selected binding still belongs to the fixed local profile.
- `ResearchSessionOperationBroker` discovers only the private owner/profile index,
  exposes redacted projections, and delegates `resume`/`cancel` through the existing
  lifecycle handlers.
- `demo-sessions` and the fake Textual TUI already consume broker projections, but
  neither offers a coherent, durable-session navigation surface.

The desired product vision includes Gateway, Web, and terminal workbenches. The
Deep Research project is nevertheless a downstream consumer: this change may only
write under `agent/` and repository-owned planning/governance documentation. It
cannot add a Gateway router, modify the upstream Web UI, or make the upstream
`deerflow` TUI import downstream code. The delivered surface is therefore an
operation-enabled local terminal workbench; its projection boundary is deliberately
adapter-ready for a later upstream-authorized product surface.

## Goals / Non-Goals

**Goals**

- Give the configured durable local profile one terminal entry point to discover,
  select, reopen, observe, answer, cancel, and revisit its own sessions.
- Present a bounded timeline and a fixed artifact catalog from retained observations
  without treating either one as lifecycle authority.
- Expose contained metadata for an explicitly cataloged artifact with strict type,
  regular-file, no-follow, and redaction policy.
- Reuse the current broker for every selection and lifecycle operation, including
  pending-input request-id correlation and the retained-root dispatch lease.
- Preserve deterministic file-SQLite restart coverage and existing legacy
  `demo-sessions list/inspect/cleanup` behavior.

**Non-Goals**

- No `backend/` or `frontend/` changes, Gateway route, Web page, upstream terminal
  workbench integration, generic production CLI, MCP/ACP interface, or multi-user
  browsing.
- No caller-selected profile, principal, binding path, bundle path, provider, recipe,
  thread, namespace, or checkpoint. A displayed opaque reference is not authority.
- No second graph/lifecycle controller, state file, pending-input source, checkpoint
  migration, report generation, or generic filesystem browser/download endpoint.
- No artifact-body rendering, including profile, diagnostic, report, or other bundle
  content; absent future report artifacts remain unavailable rather than fabricated.

## Decisions

### A runtime-owned workbench reader composes existing authorities

Add frozen public display contracts in `domain/session_workbench.py` and one
runtime-owned `LocalSessionWorkbench` in `runtime/session_workbench.py`.

```text
fixed durable local profile
        |
        v
SessionOperationAccess -> ResearchSessionOperationBroker
                                |                  |
                                |                  +-- lifecycle handlers (resume/cancel)
                                v
                    LocalSessionWorkbench
                       |                 |
                       v                 v
              RunSessionStore      contained artifact reader
                       |
                       v
            manifest + validated lifecycle trace
```

The workbench accepts an opaque `session_ref` only as a selection value. A malformed
local input or unknown artifact catalog key returns bounded unavailable before broker
work. Every remaining selected read first calls broker `open` or `status`; an
unavailable projection stays unavailable and does not trigger a fallback lookup. The
existing broker may open its established checkpoint provider as part of binding and
snapshot verification. Only after it returns an available view does the workbench read
the retained observation and bind it to the selected broker view's opaque research id
internally. That contained reader creates no additional provider, sandbox, graph, or
retained-root authority. The terminal layer receives only frozen workbench projections,
never a binding, envelope, provider, host path, or `RunSessionStore` instance.

This avoids two rejected alternatives:

- Directly reading a research-id-derived retained path from the terminal would turn
  an opaque UI value into a directory authority and bypass profile checks.
- Enriching `SessionOperationView` with raw manifest/trace/artifact bodies would
  broaden every existing CLI/TUI projection and make a read model into a content
  transport protocol.

### Timeline is an observation, never a phase cursor

`RunSessionStore` gains a contained, no-follow read that returns an already-validated
bounded tuple of lifecycle-trace records for an authorized inspection. The workbench
maps it to `WorkbenchTimelineEntry` with only sequence, timestamp, action, status,
phase, generation, pending phase/mode/request-id summary, terminal outcome, closed
failure category, and opaque diagnostic reference. It omits raw trace deltas, prompt
context, user answers, provider payloads, exception bodies, host paths, and unknown
trace fields.

The UI may order and filter these entries for display, but it cannot infer a legal
transition, reconstruct a pending request, or update session status from them. The
broker checkpoint projection remains the sole source for current status and owner
visible pending input. A malformed, oversized, stale, or unavailable trace returns a
bounded unavailable timeline while preserving the broker projection; after broker
authorization, its contained reader causes no additional provider, sandbox, or graph
operation.

### Artifact catalog is fixed, metadata-first, and profile-bound

The workbench has an explicit `ArtifactCatalogPolicy`, owned by runtime rather than
the UI. Its initial catalog contains only currently meaningful contained references:

| Catalog key | Relative reference | Presentation |
|---|---|---|
| `request-marker` | `request/marker.json` | metadata only |
| `request-profile` | `request/profile.json` | metadata only |
| `lifecycle-trace` | `diagnostics/lifecycle.jsonl` | timeline source, not raw content |
| `diagnostics` | `diagnostics/records.jsonl` | metadata only |

Future producer-owned artifacts, including a final report, require their owning change
to add a catalog key and deterministic contract before the workbench can expose them.
The catalog never recursively lists a bundle and never makes `work/`, evidence,
caches, dynamic filenames, or arbitrary `final/` files browseable by inference.

`view_artifact` takes a selected session reference plus one catalog key. It rejects an
unknown key before broker work; for a valid key it reauthorizes the selection through
the broker and maps that key to its fixed relative path. The broker may perform its
established provider verification. If it returns unavailable, the workbench performs no
retained-path read, sandbox acquisition, graph invocation, or additional provider work.
After successful authorization, the runtime reader verifies every parent and leaf
component is contained, non-symlink, regular, owner-only, and within the fixed metadata
policy before returning metadata. No catalog entry returns a body in this change: the
lifecycle trace is consumed only by the dedicated safe timeline mapper, and every other
file stays metadata-only. Responses retain no raw answer, credential, provider detail,
host path, or unchecked content-derived instruction. The workbench does not offer a
generic download command.

The alternative of allowing arbitrary relative paths after a broker selection is
rejected because it would turn one authorized session selection into a broad content
enumeration capability.

### The terminal is a reducer over workbench projections

Add `agent/scripts/session_workbench.py` as the local terminal entry point and keep
the existing fake/real demo TUI as a lifecycle showcase. The new Textual app has one
reducer-owned local presentation state with bounded states for discovery, selected
session, timeline, artifact metadata, pending input, busy, and unavailable.
It may retain the selected opaque reference and expected pending request id for the
current view, but it owns no lifecycle state inference.

All actions route as follows:

| Terminal intent | Runtime call | Mutation/sandbox behavior |
|---|---|---|
| refresh/select/status | `workbench.open` / `workbench.status` | read-only; existing broker verification may use a provider, never a sandbox or graph |
| timeline/catalog/artifact view | authorized workbench read | unknown catalog key stops before broker; otherwise broker authorizes, then the contained reader adds no provider, graph, or sandbox |
| answer pending input | `broker.resume` with current opaque request id | existing broker + handler lock; sandbox only when required |
| cancel | `broker.cancel` | existing broker + dispatch lease; no artificial controller |

The terminal obtains the fixed operation-enabled local profile before it accepts any
session reference. It presents an explicit unavailable state when durable profile setup,
authorization, binding, recipe, provider, retained bundle, or artifact validation
fails. Raw answers stay in the Textual input event and are passed only to broker resume;
they are not put in a command argument, trace, manifest, or metadata projection.

### A separate local command makes the surface honest

Add `make -C agent session-workbench` with a narrow optional launch mode suitable for
the configured local profile. Startup runs the existing profile preflight and explains
that it is a standalone local operator surface, not a Gateway/Web workbench or generic
recovery client. It may show durable-profile availability, but never synthesizes a
principal, AppConfig, sandbox, or recipe from terminal input.

`demo-sessions` retains its legacy commands and remains useful for scripts and narrow
inspection. The new entry is the only workbench navigation surface; it calls the same
underlying broker rather than wrapping CLI text output or duplicating its logic.

### Tests and evidence stay at the lowest responsible seam

Pure contracts cover frozen/redacted projections, catalog key validation, metadata-only
output, and absence of authority fields. Runtime tests cover authorization ordering,
no-follow containment, trace corruption, catalog absence, unknown-key rejection before
broker work, and the rule that a valid broker authorization is followed by no additional
provider/sandbox/graph creation in the contained reader. Textual tests drive the reducer
and user interactions with an injected broker/workbench fake; subprocess file-SQLite
evidence proves a fresh process can discover/select/reopen the same fixed profile session
but cannot use a foreign/stale selection. Existing broker resume/cancel tests remain the
authority proof and are extended only for workbench integration.

## Risks / Trade-offs

- [Workbench becomes a second lifecycle controller] -> Only broker projections drive
  status/pending input, and UI reducer tests prohibit transition inference.
- [Artifact metadata broadens file access] -> Fixed catalog keys, reauthorization,
  contained no-follow reads, regular-file checks, and no body output.
- [Trace reveals sensitive data or becomes a control source] -> Map only fixed safe
  fields; malformed traces are unavailable observations and never affect checkpoint
  operations.
- [A local tool is mistaken for product recovery] -> Explicit local-profile language,
  no Gateway/Web route, README boundaries, and UI/CLI contract tests.
- [Fresh-process actions race normal dispatch] -> Retain the broker's existing bounded
  root dispatch lease for resume/cancel; all workbench reads remain lock-free.
- [Future report support becomes speculative] -> Absent report files stay absent;
  producer-owned catalog additions require a later change and tests.

## Migration Plan

1. Add pure workbench/catalog contracts and red-before-green tests.
2. Add contained timeline/catalog/artifact runtime reads around the existing broker and
   session store, without changing binding format or checkpoint data.
3. Add the local terminal entry and its injected reducer/presentation tests.
4. Register structure/evidence, update local documentation and roadmap, then run the
   complete deterministic agent gate.

There is no data migration, owner-index backfill, binding rewrite, or checkpoint
migration. Existing phase-2/legacy bundles remain inspection-only. Rollback removes
the workbench entry and its read projections while leaving existing retained bundles,
bindings, and lifecycle operations unchanged.

## Open Questions

- Gateway/Web product integration requires a later change with explicit upstream
  ownership and API/authentication decisions; it is intentionally not resolved here.
- A future producer that creates a user-visible final report must define its artifact
  contract before adding a catalog key. This change does not assume such a report exists.
