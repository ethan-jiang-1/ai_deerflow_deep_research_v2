## Why

Deep Research lacks one safe, runtime-wide log contract for joining a Bundle fact to
the currently configured DeerFlow trace. The installed DeerFlow version already owns
Python logging configuration and trace filtering, but does not expose the custom-event
helper required by the earlier proposal; this change therefore makes logs useful now
without upgrading a dependency that is already validated for this application.

## What Changes

- Add one safe standard-Python-log projection at each material Deep Research fact
  owner, with a closed field set, redaction, level selection, duplicate prevention,
  and the invariant that observation cannot affect execution.
- Align application logging with the installed DeerFlow contract: application modules
  obtain `logging.getLogger(__name__)`; DeerFlow startup/configuration owns root
  handlers, formatters, and `TraceContextFilter`, which injects the current `trace_id`
  when available. Application code neither reconfigures root logging nor installs a
  competing trace filter.
- Bind trusted outer thread/run correlation only after Bundle admission or resolution
  when the trusted runtime boundary supplies it. Keep the Bundle Event Journal as
  bounded domain evidence, not a log, identity, lifecycle authority, or recovery
  input.
- Remove the partial raw-writer, `ProgressEmitter`, and custom-event facade rather
  than retaining an unsupported compatibility surface. Retire the allocated
  `RTO-002` requirement during implementation without reusing its registry id.
- Inventory graph, engine, runtime, and Journal fact owners; attach only their safe
  standard-log projections while preserving current classification, retry, routing,
  persistence, and terminal-result owners.

## Capabilities

### New Capabilities

- `runtime-observability`: safe, trace-correlated standard logging of Deep Research
  runtime facts without lifecycle authority or a custom-event transport.

### Modified Capabilities

- `run-event-journal`: removes raw streaming as a Journal-adjacent projection and
  retains the Journal as non-controlling bounded domain evidence.
- `runtime-integration`: extends trusted runtime adaptation with safe outer-run
  correlation for logs without accepting caller authority or reading private Gateway
  stores.

## Impact

- `deep_research_harness/src/deerflow_deep_research/runtime/` logging adapter,
  trusted runtime adaptation, Bundle lifecycle, BundleControl, graph binding, and
  node-agent bridge; the non-checkpointed projection protocol in
  `domain/invocation.py` and its graph/node/work-unit consumers; their focused tests;
  and the three owning capability specs.
- Current DeerFlow public logging configuration, `TraceContextFilter`, and current
  trace lookup are consumed as installed. No DeerFlow dependency upgrade, source
  modification, or source browsing is part of this change.
- No custom event, stream writer, SSE/Gateway transport, Bundle-local file handler,
  retention policy, CLI/TUI renderer, Gateway client, route migration, private
  `RunJournal` access, retry policy, or lifecycle/public control API is introduced.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/events.py`; the runtime logging facade owns canonical safe standard-log projection and its no-side-effect boundary, while each adjacent producer retains ownership of its direct execution fact.
- **Seam classification:** deterministic-guardrail because a closed projection schema, field allowlist, and best-effort logging adapter protect existing execution and lifecycle authority from diagnostic delivery.
- **Question:** Can every material Deep Research execution fact produce exactly one safe standard log record at its owning boundary, joined to DeerFlow's current trace where configured, without duplicating a fact, persisting a second authority, or changing the Run?
- **Necessary adjacent/external contracts:** `run-event-journal` answers which Bundle-domain facts remain retained evidence and why logs cannot control them; `runtime-integration` answers trusted-envelope correlation and the prohibition on caller/private-Gateway authority; `research-graph-lifecycle` and `workflow-failure-outcomes` answer existing graph, terminal, and legal-next-action owners; `runtime/bundle_lifecycle.py` and `runtime/bundle_control.py` answer the single lifecycle log boundary for both Gateway and Local Session Workbench callers; `domain/invocation.py` and `runtime/bundle_graph.py` answer how a runtime-created non-checkpointed projection reaches graph owners without a domain-to-runtime import or State write; `graph/builder.py`, `graph/components/work_units.py`, and `runtime/node_agent_bridge.py` answer the narrow producer boundaries for node/work/attempt/model-tool facts; DeerFlow's public logging configuration, `TraceContextFilter`, and current trace lookup answer handler/filter ownership and trace correlation. No DeerFlow source boundary is admitted.
- **Evidence seam:** `tests/unit/test_events.py` for schema, redaction, level, and logger-isolation rules; focused runtime/graph/node-agent tests for exactly-once owner projection and unchanged typed results; focused source guards for no raw writer, no custom-event imports, and no private Gateway access; no live Gateway is required.
- **Not in scope:** DeerFlow upgrades, custom events, stream-writer transport, file logging/bootstrap, retention, physical log paths, CLI/TUI rendering, Gateway streaming client or SSE proof, route/GraphHost migration, private Gateway stores, Bundle Journal schema migration beyond safe correlation, lifecycle/retry/terminal behavior changes, or modifying/source-browsing `deerflow/`.
- **Triggered review policies:** authority-and-projections, workflow-outcome-review, change-admission

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| A configured logging handler rejects a record or is unavailable | DeerFlow logging configuration owns sink availability; the originating runtime/graph/engine owner retains its direct fact | No observer retry, Bundle-local file fallback, or lifecycle action; the facade suppresses only its bounded delivery failure | Existing Run result and Bundle Journal health/outcome remain unchanged; logs may be incomplete | Diagnose the configured process log sink outside the Run and use the existing typed result | Logger fault-injection test proves the same producer result with a failing handler |
| DeerFlow trace correlation is absent | DeerFlow's current trace context owns trace availability; the originating owner retains its direct fact | No inferred trace, alternative identity, or retry | Existing Run behavior and logs without a trace remain valid | Correlate via safe Bundle/outer-run fields only when their trusted boundary supplied them | Focused absent-trace test |
| Existing provider/tool, validation, retry, cancellation, or terminal fact is observed | Its existing phase/controller and typed outcome contract | Existing bounded phase/controller recovery only; logging never retries or reclassifies | Existing typed terminal disposition and legal action | Follow the existing typed outcome's legal action | Focused node-agent, work-unit, validation, and lifecycle tests assert one safe projection and unchanged result |
| Unsafe, unknown, duplicate, token/raw-content, or malformed log candidate | `runtime/events.py` validates the projection; the producer still owns the underlying execution fact | Reject/drop the projection only; no inferred fact, route, or persistence repair | No new terminal disposition; the Run retains its current state | Use the original typed fact through its owner | Allowlist, redaction, duplicate-suppression, and no-raw-writer/custom-event tests |
