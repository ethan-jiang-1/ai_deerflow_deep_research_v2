# Evaluation Runs Use Fresh Isolated Bundles

Every Cognitive Evaluation Runner execution creates a new private local Evaluation Run
Workspace and immutable Evaluation Run Bundle. It does not reuse a prior evaluation's
checkpoint, artifacts, inputs, or bundle namespace, so prior and concurrent executions
cannot influence the observation. The current Local-First `evals/` scope preserves the
complete local materials needed for review; portable redaction is not a requirement.
