# Design: hard-real-auto (Mode 004)

## Context

Mode 003 (archived change `low-scale-real-auto`) established the intent
declaration mechanism end to end: `non_interactive_policy.profile_intent`
(`Literal["minimal"] | None`), the HITL1 auto branch constructing the profile
from the declared intent, and the wave2 gate budget resolver reading the
HITL-owned profile fields in state. The domain contract `StartRun.profile_intent`
already admits `None`, and `runtime/non_interactive.py` omits the key when the
intent is `None` — the default product path is fully implemented and unexercised
by any real automatic run.

Today the only place that selects an intent is `scripts/demo_real.py:493`:
`profile_intent="minimal" if scripted else None` (embedded smoke). The Gateway
path rejects `--scripted` entirely (the automatic policy is embedded-smoke-only).
`scripts/soft_bundle.py` already accepts `--mode 004` in argparse but has no
004 branch, no 004 fixed question, and no 004 verify/inspect coverage.

Research facts driving the design (all verified in code or by sandbox test,
2026-08-19):

- `derive_comparison_intake_seed("Compare China and US EV battery market in
  2024.")` succeeds: `comparison_required=True`, `output_language=en`, and
  subjects `('China', 'US EV battery market in 2024.')` — the auto branch will
  NOT fail closed (subjects are extractable), but the pair is asymmetric (lazy
  first, greedy second, trailing period retained). The pair flows into the
  planner's context (`topic_planning/prompts.py`).
- With no declared intent the auto profile is degraded (empty depth/cost/time),
  `single_topic=False`, planner topic count is free within `MAX_TOPICS=8`, and
  the wave2 gate budget resolver yields the default one round
  (`real_gates.py:_wave2_minimal_pair_budget_resolver`).
- The fixed question is 46 characters — far below the 256-character
  `must_answer` bound, so the auto `must_answer=(request_text,)` seeding is
  safe.

## Goals / Non-Goals

Goals:

- Make the default-intent (absent declaration) real automatic run reachable
  from the operator surface with zero product `src/` behavior changes.
- Keep mode 003 byte-identical in behavior (default flag value = `minimal`).
- Give mode 004 the same record-based bind/inspect/verify surface as 002/003.
- Document the rung honestly: observations (including the asymmetric seed) are
  recorded, not pre-fixed.

Non-Goals (design-level):

- No new intent values, no gate/domain/node/prompt changes, no budget changes
  (evidence-driven bug flow only, as established in 003).
- No Gateway-side automation (the Gateway rejects `--scripted`; changing that is
  a separate product decision).
- No fix to the comparison-subject extraction asymmetry before a real run shows
  harm.

## Decisions

- **D1 — flag shape: `--profile-intent {minimal,none}`, default minimal.** The
  flag name matches the `non_interactive_policy.profile_intent` field and
  the `StartRun.profile_intent` contract. `none` maps to Python `None`, i.e.
  the policy dict omits the key (today's absent-intent shape). The argparse
  default is a `None` sentinel meaning "no explicit selection": on the
  embedded-smoke `--scripted` route it behaves as `minimal`, preserving the
  current hardcode exactly, so mode 003 and every existing invocation without
  the flag are unchanged. An explicit selection outside that route
  (non-embedded-smoke, or non-scripted) is a usage error at argument
  validation, mirroring the existing `--profile` route rule. Alternatives
  rejected: a boolean `--no-minimal-intent` (less extensible, negative-polarity
  flag); renaming to `--research-intent` (diverges from the field name; D3 in
  the plan converged on `--profile-intent`).
- **D2 — flag scope: embedded-smoke route only.** The Gateway path continues to
  reject `--scripted` before any intent handling; the flag is admitted only on
  the embedded-smoke route (passing it on the Gateway route is a usage error,
  consistent with the existing `--scripted` rejection). The TUI does not gain
  the flag (its non-interactive runs keep declaring minimal, per DPL-003).
- **D3 — mode 004 wiring mirrors mode 003 exactly.** `MODE_QUESTIONS["004"]`
  registers the fixed comparison question; `cmd_run` gains an `elif mode ==
  "004"` branch delegating to `make demo-real-scripted` with
  `--question "<fixed>" --profile-intent none`; the bind-on-resolved-bundle
  (including non-zero exit) semantics are shared with 003; the verify
  report-required set becomes `{"002", "003", "004"}` and the inspect
  record-delegation set becomes `{"002", "003", "004"}`. No new binding logic.
- **D4 — observation points recorded, not fixed.** The runbook documents: (a)
  the asymmetric comparison subjects and what planner skew would look like
  (topics covering only one market); (b) expected topic range 2–5 (bounded by
  the 1–8 contract); (c) the likely one-round wave2 exhaustion degrading to an
  honest pass; (d) first real load on the multi-conclusion final layout path.
  Each has a bug-flow entry point; none is pre-fixed (003's evidence-driven
  rule).

## Risks / Trade-offs

- [Asymmetric seed subjects skew topic planning toward one market] → Runbook
  observation point; if the planner output covers only one subject, file the
  bug with the run's journal evidence and fix the extraction symmetrically.
- [Cost/time: worst case 8 topics × repair loops] → README already prices the
  rung at 花（多）; Ctrl-C and retry; run summary/journal observability
  (call_ordinal/usage_tokens) supports after-the-fact cost checks.
- [One-round wave2 budget exhausts immediately on a compare question] →
  Expected path: first exhaustion degrades to an honest pass with disclosure
  (inherited semantics); only repeated exhaustion blocks.
- [Final layout path under first real multi-conclusion load] → BUG-055's
  plan-order degraded layout is the guardrail; new shape failures go through
  the bug flow.
- [Hung provider SDK] → Ctrl-C + retry (inherited 003 runbook note); bridge
  hardening remains out of scope.

## Migration Plan

Additive CLI surface; no migration. Rollback = revert the two scripts and docs
(no product state, schema, or persisted-format changes).

## Open Questions

None — D1–D4 above were converged with the user (plan
`_backlog/plans/hard-real-auto-runs.md`, decisions D1–D3, 2026-08-19).
