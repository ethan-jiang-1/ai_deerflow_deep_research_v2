# Adjustment Record - C-005.a Completed-Work Tense

- Status: verified
- Authority owner: existing evaluation control/run-data layout and its owning
  `cognitive-evaluation-suite` specification.
- Affected paths: `deep_research_harness/CONTEXT.md` only.
- Before (current wording): the evaluation-control summary calls the Suite `new` and
  says the V1 structural change `must explicitly update` governance and ignore rules.
- After (applied adjustment): the summary describes the current separated control
  surface, ignored run store, Runner source layer, and distinct `tests/eval/` role
  without a completed-work future obligation.
- Reason and evidence: those directories and roles are already present; the adjustment
  record C-005.a approved retiring only the implementation tense.
- Main risk: a rewrite could drop the valid control/run-data separation.
- Possible side effects: the historical implementation sequence is less visible from
  this glossary and readers may need the current owner for details.
- Risk controls / stop condition: retain the separation and all four current owners;
  stop if a main-spec, governance, ignore-rule, or structural change is needed.
- Verification before apply: exact source paragraph reviewed against C-005.a.
- Verification after apply: scoped diff retains `evals/control/`, `evals/runs/`, the
  Runner source layer, and `tests/eval/`, while removing only `new` and the completed
  V1 structural-change obligation.
- Observed side effects (including evidence bound): none observed in the changed
  documentation diff. Historical implementation sequencing is no longer stated here;
  this check does not remove or validate historical artifacts.
- Remaining mismatch / follow-up owner: historical implementation provenance remains
  in history, not this current glossary.
- Authorization and date: user authorized Stage 2 apply on 2026-08-13.
