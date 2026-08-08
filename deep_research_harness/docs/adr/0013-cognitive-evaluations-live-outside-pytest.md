# Cognitive Evaluations Live Outside Pytest

Deep Research maintains an independently invoked `evals/` system beside `tests/` for
long-running, potentially credentialed Cognitive Evaluation Suite runs. Each
LLM-bearing node has at least one bounded Node Cognitive Smoke Scenario that exercises
the production node/bridge using a declared scenario, budget, and rubric. Normal
deterministic verification does not collect these runs. A dedicated Cognitive Evaluation
Runner, rather than pytest, performs preflight, execution, and private local
result-bundle retention. It does not apply a quality rubric or claim that one run proves
lasting model quality.
