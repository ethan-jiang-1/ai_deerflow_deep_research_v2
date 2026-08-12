# Adjustment Record - C-007 Policy Cardinality

- Status: verified
- Authority owner: Focus Card checker/parser and `deep-research-agent-charter` main spec.
- Affected paths: `openspec/CONTEXT.md`, `openspec/agent-charter/README.md` only.
- Before (current wording): the OpenSpec glossary says the Charter routes to one policy;
  the Charter says to choose one policy from its route table.
- After (applied adjustment): both documents state one primary causal owner and only
  every canonical policy whose route-table trigger actually applies.
- Reason and evidence: checker parsing uses comma-separated canonical policies and the
  main spec permits the same form; this is documentation correction, not checker change.
- Main risk: multi-policy wording could encourage loading the entire library.
- Possible side effects: a multi-trigger proposal may require more review records and
  planning work; no parser or runtime behavior changes.
- Risk controls / stop condition: retain `only actually triggered`; do not change the
  checker, policies, config, or a runtime authority. Stop if a parser/validation change
  becomes necessary.
- Verification before apply: checker behavior and charter main-spec requirement reviewed.
- Verification after apply: scoped diff touches only the two route descriptions and
  retains the no-whole-library direction; Charter governance is pending final run.
- Observed side effects (including evidence bound): no parser, policy, configuration,
  or runtime change is present in the scoped diff. This local diff review does not claim
  that all future proposals select policies correctly.
- Remaining mismatch / follow-up owner: no implementation follow-up expected.
- Authorization and date: user authorized Stage 2 apply on 2026-08-13.
