# Proposal

## Why

The phase-0 walkthrough (change `run-agent-support-evidence-walkthroughs`, evidence table
row B-3) left exactly one open question: does a real model, under the committed controller
skill, make the direction-loop case's intent mappings by itself? Local records cannot
answer it — `evals/runs/` is empty, and the case contract requires a live external model.
The human approved moving forward with the one remaining active todo
(`todo-controller-evaluation-repetition`), whose budget framing this change now concretizes:
(17 + 6) scenarios × 3 fresh repetitions = 69 controller turns on the configured
`deepseek-v4-flash` model via `DEEPSEEK_API_KEY`, with the per-execution `cost_usd` telemetry
recording the actual spend. The machinery exists (registered cases, fail-closed runner,
review protocol, credential preflight — verified this session, credentials present,
network reachable); what is missing is the real-model controller subject and the runs.

## What Changes

- **Controller live subject driver**: constructs the real DeerFlow lead-agent composition
  (committed `SKILL.md`, dedicated Agent `SOUL.md`, configured `file:read` route, public
  `deep_research` schema — the same composition pattern the activation and handoff tests
  already prove, but with the real model instead of scripted turns), drives each scenario's
  `user_turn` through it with the lifecycle tool as a bounded recording fake that returns
  only the declared typed results for that scenario's `subject_state`, and records the
  model's actual proposal per scenario plus the case's required telemetry
  (provider/model/prompt+skill+soul+tool-schema digests/tokens/cost/latency).
- **Manifest code-revision provenance (CES-003 delta)**: the evaluation bundle manifest
  records the executing git worktree's revision at execution time; the field is additive
  provenance and does not gate review admission (this is the preflight folded in from the
  archived protocols audit, DONE-009 — its only consumer is exactly these runs).
- **The runs**: `run_selected_live_case_series` for `public-controller-direction-loop@v1`
  and `topic-planning-direction-loop@v1` (3 fresh isolated bundles each), recorded under
  the ignored `evals/runs/` tree.
- **Reviews and evidence**: review submissions per the versioned protocol (four-state
  result, evidence, confidence, unknowns, owning seam, follow-up — read-only, never
  rerunning the subject), prepared by this agent operating as the human-controlled
  interface under the user's explicit direction, with the recorded per-scenario proposals
  and rubric criteria as the evidence base; a results summary lands in this change's
  `evidence/` directory; the todo then flows to `_done/_done_todos/`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `cognitive-evaluation-suite`: CES-003 gains the manifest code-revision clause and one
  scenario. No other requirement changes; the driver consumes existing composition
  surfaces and does not alter the controller's cognition, prompts, or tools.

## Impact

- New: a controller live-subject module under
  `deep_research_harness/src/deerflow_deep_research/runtime/evaluation/` plus its tests;
  run evidence files under this change's `evidence/`.
- Touched: `deep_research_harness/src/deerflow_deep_research/domain/evaluation.py`
  (manifest field), `deep_research_harness/src/deerflow_deep_research/runtime/evaluation/runner.py`
  (revision recording), the case-adjacent test seams for the driver, and
  `_backlog/todos/todo-controller-evaluation-repetition.md` at completion.
- No production graph, lifecycle, prompt, skill, or tool-schema changes; the recorded
  runs are bounded evaluation evidence (`credentialed_live_quality` layer), never release
  authority or a profile/State/route input.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/` gitlink;
  the driver reuses the same DeerFlow public-API composition pattern already exercised by
  `tests/integration/test_public_skill_activation.py` and imports no new upstream surface.

## Change Focus

- **Primary module / causal owner:** the cognitive-evaluation live path of
  `deep_research_harness/src/deerflow_deep_research/runtime/evaluation/` (the controller
  subject driver and the manifest provenance it produces), which answers "what did the
  real model itself select, under which exact code, skill, and rubric identities".
- **Seam classification:** wiring — the driver assembles the existing production
  composition and records what happens; the controller's cognitive program, prompts,
  tools, and admission boundaries are unchanged, and the manifest field is a
  deterministic additive contract.
- **Question:** Can the registered direction-loop cases be answered with real-model
  evidence today — a real composition, real model selection per scenario, honest
  telemetry, reviewable bundles naming their code revision — and what does that evidence
  say about controller intent mapping?
- **Necessary adjacent/external contracts:** the registered cases, contracts, rubrics,
  and review protocol under `evals/control/`; the composition pattern proven by
  `test_public_skill_activation.py` / `test_public_controller_handoff.py` (scripted-model
  real-composition evidence this change complements); the public `deep_research` tool
  schema (`tool.py`); git as the revision authority for the manifest provenance.
- **Evidence seam:** the six retained bundles themselves (immutable, digest-verified,
  reviewable) plus deterministic unit/contract tests for the driver's fake lifecycle and
  the manifest field (red-first), and runner-written receipts for the lanes the touched
  surfaces cover.
- **Not in scope:** changing any controller cognition (skill, SOUL, prompts, tool
  schema), wave0/1/2 node quality cases, release claims from these runs, retries or
  resume of failed executions, and anything under `deerflow/`.
- **Triggered review policies:** none: wiring and additive provenance only, with no candidate admission change, no human-judgment surface change, no control fact, no recovery boundary, and no node-agent role change — the controller's cognitive program is measured, not modified.
