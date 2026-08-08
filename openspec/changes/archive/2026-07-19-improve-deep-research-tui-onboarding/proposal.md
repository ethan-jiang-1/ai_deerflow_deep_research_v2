## Why

The real-mode TUI currently renders onboarding copy, an empty log, the full pipeline tracker, and the composer at once, so a first-time user has no clear first action. Its shared demo configuration also has no reliable demo-local web-tool binding, which can block the real pipeline even when model credentials are present.

## What Changes

- Replace the startup screen with a focused research-question composer and reveal the tracker and lifecycle log only when the lifecycle stage makes them useful.
- Preserve free-text HITL-1 and typed HITL-2 interaction, explicit lifecycle cancellation, and the existing graph/checkpoint authority; do not introduce a structured form or a second graph.
- Add a zero-credential `--fake` TUI route and `make demo-tui-fake`, while retaining `make demo-tui` as the real-mode route.
- Provide demo-local, policy-filtered Tavily search/fetch tools for the all-real recipe and require non-blank values for both a supported model credential and `TAVILY_API_KEY` before launching a real demo, without reading or mutating global DeerFlow tool configuration. Fetches are limited to URLs returned by the same agent run's search tools.
- Document the fake/real entry points and add deterministic coverage for stage visibility, fake-mode startup, real-mode prerequisite validation, and demo-local tool resolution.
- Keep progress truthful: show a bounded processing state during a blocking lifecycle call and refresh the tracker only from the returned `execution_trace`; contain unexpected lifecycle-worker failures in a visible terminal state; streaming or node-internal progress remains out of scope.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `research-demo-tui`: Simplify initial onboarding, make TUI surfaces lifecycle-stage-aware, and add an explicit zero-credential fake route alongside the bounded real-mode shell.
- `demo-pipeline`: Add demo-local real web-tool resolution and prerequisites, retain validated fake/real recipe selection, and expose the fake TUI Make target.

## Impact

- Affected agent-owned paths: `agent/scripts/demo_tui.py`, `agent/scripts/_demo_core.py`, `agent/scripts/demo_real.py`, `agent/Makefile`, `agent/pyproject.toml`, `agent/uv.lock`, demo tests, and `agent/README.md`.
- The real demo will require non-blank values for one supported model key (`DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY`) plus `TAVILY_API_KEY`; fake TUI mode requires neither credential nor network access.
- No Deep Research graph, node, checkpoint schema, production DeerFlow configuration, `backend/`, or `frontend/` change is introduced.
