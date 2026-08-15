# readiness — Judge per-question evidence sufficiency and answerability

> Reader interface only. This file is not a runtime resource or configuration.
> Code, typed contracts, approved specifications, and tests remain the authority.
> Participation mode: bounded cognitive program
> Commitment state: current accepted
> Current operating mechanism: source-audited active zero-tool evidence critic
> Primary cognitive/control program surface: per-question evidence-sufficiency and answerability candidate
> Deterministic authority boundary: hard rules, materializer, and graph handler own verdict admission and route
> Current model-branch evidence: audit only; readiness/critic direct branch

## Node Identity

Readiness runs one bounded zero-tool critic over accepted ledger evidence. The model
proposes per-question verdicts; hard rules and the materializer retain admission and
route authority.

## LLM-Node Authoring Route

For a model-bearing behavior symptom, read these local owners in order before changing
hard rules, materialization, or a graph edge.

1. **Capability and contract:** [`capabilities.py`](capabilities.py) and [`contracts.py`](contracts.py) bound the evidence-critic verdict candidate.
2. **Prompt and context:** [`critic.py`](critic.py) constructs the zero-tool critic request from accepted ledger evidence and must-answer questions.
3. **Feedback and repair:** [`critic.py`](critic.py) and [`node.py`](node.py) own the closed critic failure/result handling; this node has no invented repair branch.
4. **Proof and evaluation:** [`test_readiness_real.py`](../../../../../tests/unit/test_readiness_real.py) and the [cognitive-program evidence board](../../../../../tests/assets/node_agent_capabilities.py) identify the critic proof and answerability-evaluation limitation.
5. **Deterministic handoff:** [`hard_rules.py`](hard_rules.py), [`materializer.py`](materializer.py), and [`node.py`](node.py) conservatively admit verdicts and return the typed route outcome.

## From Symptoms

Open `critic.py`, `hard_rules.py`, `materializer.py`, and `node.py` for current
readiness facts; use `tests/unit/test_readiness_real.py` first.

## Three Cross-Module Facts

1. Accepted ledger records and must-answer questions bound the critic request.
2. A critic candidate remains read-only until deterministic materialization admits it.
3. Model, policy, parser, or bounds failure projects a conservative non-ready result;
   it cannot fabricate an all-ready route.

## Route Facts

The handler writes the typed readiness outcome consumed by the existing graph edges;
the critic cannot select that route.

## Evaluation and Verification Order

Verify the critic request and candidate path first, then hard-rule/materializer and
route behavior. Treat credentialed answerability evaluation as supplemental.
