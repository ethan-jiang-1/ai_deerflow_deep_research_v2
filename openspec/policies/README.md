# Deep Research Policy Library

> scope: recurring Deep Research design and review guidance
> authority: guidance only; never runtime control, permission, or current-state truth

This is the complete library of trigger-bearing Deep Research policies. Read the
[Agent Charter](../agent-charter/README.md) to select one relevant policy; the Charter
remains the only routing authority. These documents guide proposal authors and
reviewers while approved specifications, code, and tests retain authority over
behavior and current facts.

## Charter-Routed Design And Admission Policies

| Policy | Trigger |
|---|---|
| [local context](local-context.md) | A change needs a primary owner or bounded context route |
| [authority and projections](authority-and-projections.md) | A change adds a state record, summary, diagnostic, status view, or retained observation |
| [participant outcomes](participant-outcomes.md) | A change affects CLI, TUI, API, agent-visible, or machine-consumed lifecycle output |
| [human-interaction integrity](human-interaction-integrity.md) | A change adds or revises a human decision, semantic input, visible control, or interaction recovery |
| [node-agent workflow integrity](node-agent-workflow-integrity.md) | A change adds or materially revises a node's LLM-bearing role, tool posture, output admission, or repair semantics |
| [control and recovery](control-and-recovery.md) | A change adds retry, fallback, recovery, terminal handling, or a control check |
| [workflow outcome review](workflow-outcome-review.md) | A change adds or changes a model, tool, provider, worker, retry, terminal, diagnostic, or lifecycle projection path |
| [change admission](change-admission.md) | A contributor opens, revises, reviews, or applies an OpenSpec change |
| [agent information map](agent-information-map.md) | A contributor adds or revises an entry document |

## Cross-Cutting Review Guidance

| Policy | Trigger |
|---|---|
| [control placement](control-placement.md) | A change moves a candidate, human judgment, control fact, or deterministic admission/recovery boundary |

## Boundary

This index classifies documents for navigation only. It does not introduce a second
Agent Charter, infer policy applicability, approve a proposal, or replace an owning
capability specification. `openspec/guardrails/` is the separate home for executable,
bounded-evidence command contracts; it is neither a policy family nor native archive
authority. The policy library creates no semantic evaluator, automatic task writer,
archive coordinator, or archive blocker.
