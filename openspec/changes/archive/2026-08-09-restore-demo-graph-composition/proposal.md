## Why

The standalone real CLI and TUI currently advertise all-real research, but their
shared transport omits a `BundleGraphExecutor`. Its generic host argument is used only
by the separate `infra_probe` action, so lifecycle dispatch instead reaches the
approved full-fake fallback in `BundleControl`. That can return a bounded terminal
completion without proving the recipe, bridge, checkpoint, graph trace, or
final-delivery path that the real demo claims to exercise. Migration also left the
zero-credential full-fake commands described as fixture behavior without an explicit
command that verifies an actual fixture graph.

## What Changes

- Restore one demo-runtime composition boundary that chooses a fixed all-real or
  fixture-graph recipe internally, creates any bridge required by that recipe and a
  `BundleGraphExecutor`, and binds it to the shared lifecycle transport.
- Make real CLI and TUI entry paths use that all-real runtime composition. A missing
  executor is a bounded startup failure; graph-backed entries must not reach the
  `BundleControl` full-fake fallback.
- Persist the graph-backed runtime's selected implementation mode in the Bundle and
  project it from that authoritative state. The fixture-graph route must therefore
  report `fixture`, while retained compatibility paths without a graph executor keep
  their existing all-real default rather than gaining a caller-selectable label.
- Add the explicit verification command `make demo-fixture-graph`. It runs the
  fixture recipe through the graph composition boundary and is described in its
  `--help` and README as a verification route, not as a replacement for the
  full-fake demos.
- Preserve `make demo`, `make demo-scripted`, and `make demo-tui-fake` as their
  existing zero-credential full-fake contracts. They remain visibly non-research
  demonstrations and do not silently switch to the fixture-graph route.
- Add deterministic entry-path composition evidence. It must observe fixed recipe
  selection and executor injection for all-real entries, then run the fixture-graph
  route through the concrete Bundle checkpoint, returned graph trace, and required
  final-delivery gate terminal fact rather than accepting a full-fake terminal
  completion. Fixture verification does not publish or claim report artifacts; a
  credentialed all-real execution remains a separately bounded optional smoke.
- Tighten the scripted real-demo smoke input so it supplies an explicit comparison
  pair in a supported language before asserting bounded report delivery.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `demo-pipeline`: Require explicit runtime-owned all-real and fixture-graph
  composition, retain the separately named full-fake commands, and expose the
  fixture-graph verification route truthfully.
- `research-demo-tui`: Require the default real TUI path to obtain its all-real
  executor from the same demo runtime boundary as the real CLI, while its fake route
  preserves the full-fake contract.

## Impact

- Primary owner: `deep_research_harness/scripts/_demo_core.py`.
- Adjacent demo adapters: `scripts/demo_real.py`, `scripts/demo_tui.py`, a new
  fixture-graph verification entry, `scripts/demo.py`, and the Harness Makefile and
  README command descriptions.
- Runtime interfaces consumed without new caller authority: `ResearchGraphRecipe`,
  `BundleGraphExecutor`, Bundle-local lifecycle state, and the trusted
  `run_deep_research()` executor-injection seam. The reflected public tool schema
  remains unchanged.
- Evidence: focused demo-core composition tests, real CLI/TUI entry-path tests,
  fixture-graph subprocess and concrete-lifecycle coverage, existing full-fake
  regressions, and an optional bounded credentialed smoke. No DeerFlow source,
  `backend/`, or `frontend/` changes are in scope.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/_demo_core.py`, which
  composes demo adapters, recipes, bridge factories, lifecycle transport bindings,
  and the transition into the trusted Bundle executor.
- **Question:** How can demo runtime composition select and execute an all-real recipe
  for real CLI/TUI paths and an explicit fixture recipe for verification, while the
  older full-fake commands retain their distinct contract?
- **Necessary adjacent/external contracts:** `runtime/research.py` answers which fixed
  recipe factories may be selected; `runtime/bundle_graph.py` answers how a trusted
  composition root creates a `BundleGraphExecutor`; `runtime/bundle_lifecycle.py`
  answers how the selected mode is retained and projected from Bundle-local state;
  `tool.py` answers how that executor is injected without adding public route
  authority; `runtime/run_experience.py` answers how returned typed Bundle outcomes
  reach presentation; `demo-pipeline` and `research-demo-tui` specs answer command
  and selected-mode compatibility.
- **Evidence seam:** the production `DemoLifecycleTransport` exercised through the demo
  runtime factory and real CLI/TUI entry adapters for fixed all-real composition; the
  separately named fixture-graph route then exercises its concrete recipe, executor,
  checkpoint, trace, and final delivery without replacing all-real external adapters.
- **Not in scope:** changing the `make demo*` full-fake contracts, exposing recipe,
  checkpoint, executor, or graph-route selection as CLI/public-tool inputs, changing
  public tool authority, implementing session recovery, or modifying `deerflow/`,
  `backend/`, or `frontend/`.
- **Triggered review policies:** control-placement, workflow-outcome-review, participant-outcomes

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Demo graph implementation selection | No cognitive candidate or human judgment; entry mode is fixed by the named local command | `build_demo_runtime(mode, adapter)` selects the fixed recipe, bridge, and executor before dispatch; the Bundle records that selected mode | non-bypassable | A real or fixture-graph lifecycle cannot start without its matching `BundleGraphExecutor`; caller inputs cannot select a recipe, checkpoint, or mode label | One shared composition boundary replaces duplicated CLI/TUI host binding and avoids a presentation-owned controller | Entry-path test observes the selected concrete recipe and executor passed through `DemoLifecycleTransport` into `run_deep_research()`; fixture lifecycle asserts its returned mode |
| Reported research completion | No candidate may declare completion | The graph-owned typed Bundle result, its persisted selected mode, and fixture final-delivery gate terminal fact determine the terminal outcome | non-bypassable | A `BundleControl` full-fake terminal cannot be rendered or accepted as completed research on a graph-backed entry; startup without an executor has a bounded failure and legal setup/verification action | Reuses existing `ResearchRunExperience` outcome projection and avoids a second demo completion state | Fixture-graph lifecycle test requires `implementation_mode=fixture`, graph trace, checkpointed final-delivery gate pass, and terminal state before a completed terminal projection |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Demo runtime lacks a required graph executor or its fixed composition cannot be built | Demo runtime boundary and its typed startup failure projection | No lifecycle dispatch without an executor; setup/configuration is corrected outside the run before a fresh invocation | Bounded startup fault; no research completion or recovery claim | Run the named full-fake route for its stated contract, or correct real-demo prerequisites and start a fresh real demo | Unit and entry-adapter tests prove graph-backed dispatch is rejected before the `BundleControl` full-fake fallback can be returned |
| All-real provider execution produces no graph-backed report or terminal delivery evidence | Graph-owned Bundle lifecycle result and final-delivery phase | Existing graph/runtime bounds govern provider and graph recovery; the demo adds none | Non-completed typed terminal/fault projected by `ResearchRunExperience` | Use the one next action already supplied by the typed outcome; do not infer resume or local retry | Optional credentialed smoke observes the real transport; deterministic fixture-graph coverage separately proves trace, checkpoint, final delivery, and selected-mode projection |
| Fixture-graph verification route is unavailable or fails | The fixture graph's returned typed Bundle lifecycle result | Existing deterministic fixture behavior only; no real provider fallback | Non-completed verification result | Inspect the bounded result or run the documented full-fake command for its separate demonstration purpose | Fixture-graph subprocess and composition tests distinguish this route from `make demo` and `make demo-scripted` |
