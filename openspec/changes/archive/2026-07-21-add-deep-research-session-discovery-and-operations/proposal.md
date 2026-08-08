## Why

The first two session changes make retained bundles inspectable and prove a private
checkpoint binding can survive a file-SQLite restart, but users still cannot safely
find, reopen, or act on a prior session. The current lifecycle tool accepts only the
current outer thread's trusted envelope; treating a manifest or a binding record as a
replacement would permit scope confusion and sandbox-capability forgery.

## What Changes

- Add a runtime-owned local session discovery and operation broker. It discovers only
  owner-and-profile-indexed opaque binding references activated after retained-bundle
  publication, then resolves a selected reference only after trusted authorization and
  private binding/checkpoint/recipe revalidation.
- Add bounded local `list`, `open`, `status`, `resume`, and `cancel` operations for
  retained sessions; `open` and `status` are read-only, while resume/cancel delegate to
  the existing lifecycle handlers and their checkpointed pending-interrupt authority.
  Reopened resume derives its bounded prompt view and response correlation from the
  current checkpoint, never from a manifest, binding, or caller-selected scope.
- Add a trusted runtime resolver for a stored outer-thread scope. It starts from a
  runtime- or profile-owned operation-access capability, obtains paths and a sandbox
  through its trusted runtime/public-facility or fixed local-profile factories only after
  binding validation, and never reconstructs a historical `ToolRuntime`.
- Extend local CLI/TUI session views with safe discovery and operation projections, plus
  bounded artifact/diagnostic references. Their adapters receive an already-authorized
  broker; command-line input cannot create an authority capability, and resume answers
  are read from stdin rather than process arguments. No Gateway API, Web workbench, or
  cross-user browsing is introduced.
- Add deterministic file-SQLite restart, authorization, stale binding, artifact
  containment, and operation/no-extra-node evidence at the lifecycle seam.

## Capabilities

### New Capabilities

- `research-session-discovery-and-operations`: Authorized local discovery and lifecycle
  operations built on private bindings and authoritative checkpoints (`RDO-001` through
  `RDO-004`).

### Modified Capabilities

- `research-run-session`: Discovery projections expose only safe session/artifact facts
  and preserve legacy inspection behavior; retention revokes operability before deleting
  a retained bundle (`RUS-001`, `RUS-003`).
- `research-session-lifecycle-binding`: Private bindings gain an owner index and a
  profile-owned recipe-compatibility guard without becoming graph control state
  (`RES-001`, `RES-004`).
- `research-graph-lifecycle`: Reopened operations retain canonical scope and
  checkpoint/pending-interrupt control authority (`REG-004`, `REG-014`).
- `runtime-integration`: Runtime reconstructs an operation envelope only through trusted
  DeerFlow context and public thread/sandbox facilities (`RUI-002`, `RUI-006`).
- `research-cli-onboarding`: Local CLI renders bounded session discovery/operation
  results without leaking paths or claiming unsupported access (`REC-004`).
- `research-demo-tui`: The local TUI consumes the same safe operation projection rather
  than a second session state machine (`RED-005`).

## Impact

- Affected downstream code: runtime session binding/run-session/control/adapter paths,
  lifecycle input correlation, local demo-profile command and TUI adapters, their domain
  contracts, and deterministic tests.
- No `backend/` or `frontend/` files change. No production Gateway route, Web UI,
  public skill, MCP/ACP surface, existing-session provider migration, multi-user sharing,
  or workbench is added. A new operation-enabled local profile may use file SQLite for
  newly created local sessions only.
- Evidence class: deterministic workflow conformance at the lifecycle/runtime seam;
  file-SQLite subprocess restart is the acceptance provider. Credentialed provider
  coverage remains supplemental.
