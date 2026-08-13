# Adjustment Record - C-004 Workspace And Bundle Definitions

- Status: verified
- Authority owner: Cognitive Evaluation Runner physical layout and the
  `cognitive-evaluation-suite` specification; Deep Research Run lifecycle remains owned
  by `deep-research-harness-run-bundles`.
- Affected paths: `deep_research_harness/CONTEXT.md` only.
- Before (current wording): Evaluation Run Workspace says it contains that execution's
  inputs, runtime state, artifacts, and Bundle.
- After (applied adjustment): the glossary names the Runner-owned, per-invocation
  execution directory and its sibling immutable Evaluation Run Bundle under one
  execution root; it says neither is the DeerFlow host workspace or a Deep Research Run
  Bundle.
- Reason and evidence: `runtime/evaluation/runner.py` creates `workspace/` and
  `bundle/` as siblings; CES-008 keeps evaluation Bundles separate from Deep Research
  Bundles.
- Main risk: glossary prose could accidentally redefine storage or lifecycle authority.
- Possible side effects: readers who inferred Bundle containment must use the owning
  Runner/spec for the physical layout; the shared word `workspace` still needs its
  host/evaluation qualifier.
- Risk controls / stop condition: edit only glossary wording; do not edit Runner,
  `evals/runs/`, main specs, host wording, or lifecycle behavior. Stop if any of those
  paths or semantics must change.
- Verification before apply: exact source line review and Runner/spec evidence above.
- Verification after apply: scoped diff changes only the two evaluation glossary entries;
  their wording matches the `workspace/` and `bundle/` sibling creation in the Runner.
- Observed side effects (including evidence bound): none observed in the changed
  documentation diff or static owner cross-check. This evidence does not execute the
  Runner or prove a future layout refactor cannot change it.
- Remaining mismatch / follow-up owner: any runtime-layout or lifecycle issue belongs
  to a separate owned code/spec change.
- Authorization and date: user authorized Stage 2 apply on 2026-08-13.
