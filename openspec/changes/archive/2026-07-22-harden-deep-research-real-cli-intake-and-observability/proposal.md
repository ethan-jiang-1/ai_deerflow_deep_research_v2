# Change: Harden real CLI intake and run observability

## Why

The first all-real standalone CLI run exposed three P1 defects: localized profile
answers are silently ignored and degrade the research scope, the UI presents model
suggestions as though they can be confirmed when no durable confirmation exists, and a
retained run bundle cannot explain whether a run is still active, terminal, or why it
stopped. These defects make the current real demo unsuitable for both novice use and
professional incident diagnosis.

## What Changes

- Make HITL1 proposal and answer handling explicit, durable, localized, and
  deterministic: checkpoint a validated advisory proposal, allow an explicit correlated
  acceptance action, expose all required fields including `must_answer`, and reject a
  zero-recognition response without consuming an answer round.
- Add deterministic Chinese aliases and structured/profile-form input paths while
  preserving closed enums and Python/LangGraph ownership of lifecycle control.
- Project accepted fields, missing fields, parse feedback, proposal availability, and
  remaining answer budget through the shared run-experience prompt used by CLI and TUI.
- Make returned-only waiting and every terminal result operationally visible: display
  run reference, last confirmed phase, elapsed time, durability/recovery semantics,
  terminal outcome, diagnostic reference, and inspect command without inventing live
  node progress.
- Extend retained-session observation with a validated summary and bounded redacted
  lifecycle/work-attempt diagnostic events, then render those facts first through the
  read-only inspect command and local workbench.
- Replace the canonical bundle-root locator for new runs with a trusted UTC
  `YYYYMMDDHHMM_r_<id>` directory while preserving `research_id` as the sole
  lifecycle/checkpoint/binding identity and retaining legacy checkpoint compatibility.
- Add deterministic red-green coverage for the captured failure, invalid-answer
  preservation, proposal acceptance, terminal Wave0 work failure, visible liveness,
  and secret/path/exception redaction.

## Capabilities

### Modified Capabilities

- `hitl1-node`: durable suggestion acceptance, localized deterministic parsing, and
  no-loss invalid-answer feedback.
- `research-run-experience`: safe prompt feedback and truthful running/terminal state
  projection.
- `research-cli-onboarding`: actionable CLI rendering for profile confirmation,
  returned-only liveness, terminal outcomes, and inspection.
- `research-demo-tui`: shared typed profile-input/action rendering without local
  lifecycle inference.
- `research-run-session`: retained diagnosis summary/event observations and actionable
  legacy inspection.
- `research-graph-lifecycle`: checkpointed canonical bundle locator and a correlated
  closed human-response action without changing lifecycle identity or authority.
- `bootstrap-node`: establish and validate the locator-selected canonical bundle root.
- `work-unit-kernel`: derive work and content artifact roots from the canonical locator.
- `research-local-session-workbench`: render the same bounded diagnostic observations
  and advertised profile actions after broker authorization.
- `research-session-discovery-and-operations`: carry a typed correlated broker resume
  response without widening broker authority.
- `runtime-integration`: capture trusted bundle locators, inject one non-authoritative
  run-event recorder, and make custom checkpoint state compatible with LangGraph strict
  msgpack decoding.

### New Capabilities

None.

## Impact

Affected code is limited to `agent/` domain/runtime/graph nodes/scripts/tests and their
documentation, plus OpenSpec and backlog records. No `backend/` or `frontend/` source,
Gateway API, model-provider protocol, or arbitrary raw log retention is introduced.
