## Why

Deep Research can reach a truthful terminal lifecycle outcome while losing the process
facts needed to explain how that outcome arose. The product needs one durable,
redacted, read-only account of execution that makes every material failure and its
bounded recovery inspectable without turning diagnostics, logs, or presentation into
lifecycle authority.

This is needed now because model, provider, worker, and validation failures are normal
operating conditions. A terminal category alone cannot distinguish the concrete
validation rule, attempt, or recovery history that a contributor needs to improve the
system safely.

## What Changes

- Establish a single **Run Event Journal** inside the admitted Run Bundle's protected
  `diagnostics/` subtree: a bounded chronological record of safe observed execution
  facts that is deleted with the Bundle and distinct from raw application logs, terminal
  diagnoses, progress rendering, and Bundle lifecycle state.
- Require the journal to be available to all shared execution producers before graph
  work starts, and retain the complete correlation identity needed to relate a fact to
  its Run, refinement generation, phase, work item, and attempt.
- Define an explicit safe event vocabulary and journal-health truth. Known validation
  rules, provider/model outcomes, retry decisions, worker outcomes, and unexpected
  boundary failures retain bounded facts; a monotonic Bundle-local sequence, protected
  diagnostic anchors, and explicit dropped intervals make journal unavailability or
  retention limits honest rather than silently presenting a complete history.
- Make shared lifecycle, graph, work-unit, node-agent/provider, and deterministic
  validation seams publish those facts through the same contract. A newly discovered
  production model owner cannot bypass this coverage.
- Keep terminal diagnosis as a read-only explanation linked to authoritative outcome
  facts and journal evidence. Safe operator inspection exposes the correlation and
  diagnosis facts needed to investigate a Run without exposing raw prompts, outputs,
  exceptions, URLs, credentials, paths, or internal wires.
- Treat failed pre-admission requests as requests rather than Runs: they receive an
  immediate safe result but no ghost Bundle or persistent Journal. Bundle Loss likewise
  leaves no external diagnostic copy or recovery route.
- Leverage DeerFlow only at its supported boundaries: trusted runtime context supplies
  ingress correlation, and `custom` streaming mirrors already-safe facts live on a
  best-effort basis. Neither becomes durable evidence or a Run identity.
- Preserve the existing lifecycle owner: journal writes, inspection, diagnostics, and
  live progress cannot start, resume, cancel, refine, route, or recreate a Run.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/domain/run_observation.py`, which owns the typed meaning and invariants of retained Run observation facts.
- **Question:** What minimal, safe, durable process-fact contract lets every Deep Research execution path explain material failure and recovery without creating a second lifecycle authority?
- **Necessary adjacent/external contracts:** `domain/bundle.py` answers the contained diagnostics location; `runtime/run_observation.py` answers how the Bundle-local journal is persisted and reports health; `runtime/bundle_lifecycle.py` and `runtime/bundle_graph.py` answer when an admitted Bundle receives a producer-facing journal; `graph/builder.py`, `graph/components/work_units.py`, and `runtime/node_agent_bridge.py` answer which shared execution seams publish facts; `runtime/runtime_adapter.py` and DeerFlow's public `custom` stream writer answer trusted ingress correlation and optional live projection; `workflow-failure-outcomes` answers ownership of classified failure facts and coverage discovery; `research-run-session` answers contained inspection limits.
- **Evidence seam:** deterministic `Run Event Journal` contract tests with an admitted fixture Bundle, plus a scripted graph/work-unit/provider failure that asserts the retained redacted event chain and unchanged typed lifecycle outcome.
- **Not in scope:** changing graph routing, retry policy, provider behavior, Bundle lifecycle authority, raw structured logging, a general telemetry platform, production tracing infrastructure, or any `deerflow/`, `backend/`, or `frontend/` code.
- **Triggered review policies:** authority-and-projections, participant-outcomes, workflow-outcome-review

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Known deterministic validation rejection | The validator and its typed work-attempt result | Existing phase/work controller, within its existing repair or retry bound | Existing accepted or exhausted typed outcome | Only the lifecycle result's existing legal action | A scripted invalid candidate retains its closed validation code and leaves routing unchanged |
| Provider or node-agent invocation failure | The node-agent bridge's safe classified problem | Existing phase/controller recovery, within its declared retry budget | Existing typed phase or terminal incident | Only the lifecycle result's existing legal action | A scripted provider failure yields a redacted correlated journal event and existing terminal projection |
| Worker exhaustion after bounded attempts | The work-unit controller's typed attempt and gate facts | The existing gate/controller, with no additional journal recovery | Existing blocked or repair outcome | Only the lifecycle result's existing legal action | Concurrent fixture workers retain distinct attempt facts and the terminal journal link |
| Journal persistence or retention failure | The Bundle-local journal adapter's non-authoritative health fact | No recovery is created by the journal; a later observation write may independently succeed | The lifecycle outcome remains unchanged; the journal reports incomplete or unavailable observation | Read the typed lifecycle outcome while the Bundle remains available | A failing/limited journal leaves graph behavior unchanged and never claims a complete event history |
| Unknown boundary failure | The catching shared execution boundary's safe unknown classification | Existing failure boundary only; no diagnostic-created retry | Existing honest unknown/blocked outcome when one exists | Only the lifecycle result's existing legal action | A scripted unexpected exception yields a bounded unknown event without raw exception text |

## Capabilities

### New Capabilities

- `run-event-journal`: Defines the shared Run Event Journal vocabulary, correlation,
  completeness truth, producer and reader boundaries, and redaction invariants.

### Modified Capabilities

- `research-run-session`: Extend retained observation requirements so the journal can
  cover admitted execution safely before graph work, preserve correlation and health,
  and become unavailable with its Bundle after Bundle loss.
- `workflow-failure-outcomes`: Require classified workflow failure facts and their
  deterministic coverage inventory to reach the shared journal without changing
  recovery or terminal authority.

## Impact

- Expected downstream changes are limited to `deep_research_harness/`: the Bundle
  diagnostics path and run-observation domain/runtime, admitted graph composition,
  shared graph/work-unit and node-agent boundaries, optional DeerFlow live projection,
  operator inspection projection, and focused deterministic evidence.
- The external terminal diagnostic fallback is removed for admitted Runs. Live progress
  remains an optional projection rather than the durable journal, and pre-admission
  failures receive only their immediate safe response.
- No public DeerFlow implementation, upstream backend, frontend, provider contract, or
  lifecycle command surface changes.
