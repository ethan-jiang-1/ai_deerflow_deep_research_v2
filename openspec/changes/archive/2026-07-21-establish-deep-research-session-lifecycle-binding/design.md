## Context

The archived session contract retains a local bundle, manifest, trace, and safe
inspection view.  Those records are deliberately derived projections: the graph never
reads them for routing, pending-answer validation, or evidence acceptance.  The
authoritative `ResearchState` is already checkpointed through the official DeerFlow
provider, but the local retained session lacks a private, authenticated mapping back to
the `outer_thread_id` and checkpoint namespace required to reopen it after a process
restart.

The next discovery/operations change cannot safely expose `open`, `status`, `cancel`,
`answer`, or `resume` until that mapping exists.  Inferring it from a public manifest,
an arbitrary research id, sandbox content, or a caller-supplied path would either
create a second authority or permit cross-user/session confusion.

## Goals / Non-Goals

**Goals**

- Bind an opaque research id to one trusted user scope, outer thread identity, and
  restart-stable checkpoint namespace through a runtime-owned private record.
- Reopen the official checkpointer and validate the checkpointed identity, schema,
  terminal/pending facts, and provider durability as a prerequisite for later lifecycle
  operations.
- Preserve the existing checkpoint as the only execution-control authority and the
  manifest/trace as observation-only projections.
- Produce deterministic file-SQLite restart and scope-isolation evidence without
  model, network, Gateway, or browser dependencies.

**Non-Goals**

- No CLI/TUI/Gateway/Web discovery surface, artifact browser, report viewer, or
  workbench.  Those belong to later changes.
- No caller-selectable checkpoint DSN, host path, user id, outer thread id, or
  namespace; no Gateway configuration change; no `backend/` or `frontend/` edits.
- No checkpoint payload copy, `state.json`, provider migration, automatic binding
  backfill, multi-user sharing, or production Postgres acceptance claim.

## Decisions

### A private lifecycle binding is distinct from the public manifest

`SessionLifecycleBindingStore` will be runtime-owned and owner-only.  Its initial
local-demo implementation lives below the retained root in a non-enumerated
`.lifecycle-bindings/` subtree with `0700` directories and `0600` regular files; no
inspection command traverses or renders that subtree.  It records the opaque
`research_id`, trusted effective-user scope, trusted outer-thread identity, derived
namespace schema/version, and a provider fingerprint derived from the effective
source/kind/durability/connection selection.  The raw scope/thread/provider values
remain private storage only and never enter a manifest, trace, CLI/TUI update, model
input, or diagnostic output.

The public manifest may carry only a fixed-shape opaque binding reference and its
availability/durability classification.  This makes inspection navigable without
letting the manifest choose a provider, namespace, route, or pending response.

The alternative, deriving an outer thread id from `research_id`, is impossible by
design and would weaken identity isolation.  Storing provider DSNs in the manifest was
rejected because inspection records are user-visible and configuration drift must be
validated from the current runtime, not replayed from old storage.

### Bind at a validated lifecycle boundary and reopen only official providers

Binding creation occurs only after the normal lifecycle has returned a record-bearing,
validated checkpoint result.  The runtime derives the namespace from the injected
trusted envelope and calls the official async checkpointer provider using current
`AppConfig`; it then validates that the read checkpoint has the same research id and
supported schema before atomically publishing the private binding and safe projection.

The internal reopen verifier uses the same official provider context and current provider resolution.
It treats a missing record, scope mismatch, provider-fingerprint mismatch,
same-process-only provider after restart, malformed checkpoint, or research-id mismatch
as a typed unavailable/denied result.  It never tries another namespace or repairs a
checkpoint from a manifest/trace.

### Binding verifies recovery but does not execute lifecycle operations

The binding store returns a narrow runtime capability, not a graph state object.
The verifier returns a bounded internal fact rather than an executable session or a
replacement `TrustedRuntimeEnvelope`.  `Answer`, `Cancel`, and `Resume` remain out of
scope: reconstructing a sandbox-capable envelope for a different outer thread needs a
separate, explicit discovery/operations design.  A binding never contains a pending
answer, phase cursor, route, or permission to bypass normal intent validation.

Binding-level owner-only advisory locks serialize only binding-file create/refresh/
invalidation.  The implementation MUST NOT hold a binding lock while entering the
official provider context, reading a checkpoint, invoking a graph, or awaiting
sandbox work; it validates first, acquires the binding lock only to atomically commit
or invalidate metadata, then releases it.  They are not a replacement for existing
graph/checkpoint mutation serialization.  A stale binding is invalidated or reported
unavailable; it is never silently rebound to a different thread or user.

### Canonical id validation precedes binding and namespace selection

Every current lifecycle action computes the expected research id from the injected
effective user and outer thread.  A supplied id that differs is rejected before graph
or checkpoint access; a binding is never created for it.  This closes the current gap
where a caller-supplied opaque id can otherwise influence the derived namespace inside
the caller's thread scope.

### File-backed SQLite is the deterministic durability gate

File-backed SQLite must prove provider reopen and process-restart lifecycle recovery.
Memory and `:memory:` SQLite may create a same-process observation but cannot advertise
restart operations; they fail closed after restart.  Credentialed/provider-specific
Postgres evidence remains supplemental and is not required for this change.

## Risks / Trade-offs

- [Binding becomes a second controller] -> bindings hold only trusted lookup metadata;
  every open revalidates the actual checkpoint and graph code never reads them to route.
- [Cross-user enumeration] -> scope is injected from trusted runtime context, private
  records are owner-only, unknown/mismatched references share bounded denial output.
- [Provider drift reopens the wrong state] -> bind a redacted provider fingerprint and
  fail closed when current provider classification does not match.
- [Crash leaves a usable-looking partial binding] -> use contained atomic replacement,
  strict modes/no-follow checks, and validate provider/checkpoint before publication.
- [Lifecycle changes become a workbench] -> do not add a user-facing operation command
  or reconstruct a different thread's envelope; later discovery/operations consumes
  the narrow verifier after it designs that authority boundary.

## Migration Plan

1. Add frozen binding contracts, fail-closed scope/provider/checkpoint tests, and
   private contained store primitives, including no-enumeration and lock-order tests.
2. Integrate binding creation/refresh at the record-bearing runtime lifecycle seam;
   add safe public projection fields without changing graph authority.
3. Add read-only provider reopen verification using file SQLite restart fixtures and
   same-process-provider denial cases.
4. Add lifecycle integration tests for canonical-id, stale/mismatched binding, and
   no-operation/no-sandbox initialization guarantees; run deterministic verification
   and supplemental real-provider preflight where available.

Existing retained bundles are inspection-only legacy sessions.  They are never
backfilled by guessing from their manifest.  A later explicit migration may create a
binding only after the trusted runtime can independently prove the matching checkpoint.

## Open Questions

- Whether future production Postgres support needs a provider-specific binding
  fingerprint version or can reuse the current provider classification schema.
- Whether a secure runtime-owned binding root should be per-user on host storage or
  delegated to a future provider-backed metadata store.  This change will choose the
  local owner-only implementation needed for deterministic file-SQLite evidence.
