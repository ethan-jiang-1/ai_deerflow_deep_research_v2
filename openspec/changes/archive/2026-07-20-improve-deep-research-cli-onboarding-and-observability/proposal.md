## Why

The standalone Deep Research demos currently turn the first real interaction into
an avoidable dead end. A valid first HITL-1 suspension has a committed checkpoint
phase of bootstrap while the pending interrupt correctly says hitl1; demo_real.py
mistakes the committed phase for the pending interaction and reports an opaque
"lifecycle result cannot be recognized; retry" message. The Textual demo avoids
that exact check only by guessing the stage from action and options, so the two
entry points already disagree about the same graph state.

The failure is broader than one CLI condition. Both demos decode Command,
ToolMessage, artifact, trace, and phase details themselves; the graph discards
the useful category of model and tool failures before a user-facing surface can
explain them; and the current temporary demo workspace is deleted at exit without
an inspectable, redacted diagnostic record. A new user therefore has neither a
clear next action nor enough safe evidence to distinguish configuration, provider,
tool, protocol, or graph failure.

This change was restored from archive because its completed task list described a
small CLI presentation pass, not the cross-entry reliability and explainability
needed for the first real run. The original work remains historical evidence, but
the change must now remain open until the shared failure is fixed at its source.

## What Changes

- Establish one runtime-owned ResearchRunExperience module and pure domain
  contracts as the seam between lifecycle wire results and presentation adapters.
  CLI and TUI become thin adapters that send user intent and render RunUpdate;
  neither parses Command, ToolMessage, artifact JSON, trace prefixes, or infers a
  HITL phase from action or options.
- Preserve the semantic meaning of control.phase as the committed checkpoint fact,
  while adding a bounded, versioned pending-input projection to lifecycle results.
  The projection is derived only from PendingResearchInterrupt and is the sole
  authority for what input is currently awaited. It fixes the real
  bootstrap-plus-hitl1 suspension without duplicating a pending request into
  ResearchState.
- Make first-run preparation useful before a user submits a question: validate the
  actual local prerequisites, identify what is missing and why it is needed, make
  the selected mode and temporary-demo durability explicit, and avoid an
  unexplained virtual-environment warning at the command boundary.
- Replace generic retry copy and swallowed exceptions with closed, source-owned
  failure categories, a user-safe explanation, a concrete next action, and an
  opaque diagnostic reference. Persist only redacted diagnostic records suitable
  for the standalone demo; never expose exception text, provider bodies, paths,
  credentials, user questions, or raw model output.
- Turn HITL-1 and HITL-2 into semantic user prompts. HITL-1 renders the known,
  versioned research-brief context as a goal, proposed scope, missing information,
  and examples instead of truncating machine JSON. HITL-2 explains the consequence
  of each graph-owned decision while retaining graph-owned option validation.
- Add deterministic regression coverage through the real graph and reflected
  lifecycle shape, plus shared RunUpdate adapter fixtures for CLI and TUI. A
  monkeypatched top-level lifecycle result alone is no longer sufficient evidence
  for first-suspension behavior.
- Document the bounded standalone-demo contract: it is not a durable product
  session, cannot promise cross-process resume, and writes only redacted local
  diagnostics. The existing research run bundle remains the future session root;
  productizing that model is deliberately recorded in the backlog rather than
  partially implemented here.

## Capabilities

### New Capabilities

- research-run-experience: A shared, runtime-owned, safe presentation and
  diagnostics contract for standalone Deep Research entry points.

### Modified Capabilities

- research-cli-onboarding: The real CLI consumes the shared run experience instead
  of owning lifecycle protocol interpretation.
- research-demo-tui: The Textual demo consumes the same run experience instead of
  maintaining an independent stage inference state machine.
- demo-pipeline: Shared demo infrastructure supplies a truthful preflight and
  lifecycle transport without remaining the presentation authority.
- runtime-integration: The public lifecycle projection distinguishes checkpoint
  phase from pending human interaction.
- research-graph-lifecycle: A pending interrupt is projected safely without
  becoming a second graph control authority.
- node-agent-runtime: Source failures retain a closed safe category through graph
  routing and terminal projection.
- project-structure: The new domain and runtime modules are registered in the
  canonical architecture registry.

## Impact

- Affected agent-owned surfaces include lifecycle contracts and projection,
  runtime node-agent failure handling, the shared demo transport and diagnostics,
  demo_real.py, demo_tui.py, tests/evidence metadata, agent README, Make targets,
  and the architecture registry.
- The implementation continues to leave backend and frontend unchanged. It does
  not claim a production CLI, Gateway, Web UI, Terminal Workbench, durable
  cross-process demo session, or report workspace.
- Existing checkpoint, ledger, and bundle authority rules remain intact:
  ResearchState is the only execution-control truth, the submission ledger is
  evidence truth, and the research bundle is content truth. This change adds only
  compact safe incident metadata and a presentation projection; it does not create
  a second phase cursor or a parallel session store.
