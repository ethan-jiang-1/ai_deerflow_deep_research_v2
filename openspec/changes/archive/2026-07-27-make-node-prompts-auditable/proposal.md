## Why

Deep Research currently makes the common node-agent policy visible as Markdown, but
leaves each node-specific objective, output contract, tool request, and final user
message embedded in Python prompt builders. A reviewer cannot see the actual input to
an agent loop after a prompt change without reconstructing code paths mentally, which
makes prompt work opaque and encourages blind tuning.

This change makes the rendered, production-shaped prompt for every supported node
request branch inspectable and reviewable without invoking a model, a tool, or a real
research run.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/agents/` prompt-rendering module.
- **Question:** How can one pure, deterministic rendering interface produce the exact
  system policy and child user message used by the node-agent bridge, and a safe
  reviewable catalog of each node prompt variant, without turning generated Markdown
  into a second runtime authority?
- **Necessary adjacent/external contracts:** `node-agent-runtime` answers how the
  bridge consumes the shared rendered message; `graph` answers which node builder
  branches reach a node-agent loop and therefore require a catalog case;
  `project-structure` answers how the new renderer, generator, tests, and committed
  catalog are registered. No upstream DeerFlow interface changes are needed.
- **Evidence seam:** a source-backed inventory test scans the direct
  `NodeExecutionRequest` builders in node prompt modules, deterministic catalog tests
  render their canonical synthetic fixtures into the exact committed output tree
  through the same check adapter selected by `make test-fast`, and a captured
  canonical-case bridge test proves runtime and review use the same final system/user
  messages.
- **Not in scope:** model or tool invocation, real-user or provider data, changes to
  prompt semantics solely for this catalog, generic prompt editing UI, `backend/`,
  `frontend/`, and the pending human-interaction UX adapter work.
- **Triggered charter policies:** local-context, authority-and-projections, change-admission

## What Changes

- Add one agents-owned pure prompt rendering and catalog interface, shared by the
  runtime bridge and the deterministic catalog generator.
- Add canonical, safe synthetic fixtures for every source-backed direct node
  prompt-builder variant, including normal and repair branches where applicable.
- Generate and commit a readable `agent/node_prompts/` Markdown catalog containing
  the exact common system policy, final user message, requested output contract, and
  requested tool policy for each fixture.
- Add `make prompt-dump` and a check mode so a prompt change produces a visible diff
  and stale generated artifacts fail deterministic verification.
- Add focused tests that prevent an unregistered prompt variant or repair branch,
  duplicated rendering logic, stale generated paths, hidden raw inputs, or
  model/tool/network execution during catalog generation.

## Capabilities

### New Capabilities

- `node-prompt-catalog`: Produces a deterministic, safe, complete catalog of the
  production-shaped node-agent prompts for review and test verification.

### Modified Capabilities

- `node-agent-runtime`: Uses the shared final-prompt renderer so the catalog is a
  faithful projection of the actual embedded agent input.
- `project-structure`: Registers the agents-owned renderer, generator, tests, and
  committed prompt-catalog path.

## Impact

- Affects `agent/src/deerflow_deep_research/agents/`,
  `agent/src/deerflow_deep_research/runtime/node_agent_bridge.py`, node prompt
  builders only as catalog callers, `agent/scripts/`, `agent/Makefile`,
  `agent/node_prompts/`, deterministic tests, and focused contributor documentation.
- Adds no model-provider, tool, runtime-config, checkpoint, lifecycle, backend, or
  frontend dependency.
