# Low-Scale Real-Auto Runs (Mode 003 End-to-End)

## Why

Runbook 003 (real model + real web tools, fully automatic) must complete end to
end at the lowest practical investigation scale, without polluting the product
default behavior. An earlier attempt (v1) changed product defaults directly
(worker budgets, wave2 gate budget, node budgets, domain normalization) to make
the real run pass — that made the tested path differ from a real production run
and was reverted entirely. The scale/cost/time **intent** belongs in the
Research Profile (the HITL1-confirmed research brief, globally visible to every
node), and product defaults must stay untouched: a run without the declared
minimal intent behaves today exactly as it does now. Real-model output
adaptation (provider shapes the scripted template never produced) is a separate,
scale-independent product defect class that any real run hits.

## What Changes

- **Intent declaration mechanism (A).** `non_interactive_policy` gains an
  optional `profile_intent` (`minimal`; absent = today's behavior) — a product
  mechanism for non-interactive automatic runs to express research intent.
  `hitl1/node.py` auto branch constructs the profile from the declared intent:
  `minimal` seeds `depth=quick_overview, cost_tolerance=minimal,
  time_budget=very_quick` (still degraded, no model call), so the existing
  `single_topic` derivation forces exactly one topic; absent intent keeps the
  current degraded profile. Interactive HITL1 and the 002 scripted-template path
  are unaffected. Mode 003 (the operator entry) simply declares `minimal` — the
  run exercises the real product path with a minimal intent, not a test branch.
- **Intent consumption (B).** `GateDefinition` gains an optional budget resolver;
  the wave2 gate defines one that reads the HITL-owned profile intent fields in
  graph state (`cost_tolerance`, `time_budget`) and yields two evidence rounds
  for the minimal pair, `None` (→ the default one round) otherwise. The gate only
  READS state — the GATE-owned `repair_budget_by_phase` writer role is untouched.
  Wave worker budgets are NOT tiered (worst-case caps; bounded single-topic runs
  use 1-3 calls), and no envelope/recipe/capability API changes are made — this
  deliberately avoids the capability-construction timing problem (capabilities
  are built before the run's profile exists).
- **Real-model output adaptation (C).** `domain/synthesis.py` normalizes string
  priority labels (`high`→1, `medium`→3, `low`→5) and non-contract gap
  `source_questions` (prose folded into the description) at the deterministic
  contract boundary; `domain/targeted.py` normalizes provider source shapes
  (`url`→`canonical_url`, derived `source_id`); the wave2 repair path's second
  parse is guarded so a still-invalid repaired candidate terminates as a bounded
  `exhausted` instead of crashing the graph. The auto profile also gains
  `must_answer=(request_text,)` (any automatic run currently produces an empty
  final report — observed; requests over the 256-character must-answer bound fail
  closed, never truncated). The wave2 synthesis node budget is raised from
  scripted-template calibration to bounded real-output headroom (≈4 calls / 64K /
  16K output / 300 s) — real runs exhaust the scripted-calibrated budget on real
  output (observed `budget.exhausted`). readiness/final-delivery budgets stay
  unchanged until real runs demonstrate a need (evidence-driven). These are
  scale-independent product fixes, not test-only
  relaxation.
- **Operator entry (D).** `scripts/soft_bundle.py` mode 003 delegates to
  `make demo-real-scripted --question "<fixed>"`, records the bundle, and reuses
  the record-based inspect/verify (003 requires `final/report.md`). New
  runbook-003 and the local-demo README row document `.env` prerequisites
  (`DEEPSEEK_API_KEY`, `TAVILY_API_KEY`, `DEERFLOW_DEMO_MODEL`).

## Capabilities

### New Capabilities

- `execution-intent`: the optional non-interactive `profile_intent` declaration
  (`minimal` | absent) and its deterministic consumption — the minimal profile
  (driving the existing `single_topic` planner derivation) and the wave2 gate
  budget resolver (reading the HITL-owned profile intent fields in state); absent
  intent keeps today's behavior.
- `low-scale-real-auto`: the mode 003 end-to-end acceptance — a declared-minimal
  real auto run completes at `final_delivery` with a real `final/report.md` and
  one wave0 + one wave1 work unit; runs without the declared intent promise no
  single-topic breadth.

### Modified Capabilities

- `hitl1-node`: the non-interactive auto branch constructs the profile from the
  declared intent (minimal trio when `profile_intent=minimal`, current degraded
  profile when absent) and always seeds `must_answer=(request_text,)` (product fix:
  automatic runs currently produce an empty final report).
- `node-agent-runtime`: the wave2 synthesis node budget gains real-output headroom
  (scale-independent product fix, evidence-driven; readiness/final-delivery budgets
  unchanged).
- `wave2-synthesis-node`: provider string priority labels and natural-language gap
  `source_questions` normalize to the typed contract; a repaired candidate that
  still fails validation terminates as a bounded `exhausted`; the wave2 gate
  budget resolves from the profile intent fields in state (minimal pair → two
  evidence rounds, else the default one).
- `soft-bundle-session-cli`: mode 003 runs the real-auto embedded-smoke route
  with the minimal intent declared and requires `final/report.md` on verify.
- `demo-pipeline`: credentialed demo non-interactive runs declare the minimal
  intent at the entry, exercising the real product path.

## Impact

- `deep_research_harness/src/deerflow_deep_research/graph/nodes/hitl1/node.py` (auto
  branch: intent-constructed profile + must_answer)
- `deep_research_harness/src/deerflow_deep_research/runtime/non_interactive.py`,
  `runtime/tool.py` (optional `profile_intent` admission)
- `deep_research_harness/src/deerflow_deep_research/domain/gate.py`,
  `engine/gate_kernel.py`, `engine/real_gates.py` (gate budget resolver)
- `deep_research_harness/src/deerflow_deep_research/domain/synthesis.py`,
  `domain/targeted.py`
- `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave2_synthesis/node.py`,
  `graph/nodes/targeted_evidence/prompts.py`
- `deep_research_harness/src/deerflow_deep_research/runtime/research.py` (wave2
  synthesis budget headroom only)
- `deep_research_harness/scripts/soft_bundle.py`, `scripts/demo_real.py` (mode 003
  entry; declares `profile_intent=minimal`)
- Tests: `tests/graph/test_hitl1_node.py`, `tests/graph/test_wave2_provider_shapes.py`,
  `tests/graph/test_wave2_synthesis_real.py`, `tests/graph/test_targeted_evidence_real.py`,
  `tests/unit/test_research_runtime_capabilities.py`, `tests/unit/test_non_interactive.py`,
  `tests/engine` (gate resolver), `tests/contract/test_soft_bundle_cli.py`
- Docs: `_backlog/_local_demo/runbook-003-medium-real-auto.md` (new),
  `_backlog/_local_demo/README.md`
- No `deerflow/` gitlink changes; no product `deep_research` tool schema changes;
  no envelope or capability-construction API changes.

## Change Focus

- **Primary module / causal owner**: `deep_research_harness/src/deerflow_deep_research/graph/`
  (node behavior: hitl1 auto-profile intent and wave2 repair-path bounding).
- **Seam classification**: `deterministic-guardrail` — profile intent is
  deterministic data flowing through existing channels (profile → planner; profile
  intent fields in state → wave2 gate budget resolver); no new model role, prompt,
  or projection machinery is added.
- **Question**: How does mode 003 (real model + real web tools, fully automatic)
  run through at the lowest practical investigation scale while every product
  default (absent intent) behaves exactly as today?
- **Scope honesty**: mode 003 validates the non-interactive operator path under a
  declared minimal intent; it does not claim coverage of the Gateway interactive
  path.
- **Necessary adjacent/external contracts**:
  - `domain/profile.py`: the intent dimensions (`cost_tolerance`, `time_budget`,
    `research_depth`) and how the planner and gate resolver read them
    (typed-data question).
  - `domain/gate.py` + `engine/gate_kernel.py` + `engine/real_gates.py`: the gate
    budget resolver contract and the wave2 gate's resolver (control-placement
    question).
  - `runtime/tool.py` + `runtime/non_interactive.py`: closed admission of
    `profile_intent` (trusted-context question).
  - `domain/synthesis.py` + `domain/targeted.py`: provider-shape normalization at
    the deterministic contract boundary (real-model adaptation question).
  - `scripts/soft_bundle.py` + `scripts/demo_real.py` `--embedded-smoke --scripted`:
    operator entry declares `profile_intent=minimal` (operator-surface question).
- **Evidence seam**: `tests/graph/test_hitl1_node.py`,
  `tests/unit/test_research_runtime_capabilities.py`,
  `tests/unit/test_non_interactive.py`, `tests/engine` (gate resolver),
  `tests/graph/test_wave2_provider_shapes.py`, `tests/graph/test_wave2_synthesis_real.py`,
  `tests/graph/test_targeted_evidence_real.py`, `tests/contract/test_soft_bundle_cli.py`;
  end-to-end: zero-cost 002 scripted-real regression plus one real 003 run
  (RESULT: PASS, real report, one work unit per wave).
- **Not in scope**: Gateway observer route, runbook 004, interactive HITL1
  journeys, `deerflow/` gitlink, bridge timeout hardening against a hung provider
  SDK (independent concern), `MAX_SOURCE_REFS` and other domain constants.
- **Triggered review policies**: `node-agent, workflow-control, deep-research`

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wave2 synthesis node (initial + repair) | cognitive-program (unchanged role) | Synthesize accepted evidence into structured findings/gaps; the node's cognitive contract is unchanged — this change only hardens admission and failure | Only assigned accepted evidence from the selected Run Bundle (unchanged) | Zero tools; `tools_resolver` returns none (unchanged) | `parse_synthesis_output` → `domain/synthesis.py` normalization → `SynthesisResult` validation; provider shapes normalize deterministically | Repair path failure → bounded `exhausted` with typed `output.structured_invalid`; budget → typed exhausted (unchanged) | `tests/graph/test_wave2_provider_shapes.py`, `tests/graph/test_wave2_synthesis_real.py` |
| hitl1 auto-profile branch | deterministic-guardrail (no model call) | No agent: the non-interactive policy constructs the minimal profile deterministically | Non-interactive policy admitted only through the trusted runtime context (`tool.py`) | No tools; branch never calls `run_agent` | Profile written via `RequestBundleStore`; planner enforces `single_topic` from the profile intent | None (deterministic); planner mismatch is its own repair bound | `tests/graph/test_hitl1_node.py` |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Wave2 repaired candidate still fails validation | wave2 node repair path | Node-local: one repair round; still-invalid repaired candidate terminates (no unbounded loop) | `exhausted` route, terminal blocked, incident `output.structured_invalid` | Start a new research run (fresh start) | `tests/graph/test_wave2_synthesis_real.py` |
| Wave2 searchable gaps persist across evidence rounds | wave2 gate (`_wave2_searchable_gap_rule` + budget resolver) | Gate budget resolver: minimal profile intent pair → two rounds; otherwise one, unchanged | `evidence_needed` → targeted evidence; budget exhausted → blocked | Fresh start or profile change | `tests/engine` (gate resolver), real-run journal |
| Model call exceeds budget | Node policy budget | Budget enforcement at the bridge; no retry once exhausted | Typed exhausted projection (unchanged) | Adjust scope/budget or start a new run | Real-run event journal |
