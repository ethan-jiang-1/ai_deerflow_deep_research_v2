## Why

The declared non-interactive policy is currently admitted only as loose runtime
context and is not carried into the graph's initial state. Consequently, a trusted
scripted invocation cannot prove the graph-owned path that its contract promises,
and a presentation adapter could be tempted to substitute its own lifecycle control.

## What Changes

- Introduce one closed, validated action-input boundary for a trusted non-interactive
  policy. It accepts the canonical `non_interactive=True` marker, or the existing
  trusted `disable_clarification=True` compatibility marker, only with both
  `auto_profile=True` and `auto_proceed=True` as actual booleans; absent, incomplete,
  or malformed policy remains a bounded denial before Bundle mutation.
- Project explicit scripted intent through `ResearchRunExperience` without granting
  the presentation layer graph, route, profile, or checkpoint authority.
- When trusted runtime composition supplies a `BundleGraphExecutor`, write the
  admitted policy exactly once with that new Bundle's initial graph values. The
  selected Bundle checkpoint then owns it across graph continuation and resume;
  later actions do not reinject or replace it. Policy propagation neither selects
  an executor nor turns an uncomposed fallback/full-fake lifecycle into graph work.
- Make the existing HITL1/HITL2 policy consumers observable through the real graph:
  HITL1 only records a degraded default profile after its comparison/language
  admission, HITL2 proceeds with an audit note, and an unsupported scripted profile
  condition follows the existing truthful `GATE_BLOCKED` outcome.
- Preserve ordinary interactive lifecycle behavior and all existing public action
  authority. No code under `deerflow/`, `backend/`, or `frontend/` is in scope.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `runtime-operations`: tighten trusted non-interactive policy admission, initial
  graph-state propagation, checkpoint ownership, and deterministic policy outcomes.
- `runtime-integration`: make the reflected lifecycle boundary distinguish a valid
  trusted scripted policy from a non-interactive request that must be denied before
  mutation.
- `research-run-experience`: project scripted intent as typed action input without
  turning the run-experience adapter into a lifecycle controller.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/bundle_graph.py` (`BundleGraphExecutor`) owns the one-time transition from an admitted action input to initial graph values for a selected Bundle when trusted runtime composition supplies that executor.
- **Question:** How can a complete trusted non-interactive policy enter a new composed Bundle graph's initial state exactly once, then remain checkpoint-owned through continuation and resume?
- **Necessary adjacent/external contracts:** `tool.py` answers trusted runtime-context admission and bounded pre-mutation denial; `runtime/run_experience.py` answers how explicit scripted intent is projected without lifecycle authority; `runtime/bundle_control.py` answers how the selected Bundle invokes the graph executor; HITL1/HITL2 answer how checkpointed policy is consumed through existing node-owned validation and routes; no DeerFlow internals are needed.
- **Evidence seam:** A deterministic lifecycle integration test calls production `run_deep_research()` with an actual `BundleGraphExecutor` and controlled external adapters, then observes the initial-state handoff, checkpoint reload, and graph-owned terminal/projection result.
- **Not in scope:** Demo recipe or CLI/TUI composition, caller-selectable graph routes or executors, changing the uncomposed fallback/full-fake lifecycle, new public tool fields, synthetic HITL responses, generic GraphHost behavior, provider live evidence as a substitute for deterministic proof, and all `deerflow/`, `backend/`, and `frontend/` changes.
- **Triggered review policies:** change-admission, local-context, authority-and-projections, human-interaction-integrity, control-and-recovery, workflow-outcome-review, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Admission of a scripted policy | None; trusted runtime context carries an asserted mode | `tool.py` validates the closed typed action input before Bundle mutation | non-bypassable | Only an explicit `True`/`True` policy may bypass interactive input; malformed or incomplete input has the existing bounded denial | Avoids context-truthiness checks and presentation-side approval | Direct tool-boundary validation cases |
| Initial policy ownership | None | A trusted-composed `BundleGraphExecutor` writes initial graph values; the selected Bundle checkpoint owns later reads | non-bypassable | Resume cannot inject, replace, or create a parallel policy owner; an uncomposed lifecycle does not acquire graph work | Avoids a second controller in CLI/TUI or `ResearchRunExperience`, and avoids changing the fallback contract | Production lifecycle plus checkpoint-reload integration test |
| Scripted profile/proceed effects | No new human decision; HITL1/HITL2 consume a checkpointed policy | HITL1 validates profile facts and HITL2 owns its existing route | bounded-repair | Unsupported profile facts block truthfully; no default pair/language or fabricated response | Reuses node validation and terminal outcome instead of a demo workaround | Graph lifecycle test with valid and blocked scripted inputs |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Missing, incomplete, or non-boolean trusted policy | Tool action admission | None; reject before Bundle mutation | Existing bounded interactive-required denial | Use an interactive invocation with legal input | Tool-boundary table test |
| Scripted profile lacks an admissible pair or language | HITL1's checkpointed validation/result | HITL1 has no policy repair for missing required facts | Existing `GATE_BLOCKED` terminal with no profile artifact | Start a new interactive research request | Lifecycle integration test verifies terminal facts and absent artifact |
| Graph continuation/restart after admitted policy | Selected Bundle checkpoint and graph executor | Existing Bundle continuation only; no later input injection | Existing Bundle-owned result | Existing lifecycle action derived from the Bundle result | Checkpoint reload and resume integration test |

## Impact

- Runtime: `tool.py`, `runtime/run_experience.py`, `runtime/bundle_control.py`, and
  `runtime/bundle_graph.py`.
- Graph consumers: HITL1/HITL2 only at their existing checkpointed policy seams.
- Tests: focused tool, runtime lifecycle, graph policy, and checkpoint-reload
  integration evidence using controlled adapters and an explicitly composed executor.
- Existing uncomposed fallback/full-fake lifecycle behavior remains unchanged; demo
  composition remains owned by the later Stage 2 change.
- No dependency, public reflected-tool schema, DeerFlow framework, or external
  provider contract changes.
