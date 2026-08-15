# topic_planning — Decompose a confirmed profile into a research-plan candidate

> Reader interface only. This file is not a runtime resource or configuration.
> Code, typed contracts, approved specifications, and tests remain the authority.
> Participation mode: bounded cognitive program
> Commitment state: current accepted
> Current operating mechanism: source-audited active zero-tool planner and repair loop
> Primary cognitive/control program surface: bounded TopicPlan candidate
> Deterministic authority boundary: `domain/topics.py` materializes ids, coverage, state, and route
> Current model-branch evidence: audit only; two direct branches

## Node Identity

The planner proposes a plan; deterministic materialization creates stable topic
identity and refuses invalid/overlapping coverage.

## LLM-Node Authoring Route

For a model-bearing behavior symptom, read these local owners in order before changing
materialization or graph routing.

1. **Capability and contract:** [`capabilities.py`](capabilities.py) and [`contracts.py`](contracts.py) bound the planner and repair candidates.
2. **Prompt and context:** [`prompts.py`](prompts.py) projects the confirmed profile, output contract, repair feedback, and delimited context.
3. **Feedback and repair:** [`node.py`](node.py) owns the bounded planner-repair loop and its stop condition.
4. **Proof and evaluation:** [`test_topic_planning_node.py`](../../../../../tests/graph/test_topic_planning_node.py) and the [cognitive-program evidence board](../../../../../tests/assets/node_agent_capabilities.py) retain the two branch-local proof/evaluation limits.
5. **Deterministic handoff:** [`topics.py`](../../../domain/topics.py) materializes IDs and coverage; [`node.py`](node.py) returns the typed outcome consumed by the graph.

## From Symptoms

| Symptom | First owner | Proof seam |
| --- | --- | --- |
| Wrong profile inputs or planner role | `prompts.py` | `tests/graph/test_topic_planning_node.py` |
| Invalid topic coverage or ids | `domain/topics.py::materialize_topic_plan` | `tests/graph/test_topic_planning_node.py` |

## Three Cross-Module Facts

1. Confirmed `ResearchState` profile fields are planner input authority.
2. Repair is bounded and distinct from provider recovery.
3. The planner does not write topic registry or graph route authority.

## Route Facts

`build_real` emits typed `next` or `exhausted`; graph topology consumes the result.

## Evaluation and Verification Order

Use the planner/materializer test first, then local capability/prompt checks, and
open graph topology only after the typed node outcome is established.
