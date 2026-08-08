# Evaluation Agent Is Review Only

The Cognitive Evaluation Agent Workflow is a bounded, multi-turn review activity, not a
new runtime Controller or graph node. In V1, a Coding Agent follows one concise,
versioned Evaluation Review Protocol to inspect an Evaluation Run Bundle, Node Cognitive
Control Contract, rubric, source seams, and deterministic evidence, then issue a
structured Cognitive Evaluation Review. It cannot modify production prompts, code,
rubrics, bundles, or runtime state, and it cannot rerun costly evaluation execution
autonomously. A Coding Agent or human may use its review as evidence for a separately
governed follow-up change.
