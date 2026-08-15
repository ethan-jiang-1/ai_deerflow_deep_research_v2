# Deep Research Node Edit Map

> role: one-page terminology map from a node symptom to its correct first edit
> scope: `deep_research_harness/` LLM-Bearing Node work and its OpenSpec admission
> authority: guidance only; never runtime control, permission, or current-state truth

## LLM-Bearing Node Quick Reference

An LLM-Bearing Node is a two-part program: the **cognitive program proposes**, the
**deterministic boundary decides** — the **cognitive program is the first modification
seam**.

| Question | Product term · governance/implementation term | Focus Card value | Fix here first |
| --- | --- | --- | --- |
| Does this node have a model? | LLM-Bearing Node · node-agent | Node Agent Review `Classification`: `node-agent` / `no-agent` | — |
| Cognitive symptom: role, policy, candidate, or feedback wrong | Node Cognitive Control Program · capability Markdown + prompt builder | `cognitive-program` | capability Markdown / prompt builder / feedback |
| Cognitive work correct but still out of bounds | Deterministic Control Boundary · parser / gate / route / bridge | `deterministic-guardrail` | deterministic code |

Definitions live in `../../deep_research_harness/CONTEXT.md` (product glossary). Retired
terms `Phase Agent` and `MD controller` (DPT reference) are superseded by node-agent /
cognitive program. This page maps terms to their first edit and copies no definition.
