# Runner And Evaluator Are Separate Programs

`evals/` has two independently evolvable layers. A Python Cognitive Evaluation Runner
prepares the environment, runs the production node or flow, and freezes an objective,
private local Evaluation Run Bundle with its execution status. A separate multi-turn
Cognitive Evaluation Agent Workflow, potentially operated by a Coding Agent, inspects
that bundle against the Node Cognitive Control Contract and rubric to produce a cognitive
judgment and guidance. The Runner never evaluates quality; the evaluator never changes
the captured execution.
