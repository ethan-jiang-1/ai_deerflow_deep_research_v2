# Controller evaluation results — public-controller-direction-loop@v1

First credentialed-live evidence for the phase-0 walkthrough's open question
(B-3: does a real model, under the committed controller skill, make the
direction-loop case's intent mappings by itself?). Four executions on
`deepseek-v4-flash` via `DEEPSEEK_API_KEY` on 2026-09-27: one canary plus the
declared repetition series of three. Every bundle records the working-tree
code revision (CES-003 provenance) and the case's pinned control digests; the
lifecycle layer was a bounded recording fake, so these runs measure intent
mapping and proposal selection — lifecycle execution stays owned by the
scripted handoff tests.

## Executions

| execution | status | calls (bound 50) | tokens in/out | actions match | skill-read-first | review |
| --- | --- | --- | --- | --- | --- | --- |
| e_8b43ec1… (canary) | completed | 43 | 362k / 42k | 10/17 | 4/17 | `r_238f17…` **failed** |
| e_08f9eac4… (rep 1) | completed | 45 | 374k / 38k | 12/17 | 4/17 | `r_93afb0…` **failed** |
| e_9d6dfc49… (rep 2) | failed: `execution_resource_bound_exceeded` | >50 | — | 8/17* | 3/17* | not reviewable (failed execution; observation summaries only) |
| e_b66b54b5… (rep 3) | completed | 50 (at bound) | 399k / 30k | 9/17 | 2/17 | `r_b33078…` **failed** |

\* directional only: the runner rejected the aggregate call bound and did not
admit the subject output as evidence; per-scenario observation summaries
retain the proposals.

Cost: `cost_usd` recorded 0.0 with `cost_unpriced: true` (no price rates
declared for this run); the real token telemetry is the spend record —
roughly 1.53M input + 140k output tokens across the four executions on the
flash tier.

## What the real model did

- **Action mapping is partial and unstable**: 8–12 of 17 scenarios per
  repetition. Stable hits across all four: `new-request` (3/4),
  `correlated-answer` (3/4), `status` (3/4), `explicit-stop` (3/4),
  `exhausted-terminal-no-direction` (3/4), `unavailable-target` (3/4).
  Systematic misses across all four: `terminal-queued-direction-continuation`
  (0/4 — never selects refine on the terminal bundle), `ambiguous-terminal-
  follow-up` (0/4 — always acts instead of clarifying),
  `precommit-recovery-conflict` (0/4), `active-conflict` (0/4),
  `mixed-answer-direction` (1/4).
- **The load-before-select discipline is systematically weak**: the model
  read the committed skill before proposing in only 2–4 of 17 scenarios per
  repetition, despite each scenario running on a fresh thread. This is the
  rubric's critical criterion (`controller.load-before-select`) and it fails
  in every repetition — the reason all three reviewable bundles carry a
  **failed** verdict.
- **infra_probe drift**: six instances across repetitions, concentrated in
  the direction-change and conflict scenarios — the model probes
  infrastructure when it is uncertain about the direction semantics.
- **Budget discipline is marginal**: 43 / 45 / 50 / over-50 calls. One of
  four repetitions busted the amended bound; two landed at the edge.

## Honest boundaries

- The lifecycle answers were declared typed results per `subject_state`, not
  real lifecycle execution; the seeded conversation prefixes carried neutral
  state facts. A different state-establishment design could shift proposals.
- One model, one tier, four executions: variance observed (8–12/17), no
  cross-model or prompt-variation comparison.
- Whether the skill-read skipping is model choice or a composition-hint
  artifact is UNVERIFIED here: the handoff tests prove the loading path works
  when scripted; the raw responses in the retained bundles are the next
  diagnostic input.
- The `cost_usd` figures are unpriced placeholders (tokens are the real
  record).

## Disposition

The controller half of `todo-controller-evaluation-repetition` is answered
with measured evidence: the controller's real-model intent mapping on this
case is **not reliable enough to pass its own rubric** — the critical
skill-loading discipline fails in every repetition, and the refine-family
scenarios never pass. The follow-up seam recorded in every review: diagnose
the skill-read skip first (composition hint vs model judgment), then the
direction-change scenarios. The topic-planning node subject (tasks 2.4/3.4)
remains open in this change for the next session; until it lands, the todo
stays active with its controller half delivered.
