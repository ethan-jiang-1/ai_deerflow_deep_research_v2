# wave0 — Acquire authoritative-source evidence for assigned work

> Reader interface only. This file is not a runtime resource or configuration.
> Code, typed contracts, approved specifications, and tests remain the authority.
> Participation mode: bounded cognitive program
> Commitment state: current accepted
> Current operating mechanism: source-audited retrieval worker with zero-tool repair
> Primary cognitive/control program surface: bounded source metadata candidate
> Deterministic authority boundary: work-unit validator, controller, ledger, and gate admit evidence and route
> Current model-branch evidence: audit only; worker and repair branches

## Node Identity

Workers propose untrusted source metadata; no worker accepts evidence, writes the
ledger, decides retry, or selects a route.

## LLM-Node Authoring Route

For a model-bearing behavior symptom, read these local owners in order before changing
validation, the ledger, or a gate.

1. **Capability and contract:** [`capabilities.py`](capabilities.py) and [`contracts.py`](contracts.py) state the bounded worker and repair responsibilities.
2. **Prompt and context:** [`prompts.py`](prompts.py) separates trusted assignment/output facts from delimited retrieved or draft content.
3. **Feedback and repair:** [`subgraph.py`](subgraph.py) carries only bounded validation feedback into the zero-tool repair branch.
4. **Proof and evaluation:** [`test_wave0_work_units.py`](../../../../../tests/integration/test_wave0_work_units.py) and the [cognitive-program evidence board](../../../../../tests/assets/node_agent_capabilities.py) cover the worker and repair branches without claiming source quality.
5. **Deterministic handoff:** [`subgraph.py`](subgraph.py) and [`node.py`](node.py) send candidates to the existing validator, controller, ledger, and gate; workers cannot admit evidence or select a route.

## From Symptoms

| Symptom | First owner | Proof seam |
| --- | --- | --- |
| Wrong topic, tool posture, or request | `prompts.py` and local capability | `tests/integration/test_wave0_work_units.py` |
| Candidate admission or source identity is wrong | `engine/work_units/validation.py` | `tests/engine/test_wave0_validation.py` |

## Three Cross-Module Facts

1. The two runtime-loaded local capability resources own reusable initial-intake and
   one-repair cognitive methods; `prompts.py` supplies only bounded assignment,
   output-contract, validation-category, and delimited untrusted-data projections.
2. Runtime bridge policy, not Markdown, enforces the initial worker's configured
   retrieval tools, attempt roots, one-to-three call bound, cancellation, and the
   repairer's zero-tool posture.
3. Retrieved material, drafts, and candidates remain untrusted until the existing
   parser, artifact writer, submit validator, ledger, controller, and gate decide
   admission, retry aggregation, and route outcome.

## Route Facts

The Wave0 gate writes `pass`, `repair`, or `exhausted`; the graph consumes that typed
result rather than worker text.

## Evaluation and Verification Order

Start at worker, validator, or gate proof depending on the symptom; inspect bridge
or builder only when the issue crosses their respective boundary.

`wave0-cognitive-program@v1` is a closed deterministic handoff corpus for normal
retrieval, hostile retrieved text, shortfall, one malformed-output repair, and
post-candidate validation isolation. Its capability/schema digests identify the method
under test; it does not establish provider or live source-quality evidence and is not a
selected-live case.
