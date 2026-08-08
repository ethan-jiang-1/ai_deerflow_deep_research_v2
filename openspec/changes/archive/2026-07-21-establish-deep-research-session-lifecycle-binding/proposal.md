## Why

The archived run-session contract makes a local research bundle inspectable, but its
manifest and trace are intentionally derived observations.  They cannot reopen the
checkpoint after a process restart, so an opaque `research_id` cannot yet support
truthful lifecycle operations.

This change establishes the missing durable, authenticated binding between a session
reference and its checkpoint namespace/provider.  It is the necessary control-plane
foundation before a later discovery/operations change can offer `open`, `status`,
`cancel`, `answer`, or `resume`.

## What Changes

- Add a runtime-owned, redacted session-lifecycle binding tied to one authenticated
  user scope, research id, restart-stable checkpoint namespace, and provider
  durability classification.
- Add a read-only checkpoint-reopen verifier that validates checkpoint
  identity/schema/pending-interrupt facts through the official provider and fails
  closed when a binding is stale, mismatched, unauthorized, or non-durable.
- Enforce that every current lifecycle action's `research_id` equals the canonical id
  derived from its trusted user/thread envelope before deriving a checkpoint namespace.
- Keep manifests/traces as observations: they may carry a safe binding reference but
  never provider credentials, host paths, pending answers, checkpoint payloads, or
  lifecycle routing authority.
- Add deterministic file-SQLite restart/reopen, scope-isolation, stale-binding,
  concurrent-operation, and redaction evidence at the runtime lifecycle seam.

## Capabilities

### New Capabilities

- `research-session-lifecycle-binding`: Durable, authenticated binding and recovery
  contract for a session's authoritative checkpoint lifecycle (`RES-001` through
  `RES-004`).

### Modified Capabilities

- `research-run-session`: Its safe session projection gains an opaque lifecycle
  binding reference without exposing provider implementation details or becoming
  control authority (`RUS-001`).
- `research-graph-lifecycle`: Current lifecycle actions reject non-canonical ids and
  keep manifest/trace/binding metadata out of routing and pending response validation
  (`REG-004`, `REG-014`).
- `runtime-integration`: The reflected runtime lifecycle uses its authenticated
  envelope to create bindings and exposes no new operation command (`RUI-006`).

## Impact

- Affected downstream code: `agent/src/deerflow_deep_research/runtime/checkpoint.py`,
  `runtime/research.py`, run-session contracts/store, and their domain, contract,
  integration, blocking-I/O, and restart tests.
- No new Gateway API, Web UI, production CLI command, public skill, MCP, ACP, or
  subagent surface is introduced.  `backend/` and `frontend/` remain unchanged.
- File-backed SQLite is the deterministic restart-durable acceptance provider;
  memory and SQLite-memory remain explicit same-process-only test/development modes.
- This change does not implement session listing/browsing UX, artifact discovery,
  report viewing, retention policy changes, multi-user collaboration, a workbench, or
  user-facing cross-process open/status/resume/cancel/answer operations.
