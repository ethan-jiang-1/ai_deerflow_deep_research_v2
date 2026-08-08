## Why

The first three run-bundle session changes make a locally durable Deep Research
session safe to discover, inspect, reopen, resume, and cancel, but an owner must
still stitch those facts together from separate demo CLI/TUI views. A single
operator workbench is needed to navigate an authorized local session, understand
its bounded timeline and available artifacts, and take the next legal action
without creating a second lifecycle or artifact authority.

The downstream project boundary does not permit this change to modify DeerFlow's
upstream `backend/` or `frontend/` mirrors. This change therefore delivers the
local terminal workbench and an adapter-ready safe projection; Gateway and Web
product workbench integration remains a separately authorized future change.

## What Changes

- Add an operation-enabled local terminal session workbench entry point under
  `agent/`. It discovers only sessions from the configured durable local profile,
  lets an owner select one opaque reference, and renders a bounded session view.
- Add a runtime-owned, read-only workbench projection that combines the existing
  authorized broker result with safe retained-session timeline and artifact-catalog
  facts. It never interprets a manifest, trace, or artifact as graph control state.
- Add a contained artifact-view operation for a fixed whitelist of owner-visible
  session artifacts. It validates the selected broker-authorized session, relative
  reference, regular-file type, size, and text/binary presentation policy before
  returning bounded metadata only; arbitrary paths and artifact bodies are never
  enumerated or exposed.
- Add a dedicated local Textual workbench that uses the same broker for `discover`,
  `open`/`status`, `resume`, and `cancel`, and retain the existing pending-input
  request-id correlation. It presents timeline/artifact navigation as observation
  only and does not construct an alternate controller.
- Add deterministic contract, runtime, terminal interaction, and fresh-process
  file-SQLite evidence for redaction, authorization, containment, stale selection,
  read-only behavior, and duplicate-response safety. Update local-user documentation
  and the session/workbench roadmap.

## Capabilities

### New Capabilities

- `research-local-session-workbench`: A bounded, local terminal workbench over
  authorized Deep Research session projections, timeline facts, artifact navigation,
  and existing lifecycle operations (`RWB-001` through `RWB-004`).
- `research-session-artifact-view`: Authorized, contained, size- and type-bounded
  viewing of an explicitly cataloged local session artifact (`RSV-001` through
  `RSV-003`).

### Modified Capabilities

- `research-run-session`: Retained session observations gain a bounded timeline and
  fixed artifact catalog without turning bundle metadata into control authority
  (`RUS-001`, `RUS-003`).
- `research-cli-onboarding`: Local commands expose the workbench entry point and
  accurately distinguish it from Gateway, Web, and production recovery (`REC-003`,
  `REC-004`).
- `project-structure`: Register the workbench-owned domain/runtime modules and
  focused tests in the structure registry (`PRS-006`).

## Impact

- Affected downstream code: `agent/` domain and runtime projections, retained-session
  observation paths, local terminal scripts/entry points, tests, README, and the
  session/workbench roadmap.
- No `backend/` or `frontend/` code changes, no Gateway route, no Web page, no
  production terminal integration, no caller-selected authority, no multi-user
  browsing, and no generic filesystem/artifact browser.
- Evidence class: deterministic workflow conformance at the local session/runtime
  boundary, using the existing file-SQLite durable profile. Credentialed provider and
  full product UI acceptance remain supplemental or deferred.
