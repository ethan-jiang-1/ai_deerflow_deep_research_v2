# Evaluation Control And Run Data Are Separate

The Cognitive Evaluation Suite resides under `deep_research_harness/` without mixing
slow-changing control authority and fast-changing execution material. `evals/control/`
contains source-controlled Cases, Rubrics, Review Protocol, and registries.
`evals/runs/` is ignored local output for isolated workspaces, immutable Bundles, and
separate Review Records. The Python Runner remains in the governed
`src/deerflow_deep_research/runtime/evaluation/` source layer. Existing `tests/eval/`
continues to be deterministic pytest coverage, not the Cognitive Evaluation Suite.
