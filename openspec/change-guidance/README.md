# Deep Research Change Guidance

> authority: local routing only; guidance never creates runtime behavior or permission

For product orientation read [product/README.md](../product/README.md). Start ordinary
changes with [Core Change Practice](core/change-practice.md) and one primary causal owner.

For creating, changing, or reviewing an LLM-Bearing Node, first read the
[portable Node-Agent contract](profiles/node-agent/node-agent.md), then the adopting
application's own coding guide. In this repository the application-owned first read is
[`deep_research_harness/AGENTS.md`](../../deep_research_harness/AGENTS.md); the
application does not link back to this development framework.

## Policy Route

| Trigger | Canonical policy | Owner |
| --- | --- | --- |
| State, recovery, human decision, outcome, or control placement | rules in `workflow-control.md` | [workflow-control](profiles/workflow-control/workflow-control.md) |
| LLM role, tool posture, candidate admission, repair, or classification | rules in `node-agent.md` | [node-agent](profiles/node-agent/node-agent.md) |
| DeerFlow public interface, gitlink, or upstream compatibility | rules in `deerflow-downstream.md` | [deerflow-downstream](profiles/deerflow-downstream/deerflow-downstream.md) |
| Local module/seam, Program, operation, or information-map rule | rules in `deep-research.md` | [local composition](local/deep-research.md) |
| Fact owner versus projection and change admission | rules in `change-practice.md` | [core](core/change-practice.md) |

Canonical documents: [core/change-practice.md](core/change-practice.md),
[profiles/workflow-control/workflow-control.md](profiles/workflow-control/workflow-control.md),
[profiles/node-agent/node-agent.md](profiles/node-agent/node-agent.md),
[profiles/deerflow-downstream/deerflow-downstream.md](profiles/deerflow-downstream/deerflow-downstream.md),
and [local/deep-research.md](local/deep-research.md).

All three profiles are enabled for this project. A change selects every triggered
canonical policy; disabled profiles would contribute no selectable policy or review.
Local Program grammar, paths, budgets, module map, and operations remain under
`local/`. Exact paths remain solely in `governance/project-structure.toml`.
