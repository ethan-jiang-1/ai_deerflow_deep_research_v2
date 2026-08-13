# Deep Research Agent Charter

> scope: `deep_research_harness/` design and OpenSpec change admission
> authority: guidance only; never runtime control, permission, or current-state truth

This directory is the permanent starting point for the Deep Research product's
cross-cutting design principles. It exists because this project is a downstream
agent inside a larger DeerFlow checkout: the root guides protect the host boundary,
while this charter gives work inside `deep_research_harness/` a local product orientation.

## Start Here

For a change under `deep_research_harness/`, first read the focus gate at the start of
`deep_research_harness/AGENTS.md`, then select one primary module or causal owner. Read its active
capability spec/delta, closest implementation, and lowest responsible test seam.
Read a DeerFlow public interface only when the named local change actually depends
on it and can state the question that interface must answer. A possible future use is
not enough to expand scope. Do not load this whole directory by default; select every
canonical policy from the route table whose trigger actually applies. A change still
has one primary module or causal owner.

## Policy Route

| Trigger | Read this policy | It answers |
|---|---|---|
| Unsure where to start or how much source to inspect | [local context](../policies/local-context.md) | Which module owns the decision and what is the minimum context? |
| Adding a state record, summary, diagnostic, status view, or retained observation | [authority and projections](../policies/authority-and-projections.md) | Which existing source owns the fact, and what remains only a projection? |
| Changing CLI/TUI/API/agent-visible lifecycle output | [participant outcomes](../policies/participant-outcomes.md) | What must people and AI consumers receive from the same typed facts? |
| Adding or revising a human decision, semantic input, visible control, or interaction recovery | [human-interaction integrity](../policies/human-interaction-integrity.md) | What does the person mean, which authority interprets it, and how do visible controls remain actionable? |
| Adding, removing, or materially revising a node's LLM-bearing role, capability policy, tool posture, output admission, repair semantics, or model/non-model classification | [node-agent workflow integrity](../policies/node-agent-workflow-integrity.md) | What bounded cognitive job is present, who enforces tools, and which deterministic owner may admit its candidate? |
| Adding retry, fallback, recovery, terminal handling, or a control check | [control and recovery](../policies/control-and-recovery.md) | Who owns the recovery, what is bounded, and what action is legal next? |
| Adding or changing a model, tool, provider, worker, retry, terminal, diagnostic, or lifecycle projection path | [workflow outcome review](../policies/workflow-outcome-review.md) | What failure table, fact owner, bounded recovery, terminal disposition, next action, and proof seam must the proposal record? |
| Moving a candidate, human judgment, control fact, or deterministic admission/recovery boundary | [control placement](../policies/control-placement.md) | Which deterministic owner receives the fact, which posture protects the boundary, and what evidence proves the handoff? |
| Opening, revising, or reviewing an OpenSpec change | [change admission](../policies/change-admission.md) | What belongs in the charter, a policy, an owning spec, or an operational procedure? |
| Adding or revising a contributor entry document | [agent information map](../policies/agent-information-map.md) | Which reader needs it, what is the smallest route, and where does detail belong? |

## Where Rules Belong

| Kind of statement | Canonical home | Does not own |
|---|---|---|
| Durable concept vocabulary / terminology map | [concepts.md](concepts.md) | Behavior, routes, or a per-change rule |
| Durable, cross-capability Deep Research principle | [charter.md](charter.md) | Runtime behavior or a one-off feature contract |
| Repeated design/review rule with a concrete trigger | `../policies/<topic>.md` | State fields, routes, commands, or permissions |
| Observable behavior, schema, action, or security boundary | Owning capability main spec and active delta | A different capability's behavior |
| Operator procedure or incident response | Scoped runbook or operational document | Current run state or a behavioral requirement |
| Current fact and conformance evidence | Owning typed contract, checkpoint/ledger/content authority, code, and tests | Future policy or approval |

## Authority Boundary

The charter helps a contributor choose the right owner. It cannot invent a graph
route, provider retry, command, state field, user authorization, checkpoint fact, or
recovery capability. Approved main specs own required behavior; one active delta owns
pending behavior; runtime authorities and executable contracts own current facts.
Human-facing text, AI-facing projections, summaries, diagnostics, and this directory
remain explanations of those facts.

## Adding A Policy

Add a policy only when a rule recurs across more than one capability and has a
specific trigger that lets a contributor know when to read it. Keep it shorter and
less authoritative than the work it guides. Give it a route-table entry, its
non-authority boundary, and an owning capability/spec reference for any concrete
behavior. A proposal for new behavior belongs in an OpenSpec delta even when a policy
motivates it.
