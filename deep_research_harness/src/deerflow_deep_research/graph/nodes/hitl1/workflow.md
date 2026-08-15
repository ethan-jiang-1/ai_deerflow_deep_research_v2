# hitl1 — Turn a human request into an approved research profile

> Reader interface only. This file is not a runtime resource or configuration.
> Code, typed contracts, approved specifications, and tests remain the authority.
> Participation mode: bounded cognitive program
> Commitment state: current accepted
> Current operating mechanism: source-audited active model loop with graph-owned human input
> Primary cognitive/control program surface: advisory brief and semantic reply candidate
> Deterministic authority boundary: profile parser/domain and graph handler publish profile and route
> Current model-branch evidence: audit only; four direct branches

## Node Identity

The model proposes a brief or semantic candidate; it cannot accept a reply, publish
`profile.json`, mutate checkpoint authority, or choose a route.

## LLM-Node Authoring Route

For a model-bearing behavior symptom, read these local owners in order before changing
the parser or graph path.

1. **Capability and contract:** [`capabilities.py`](capabilities.py) and [`contracts.py`](contracts.py) define the bounded brief and semantic-candidate responsibility.
2. **Prompt and context:** [`prompts.py`](prompts.py) composes the original question, proposal, reply, and constrained model-visible request.
3. **Feedback and repair:** [`node.py`](node.py) owns bounded invalid-output feedback and the repair invocation boundary.
4. **Proof and evaluation:** [`test_hitl1_node.py`](../../../../../tests/graph/test_hitl1_node.py) and the [cognitive-program evidence board](../../../../../tests/assets/node_agent_capabilities.py) identify the four current branches and their limits.
5. **Deterministic handoff:** [`node.py`](node.py) parses and resolves candidates; only the typed/domain and graph owners publish a profile or route.

## From Symptoms

| Symptom | First owner | Proof seam |
| --- | --- | --- |
| Brief or semantic candidate is wrong | `prompts.py`, then `node.py` | `tests/graph/test_hitl1_node.py` |
| Reply/correlation or profile publication is wrong | `node.py::_classify_proposal_reply`, `domain/human_interaction.py` | `tests/graph/test_hitl1_node.py` |

## Three Cross-Module Facts

1. Local capability bodies define model-visible policy; metadata does not grant authority.
2. `AcceptedHumanResponse` correlation is graph/domain-owned.
3. The parser/domain owner, not the model, admits a candidate and publishes profile state.

## Route Facts

`node.py::build_real` returns typed outcomes; the graph consumes `accepted`,
`needs_followup`, `cancel`, or `exhausted`.

## Evaluation and Verification Order

Start with the named HITL1 test, then capability/prompt tests for model-visible
changes, then the digest-bound `hitl1-cognitive-program@v1` control case for normal
confirmation, revision, question, ambiguity, adversarial reply, and repair. Its
ordinary execution proves only deterministic resource/candidate/admission handoff;
the manifest cannot publish profile State or choose a route. Selected credentialed
evaluation remains separately preflighted and is never release authority. Inspect
`graph/builder.py` only for a typed route symptom.
