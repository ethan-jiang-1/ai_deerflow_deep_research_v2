## Why

The real Deep Research demo can consume its single 30-second HITL1 bridge/model-invocation budget and terminate with `provider.timeout` after making no automatic recovery attempt. The terminal does not distinguish an exhausted automatic recovery from a fresh start, identify the safe configured service or observed response outcome, or preserve one trustworthy account of the bounded graph invocations in diagnostics and presentation.

This makes a routine transient provider failure look like an opaque terminal fault and prevents operators from distinguishing a recoverable outage from authentication, configuration, cancellation, a local runtime problem, or structured-output failure.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/graph/nodes/hitl1/`; it owns one brief-generation visit, its two-call budget, and its blocked route. This is phase-local policy rather than a reusable engine retry abstraction.
- **Question:** how one first-attempt, directly classified transient HITL1 provider failure receives exactly one bounded recovery and leaves a truthful, safe terminal account when recovery does not complete.
- **Necessary adjacent/external contracts:**
  - `runtime/node_agent_bridge.py` and `NodeProblem`: which direct, public `httpx` and OpenAI SDK exception carriers from a trusted `hitl1` zero-tool invocation are retry-eligible, and which safe configured-service label, sanitized configured endpoint authority, and observed HTTP/no-response facts can cross the raw binding boundary.
  - `agent/pyproject.toml` and `agent/uv.lock`: how the bridge declares and locks the `httpx` and OpenAI SDK classifier types it imports directly, rather than relying on incidental transitive installs.
  - `openspec/governance/project-structure.toml`, its active `project-structure` requirement, and `check_project_architecture.py`: how the mechanical import policy declares those two direct classifier namespaces only for the raw-binding bridge, rather than hiding the dependency behind a dynamic import or widening the runtime layer generally.
  - `domain/run_experience.py`, `runtime/run_experience.py`, and `runtime/run_diagnostics.py`: how the existing run-experience domain contract validates safe recovery facts, its checkpointed incident projects every provider-diagnostic terminal into shared human/AI `RunFailure`, and diagnostics retain an honest location without claiming live retry progress or inventing a second reference.
  - `domain/invocation.py`, `domain/run_session.py`, `runtime/run_session.py`, and `runtime/session_operations.py`: how the existing injected `RunEventRecorderProtocol` accepts only closed recovery facts, a retained-session summary copies only bounded terminal history, every publisher accepts the incident diagnostic reference, a terminal session view proves its reference correlation, and observational events keep causal order through a recovery correlation rather than deriving a reference.
  - `scripts/demo_real.py` and `scripts/demo_tui.py`: how both presentation adapters render only the shared safe failure fields and a static fresh-start command with no user question.
  - `scripts/_demo_core.py`: how the real demo supplies a vetted configured-service label and sanitized configured endpoint authority without exposing a base URL or credential.
- **Evidence seam:** `agent/tests/unit/test_node_agent_bridge.py` and `agent/tests/graph/test_hitl1_node.py` first; then `test_run_experience_failures.py`, `test_run_session_store.py`, `test_demo_real.py`, and `test_demo_tui.py` consume their typed results.
- **Not in scope:** provider SDK retry policy, global or unbounded retries, streamed retry progress, other graph phases, raw provider diagnostics or full URLs, user-question handoff through a shell command, generic cross-process resume, `backend/`, and `frontend/`.

## What Changes

- Add a graph-owned, two-invocation maximum recovery policy for a first-attempt `provider.timeout` or narrowly classified `provider.unavailable` at real HITL1 brief generation, with an exact 1,000 ms cancellable backoff and an explicit terminal disposition. The classifier is limited to a trusted `NodeAgentContext.node_name=hitl1` zero-tool request and recognizes only direct public `httpx` or OpenAI SDK carriers. Declare both classifier packages as direct `agent/` runtime dependencies rather than relying on transitive packages.
- Preserve one typed account of HITL1 bridge/model invocations, the retry-trigger invocation ordinal, automatic retries, terminal recovery disposition, safe configured-service label, sanitized configured endpoint authority, and observed HTTP/no-response fact through the checkpointed terminal incident. These counts never claim to be physical provider HTTP-request counts because SDK retry policy remains outside this change. The frozen `ProviderObservation` and recovery projection contracts remain owned by `domain/run_experience.py`; the default resolver returns an explicit `ResolvedNodeModel` binding for the exact selected configuration, while a raw custom resolver result has no label or authority. These projections do not store provider exceptions, prompt/request text, model responses, full URLs, host paths, or credentials.
- Project every provider-diagnostic terminal (a recovery projection and/or final safe provider observation) through the shared `RunFailure` used by CLI and TUI. It retains one pre-derived diagnostic reference, an honest diagnostic-record location, and `research_record_created` truth that is satisfied only by an available retained terminal session bundle whose reference matches. A closed `recovery_action` is present only when a distinct fresh start is legal; it is the only rendered actionable control. Returned-only waiting remains honest local waiting; no adapter or AI consumer is told that an in-flight retry is observable.
- Record causal HITL1 bridge/model-invocation, scheduled-retry/backoff, exhaustion, and terminal observations through the runtime-owned session recorder. A recovery correlation id joins pre-terminal events; only the terminal event and terminal projections carry the diagnostic reference. Cancellation remains immediate and does not promise a retained cancellation event or inspection timeline. A bounded retained summary copied from the checkpointed recovery projection and its reference cross every `RecordBearingLifecycleFact` publisher into retained inspection, and an unavailable retained publisher falls back to the support journal using that same reference rather than inventing another.
- Make real CLI/TUI terminal feedback state the safe provider category, configured-service label and sanitized endpoint authority when available, observed HTTP status or no-response fact, phase, bridge/model-invocation counts, recovery disposition, diagnostic reference, actual diagnostic-record availability, and the one legal next action. A copyable command is the static `make demo-real` fresh start from `agent/`; it never embeds the original question or claims resume.
- Add deterministic tests at the runtime bridge, HITL1 node, run-experience/session projection, and CLI rendering seams. Live provider calls remain supplemental.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `node-agent-runtime`: classify only supported transient provider failures for bounded retry and expose redacted service/response observations without weakening execution budgets or cancellation.
- `hitl1-node`: recover transient real brief-generation provider failures before taking the existing exhausted route.
- `research-run-experience`: expose bounded, redacted terminal recovery history, a closed fresh-start action, and an honest diagnostic-record location through shared safe run updates.
- `research-run-session`: record causally ordered, correlated provider recovery observations and receive one terminal diagnostic reference without becoming a diagnostic-reference or lifecycle authority.
- `research-cli-onboarding`: render actionable real-demo failure feedback and a static fresh-start command without leaking the question or overclaiming resume.
- `project-structure`: declare and mechanically enforce the narrow raw-binding import boundary for the direct `httpx` and OpenAI SDK classifier namespaces.

Requirement IDs: `NOA-008`, `HIN-008`, `RER-009`, `RUS-006`, `REC-006`, and `PRS-002`.

## Impact

Affected downstream code is limited to `agent/pyproject.toml` and its lock metadata, `agent/src/deerflow_deep_research/runtime/node_agent_bridge.py`, the safe real-demo model-label/endpoint-authority projection, `agent/src/deerflow_deep_research/graph/nodes/hitl1/`, `domain/invocation.py`, run-experience/run-diagnostics/run-session/session-operation contracts and adapters, plus `agent/scripts/demo_real.py` and `agent/scripts/demo_tui.py`. The existing `project-structure` registry, requirement, checker, and deterministic checker fixture receive the narrow declaration necessary for the bridge's two direct classifier imports. Tests live under `agent/tests/`; detailed operator behavior belongs in `agent/docs/local-operations.md`, with only a concise README pointer if needed.

No `backend/` or `frontend/` files, Gateway configuration, public skills, MCP/ACP, or DeerFlow task-subagent surface are modified. There is no restart impact because no runtime configuration or mount contract changes. The lowest responsible deterministic evidence seams are the bridge and real HITL1 node using scripted provider outcomes; CLI/session tests consume their typed results. The existing requirement-governance checker already accepts pending delta IDs, so this change verifies it rather than modifying it. No persisted trace replay is needed.
