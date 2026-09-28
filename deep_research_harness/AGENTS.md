# Deep Research Coding Guide

This file is the self-contained code-change map for `deep_research_harness/`. The
application does not depend on the repository's development-governance framework.
`deerflow/` is a read-only upstream runtime framework: use its public API, never modify
or source-browse it for ordinary application work.

## Application Focus

Select one primary causal owner. Start with its closest implementation and lowest
responsible test seam; widen only for a named interface, authority, compatibility, or
observed-failure question. A possible future use is not enough to expand scope.

| Changed decision | Primary application owner | Try first; escalate when |
| --- | --- | --- |
| Typed meaning, invariant, or pure data contract | `src/deerflow_deep_research/domain/` | Config/profile expression first; escalate only when the typed contract itself must change |
| Deterministic validation, gate, or retry policy | `src/deerflow_deep_research/engine/` | Config knobs (`timeout`, `max_retries`, toggles) first; escalate when config cannot express the admission |
| Bounded model role, prompt, context, middleware, or candidate | `src/deerflow_deep_research/agents/` | Model/tool posture in `config.yaml` first; escalate when a bounded policy or middleware change is required |
| Phase composition, routing, or capability injection | `src/deerflow_deep_research/graph/` | Existing profile/composition knobs first; escalate when routing needs a new node or `NODE_SPEC` change |
| DeerFlow binding, trusted I/O, persistence, or lifecycle adapter | `src/deerflow_deep_research/runtime/` | Config/profile binding first; escalate when a trusted adapter or lifecycle seam must change |
| Presentation-only behavior | Its adapter/doc and the named owning result contract | Existing result projection first; escalate when a new observable fact must be owned |

## LLM-Node Authoring Gate

For a Coding Agent creating, changing, or reviewing an LLM-bearing node or direct
model branch, use this route before implementation navigation. Never infer the seam
from the first file found or from presence or absence of a model call.

This section is the complete application-owned cognition-versus-code contract: the
numbered route below plus the explicit Non-Model Work branch.

1. **Classify the surface** as `cognitive-program`, `deterministic-guardrail`,
   `human-decision`, or `wiring`. A model-bearing behavior symptom reaches cognition
   first unless rejected with a causal rationale; non-model work fabricates no prompt.
2. **Node Cognitive Control Contract and local capability**: read the owning contract;
   state the bounded cognitive responsibility, useful candidate,
   uncertainty/degradation posture, and what the model cannot decide.
3. **Prompt builder and model-visible context**: inspect the exact builder;
   distinguish trusted assignment and output-contract input from delimited untrusted
   content; name the requested method/tool posture and its runtime enforcer. A prompt
   cannot grant tools, permissions, writes, routes, retries, or result acceptance.
4. **Structured output, feedback, and repair**: trace candidate shape, feedback source
   and recipient, repair bound, and stop condition. Feedback is data, not authority to
   widen the task, select a route, or admit an effect.
5. **Focused proof and applicable cognitive evaluation**: use the lowest deterministic
   composition/admission proof, then state the cognitive evaluation and its limitation.
6. **Deterministic handoff owners**: only then inspect parser, evaluator/materializer,
   ledger, gate, graph, and other owners that admit legal effects and choose observable
   behavior.

## Where These Decisions Live

| Question | Application-owned first read |
| --- | --- |
| What may this node think about and return? | `src/deerflow_deep_research/agents/capabilities.py`, then the node package's `workflow.md` |
| What policy and context does the model see? | `src/deerflow_deep_research/agents/node_cognitive_control_program.py`, the node's `prompts.py`, and `agents/prompts.py` |
| Which tools/budgets are actually allowed? | `src/deerflow_deep_research/agents/policies.py`, `agents/middleware.py`, and the runtime adapter |
| What candidate shape is legal? | `src/deerflow_deep_research/agents/structured_output.py` and the node parser/domain contract |
| Who owns feedback and bounded repair? | The node's `workflow.md`, `prompts.py`, and `node.py` |
| What proves composition/admission? | Closest unit/graph/contract test for that owner |
| What supports a model-quality claim? | `tests/eval/` and applicable `tests/live/` evidence, with limitations stated |
| Who admits state, routes, and effects? | The node's `node.py`, then `engine/`, `graph/`, and `runtime/` owners |

Every node package `workflow.md` is a reader projection to its exact local sources. It
does not configure runtime behavior and does not replace code, typed contracts, or tests.

## Non-Model Work

For deterministic, human-decision, or wiring work without a causal model-bearing
symptom, begin at the actual typed/domain/control/graph/adapter owner and record why
cognition is not causal. Do not invent a capability, prompt, or repair loop.

## Information Map

| Need | Read first |
| --- | --- |
| How one run unfolds end to end (lifecycle vocabulary in order) | [`docs/run-lifecycle-walkthrough.md`](docs/run-lifecycle-walkthrough.md) |
| Product use, setup, demo ladder, commands and targets | [`README.md`](README.md), [`COMMANDS.md`](COMMANDS.md), [`Makefile`](Makefile) |
| How do I prove a change (lanes, receipts, mutations)? | [`docs/testing-and-evaluation.md`](docs/testing-and-evaluation.md) (Delivery lanes and receipts) |
| Runtime and authority boundaries | [`docs/runtime-architecture.md`](docs/runtime-architecture.md) |
| Local commands and profiles | [`docs/local-operations.md`](docs/local-operations.md) |
| Local demo ladder / operator runbooks (001–004 / 010 / 020 / 030 / 031) | [`docs/runbooks/README.md`](docs/runbooks/README.md) |
| Test-owned evidence/inventory support library (not tests) | [`tests/assets/README.md`](tests/assets/README.md) |

## Boundaries

- Keep current facts in owning code, typed contracts, tests, checkpoints, ledgers, or
  content authorities. A guide, summary, or diagnostic is not a second authority.
- Keep blocking I/O off the async event loop.
- Explore with `rg` (it honors `.gitignore`); avoid `find` / `grep -r` from this
  directory, which descend into the generated, ignored trees
  (`.deep-research-demo-runs/`, `.reports/`, `evals/runs/`, `.venv/`).
- Keep application tests and build commands independently runnable from this directory.
- Do not add nested `AGENTS.md` files or copy this guide into `CLAUDE.md`.

## Verification

Run the narrowest relevant test first; for TUI paths `make tui-journey` / `make debugger-proof`.
Record receipts (`make proof LANE=…`), prove guards (`make mutation-check`). Complete gate:
`UV_OFFLINE=1 make verify`.

## Structural Authority

The active `project-structure` spec owns structural requirements; exact inventory
lives in the structure registry. Do not edit the generated block below by hand;
update the owning change and registry, then re-render with the architecture checker.

<!-- BEGIN GENERATED: PROJECT-STRUCTURE -->
## Canonical Structure Locator

Exact inventory: the structure registry declared by the owning `project-structure` spec.

- Source root: `deep_research_harness/src/deerflow_deep_research/`
- Fixture source root: `deep_research_harness/src_fixtures/deerflow_deep_research_fixtures/`
- Test root: `deep_research_harness/tests/`
- Ownership layers: `runtime`, `domain`, `engine`, `agents`, `graph`
- Node grammar: `deep_research_harness/src/deerflow_deep_research/graph/nodes/` packages export `NODE_SPEC`; see the registry for files
- Validate: repository architecture governance (`check_project_architecture.py`)
<!-- END GENERATED: PROJECT-STRUCTURE -->
