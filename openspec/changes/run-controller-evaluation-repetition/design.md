# Design

## Context

See proposal.md — Why. The runner, series entrypoint, credential preflight, cases,
rubrics, and review protocol all exist and were verified this session; credentials
(`DEEPSEEK_API_KEY`, model `deepseek-v4-flash`) are present on this machine and the
provider endpoint is reachable. The handoff tests prove the composition with scripted
model turns ("the handoff after selection, not model judgment", DEC-003/004); this
change supplies the missing complement: real model judgment through the same real
composition. One invocation = one immutable bundle; the subject itself iterates the
case's scenarios (17 or 6 real-model turns) and returns one aggregated
`SubjectExecution`.

## Goals / Non-Goals

**Goals:**

- A real-model controller live subject whose composition is exactly the committed
  surface (digest-verified SKILL/SOUL/tool schema) and whose lifecycle layer is a
  bounded recording fake returning only the declared typed results for each
  scenario's `subject_state`.
- Every bundle names the code revision that produced it (additive manifest
  provenance, review-admission-neutral).
- Six retained, reviewable bundles (2 cases × 3 repetitions) plus review records and
  an honest summary — whatever the model did, including failure to map intent.

**Non-Goals:**

- No change to controller cognition (skill, SOUL, prompts, tool schema), no wave
  node cases, no release claims, no retry/resume of failed executions (a provider
  failure is an honest `failed` bundle, per the case contract).
- No auto-review: review submissions are explicitly initiated per CES-004, by this
  agent as the human-controlled interface under the user's direction.

## Decisions

- **Subject module placement**: `src/deerflow_deep_research/runtime/evaluation/`
  beside `live.py` — it is production-adjacent eval tooling like the other subjects,
  importable by the manual invocation, with deterministic tests beside the existing
  eval suite. The invocation itself stays manual Python (the suite's documented
  pattern), driven from `deep_research_harness/` with `.env` exported into the
  process environment.
- **Real composition, real model**: reuse the `configure.py` + config pattern proven
  by `test_public_skill_activation.py` (isolated DeerFlow home, committed skill at
  the container path, `file:read` route, `deep_research` tool) but with the real
  model endpoint: OpenAI-compatible `ChatOpenAI` against the configured
  `deepseek-v4-flash`, the API key read from `DEEPSEEK_API_KEY` at runtime and
  written only into the execution workspace's temp home — never into a committed
  file. The model identity lands in telemetry (`provider`/`model`), and the runner's
  digest validation proves the committed skill/soul/tool-schema actually loaded.
- **Lifecycle fake per scenario**: the fake answers only with `BundleControlResult`
  -shaped declared results implied by the scenario's `subject_state` (e.g.
  `suspended_with_correlated_subject` → status/resume surfaces that bundle;
  `terminal_with_queued_direction` → terminal + retained refinement projection),
  freshly installed per scenario so no state crosses scenarios. The fake is
  deterministic and unit-tested against every `subject_state` the two cases declare;
  an undeclared state fails closed rather than improvising a result.
- **Capture semantics**: per scenario, record the model's observable proposal —
  whether it read the skill first (the `file:read` tool call to the skill container
  path), and what it proposed (the `deep_research` action call arguments, or a
  clarification reply with no lifecycle call) — plus turn telemetry. The aggregate
  `SubjectExecution.output` carries one record per scenario; `resource_use` carries
  the case's required fields including the four control digests.
- **Manifest provenance**: `EvaluationBundleManifest` gains
  `code_revision: str | None = None` (schema stays 1; additive optional, so
  pre-existing manifests remain valid and review admission does not require it).
  The runner resolves the revision from the repository root at execution start
  (`git rev-parse HEAD`, best-effort: absent outside a worktree) — matching the
  CES-003 delta's "when the executing repository is a git worktree".
- **Two subject architectures (implementation discovery)**: the two registered cases
  measure different surfaces and need different subjects —
  `public-controller-direction-loop@v1` drives the real lead-agent composition
  (this change's core B-3 question), while `topic-planning-direction-loop@v1`
  drives the `topic_planning` node's cognitive program through
  `graph_context.run_agent` (a node-bridge subject, like the wave cases' shape).
  No live subject exists for any case yet (`evals/runs/` is empty; the suite
  doc's dependency helpers are caller-supplied examples), so this change builds
  both, controller first.
- **Corpus budget correction (implementation discovery)**: the case's declared
  `max_model_calls: 18` was calibrated for a single-call-per-scenario node
  subject and is incoherent with the case's own contract: the real lead-agent
  composition needs at least read + proposal + closing response per action
  scenario (the handoff tests script exactly three responses), so any honest
  controller subject consumes ~48 calls for 17 scenarios. Amended in place from
  18 to 50 (the domain contract's own ceiling for the field; the never-consumed
  v1 — `evals/runs/` is empty, no test or registry digest pins the value) with
  modest headroom for occasional extra responses; tool budget 54 already covers
  the ~34 tool calls; the 900s timeout holds a full fresh-thread session on the
  flash-tier model. If a live model busts the 50 ceiling, the recorded fallback
  is the leaner shared-thread subject (one amortized skill read, ~35 calls).
  Recorded loudly here and in the evidence rather than absorbed silently.
- **Staged spend**: validate the whole pipeline with ONE controller invocation
  (17 real-model turns — composition, model, fake lifecycle, capture, manifest,
  reviewability) before the full series; then the controller series (×3); the
  topic-planning subject and its series (6 × 3) land after the controller
  evidence, still inside this change. Total ≈ 69 + 17 canary real-model turns on
  the flash-tier model; actual cost is recorded per execution in `cost_usd` and
  reported in the evidence summary rather than estimated.

## Risks / Trade-offs

- **Live flakiness**: provider hiccups produce honest `failed` bundles (no retry per
  the entrypoint's contract); the summary reports execution status separately from
  the four-state review result, so a failed execution is never read as a cognitive
  pass.
- **Fake-vs-real boundary**: the lifecycle fake means these runs measure intent
  mapping and proposal selection, not lifecycle execution (the handoff tests own
  that half). The evidence summary states this boundary explicitly.
- **Model variance**: three repetitions per case give a first variance signal, not a
  statistical claim; review results use the protocol's confidence and unknowns
  fields rather than overclaiming.
- **Timeout fit**: the case-declared execution timeout must cover a full
  multi-scenario real-model session; the apply phase verifies the declared bounds
  before the first run and stops if the declared budget cannot hold the series.
